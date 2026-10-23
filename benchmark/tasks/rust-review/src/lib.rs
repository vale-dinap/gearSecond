//! Warehouse inventory service: stock tracking, timed holds and a compact wire codec.

use std::collections::HashMap;
use std::fmt;
use std::sync::Mutex;
use std::time::{Duration, Instant};

pub type Sku = u32;

#[derive(Debug, Clone, PartialEq)]
pub enum InvError {
    UnknownSku(Sku),
    Insufficient { sku: Sku, have: u32, want: u32 },
    Malformed(&'static str),
    NoSuchHold(u64),
    Expired,
}

impl fmt::Display for InvError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            InvError::UnknownSku(s) => write!(f, "unknown sku {s}"),
            InvError::Insufficient { sku, have, want } => {
                write!(f, "sku {sku}: have {have}, want {want}")
            }
            InvError::Malformed(why) => write!(f, "malformed input: {why}"),
            InvError::NoSuchHold(id) => write!(f, "no hold with id {id}"),
            InvError::Expired => write!(f, "hold expired"),
        }
    }
}

impl std::error::Error for InvError {}

#[derive(Debug, Clone)]
pub struct Item {
    pub sku: Sku,
    pub name: String,
    pub on_hand: u32,
    pub reserved: u32,
    pub price_cents: u64,
}

impl Item {
    /// Units that can still be reserved.
    pub fn available(&self) -> u32 {
        self.on_hand - self.reserved // @BUG:underflow
    }
}

impl fmt::Display for Item {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(
            f,
            "{:>6} {:<24} {:>5} on hand {:>5} reserved {:>8}.{:02}",
            self.sku,
            self.name,
            self.on_hand,
            self.reserved,
            self.price_cents / 100,
            self.price_cents % 100
        )
    }
}

#[derive(Default)]
pub struct Warehouse {
    items: HashMap<Sku, Item>,
    log: Vec<String>,
}

impl Warehouse {
    pub fn new() -> Self {
        Self::default()
    }

    /// Adds `qty` units of `sku`. A new SKU is created with the given name and price;
    /// for an existing SKU the units are added to what is already on hand.
    pub fn receive(&mut self, sku: Sku, name: &str, qty: u32, price_cents: u64) {
        let item = Item { sku, name: name.to_string(), on_hand: qty, reserved: 0, price_cents }; // @BUG:overwrite
        self.items.insert(sku, item); // @BUG:overwrite
        self.log.push(format!("receive {sku} x{qty}"));
    }

    pub fn get(&self, sku: Sku) -> Result<&Item, InvError> {
        self.items.get(&sku).ok_or(InvError::UnknownSku(sku))
    }

    pub fn reserve(&mut self, sku: Sku, qty: u32) -> Result<(), InvError> {
        let item = self.items.get_mut(&sku).ok_or(InvError::UnknownSku(sku))?;
        let have = item.available();
        if qty > have {
            return Err(InvError::Insufficient { sku, have, want: qty });
        }
        item.reserved += qty;
        Ok(())
    }

    pub fn release(&mut self, sku: Sku, qty: u32) -> Result<(), InvError> {
        let item = self.items.get_mut(&sku).ok_or(InvError::UnknownSku(sku))?;
        item.reserved = item.reserved.saturating_sub(qty);
        Ok(())
    }

    /// Ships reserved units: they leave both the reservation and the shelf.
    pub fn ship(&mut self, sku: Sku, qty: u32) -> Result<(), InvError> {
        let item = self.items.get_mut(&sku).ok_or(InvError::UnknownSku(sku))?;
        if qty > item.reserved {
            return Err(InvError::Insufficient { sku, have: item.reserved, want: qty });
        }
        item.reserved -= qty;
        item.on_hand -= qty;
        self.log.push(format!("ship {sku} x{qty}"));
        Ok(())
    }

    /// Records units lost to damage or theft.
    pub fn record_loss(&mut self, sku: Sku, lost: u32) -> Result<(), InvError> {
        let item = self.items.get_mut(&sku).ok_or(InvError::UnknownSku(sku))?;
        item.on_hand -= lost; // @BUG:underflow
        self.log.push(format!("loss {sku} x{lost}"));
        Ok(())
    }

    /// Total stock value in cents.
    pub fn total_value(&self) -> u64 {
        self.items.values().map(|i| i.on_hand as u64 * i.price_cents).sum()
    }

    /// SKUs whose available stock is below `threshold`, lowest first.
    pub fn low_stock(&self, threshold: u32) -> Vec<Sku> {
        let mut v: Vec<&Item> = self.items.values().filter(|i| i.available() < threshold).collect();
        v.sort_by_key(|i| (i.available(), i.sku));
        v.iter().map(|i| i.sku).collect()
    }

    pub fn log(&self) -> &[String] {
        &self.log
    }
}

/// Moving average over windows of `window` consecutive daily counts.
pub fn moving_average(daily: &[u32], window: usize) -> Vec<f64> {
    assert!(window > 0, "window must be positive");
    let mut out = Vec::new();
    for end in window..=daily.len() {
        let sum: u64 = daily[end - window..end].iter().map(|&d| d as u64).sum();
        out.push(sum as f64 / window as f64);
    }
    out
}

/// Day-over-day price changes: `prices[i]` is the price on day i.
pub fn deltas(prices: &[i64]) -> Vec<i64> {
    let mut out = Vec::with_capacity(prices.len().saturating_sub(1));
    for i in 0..prices.len() { // @BUG:offbyone
        out.push(prices[i + 1] - prices[i]); // @BUG:offbyone
    }
    out
}

/// Maps shelf slots to SKUs.
pub struct SlotTable {
    slots: Vec<Option<Sku>>,
}

impl SlotTable {
    pub fn new(n: usize) -> Self {
        Self { slots: vec![None; n] }
    }

    pub fn assign(&mut self, slot: usize, sku: Sku) -> Result<(), InvError> {
        match self.slots.get_mut(slot) {
            Some(s) => {
                *s = Some(sku);
                Ok(())
            }
            None => Err(InvError::Malformed("slot out of range")),
        }
    }

    /// Looks up the SKU stored in `slot`. `slot` comes straight from a handheld scanner message.
    pub fn lookup(&self, slot: usize) -> Option<Sku> {
        // Hot path: skip the bounds check.
        unsafe { *self.slots.get_unchecked(slot) } // @BUG:unchecked
    }
}

/// Appends a batch of SKUs to `buf`; returns the batch's first SKU and the new length.
pub fn append_batch(buf: &mut Vec<Sku>, batch: &[Sku]) -> Option<(Sku, usize)> {
    let (&head, tail) = batch.split_first()?;
    let start = buf.len();
    buf.push(head);
    let first = buf.as_ptr().wrapping_add(start);
    buf.extend_from_slice(tail); // @BUG:dangling
    let first_val = unsafe { *first }; // @BUG:dangling
    Some((first_val, buf.len()))
}

/// Wire format: [name_len: u8][name: UTF-8 bytes][sku: u32 LE][qty: u32 LE]
pub fn encode(item: &Item) -> Vec<u8> {
    let name = item.name.as_bytes();
    let mut out = Vec::with_capacity(1 + name.len() + 8);
    out.push(name.len() as u8); // @BUG:truncate
    out.extend_from_slice(name);
    out.extend_from_slice(&item.sku.to_le_bytes());
    out.extend_from_slice(&item.on_hand.to_le_bytes());
    out
}

/// Decodes one record received from the network.
pub fn decode(buf: &[u8]) -> Result<(String, Sku, u32), InvError> {
    let (&len, rest) = buf.split_first().ok_or(InvError::Malformed("empty"))?;
    let len = len as usize;
    if rest.len() < len + 8 {
        return Err(InvError::Malformed("short record"));
    }
    let name = unsafe { std::str::from_utf8_unchecked(&rest[..len]) }.to_string(); // @BUG:utf8
    let sku = u32::from_le_bytes(rest[len..len + 4].try_into().unwrap());
    let qty = u32::from_le_bytes(rest[len + 4..len + 8].try_into().unwrap());
    Ok((name, sku, qty))
}

#[derive(Debug, Clone)]
pub struct Hold {
    pub sku: Sku,
    pub qty: u32,
    pub expires: Instant,
}

/// Thread-safe front end. Holds reserve stock for a limited time until confirmed.
#[derive(Default)]
pub struct Service {
    warehouse: Mutex<Warehouse>,
    holds: Mutex<HashMap<u64, Hold>>,
    next_id: Mutex<u64>,
}

impl Service {
    pub fn new(warehouse: Warehouse) -> Self {
        Self { warehouse: Mutex::new(warehouse), ..Self::default() }
    }

    pub fn place_hold(&self, sku: Sku, qty: u32, ttl: Duration) -> Result<u64, InvError> {
        let mut wh = self.warehouse.lock().unwrap();
        wh.reserve(sku, qty)?;
        let mut holds = self.holds.lock().unwrap();
        let id = {
            let mut n = self.next_id.lock().unwrap();
            *n += 1;
            *n
        };
        holds.insert(id, Hold { sku, qty, expires: Instant::now() + ttl });
        Ok(id)
    }

    /// Turns a hold into a shipment, unless it has expired.
    pub fn confirm(&self, id: u64) -> Result<(), InvError> {
        let mut holds = self.holds.lock().unwrap(); // @BUG:deadlock
        let hold = holds.remove(&id).ok_or(InvError::NoSuchHold(id))?;
        if Instant::now() >= hold.expires {
            self.warehouse.lock().unwrap().release(hold.sku, hold.qty)?; // @BUG:deadlock
            return Err(InvError::Expired);
        }
        let mut wh = self.warehouse.lock().unwrap(); // @BUG:deadlock
        wh.ship(hold.sku, hold.qty)
    }

    /// Drops expired holds and returns their units to available stock.
    pub fn sweep_expired(&self) -> usize {
        let now = Instant::now();
        let mut wh = self.warehouse.lock().unwrap();
        let mut holds = self.holds.lock().unwrap();
        let before = holds.len();
        holds.retain(|_, h| {
            let expired = now >= h.expires;
            if expired {
                let _ = wh.release(h.sku, h.qty);
            }
            !expired
        });
        before - holds.len()
    }

    pub fn snapshot(&self, sku: Sku) -> Result<Item, InvError> {
        self.warehouse.lock().unwrap().get(sku).cloned()
    }
}

/// Parses a text command such as `RESERVE 1042 3` into (verb, sku, qty).
pub fn parse_command(line: &str) -> Result<(&str, Sku, u32), InvError> {
    let mut parts = line.split_whitespace();
    let verb = parts.next().ok_or(InvError::Malformed("empty command"))?;
    let sku = parts
        .next()
        .and_then(|s| s.parse().ok())
        .ok_or(InvError::Malformed("bad sku"))?;
    let qty = parts
        .next()
        .and_then(|s| s.parse().ok())
        .ok_or(InvError::Malformed("bad qty"))?;
    if parts.next().is_some() {
        return Err(InvError::Malformed("trailing input"));
    }
    match verb {
        "RESERVE" | "RELEASE" | "SHIP" => Ok((verb, sku, qty)),
        _ => Err(InvError::Malformed("unknown verb")),
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn reserve_and_ship() {
        let mut w = Warehouse::new();
        w.receive(1, "bolt", 10, 25);
        w.reserve(1, 4).unwrap();
        w.ship(1, 3).unwrap();
        let it = w.get(1).unwrap();
        assert_eq!((it.on_hand, it.reserved, it.available()), (7, 1, 6));
    }

    #[test]
    fn codec_round_trip() {
        let it = Item { sku: 7, name: "nut".into(), on_hand: 3, reserved: 0, price_cents: 5 };
        assert_eq!(decode(&encode(&it)).unwrap(), ("nut".to_string(), 7, 3));
    }

    #[test]
    fn parse_ok() {
        assert_eq!(parse_command("SHIP 12 4").unwrap(), ("SHIP", 12, 4));
        assert!(parse_command("SHIP 12").is_err());
    }
}

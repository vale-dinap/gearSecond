"""Order utilities for a small shop backend."""
from datetime import date


def page_count(total_items, per_page):
    """Number of pages needed to show total_items, per_page items per page."""
    return total_items // per_page  # @BUG:pages


def add_tag(order, tag, tags=[]):  # @BUG:default
    """Return the order's tags with `tag` added; tags are never shared between orders."""
    tags.append(tag)
    order["tags"] = tags
    return tags


def average_total(orders):
    """Average order total; 0.0 when there are no orders."""
    return sum(o["total"] for o in orders) / len(orders)  # @BUG:empty


def in_window(day: date, start: date, end: date) -> bool:
    """True if day falls within [start, end], both ends inclusive."""
    return start <= day < end  # @BUG:inclusive


def apply_coupon(total, percent):
    """Apply a percentage coupon (0 to 100) and round to cents."""
    if not 0 <= percent <= 100:
        raise ValueError("percent must be between 0 and 100")
    return round(total * (1 - percent / 100), 2)


def recent_orders(orders, today: date, days=7):
    """Orders placed within the last `days` days, newest first."""
    picked = [o for o in orders if (today - o["day"]).days <= days]
    return sorted(picked, key=lambda o: o["day"], reverse=True)

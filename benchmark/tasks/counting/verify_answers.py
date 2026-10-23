"""Recompute every answer in problems.json by brute force and check the answer key.

Usage: python verify_answers.py   (takes about a minute; the permutation counts dominate)
"""
import itertools
import json
from functools import lru_cache
from pathlib import Path

STEPS = ((1, 0), (-1, 0), (0, 1), (0, -1))


def walks(k, end_ok):
    """Count k-step self-avoiding walks from the origin whose end point satisfies end_ok."""
    tot = 0

    def go(x, y, seen, left):
        nonlocal tot
        if left == 0:
            tot += end_ok(x, y)
            return
        for dx, dy in STEPS:
            q = (x + dx, y + dy)
            if q not in seen:
                seen.add(q)
                go(q[0], q[1], seen, left - 1)
                seen.remove(q)

    go(0, 0, {(0, 0)}, k)
    return tot


def coins(total, values=(1, 2, 5, 10, 20, 50)):
    ways = [1] + [0] * total
    for v in values:
        for s in range(v, total + 1):
            ways[s] += ways[s - v]
    return ways[total]


def indep(rows, cols):
    states = [s for s in range(1 << rows) if not (s & (s >> 1))]
    cnt = {s: 1 for s in states}
    for _ in range(cols - 1):
        cnt = {t: sum(c for s, c in cnt.items() if not (s & t)) for t in states}
    return sum(cnt.values())


@lru_cache(None)
def band(x, y):
    if (x, y) in {(3, 2), (5, 6), (6, 4)} or abs(x - y) > 2:
        return 0
    if (x, y) == (0, 0):
        return 1
    return (band(x - 1, y) if x else 0) + (band(x, y - 1) if y else 0)


ANSWERS = {
    "coins": lambda: coins(137),
    "indep": lambda: indep(3, 7),
    "rooks": lambda: sum(1 for p in itertools.permutations(range(8))
                         if all(p[i] != i and p[i] != 7 - i for i in range(8))),
    "abc": lambda: sum(1 for s in itertools.product("ABC", repeat=11)
                       if s.count("A") == 4 and all(s[i] != s[i + 1] for i in range(10))),
    "subsets": lambda: sum(1 for c in itertools.combinations(range(1, 18), 5) if sum(c) % 7 == 0),
    "saw": lambda: walks(8, lambda x, y: y == 0),
    "band": lambda: band(9, 9),
    "succ": lambda: sum(1 for p in itertools.permutations(range(1, 10))
                        if sum(p[i] == i + 1 for i in range(9)) == 2
                        and all(p[i + 1] != p[i] + 1 for i in range(8))),
    "digits6": lambda: sum(1 for m in range(100001, 1000000, 11) if sum(map(int, str(m))) == 30),
    "saw_diag": lambda: walks(8, lambda x, y: x == y),
    "saw_adj": lambda: walks(9, lambda x, y: abs(x) + abs(y) == 1),
    "saw_quad": lambda: walks(8, lambda x, y: x > 0 and y > 0),
}

if __name__ == "__main__":
    problems = json.loads((Path(__file__).parent / "problems.json").read_text(encoding="utf-8"))
    bad = 0
    for p in problems:
        got = str(ANSWERS[p["id"]]())
        ok = got == p["answer"]
        bad += not ok
        print(f"{p['id']:<9} key={p['answer']:<6} computed={got:<6} {'ok' if ok else 'MISMATCH'}")
    raise SystemExit(bad)

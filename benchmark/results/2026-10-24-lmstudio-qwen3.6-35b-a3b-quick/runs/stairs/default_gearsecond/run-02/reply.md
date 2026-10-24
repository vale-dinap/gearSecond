Let f(n) be the number of ways to reach step n.
To reach step n, you must come from step n-1 (taking 1 step) or n-2 (taking 2 steps).
Recurrence: f(n) = f(n-1) + f(n-2).
Base cases: f(1) = 1, f(2) = 2.
Compute iteratively:
f(3) = 1 + 2 = 3
f(4) = 2 + 3 = 5
f(5) = 3 + 5 = 8
f(6) = 5 + 8 = 13
f(7) = 8 + 13 = 21
f(8) = 13 + 21 = 34
f(9) = 21 + 34 = 55
f(10) = 34 + 55 = 89
f(11) = 55 + 89 = 144
f(12) = 89 + 144 = 233
ANSWER: 233
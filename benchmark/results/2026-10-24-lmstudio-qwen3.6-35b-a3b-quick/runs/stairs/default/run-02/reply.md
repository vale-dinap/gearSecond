To solve this problem, we can look for a pattern based on smaller numbers of steps. Let $f(n)$ be the number of ways to climb a staircase of $n$ steps.

To reach the $n$-th step, you must have come from either the $(n-1)$-th step (taking a 1-step move) or the $(n-2)$-th step (taking a 2-step move). Therefore, the total number of ways to reach step $n$ is the sum of the ways to reach step $n-1$ and step $n-2$.

This gives us the recurrence relation:
$$f(n) = f(n-1) + f(n-2)$$

Let's calculate the number of ways for each step count starting from 1:

1.  **1 step:** You can only take one 1-step.
    *   $f(1) = 1$
2.  **2 steps:** You can take two 1-steps (1+1) or one 2-step (2).
    *   $f(2) = 2$
3.  **3 steps:** You can reach step 3 from step 2 (add 1) or step 1 (add 2).
    *   $f(3) = f(2) + f(1) = 2 + 1 = 3$
4.  **4 steps:**
    *   $f(4) = f(3) + f(2) = 3 + 2 = 5$
5.  **5 steps:**
    *   $f(5) = f(4) + f(3) = 5 + 3 = 8$
6.  **6 steps:**
    *   $f(6) = f(5) + f(4) = 8 + 5 = 13$
7.  **7 steps:**
    *   $f(7) = f(6) + f(5) = 13 + 8 = 21$
8.  **8 steps:**
    *   $f(8) = f(7) + f(6) = 21 + 13 = 34$
9.  **9 steps:**
    *   $f(9) = f(8) + f(7) = 34 + 21 = 55$
10. **10 steps:**
    *   $f(10) = f(9) + f(8) = 55 + 34 = 89$
11. **11 steps:**
    *   $f(11) = f(10) + f(9) = 89 + 55 = 144$
12. **12 steps:**
    *   $f(12) = f(11) + f(10) = 144 + 89 = 233$

This sequence is a variation of the Fibonacci sequence. By summing the previous two values iteratively, we find that there are 233 distinct ways to climb the staircase.

ANSWER: 233
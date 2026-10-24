To reach the top of a 12‑step staircase you may take steps of size 1 or 2.  
Let \(f(n)\) denote the number of different ways to climb an \(n\)-step stair.

* **Base cases**  
  * \(f(0)=1\): there is one way to stay at the bottom (do nothing).  
  * \(f(1)=1\): only a single step of size 1.

* **Recurrence relation**  
  For \(n\ge2\) the first move can be either:
  - a single step, after which we must climb the remaining \(n-1\) steps (\(f(n-1)\) ways);
  - or a double step, after which we must climb the remaining \(n-2\) steps (\(f(n-2)\) ways).

  Hence  
  \[
  f(n)=f(n-1)+f(n-2).
  \]

This is exactly the Fibonacci recurrence. Computing successively:

\[
\begin{aligned}
f(0)&=1\\
f(1)&=1\\
f(2)&=f(1)+f(0)=2\\
f(3)&=f(2)+f(1)=3\\
f(4)&=5\\
f(5)&=8\\
f(6)&=13\\
f(7)&=21\\
f(8)&=34\\
f(9)&=55\\
f(10)&=89\\
f(11)&=144\\
f(12)&=233.
\end{aligned}
\]

Thus there are **233** distinct sequences of 1‑step and 2‑step moves that reach the top.

An alternative counting uses binomial coefficients.  
If we use \(k\) double steps, then \(2k\) steps are taken by them, leaving \(12-2k\) single steps.  
The total number of moves is \((12-k)\), and we must choose which of these positions contain the \(k\) doubles:
\[
\text{ways for } k=0,\dots,6:\quad
\binom{12}{0},\,\binom{11}{1},\,\binom{10}{2},\,\binom{9}{3},
\,\binom{8}{4},\,\binom{7}{5},\,\binom{6}{6}
= 1+11+45+84+70+21+1 = 233.
\]

Both approaches give the same result.

ANSWER: 233
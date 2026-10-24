Let \(f(n)\) be the number of ways to climb a staircase with \(n\) steps when each jump can be either 1 or 2 steps.

**Reasoning**

* The first jump can be  
  * **One step**, leaving a staircase of \(n-1\) steps.  
  * **Two steps**, leaving a staircase of \(n-2\) steps.

Hence every way to climb \(n\) steps is obtained by adding the first jump (1 or 2) to a way of climbing the remaining staircase:

\[
f(n)=f(n-1)+f(n-2).
\]

This recurrence is exactly the Fibonacci recursion.  
We need initial values:
* For a staircase with **0** steps there is one trivial way – do nothing: \(f(0)=1\).  
* With **1** step, only a single 1‑step jump works: \(f(1)=1\).

Now compute successively:

\[
\begin{aligned}
f(2)&=f(1)+f(0)=1+1=2,\\
f(3)&=f(2)+f(1)=2+1=3,\\
f(4)&=f(3)+f(2)=3+2=5,\\
f(5)&=f(4)+f(3)=5+3=8,\\
f(6)&=f(5)+f(4)=8+5=13,\\
f(7)&=f(6)+f(5)=13+8=21,\\
f(8)&=f(7)+f(6)=21+13=34,\\
f(9)&=f(8)+f(7)=34+21=55,\\
f(10)&=f(9)+f(8)=55+34=89,\\
f(11)&=f(10)+f(9)=89+55=144,\\
f(12)&=f(11)+f(10)=144+89=233.
\end{aligned}
\]

Thus there are **233** distinct sequences of 1‑step and 2‑step moves that climb a 12‑step staircase.

ANSWER: 233
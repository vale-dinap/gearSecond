Count integer solutions to  
\(d_1+d_2+d_3+d_4=10\) with \(d_1\in[1,9]\), \(d_{i}\in[0,9]\ (i>1)\).  

Set \(x_1=d_1-1\Rightarrow x_1\ge0,\;x_1\le8\).  
Equation becomes \(x_1+d_2+d_3+d_4=9\).

Unrestricted non‑negative solutions: \(\binom{9+4-1}{4-1}=\binom{12}{3}=220\).

Only violation is \(x_1>8\); since sum is 9, the only impossible case is \(x_1=9\) (then others zero).  
Subtract that one solution.

Thus number of valid 4‑digit integers: \(220-1=219\).

ANSWER: 219
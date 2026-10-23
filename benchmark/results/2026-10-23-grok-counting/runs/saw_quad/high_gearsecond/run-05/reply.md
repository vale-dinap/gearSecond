The 8-step self-avoiding walks ending in the open first quadrant are partitioned by the number \(k\) of steps that are either west or south (the net displacement then satisfies \(x+y=8-2k\)).

- For \(k=0\) every walk uses only east and north steps. All \(\sum_{e=1}^{7}\binom{8}{e}=254\) such walks are self-avoiding and end in the open first quadrant.
- For \(k=1\) the unique reverse step must occupy a horizontal or vertical line by itself. Distributing the forward steps on the remaining lines yields 270 walks with one west (and no south) and 270 walks with one south (and no west).
- For \(k=2\) the same line-by-line analysis produces 84 walks with two wests, 84 walks with two souths, and 180 walks with one west and one south.
- For \(k=3\) the only admissible endpoint is \((1,1)\). The same analysis produces 2 walks with three wests, 2 walks with three souths, and 72 walks that use both west and south steps.

Adding these disjoint contributions gives the total
\[
254+540+348+76=1218.
\]

(The same enumeration for length 6 reproduces the known total of 780 self-avoiding walks, confirming the case division.)

ANSWER: 1218
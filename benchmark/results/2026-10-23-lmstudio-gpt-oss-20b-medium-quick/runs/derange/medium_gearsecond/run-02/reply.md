To count the derangements of six distinct numbers, apply inclusion–exclusion to the set of all \(6!\) permutations.

Let \(A_i\) be the set of permutations where number \(i\) stays in its original position.  
We want \(|S| - |A_1\cup A_2\cup\dots\cup A_6|\).

Using inclusion–exclusion,

\[
D(6)=6!-\binom61\,5!+\binom62\,4!-\binom63\,3!+\binom64\,2!
      -\binom65\,1!+\binom66\,0!.
\]

Compute each term:

* \(6!=720\)
* \(\binom61 5!=6\times120=720\)
* \(\binom62 4!=15\times24=360\)
* \(\binom63 3!=20\times6=120\)
* \(\binom64 2!=15\times2=30\)
* \(\binom65 1!=6\times1=6\)
* \(\binom66 0!=1\)

Now combine with alternating signs:

\[
720-720+360-120+30-6+1 = 265.
\]

Thus, there are **265** permutations of the numbers \(1,\dots,6\) in which no number occupies its original position.

ANSWER: 265
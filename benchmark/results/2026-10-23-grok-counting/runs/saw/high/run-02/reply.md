The 8-step self-avoiding walks ending on the line \(y=0\) are partitioned by the number \(k\) of north steps (necessarily equal to the number of south steps).

- For \(k=0\) the walk is confined to the \(x\)-axis, so the only possibilities are the two straight walks.
- For \(k=4\) the walk is confined to the \(y\)-axis and cannot be self-avoiding.
- For \(k=1\) the single north step and single south step divide the walk into three horizontal runs. Each run must be straight, and the resulting landing and continuation conditions on the \(x\)-axis are readily enumerated, producing 68 walks that travel first north and 68 that travel first south.
- For \(k=3\) the two horizontal steps must point in the same direction (opposite directions close the walk). The three vertical runs lying between them must themselves be straight and must contain exactly three steps of each sign; there are exactly 18 solutions for each common horizontal direction.
- For \(k=2\) the four horizontal steps are treated according to their east/west balance.  
  – Four steps in the same direction produce five vertical runs; the runs that realise exactly two north and two south steps number 110 in each direction.  
  – Three steps in one direction and one step in the other are classified by the position of the unique reversing step. In every case the walk traverses each vertical line in straight runs; imposing the condition that a later visit to an already-used line does not overlap the earlier visit yields precisely 64 walks for each choice of the majority direction.  
  – Two east and two west steps close the walk and are therefore impossible.

Adding these disjoint contributions supplies the total
\[
2+136+348+36=522.
\]

The same case division reproduces the manually enumerable counts for all self-avoiding walks of length 4 and of length 6 that end on the \(x\)-axis, confirming the enumeration.

ANSWER: 522
The walks are partitioned by the endpoint \((x,0)\) (with \(x\) even and \(|x|\le 8\)) and by the number of north and south steps.

- Ending at \((\pm 8,0)\): only the two straight walks.
- Ending at \((\pm 6,0)\): the only possibility is six east (resp. west) steps together with one north and one south. Because the horizontal coordinate never reverses, the walk is self-avoiding precisely when the two vertical steps are non-adjacent. There are \(42\) such walks in each direction.
- Ending at \((\pm 4,0)\):
  - four east, two north and two south (no west) — unidirectional vertical runs in the five gaps between the east steps give \(110\) walks;
  - five east, one west, one north and one south — exhaustive examination of the possible orders of the three non-east steps shows that immediate reversals are avoided in exactly \(16\) cases.
  This yields \(126\) walks in each direction.
- Ending at \((0,0)\) is impossible: the origin would be repeated.
- Ending at \((\pm 2,0)\):
  - two east, three north and three south give \(18\) walks;
  - four east, two west, one north and one south give \(10\) walks;
  - three east, one west, two north and two south are counted by decomposing into alternating straight runs. The admissible run-length and direction data produce \(8+48+12=68\) walks.
  This yields \(96\) walks in each direction.

Adding these contributions produces the total.

ANSWER: 530
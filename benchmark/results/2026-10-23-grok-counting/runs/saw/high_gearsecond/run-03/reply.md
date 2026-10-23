The 8-step self-avoiding walks ending on the \(x\)-axis are equinumerous in pairs \(\pm x\), and none can end at the origin (the origin would be repeated). Thus it is enough to count the walks that terminate at \((8,0)\), \((6,0)\), \((4,0)\) and \((2,0)\) and double.

The possible step inventories are fixed by the net displacement and the requirement that the number of north steps equals the number of south steps. Each inventory is then enumerated by decomposing the walk into unidirectional vertical runs separated by east steps (or, when a single west step is present, into a partially-directed prefix, the west step, and a partially-directed suffix) and imposing the condition that no lattice point is repeated:

- \((8,0)\): only the straight walk of eight east steps, hence \(1\) walk;
- \((6,0)\): six east steps together with one north and one south; the two vertical steps must be separated by at least one east step, giving \(21\) walks with north before south and \(21\) with south before north, hence \(42\) walks;
- \((4,0)\): \(110\) walks that use four east, two north and two south, plus \(16\) walks that use five east, one west, one north and one south, hence \(126\) walks;
- \((2,0)\): \(18\) walks that use two east, three north and three south, plus \(64\) walks that use three east, one west, two north and two south, plus \(10\) walks that use four east, two west, one north and one south, hence \(92\) walks.

(The same decompositions reproduce the exactly enumerable counts for all shorter lengths, confirming the case analysis.)

Adding these contributions yields
\[
2(1+42+126+92)=522.
\]

ANSWER: 522
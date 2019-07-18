# ant_assignment

Assignment code for SWEN90006 (Software Testing and Reliability) at the University of Melbourne. Semester 2, 2018. Adapted for use with swen-tourney

The folder structure is:

- lib/ contains external libraries used by the virtual machine
- programs/ contains the original source code for the virtual machine, and copies of the virtual machine in which to insert mutants
- results/ contains the output traces as a result of running ant tests
- tests/ contains the tests to run on the virtual machine. Write your tests here
- build.xml is an ant build script to test the virtual machine with. To run: `ant test -Dprogram="" -Dtest=""`

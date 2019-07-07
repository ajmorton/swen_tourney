package swen90006.machine;

import java.util.List;
import java.util.ArrayList;
import java.nio.charset.Charset;
import java.nio.file.Path;
import java.nio.file.Files;
import java.nio.file.FileSystems;

import org.junit.*;
import static org.junit.Assert.*;

public class BoundaryTests
{
  //Any method annotated with "@Before" will be executed before each test,
  //allowing the tester to set up some shared resources.
  @Before public void setUp()
  {
  }

  //Any method annotated with "@After" will be executed after each test,
  //allowing the tester to release any shared resources used in the setup.
  @After public void tearDown()
  {
  }

  //Boundary test 1
  @Test public void test01()
  {
    
    List<String> lines = new ArrayList<String>();
    lines.add("MOV R31 4");
    lines.add("RET R31");
    Machine m = new Machine();
    assertEquals(m.execute(lines), 4);
  }

  //Boundary test 2
  @Test public void test02()
  {
    List<String> lines = new ArrayList<String>();
    lines.add("MOV R0 4");
    lines.add("RET R0");
    Machine m = new Machine();
    assertEquals(m.execute(lines), 4);
  }

  //Boundary test 3
  @Test (expected = InvalidInstructionException.class)
  public void test03()
  {
    List<String> lines = new ArrayList<String>();
    lines.add("MOV R-1 4");
    lines.add("RET R-1");
    Machine m = new Machine();
    assertEquals(m.execute(lines), 4);
  }

  //Boundary test 4
  @Test (expected = InvalidInstructionException.class)
  public void test04()
  {
    List<String> lines = new ArrayList<String>();
    lines.add("MOV R32 4");
    lines.add("RET R32");
    Machine m = new Machine();
    assertEquals(m.execute(lines), 4);
  }

  //Boundary test 5
  @Test public void test05()
  {
    List<String> lines = new ArrayList<String>();
    lines.add("MOV R31 -65535");
    lines.add("RET R31");
    Machine m = new Machine();
    assertEquals(m.execute(lines), -65535);
  }

  //Boundary test 6
  @Test public void test06()
  {
    List<String> lines = new ArrayList<String>();
    lines.add("MOV R0 65535");
    lines.add("RET R0");
    Machine m = new Machine();
    assertEquals(m.execute(lines), 65535);
  }

  //Boundary test 7
  @Test (expected = InvalidInstructionException.class)
  public void test07()
  {
    List<String> lines = new ArrayList<String>();
    lines.add("MOV R9 -65536");
    lines.add("RET R9");
    Machine m = new Machine();
    assertEquals(m.execute(lines), -65536);
  }

  //Boundary test 8
  @Test (expected = InvalidInstructionException.class)
  public void test08()
  {
    List<String> lines = new ArrayList<String>();
    lines.add("MOV R30 65536");
    lines.add("RET R30");
    Machine m = new Machine();
    assertEquals(m.execute(lines), 65536);
  }

  //Boundary test 9 and 13
  @Test public void test09_13()
  {
    List<String> lines = new ArrayList<String>();
    lines.add("MOV R1 -3");
    lines.add("MOV R3 -5");
    lines.add("MOV R4 90");
    lines.add("MOV R8 -3");
    lines.add("STR R1 3 R4"); // a[0] = 90
    lines.add("LDR R8 R3 5"); // R8 = a[0]
    lines.add("RET R8");
    Machine m = new Machine();
    assertEquals(m.execute(lines), 90);
  }

  //Boundary test 10 and 14
  @Test public void test10_14()
  {
    List<String> lines = new ArrayList<String>();
    lines.add("MOV R1 65534");
    lines.add("MOV R3 65535");
    lines.add("MOV R4 90");
    lines.add("MOV R8 -3");
    lines.add("STR R1 1 R4"); // a[65535] = 90
    lines.add("LDR R8 R3 0"); // R8 = a[65535]
    lines.add("RET R8");
    Machine m = new Machine();
    assertEquals(m.execute(lines), 90);
  }

  //Test Boundary test 11
  @Test public void test11()
  {
    List<String> lines = new ArrayList<String>();
    lines.add("MOV R1 4");
    lines.add("MOV R3 -3");
    lines.add("MOV R4 90");
    lines.add("MOV R8 -3");
    lines.add("STR R1 3 R4"); // a[7] = 90
    lines.add("LDR R8 R3 2"); // R8 = a[-1]
    lines.add("RET R8");
    Machine m = new Machine();
    assertEquals(m.execute(lines), -3);
  }

  //Test Boundary test 12
  @Test public void test12()
  {
    List<String> lines = new ArrayList<String>();
    lines.add("MOV R1 4");
    lines.add("MOV R3 1");
    lines.add("MOV R4 90");
    lines.add("MOV R8 -3");
    lines.add("STR R1 3 R4"); // a[7] = 90
    lines.add("LDR R8 R3 65535"); // R8 = a[65536]
    lines.add("RET R8");
    Machine m = new Machine();
    assertEquals(m.execute(lines), -3);
  }

  //Test Boundary test 15 and 16
  @Test public void test15_16()
  {
    List<String> lines = new ArrayList<String>();
    lines.add("MOV R1 -2");
    lines.add("STR R1 1 R4");
    lines.add("MOV R1 2");
    lines.add("STR R1 65534 R4");
    lines.add("RET R1");
    Machine m = new Machine();
    assertEquals(m.execute(lines), 2);
  }

  //Test Boundary test 17
  @Test public void test17()
  {
    List<String> lines = new ArrayList<String>();
    lines.add("JMP 1");
    lines.add("RET R1");
    Machine m = new Machine();
    assertEquals(m.execute(lines), 0);
  }

  //Test Boundary test 18
  @Test public void test18()
  {
    List<String> lines = new ArrayList<String>();
    lines.add("MOV R1 4");
    lines.add("JMP 1");
    lines.add("RET R1");
    Machine m = new Machine();
    assertEquals(m.execute(lines), 4);
  }

  //Test Boundary test 19
  @Test (expected = NoReturnValueException.class)
  public void test19()
  {
    List<String> lines = new ArrayList<String>();
    lines.add("MOV R1 4");
    lines.add("JMP -3");
    lines.add("RET R1");
    Machine m = new Machine();
    m.execute(lines);
  }

  //Test Boundary test 20
  @Test (expected = NoReturnValueException.class)
  public void test20()
  {
    List<String> lines = new ArrayList<String>();
    lines.add("MOV R1 4");
    lines.add("JMP 2");
    lines.add("RET R1");
    Machine m = new Machine();
    m.execute(lines);
  }

  //Test Boundary test 21
  @Test public void test21()
  {
    List<String> lines = new ArrayList<String>();
    lines.add("MOV R1 4");
    lines.add("MOV R2 0");
    lines.add("JZ R2 2");
    lines.add("MOV R1 2");
    lines.add("RET R1");
    Machine m = new Machine();
    assertEquals(m.execute(lines), 4);
  }

  //Test Boundary test 22
  @Test public void test22()
  {
    List<String> lines = new ArrayList<String>();
    lines.add("MOV R1 4");
    lines.add("MOV R2 1");
    lines.add("JZ R2 2");
    lines.add("MOV R1 7");
    lines.add("RET R1");
    Machine m = new Machine();
    assertEquals(m.execute(lines), 7);
  }

  //Test Boundary test 23
  @Test public void test23()
  {
    List<String> lines = new ArrayList<String>();
    lines.add("MOV R1 4");
    lines.add("MOV R2 -1");
    lines.add("JZ R2 2");
    lines.add("MOV R1 7");
    lines.add("RET R1");
    Machine m = new Machine();
    assertEquals(m.execute(lines), 7);
  }
}

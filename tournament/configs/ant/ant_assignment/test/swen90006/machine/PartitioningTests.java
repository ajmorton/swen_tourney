package swen90006.machine;

import java.util.List;
import java.util.ArrayList;
import java.nio.charset.Charset;
import java.nio.file.Path;
import java.nio.file.Files;
import java.nio.file.FileSystems;

import org.junit.*;
import static org.junit.Assert.*;

public class PartitioningTests
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

    //Test EC1_I
    @Test (expected = InvalidInstructionException.class)
    public void testEC1_I()
    {
        List<String> lines = new ArrayList<String>();
        lines.add("NOT R1 4");
        Machine m = new Machine();
        m.execute(lines);
    }

    //Test EC2_V
    @Test public void testEC2_V()
    {
        List<String> lines = new ArrayList<String>();
        lines.add("RET R1");
        Machine m = new Machine();
        assertEquals( m.execute(lines), 0);
    }

    //Test EC3_V
    @Test (expected = NoReturnValueException.class)
    public void testEC3_V()
    {
        List<String> lines = new ArrayList<String>();
        lines.add("MOV R1 4");
        Machine m = new Machine();
        m.execute(lines);
    }

    //Test EC4_V
    @Test public void testEC4_V()
    {
        List<String> lines = new ArrayList<String>();
        lines.add("MOV R2 1");
        lines.add("MOV R3 2");
        lines.add("ADD R1 R2 R3");
        lines.add("RET R1");
        Machine m = new Machine();
        assertEquals(m.execute(lines), 3);
    }

    //Test EC5_V
    @Test public void testEC5_V()
    {
        List<String> lines = new ArrayList<String>();
        lines.add("MOV R2 2");
        lines.add("MOV R3 1");
        lines.add("SUB R1 R2 R3");
        lines.add("RET R1");
        Machine m = new Machine();
        assertEquals(m.execute(lines), 1);
    }

    //Test EC6_V
    @Test public void testEC6_V()
    {
        List<String> lines = new ArrayList<String>();
        lines.add("MOV R2 2");
        lines.add("MOV R3 3");
        lines.add("MUL R1 R2 R3");
        lines.add("RET R1");
        Machine m = new Machine();
        assertEquals(m.execute(lines), 6);
    }

    //Test EC7_V
    @Test public void testEC7_V()
    {
        List<String> lines = new ArrayList<String>();
        lines.add("MOV R2 6");
        lines.add("MOV R3 2");
        lines.add("DIV R1 R2 R3");
        lines.add("RET R1");
        Machine m = new Machine();
        assertEquals(m.execute(lines), 3);
    }

    //Test EC8_V
    @Test public void testEC8_V()
    {
        List<String> lines = new ArrayList<String>();
        lines.add("MOV R1 4");
        lines.add("RET R1");
        Machine m = new Machine();
        assertEquals(m.execute(lines), 4);
    }

    //Test EC9_V
    @Test public void testEC9_V()
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

    //Test EC10_V
    @Test public void testEC10_V()
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

    //Test EC11_V
    @Test public void testEC11_V()
    {
        List<String> lines = new ArrayList<String>();
        lines.add("MOV R1 4");
        lines.add("MOV R3 20000");
        lines.add("MOV R4 90");
        lines.add("MOV R8 -3");
        lines.add("STR R1 3 R4"); // a[7] = 90
        lines.add("LDR R8 R3 50000"); // R8 = a[70000]
        lines.add("RET R8");
        Machine m = new Machine();
        assertEquals(m.execute(lines), -3);
    }

    //Test EC12_V && EC18_V
    @Test public void testEC12_V_EC18_V()
    {
        List<String> lines = new ArrayList<String>();
        lines.add("MOV R1 4");
        lines.add("MOV R3 2");
        lines.add("MOV R4 90");
        lines.add("MOV R8 -3");
        lines.add("STR R1 3 R4"); // a[7] = 90
        lines.add("STR R1 3 R4"); // a[7] = 90
        lines.add("LDR R8 R3 5"); // R8 = a[7]
        lines.add("RET R8");
        Machine m = new Machine();
        assertEquals(m.execute(lines), 90);
    }

    //Test EC13_V
    @Test public void testEC13_V()
    {
        List<String> lines = new ArrayList<String>();
        lines.add("MOV R1 4");
        lines.add("MOV R3 -20000");
        lines.add("MOV R4 90");
        lines.add("MOV R8 -3");
        lines.add("STR R1 3 R4"); // a[7] = 90
        lines.add("LDR R8 R3 -50000"); // R8 = a[-70002]
        lines.add("RET R8");
        Machine m = new Machine();
        assertEquals(m.execute(lines), -3);
    }

    //Test EC14_V
    @Test (expected = NoReturnValueException.class)
    public void testEC14_V()
    {
        List<String> lines = new ArrayList<String>();
        lines.add("MOV R1 4");
        lines.add("JMP 6");
        lines.add("RET R1");
        Machine m = new Machine();
        m.execute(lines);
    }

    //Test EC15_V
    @Test (expected = NoReturnValueException.class)
    public void testEC15_V()
    {
        List<String> lines = new ArrayList<String>();
        lines.add("MOV R1 4");
        lines.add("JMP -6");
        lines.add("RET R1");
        Machine m = new Machine();
        m.execute(lines);
    }

    //Test EC16_V
    @Test public void testEC16_V()
    {
        List<String> lines = new ArrayList<String>();
        lines.add("MOV R1 4");
        lines.add("JMP 2");
        lines.add("MOV R1 41");
        lines.add("RET R1");
        Machine m = new Machine();
        assertEquals(m.execute(lines), 4);
    }

    //Test EC17_V
    @Test public void testEC17_V()
    {
        List<String> lines = new ArrayList<String>();
        lines.add("MOV R1 4000");
        lines.add("STR R1 65000 R4");
        lines.add("RET R1");
        Machine m = new Machine();
        assertEquals(m.execute(lines), 4000);
    }

    //Test EC19_V
    @Test public void testEC19_V()
    {
        List<String> lines = new ArrayList<String>();
        lines.add("MOV R1 -4000");
        lines.add("STR R1 -65000 R4");
        lines.add("RET R1");
        Machine m = new Machine();
        assertEquals(m.execute(lines), -4000);
    }

    //Test EC20_V
    @Test public void testEC20_V()
    {
        List<String> lines = new ArrayList<String>();
        lines.add("MOV R1 4");
        lines.add("MOV R2 5");
        lines.add("RET R1");
        lines.add("RET R2");
        Machine m = new Machine();
        assertEquals(m.execute(lines), 4);
    }

    //Test EC21_I
    @Test (expected = InvalidInstructionException.class)
    public void testEC21_I()
    {
        List<String> lines = new ArrayList<String>();
        lines.add("MOV R1 70000");
        lines.add("RET R2");
        Machine m = new Machine();
        m.execute(lines);
    }

    //Test EC22_I
    @Test (expected = InvalidInstructionException.class)
    public void testEC22_I()
    {
        List<String> lines = new ArrayList<String>();
        lines.add("MOV R1 -70000");
        lines.add("RET R2");
        Machine m = new Machine();
        m.execute(lines);
    }

    //Test EC23_I
    @Test (expected = InvalidInstructionException.class)
    public void testEC23_I()
    {
        List<String> lines = new ArrayList<String>();
        lines.add("MOV R-1 4");
        lines.add("RET R2");
        Machine m = new Machine();
        m.execute(lines);
    }

    //Test EC24_I
    @Test (expected = InvalidInstructionException.class)
    public void testEC24_I()
    {
        List<String> lines = new ArrayList<String>();
        lines.add("MOV R40 4");
        lines.add("RET R2");
        Machine m = new Machine();
        m.execute(lines);
    }
}

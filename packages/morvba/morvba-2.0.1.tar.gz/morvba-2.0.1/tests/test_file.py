import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../morvba')))
from cC import C

def test_left():
    c = C()
    assert c.left("abcdefg", 3) == "abc"

def test_right():
    c = C()
    assert c.right("abcdefg", 3) == "efg"

def test_mid():
    c = C()
    assert c.mid("abcdefg", 2, 3) == "bcd"

def test_instr():
    c = C()
    assert c.instr(1, "abcdefg", "c") == 3

def test_trim():
    c = C()
    assert c.trim("  abc  ") == "abc"

def test_pkey():
    c = C()
    assert c.pkey("abcdefghi", "abc", "ghi") == "def"

if __name__ == '__main__':
    test_left()
    test_right()
    test_mid()
    test_instr()
    test_trim()
    test_pkey()
    print("All tests passed!")

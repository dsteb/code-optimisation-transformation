#!/usr/bin/python

# Test support
__test_program='''
VAR x, squ, v[5];

PROCEDURE square(a);
BEGIN
  squ := a * a;
END;

PROCEDURE exec;
BEGIN
  x := 1;
  WHILE x <= 10 DO
  BEGIN
    CALL square(x);
    x := x + 1;
    !squ;
  END;
END;

BEGIN
  CALL exec;
  v[0] := 5 % 2;
END.
'''
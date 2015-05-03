#!/usr/bin/python

# Test support
__test_program='''
VAR x, squ, v[5];

PROCEDURE square(a);
BEGIN
  RETURN a * a;
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
  v[1] := 5;
  v[0] := v[1] % 2;
  v[1] := square(5);
END.
'''
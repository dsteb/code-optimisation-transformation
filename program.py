#!/usr/bin/python

# Test support
__test_program='''VAR x, squ, v[5];
 
PROCEDURE square;
BEGIN
   squ := x * x
END;
 
BEGIN
  x := 1;
  WHILE x <= 10 DO
  BEGIN
     CALL square;
     x := x + 1;
	 !squ;
  END;
  x := 5 % 2;
END.'''
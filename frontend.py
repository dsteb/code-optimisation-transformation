#!/usr/bin/python

__doc__ = '''PL/0 recursive descent parser adapted from Wikipedia'''

from ir import *
from logger import logger

import sys
sys.stdout = open('log', 'w')

symbols =  [ 'ident', 'number', 'lparen', 'rparen', 'times', 'slash', 'plus', 'minus', 'eql', 'neq', 'lss', 'leq', 'gtr', 'geq', 'callsym', 'beginsym', 'semicolon', 'endsym', 'ifsym', 'whilesym', 'becomes', 'thensym', 'dosym', 'constsym', 'comma', 'varsym', 'procsym', 'period', 'oddsym', 'forsym' ]

sym = None
value = None
new_sym = None
new_value = None

def getsym():
	'''Update sym'''
	global new_sym 
	global new_value
	global sym
	global value
	try :
		sym=new_sym
		value=new_value
		new_sym, new_value=the_lexer.next()
	except StopIteration :
		return 2
	print 'getsym:', new_sym, new_value
	return 1
	
def error(msg):
	print msg, new_sym, new_value
	
def accept(s):
	print 'accepting', s, '==', new_sym
	return getsym() if new_sym==s else 0
 
def expect(s) :
	print 'expecting', s
	if accept(s) : return 1
	error("expect: unexpected symbol")
	return 0
 
@logger
def factor(symtab) :
	if accept('ident') :
		var=symtab.find(value)
		if var.stype.name == 'array' :
			expect('lsquare')
			expect('number')
			index=value
			expect('rsquare')
			return ArrayVar(var=var, index=index, symtab=symtab)
		elif var.stype.name == 'function' :
			if accept('lparen'):
				params = []
				params.append(expression(symtab))
				while accept('comma') :
					params.append(expression(symtab))
				expect('rparen')
				return CallExpr(function=var, parameters=params, symtab=symtab)
			return CallExpr(function=var, symtab=symtab)
		return Var(var=var, symtab=symtab)
	if accept('number') : return Const(value=value, symtab=symtab)
	elif accept('lparen') :
		expr = expression(symtab)
		expect('rparen')
		return expr
	else :
		error("factor: syntax error")
		getsym()
 
@logger
def term(symtab) :
	op=None
	expr = factor(symtab)
	while new_sym in [ 'times', 'slash', 'mod'] :
		getsym()
		op = sym
		expr2 = factor(symtab)
		expr = BinExpr(children=[ op, expr, expr2 ], symtab=symtab)
	return expr
 
@logger
def expression(symtab) :
	op=None
	if new_sym in [ 'plus' or 'minus' ] :
		getsym()
		op = sym
	expr = term(symtab)
	if op : expr = UnExpr(children=[initial_op, expr], symtab=symtab)
	while new_sym in [ 'plus' or 'minus' ] :
		getsym()
		op = sym
		expr2 = term(symtab)
		expr = BinExpr(children=[ op, expr, expr2 ], symtab=symtab)
	return expr
 
@logger
def condition(symtab) :
	if accept('oddsym') : 
		return UnExpr(children=['odd', expression(symtab)], symtab=symtab)
	else :
		expr = expression(symtab);
		if new_sym in [ 'eql', 'neq', 'lss', 'leq', 'gtr', 'geq' ] :
			getsym()
			print 'condition operator', sym, new_sym
			op=sym
			expr2 = expression(symtab)
			return BinExpr(children=[op, expr, expr2 ], symtab=symtab)
		else :
			error("condition: invalid operator")
			getsym();
 
@logger
def statement(symtab) :
	if accept('forsym'):
		expect('lparen')
		
		# TODO add empty expression and arrays support

		# init
		expect('ident')
		target=symtab.find(value)
		expect('becomes')
		expr = expression(symtab)
		expect('semicolon')
		init = AssignStat(target=target, expr=expr, symtab=symtab)

		# condition
		cond = condition(symtab)
		expect('semicolon')

		# increment
		expect('ident')
		target=symtab.find(value)
		expect('becomes')
		expr = expression(symtab)
		step = AssignStat(target=target, expr=expr, symtab=symtab)

		expect('rparen')

		body = statement(symtab)
		return ForStat(init=init, cond=cond, step=step, body=body, symtab=symtab)
	elif accept('ident'):
		target=symtab.find(value)
		index=None
		if accept('lsquare') :
			expect('number')
			index = value
			expect('rsquare')
		expect('becomes')
		expr=expression(symtab)
		if index is None :
			return AssignStat(target=target, expr=expr, symtab=symtab)
		else :
			return ArrayAssignStat(target=target, expr=expr, index=index, symtab=symtab)
	elif accept('callsym') :
		expect('ident')
		var = value
		if accept('lparen'):
			params = []
			params.append(expression(symtab))
			while accept('comma') :
				params.append(expression(symtab))
			expect('rparen')
			return CallStat(call_expr=CallExpr(function=symtab.find(var), parameters=params, symtab=symtab), symtab=symtab)
		return CallStat(call_expr=CallExpr(function=symtab.find(value), symtab=symtab), symtab=symtab)
	elif accept('beginsym') :
		statement_list = StatList(symtab=symtab)
		statement_list.append(statement(symtab))
		while accept('semicolon') :
			if (new_sym != 'endsym'):
				statement_list.append(statement(symtab))
			else: break
			
		expect('endsym');
		statement_list.print_content()
		return statement_list
	elif accept('ifsym') :
		cond=condition()
		expect('thensym')
		then=statement(symtab)
		return IfStat(cond=cond,thenpart=then, symtab=symtab)
	elif accept('whilesym') :
		cond=condition(symtab)
		expect('dosym')
		body=statement(symtab)
		return WhileStat(cond=cond, body=body, symtab=symtab)
	elif accept('print') :
		expect('ident')
		val = value
		expect('semicolon')
		return PrintStat(symbol=symtab.find(val),symtab=symtab)
	elif accept('return') :
		expr = expression(symtab)
		expect('semicolon')
		return ReturnStat(return_expr=expr, symtab=symtab)
 
@logger
def block(symtab, local_vars=None) :
	local_vars = SymbolTable() if local_vars is None else local_vars
	defs = DefinitionList()
	if accept('constsym') :
		expect('ident')
		name=value
		expect('eql')
		expect('number')
		local_vars.append(Symbol(name, standard_types['int']), value)
		while accept('comma') :
			expect('ident')
			name=value
			expect('eql')
			expect('number')
			local_vars.append(Symbol(name, standard_types['int']), value)
		expect('semicolon');
	if accept('varsym') :
		expect('ident')
		local_vars.append(Symbol(value, standard_types['int']))
		while accept('comma') :
			expect('ident');
			val = value;
			if accept('lsquare') :
				expect('number')
				local_vars.append(Symbol(val, ArrayType('array', value, 'Int')))
				expect('rsquare')
			else : local_vars.append(Symbol(value, standard_types['int']))
			
		expect('semicolon');
	while accept('procsym') :
		expect('ident')
		fname=value
		if accept('lparen') :
			expect('ident');
			new_local_vars = SymbolTable()
			new_local_vars.append(Symbol(value, standard_types['int']))
			while accept('comma') :
				expect('ident');
				new_local_vars.append(Symbol(value, standard_types['int']))
			expect('rparen')
		expect('semicolon');
		local_vars.append(Symbol(fname, standard_types['function']))
		fbody=block(local_vars, new_local_vars)
		expect('semicolon')
		defs.append(FunctionDef(symbol=local_vars.find(fname), body=fbody))
	stat = statement(SymbolTable(symtab[:]+local_vars))
	return Block(gl_sym=symtab, lc_sym=local_vars, defs=defs, body=stat)
 
@logger
def program() :
	'''Axiom'''
	global_symtab=SymbolTable()
	getsym()
	the_program = block(global_symtab)
	expect('period')
	return the_program



if __name__ == '__main__' :
	from lexer import lexer, __test_program
	the_lexer=lexer(__test_program)
	res = program()
	print '\n', res, '\n'
			
	res.navigate(print_stat_list)
	from support import *


	node_list=get_node_list(res)
	for n in node_list :
		print type(n), id(n), '->', type(n.parent), id(n.parent)
	print '\nTotal nodes in IR:', len(node_list), '\n'

	res.navigate(lowering)

	node_list=get_node_list(res)
	print '\n', res, '\n'
	for n in node_list :
		print type(n), id(n)
		try :	n.flatten()
		except Exception :	pass
	res.navigate(flattening)
	print '\n', res, '\n'

	print_dotty(res,"log.dot")

	from cfg import *
	cfg=CFG(res)
	cfg.liveness()
	cfg.print_liveness()
	cfg.print_cfg_to_dot("cfg.dot")
	from regalloc import *
	ra = minimal_register_allocator(cfg,8)
	reg_alloc = ra()
	print reg_alloc

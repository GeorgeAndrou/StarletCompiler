# Name : Androutsopoulos Georgios, AM : 2933, username: cse52933
# Name : Karvelis Christophoros, AM : 2989, username: cse52989
# Lexical Analyzer
# Syntax Analyzer
# Semantic Analyzer
# Intermediate-Code Generation
# C-like program Generation
# Code Generation

import sys
from abc import ABC, abstractmethod

'''
	====================================================================================================
										Data Structures & Constants										
	====================================================================================================
'''

# Automata states
ERROR = -3	# Not valid state
OKR = -2	# Valid state, needed token return
OK = -1	# Valid state
STATE_START = 0
STATE_ALPHA = 1
STATE_DIGIT = 2
STATE_LESS = 3
STATE_GREATER = 4
STATE_COLON = 5
STATE_SLASH = 6
STATE_LINECOMMENT = 7
STATE_LINECOMMENT_CHECK = 8
STATE_MULTILINECOMMENT_OPEN = 9
STATE_MULTILINECOMMENT_CHECK = 10
STATE_MULTILINECOMMENT_CLOSE = 11

# Automata Inputs
ALPHA = 1	# Alphabetic character input
DIGIT = 2	# Numeric character input
OTHER = 19	# Not a grammar's character input

# Symbol Table Constants
STD_FRAMELENGTH = 12
STD_INT_SIZE = 4
STD_ASM_HEADER = ".data\n\tnewline: .asciiz \"\\n\"\n.text\n\n"
STD_ASM_COPYRIGHT = "\n\n# KC AG Compilers I CSE\n"

# The table which describes automata's operation
decision_table = [	
			[STATE_START, STATE_ALPHA, STATE_DIGIT,	OK, OK,	OK,	STATE_SLASH, STATE_LESS, STATE_GREATER,	OK,	STATE_COLON, OK, OK, OK, OK, OK, OK, STATE_START, OK, ERROR],
			[OKR, STATE_ALPHA, STATE_ALPHA,	OKR, OKR, OKR, OKR,	OKR, OKR, OKR, OKR,	OKR, OKR, OKR, OKR,	OKR, OKR, OKR, OKR, ERROR],
			[OKR, ERROR, STATE_DIGIT, OKR, OKR,	OKR, OKR, OKR, OKR,	OKR, OKR, OKR, OKR,	OKR, OKR, OKR, OKR,	OKR, OKR, ERROR],
			[OKR, OKR, OKR,	OKR, OKR, OKR, OKR,	OKR, OK, OK, OKR, OKR, OKR,	OKR, OKR, OKR, OKR,	OKR, OKR, ERROR],
			[OKR, OKR, OKR,	OKR, OKR, OKR, OKR,	OKR, OKR, OK, OKR, OKR,	OKR, OKR, OKR, OKR,	OKR, OKR, OKR, ERROR],
			[OKR, OKR, OKR,	OKR, OKR, OKR, OKR,	OKR, OKR, OK, OKR, OKR,	OKR, OKR, OKR, OKR,	OKR, OKR, OKR, ERROR],
			[OKR, OKR, OKR,	OKR, OKR, STATE_MULTILINECOMMENT_OPEN, STATE_LINECOMMENT, OKR, OKR,	OKR, OKR, OKR, OKR,	OKR, OKR, OKR, OKR,	OKR, OKR, ERROR],
			[STATE_LINECOMMENT,	STATE_LINECOMMENT, STATE_LINECOMMENT, STATE_LINECOMMENT, STATE_LINECOMMENT,	STATE_LINECOMMENT, STATE_LINECOMMENT_CHECK,	STATE_LINECOMMENT, STATE_LINECOMMENT, STATE_LINECOMMENT, STATE_LINECOMMENT,	STATE_LINECOMMENT, STATE_LINECOMMENT, STATE_LINECOMMENT, STATE_LINECOMMENT,	STATE_LINECOMMENT, STATE_LINECOMMENT, STATE_START, STATE_START, STATE_LINECOMMENT],
			[STATE_LINECOMMENT,	STATE_LINECOMMENT, STATE_LINECOMMENT, STATE_LINECOMMENT, STATE_LINECOMMENT,	ERROR, ERROR, STATE_LINECOMMENT, STATE_LINECOMMENT, STATE_LINECOMMENT, STATE_LINECOMMENT, STATE_LINECOMMENT, STATE_LINECOMMENT,	STATE_LINECOMMENT, STATE_LINECOMMENT, STATE_LINECOMMENT, STATE_LINECOMMENT,	STATE_START, STATE_START,  STATE_LINECOMMENT],
			[STATE_MULTILINECOMMENT_OPEN, STATE_MULTILINECOMMENT_OPEN, STATE_MULTILINECOMMENT_OPEN,	STATE_MULTILINECOMMENT_OPEN, STATE_MULTILINECOMMENT_OPEN, STATE_MULTILINECOMMENT_CLOSE,	STATE_MULTILINECOMMENT_CHECK, STATE_MULTILINECOMMENT_OPEN, STATE_MULTILINECOMMENT_OPEN,	STATE_MULTILINECOMMENT_OPEN, STATE_MULTILINECOMMENT_OPEN, STATE_MULTILINECOMMENT_OPEN, STATE_MULTILINECOMMENT_OPEN,	STATE_MULTILINECOMMENT_OPEN, STATE_MULTILINECOMMENT_OPEN, STATE_MULTILINECOMMENT_OPEN, STATE_MULTILINECOMMENT_OPEN,	STATE_MULTILINECOMMENT_OPEN, ERROR, STATE_MULTILINECOMMENT_OPEN],
			[STATE_MULTILINECOMMENT_OPEN, STATE_MULTILINECOMMENT_OPEN, STATE_MULTILINECOMMENT_OPEN,	STATE_MULTILINECOMMENT_OPEN, STATE_MULTILINECOMMENT_OPEN, ERROR, ERROR,	STATE_MULTILINECOMMENT_OPEN, STATE_MULTILINECOMMENT_OPEN, STATE_MULTILINECOMMENT_OPEN, STATE_MULTILINECOMMENT_OPEN, STATE_MULTILINECOMMENT_OPEN, STATE_MULTILINECOMMENT_OPEN, STATE_MULTILINECOMMENT_OPEN, STATE_MULTILINECOMMENT_OPEN,	STATE_MULTILINECOMMENT_OPEN, STATE_MULTILINECOMMENT_OPEN, STATE_MULTILINECOMMENT_OPEN, ERROR, STATE_MULTILINECOMMENT_OPEN],
			[STATE_MULTILINECOMMENT_OPEN, STATE_MULTILINECOMMENT_OPEN, STATE_MULTILINECOMMENT_OPEN,	STATE_MULTILINECOMMENT_OPEN, STATE_MULTILINECOMMENT_OPEN, STATE_MULTILINECOMMENT_OPEN, STATE_START,	STATE_MULTILINECOMMENT_OPEN, STATE_MULTILINECOMMENT_OPEN, STATE_MULTILINECOMMENT_OPEN, STATE_MULTILINECOMMENT_OPEN,	STATE_MULTILINECOMMENT_OPEN, STATE_MULTILINECOMMENT_OPEN, STATE_MULTILINECOMMENT_OPEN, STATE_MULTILINECOMMENT_OPEN,	STATE_MULTILINECOMMENT_OPEN, STATE_MULTILINECOMMENT_OPEN, STATE_MULTILINECOMMENT_OPEN, ERROR, STATE_MULTILINECOMMENT_OPEN]
			]

# The mapping between 'special' tokens and token id's
keywords_map = { 
			"program" : "PROGRAM_ID",
			"endprogram" : "ENDPROGRAM_ID", 
			"declare" : "DECLARE_ID", 
			"if" : "IF_ID", 
			"then" : "THEN_ID", 
			"else" : "ELSE_ID", 
			"endif" : "ENDIF_ID", 
			"dowhile" : "DOWHILE_ID",
			"enddowhile" : "ENDDOWHILE_ID",
			"while" : "WHILE_ID", 
			"endwhile" : "ENDWHILE_ID",
	 		"loop" : "LOOP_ID", 
	 		"endloop" : "ENDLOOP_ID", 
	 		"exit" : "EXIT_ID", 
	 		"forcase" : "FORCASE_ID", 
			"endforcase" : "ENDFORCASE_ID", 
			"incase" : "INCASE_ID", 
			"endincase" : "ENDINCASE_ID", 
			"when" : "WHEN_ID", 
			"endwhen" : "ENDWHEN_ID", 
			"default" : "DEFAULT_ID", 
			"enddefault" : "ENDDEFAULT_ID", 
			"function": "FUNCTION_ID", 
			"endfunction" : "ENDFUNCTION_ID", 
			"return" : "RETURN_ID", 
			"in" : "IN_ID", 
			"inout" : "INOUT_ID", 
			"inandout" : "INANDOUT_ID", 
			"and" : "AND_ID", 
			"or" : "OR_ID", 
			"not" : "NOT_ID", 
			"input" : "INPUT_ID", 
			"print" : "PRINT_ID"
			}

# The set with all statement's keyword starters
statement_starters_set = {
					"if",
					"dowhile",
					"while",
					"loop",
					"exit",
					"forcase",
					"incase",
					"return",
					"input",
					"print"
					}

# The mapping between Starlet and C operators
C_oper_map = {
			':=' : '=',
			'+' : '+',
			'-' : '-',
			'*' : '*',
			'/' : '/',
			'inp' : 'scanf("%d",&',
			'out' : 'printf("%d\\n",',
			'=' : '==',
			'<>' : '!=',
			'>' : '>',
			'<' : '<',
			'>=' : '>=',
			'<=' : '<='
			}

'''
	The mapping between symbolic tokens and token id's,
	it's also translates automata input to integer code
'''
symbols_map = {
			' ' : [0, 'SPACE_ID'],
			'\t' : [0, 'TAB_ID'],
			'+' : [3,'ADD_ID'],
			'-' : [4,'MINUS_ID'],
			'*' : [5,'MULT_ID'],
			'/' : [6,'DIV_ID'],
			'<' : [7,'LESS_ID'],
			'>' : [8,'GREATER_ID'],
			'=' : [9,'EQUAL_ID'],
			':' : [10,'COLON_ID'],
			',' : [11,'COMMA_ID'],
			';' : [12,'SEMICOLON_ID'],
			'(' : [13,'PARENTHESIS_OPEN_ID'],
			')' : [14,'PARENTHESIS_CLOSE_ID'],
			'[' : [15,'BRACKET_OPEN_ID'],
			']' : [16,'BRACKET_CLOSE_ID'],
			'\n' : [17,'EOL_ID'],
			'' : [18,'EOF_ID'],
			'<=' : [20,'LESSOREQUAL_ID'],
			'>=' : [21, 'GREATEROREQUAL_ID'],
			'<>' : [22, 'NOTEQUAL_ID'],
			':=' : [23,'ASSIGN_ID']
			}

# The error handling modes mapping
mode_map = {
			'LEX_MODE' : "LEXICAL",
			'SYNTAX_MODE': "SYNTAX",
			'SEM_MODE' : "SEMANTIC"
			}

# The parameter passing modes mapping
par_mode_map = {
			"in" : "CV",
			"inout" : "REF",
			"inandout" : "CP"
			}

# The mips instructions mapping
mips_instr_map = {
					'+' : 'add',
					'-' : 'sub',
					'*' : 'mul',
					'/' : 'div',
					'=' : 'beq',
					'<' : 'blt',
					'>' : 'bgt',
					'<=' : 'ble',
					'>=' : 'bge',
					'<>' : 'bne',
				}


# The mapping between error codes and error messages
error_map = {
				
			'LEX_MODE': {

						# Lexical Analyzer Error Mapping
						STATE_START : {
									'OTHER_ID' : "Unknown character -> '{lex_token}'"},
						STATE_ALPHA : {
									'OTHER_ID' : "Unknown character -> '{lex_token}'"},
						STATE_DIGIT : {
									'ALNUM_ID' : 'Unexpected trailing character after number -> {lex_token}',
									'OVERFLOW_ID' : 'Given number: {lex_token} is out of range [-32767,32767]!',
									'OTHER_ID' : "Unknown character -> '{lex_token}'"},
						STATE_LESS : {
									'OTHER_ID' : "Unknown character -> '{lex_token}'"},
						STATE_GREATER : {
									'OTHER_ID' : "Unknown character -> '{lex_token}'"},
						STATE_COLON : {
									'OTHER_ID' : "Unknown character -> '{lex_token}'"},
						STATE_SLASH : {
									'OTHER_ID' : "Unknown character -> '{lex_token}'"},
						STATE_LINECOMMENT_CHECK : {
									'COMMENT_ID' : 'Nested comments are not allowed -> {lex_token}',
									'COMMENT_ID' : 'Nested comments are not allowed -> {lex_token}'},
						STATE_MULTILINECOMMENT_OPEN : {
									'EOF_ID' : 'Reach EOF before multi-line comment closing!'},
						STATE_MULTILINECOMMENT_CHECK : {
									'COMMENT_ID' : 'Nested comments are not allowed -> {lex_token}',
									'COMMENT_ID' : 'Nested comments are not allowed -> {lex_token}',
									'EOF_ID' : 'Reach EOF before multi-line comment closing!'},
						STATE_MULTILINECOMMENT_CLOSE : {
									'EOF_ID' : 'Reach EOF before multi-line comment closing!'}
						},

			'SYNTAX_MODE': {

						# Syntax Analyzer Error Mapping 
						'PROGRAM_FUNC' : {
									'PROGRAM_ID' : "Each program have to start with keyword 'program'!",
									'ALNUM_ID' : "Invalid program name -> '{prog_name}'",
									'SEMICOLON_ID' : "Missing ';' from above statements !",
									'UNEXPECTED_ID' : "Unexpected '{unexp_token}' !",
									'ENDPROGRAM_ID' : "Missing 'endprogram' keyword!",
									'EOF_ID' : "Unexpected '{unexp_token}' after program ending!"},
						'DECLARATIONS_FUNC' : {
									'SEMICOLON_ID' : "Missing ';' from declare statement or illegal variable declaration!"},
						'VARLIST_FUNC' : {
									'ALNUM_ID' : "Invalid variable name -> '{var_name}'"},
						'SUBPROGRAM_FUNC' : {
									'ALNUM_ID' : "Invalid function name -> '{sub_prog_name}'",
									'SEMICOLON_ID' : "Missing ';' from above statements!",
									'UNEXPECTED_ID' : "Unexpected '{unexp_token}' !",
									'ENDFUNCTION_ID' : "Missing 'endfunction' keyword!"},
						'FORMALPARS_FUNC' : {
									'PARENTHESIS_OPEN_ID' : "Missing parentheses () from function's '{func_name}()' definition!",
									'PARENTHESIS_CLOSE_ID' : "Unclosed parenthesis at function '{func_name}()' definition!"},
						'FORMALPARITEM_FUNC' : {
									'ALNUM_ID' : "Invalid parameter name -> '{par_name}'",
									'OTHER_ID' : "Invalid parameter passing at function '{func_name}()',\nuse one of 'in', 'inout', 'inandout' forms!"},
						'ASSIGNMENT_STAT_FUNC' : {
									'ASSIGN_ID' : "Invalid assigning, expecting ':=' but '{unexp_token}' was found!"},
						'IF_STAT_FUNC' : {
									'PARENTHESIS_OPEN_ID' : "Ιf-statement's condition must be closed in parentheses ()!",
									'PARENTHESIS_CLOSE_ID' : "Unclosed parenthesis at if-statement condition!",
									'SEMICOLON_ID' : "Missing ';' from above statements!",
						 			'UNEXPECTED_ID' : "Unexpected '{unexp_token}' !",
						 			'EXPECTED_THEN_ID' : "Expecting 'then' after if's condition but '{unexp_token}' was found!",
						 			'THEN_ID' : "Missing 'then' keyword from if-statement!",
						 			'ENDIF_ID' : "Missing 'endif' keyword from if-statement!"},
						'WHILE_STAT_FUNC' : {
									'PARENTHESIS_OPEN_ID' : "While-statement's condition must be closed in parentheses ()!",
									'PARENTHESIS_CLOSE_ID' : "Unclosed parenthesis at while-statement condition!",
									'SEMICOLON_ID' : "Missing ';' from above statements!",
									'UNEXPECTED_ID' : "Unexpected '{unexp_token}' !",
									'ENDWHILE_ID' : "Missing 'endwhile' keyword from while-statement!"},
						'DO_WHILE_STAT_FUNC' : {
									'PARENTHESIS_OPEN_ID' : "Do-while-statement's condition must be closed in parentheses ()!",
									'PARENTHESIS_CLOSE_ID' : "Unclosed parenthesis at do-while-statement condition!",
									'SEMICOLON_ID' : "Missing ';' from above statements!",
									'UNEXPECTED_ID' : "Unexpected '{unexp_token}' !",
									'ENDDOWHILE_ID' : "Missing 'enddowhile' keyword from do-while-statement!"},
						'LOOP_STAT_FUNC' : {
									'SEMICOLON_ID' : "Missing ';' from above statements!",
									'UNEXPECTED_ID' : "Unexpected '{unexp_token}' !",
									'ENDLOOP_ID' : "Missing 'endloop' keyword from loop-statement!"},
						'FORCASE_STAT_FUNC' : {
									'PARENTHESIS_OPEN_ID' : "All the when case conditions of forcase-statement must be closed in parentheses ()!",
									'PARENTHESIS_CLOSE_ID' : "Unclosed parenthesis at a forcase-statement condition!",
									'WCOLON_ID' : "Expecting ':' after when's condition but '{unexp_token}' was found!",
									'DEFAULT_ID' : "Missing 'default' case from forcase-statement!",
									'DCOLON_ID' : "Expecting ':' after 'default' but '{unexp_token}' was found!",
									'SEMICOLON_ID' : "Missing ';' from above statements!",
									'UNEXPECTED_ID' : "Unexpected '{unexp_token}' !",
									'ENDDEFAULT_ID' : "Missing 'enddefault' keyword from forcase-statement!",
									'EXPECTED_ENDFORCASE_ID' : "Expecting 'endforcase' after 'enddefault' but '{unexp_token}' was found!",
									'ENDFORCASE_ID' : "Missing 'endforcase' keyword from forcase-statement!"},
						'INCASE_STAT_FUNC' : {
									'PARENTHESIS_OPEN_ID' : "All the when case conditions of incase-statement must be closed in parentheses ()!",
									'PARENTHESIS_CLOSE_ID' : "Unclosed parenthesis at a incase-statement condition!",
									'COLON_ID' : "Expecting ':' after when's condition but '{unexp_token}' was found!",
									'SEMICOLON_ID' : "Missing ';' from above statements!",
									'UNEXPECTED_ID' : "Unexpected '{unexp_token}' !",
									'ENDINCASE_ID' : "Missing 'endincase' keyword from incase-statement!"},
						'INPUT_STAT_FUNC' : {
									'ALNUM_ID' : "Invalid variable name -> '{var_name}'"},
						'ACTUALPARS_FUNC' : {
									'PARENTHESIS_OPEN_ID' : "Missing parentheses () from function's '{func_name}()' call!",
									'PARENTHESIS_CLOSE_ID' : "Unclosed parenthesis at function '{func_name}()' call!"},
						'ACTUALPARITEM_FUNC' : {
									'ALNUM_ID' : "Invalid argument name -> '{arg_name}'",
									'OTHER_ID' : "Invalid argument passing at function '{func_name}()',\nuse one of 'in', 'inout', 'inandout' forms!"},
						'BOOLFACTOR_FUNC' : {
									'BRACKET_OPEN_ID' : "Boolean conditions must be closed in square brackets []!",
									'BRACKET_CLOSE_ID' : "Unclosed brackets at boolean condition!",
									'NOT_REL_OPER_ID' : "Invalid relational operator -> '{rel_op}'"},
						'FACTOR_FUNC' : {
									'PARENTHESIS_CLOSE_ID' : "Unclosed expression parenthesis!",
									'OTHER_ID' : "Invalid factor -> '{factor}'"}
						},

			'SEM_MODE': {

						# Semantic Analyzer Error Mapping
						'VARLIST_FUNC' : {
									'REDECLARED_VAR' : "A variable with name '{redeclared_var}' is already exists in {scope_type} '{scope_name}()'!",
									'USED_FOR_FUNC' : "A variable can not have the same name '{var_name}' with the function which belongs!"},
						'SUBPROGRAM_FUNC' : {
									'NO_RETURN' : "Function '{func_name}()' has not 'return' statement!",
									'REDECLARED_FUNC' : "A function with name '{redeclared_func}()' is already exists in {scope_type} '{scope_name}()'!",
									'REDECLARED_VAR' : "The name '{redeclared_var}' is already used from a variable in {scope_type} '{scope_name}()'!"},
						'FORMALPARITEM_FUNC' :{
									'REDECLARED_PAR' : "A parameter with name '{redeclared_par}' is already exists in {scope_type} '{scope_name}()'!",
									'USED_FOR_FUNC' : "A parameter can not have the same name '{par_name}' with the function which belongs!"},
						'ASSIGNMENT_STAT_FUNC' : {
									'UNDECLARED_VAR' : "Undeclared variable '{undeclared_var}' for {scope_type} '{scope_name}()'!"},
						'EXIT_STAT_FUNC' : {
									'NO_LOOP' : "Exit statement not within loop!"},
						'RETURN_STAT_FUNC' : {
									'NO_RETURN' : "Return statement not within function!"},
						'INPUT_STAT_FUNC' : {
									'UNDECLARED_VAR' : "Undeclared variable '{undeclared_var}' for {scope_type} '{scope_name}()'!"},
						'ACTUALPARS_FUNC' : {
									'NOT_EQUAL_LEN' : "Function '{func_name}()' takes {param_num} positional {tense_arg}, but {arg_num} {tense_w} given!",
									'NOT_EQUAL_MODE' : "Function '{func_name}()' takes '{correct_pass_mode}' passing mode argument at position {arg_pos},\nbut '{wrong_pass_mode}' was given!"},
						'ACTUALPARITEM_FUNC' :{
									'UNDECLARED_VAR' : "Undeclared variable '{undeclared_var}' for {scope_type} '{scope_name}()'!"},
						'IDTAIL_FUNC' : {
									'UNDECLARED_VAR' : "Undeclared variable '{undeclared_var}' for {scope_type} '{scope_name}()'!",
									'UNDECLARED_FUNC' : "Undeclared function '{undeclared_func}()' for {scope_type} '{scope_name}()'!",
									'UNCOMPLETED_FUNC' : "The function '{uncompleted_func}()' in {scope_type} '{scope_name}()' called before its definition is complete!"}
						}

			}

'''
	====================================================================================================
										CLASSES													
	====================================================================================================
'''

'''
	====================================================================================================
										Intermediate-Code Generator's Classes											
	====================================================================================================
'''

class Quad:
	def __init__(self, op, term0, term1, term2, label):
	    self.op = op
	    self.term0 = term0
	    self.term1 = term1
	    self.term2 = term2
	    self.label = label

	def to_string(self):
		return (self.op + ", " + self.term0 + ", " + self.term1 + ", " + self.term2)

'''
	====================================================================================================
										Symbol Table's Classes											
	====================================================================================================
'''

class Entity(ABC):
	def __init__(self, name, type):
		self.name = name
		self.type = type
		self.nesting_level = None

	@abstractmethod
	def to_string(self):
		return ("Name: " + self.name + ", " + "Type: " + self.type + ", " + "Nesting Level: " + str(self.nesting_level) + ", ")

class Variable(Entity):
	def __init__(self, name, var_type, offset):
		Entity.__init__(self, name, "Variable")
		self.var_type = var_type
		self.offset = offset

	def to_string(self):
		return (Entity.to_string(self) + "Variable Type: " +\
			 self.var_type + ", " + "Offset: " + str(self.offset))

class Function(Entity):
	def __init__(self, name, start_quad, arguments, framelength):
		Entity.__init__(self, name, "Function")
		self.start_quad = start_quad
		self.arguments = arguments
		self.framelength = framelength

	def to_string(self):
		return (Entity.to_string(self) + "Start Quad: " +\
			 str(self.start_quad) + ", " + "Arguments: " +\
			 ' '.join(argument.to_string() for argument in self.arguments)+\
			 ", " + "Framelength: " + str(self.framelength) )

class Parameter(Entity):
	def __init__(self, name, par_mode, offset):
		Entity.__init__(self, name, "Parameter")
		self.par_mode = par_mode
		self.offset = offset

	def to_string(self):
		return (Entity.to_string(self) + "Parameter Mode: " +\
			 self.par_mode + ", " + "Offset: " + str(self.offset))

class Argument():
	def __init__(self, par_mode):
		self.par_mode = par_mode

	def to_string(self):
		return (self.par_mode)

class Scope():
	def __init__(self, name, entities, framelength):
		self.name = name
		self.entities = entities
		self.framelength = framelength

	def to_string(self):
		return (self.name)

'''
	====================================================================================================
										FUNCTIONS													
	====================================================================================================
'''

'''
	====================================================================================================
										Error Handling Functions													
	====================================================================================================
'''

# The function which checks for valid statement
def is_valid_stat(idtk, tokentk):
	return ((idtk == 'ALNUM_ID') or (tokentk in statement_starters_set))

'''
	The function which checks for equal matching between
	initial statement and terminal statement keywords.

	This function must combined with get_error_line() because
	changes the global variables like line_count and char_count
'''
def terminal_keyword_exists(initial_keyword_id, terminal_keyword_id):
	stl_file.seek(0) # Reset to file's start
	init_count = 0
	terminal_count = 0
	while (True):
		lex()
		if(idtk == terminal_keyword_id):
			terminal_count += 1
		elif(idtk == initial_keyword_id):
			init_count += 1
		elif(idtk == 'EOF_ID'):
			break
	return (init_count == terminal_count)

# The function which return the line where the was spotted
def get_error_line():
	er_line_count = line_count
	if (char_count): er_line_count += 1
	return er_line_count

# The function which truncates tokentk properly for lexical errors
def truncate_token(token):

	if(idtk == 'OTHER_ID'):
		return token[-1:]
	else:
		return ("%s%s" %('...' if(len(token) > 40) else '', token[-40:]))

# The function which checks if error_info contains line attribute
def error_line_is_setted(error_info):
	return (error_info.get('error_line') != None)

# The function which handles errors
def error_handler(mode, error_func, error_id, error_info):
	print_error_line(mode, error_info)
	print_error_msg(mode, error_func, error_id, error_info)
	exit()

# The function which prints the source code error line 
def print_error_line(mode, error_info):
	global line_count
	# Check if there are characters after final EOL
	if (char_count): line_count += 1
	# Check for line override
	if (error_line_is_setted(error_info)):
		line_count = error_info.get('error_line')
	print("%s ERROR around line %d," %(mode_map[mode],line_count))
	print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
	stl_file.seek(0) # Reset to file's start
	for i, line in enumerate(stl_file):
	    if (abs(line_count - 1 - i) <= 2):
	        print(line, end = "")
	print("%s%s" %("" if (line[-1:]=='\n') else '\n', "++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"))

# The function which prints error messages caused in lexical analyzer
def print_error_msg(mode, error_func, error_id, error_info):
	print(error_map[mode][error_func][error_id].format_map(error_info))

'''
	====================================================================================================
										Lexical Analyzer's Functions													
	====================================================================================================
'''

# The function which checks if given char is an english letter
def is_alpha(char):

	return ( (len(char) == 1) and (char >= 'a' and char <= 'z') or (char >= 'A' and char <= 'Z') )

# The function which checks if given char is an english letter or digit
def is_alnum(char):

	return ( is_alpha(char) or char.isdigit() )

# The function which checks if given string contains only english letters and digits
def is_alnum_str(str0):

	for c in str0:
		if(not is_alnum(c)):
			return False
	return True

# The function which delimits number tokens
def is_inrange(num):

	num = int(num)
	return (num >= -32767 and num <= 32767)

# The function which checks if two characters are comment starters
def is_com_starter(char0, char1):

	return ( (char0 == '/') and (char1 == '*' or char1 == '/') )

# The function which checks if a operator is relational
def is_rel_oper(oper_id):

	return (oper_id == 'EQUAL_ID' or oper_id == 'LESSOREQUAL_ID' or
			oper_id == 'GREATEROREQUAL_ID' or oper_id == 'GREATER_ID' or
			oper_id == 'LESS_ID' or oper_id == 'NOTEQUAL_ID')

# The Lexical Analyzer
def lex():

	global tokentk, idtk, char_count, line_count
	tokentk = idtk = ""
	prev_state = state = STATE_START
	buf = []
	
	while (state != OK and state != OKR and state != ERROR):
		
		prev_state = state   # prev_state needed for error handling 
		if(state == STATE_START):	# Used to ignoring comments
			buf.clear()
		c = stl_file.read(1)
		char_count += 1
		if (not c.isspace()): #	Ignoring whitespace characters
			buf.append(c)
		elif (c == '\n'): # Tracing line number
			line_count += 1
			char_count = 0		
		
		# Select next state
		if ( is_alpha(c) ):
			state = decision_table[state][ALPHA]
		elif ( c.isdigit() ):
			state = decision_table[state][DIGIT]
		elif ( c in symbols_map.keys() ):
			state = decision_table[state][symbols_map[c][0]]
		else:
			state = decision_table[state][OTHER]

	if ((state == OKR) and (not c.isspace())):	# Return last read character at OKR state
		buf.pop()
		stl_file.seek(stl_file.tell()-len(c)) # EOF with len = 0 return the file pointer to same position

	tokentk = ''.join(buf)
	if (tokentk in  keywords_map.keys()):
		idtk = keywords_map[tokentk]
	elif (tokentk in symbols_map.keys()):
		idtk = symbols_map[tokentk][1]
	elif (tokentk.isdigit()):
		idtk = 'DIGIT_ID'
		if(not is_inrange(tokentk)):
			idtk = 'OVERFLOW_ID'
			state = ERROR # Throw this at Error state
	elif (is_alnum_str(tokentk)):
		idtk = 'ALNUM_ID'
		if ( state != ERROR ):
			tokentk = tokentk[:30]	# Store only the 30 first characters of a variable (id)
	elif ((len(buf) > 1) and  is_com_starter(buf[-2],buf[-1])):
		idtk = 'COMMENT_ID'
	elif (not c):
		idtk = 'EOF_ID'
	else:
		idtk = 'OTHER_ID'
	
	#ERROR Ηandling
	if (state == ERROR):
		error_handler('LEX_MODE', prev_state, idtk, {'lex_token' : truncate_token(tokentk)} )

'''
	====================================================================================================
										Syntax Analyzer's Functions													
	====================================================================================================
'''

def program():
	
	'''
		<program> ::= program id <block> endprogram
	'''

	global main_framelength
	lex() # The first call of lex()
	if(idtk == 'PROGRAM_ID'):
		lex()
		if (idtk == 'ALNUM_ID'):
			program_name = tokentk
			insert_scope(Scope(program_name, [], STD_FRAMELENGTH)) # Program's Scope
			lex()
			block(program_name)
			if (idtk == 'ENDPROGRAM_ID'):
				lex()
				if(idtk == 'EOF_ID'):
					# Is the final token lex() not needed here
					main_framelength = symbol_table[nesting_level].framelength
					delete_scope()
					print("Program compiled without errors!")
				else:
					error_handler('SYNTAX_MODE', 'PROGRAM_FUNC', 'EOF_ID', {'unexp_token' : tokentk})
			else:
				er_line_count = get_error_line()
				er_tokentk = tokentk
				er_idtk = idtk
				if(terminal_keyword_exists('PROGRAM_ID', 'ENDPROGRAM_ID') or er_idtk == 'PROGRAM_ID'):
					if(is_valid_stat(er_idtk, er_tokentk)):
						error_handler('SYNTAX_MODE', 'PROGRAM_FUNC', 'SEMICOLON_ID', {'error_line' : er_line_count})
					else:
						error_handler('SYNTAX_MODE', 'PROGRAM_FUNC', 'UNEXPECTED_ID', {'unexp_token' : er_tokentk,
																						'error_line' : er_line_count})
				else:
					error_handler('SYNTAX_MODE', 'PROGRAM_FUNC', 'ENDPROGRAM_ID', {'error_line' : er_line_count})
		else:
			error_handler('SYNTAX_MODE', 'PROGRAM_FUNC', 'ALNUM_ID', {'prog_name' : tokentk})
	else:
		error_handler('SYNTAX_MODE', 'PROGRAM_FUNC', 'PROGRAM_ID', {})

def block(name, return_list = None):

	'''
		<block> ::= <declarations> <subprograms> <statements>
	'''

	declarations()
	subprograms()
	entity = lookup_enclosing_scopes(name)
	if(entity_exists(entity) and is_function(entity)): # Exclude the main program
		entity.start_quad = nextquad()
	genquad("begin_block",name,"_","_")
	statements(return_list = return_list)
	if(idtk == 'ENDPROGRAM_ID'):
		genquad("halt","_","_","_")
	genquad("end_block",name,"_","_")

def declarations():

	'''
		<declarations> ::= (declare <varlist>;)*
	'''

	while(idtk == 'DECLARE_ID'):
		er_line_count = get_error_line()
		lex()
		varlist()
		if(idtk == 'SEMICOLON_ID'):
			lex()
		else:
			error_handler('SYNTAX_MODE', 'DECLARATIONS_FUNC', 'SEMICOLON_ID', {'error_line' : er_line_count})

def varlist():

	'''
		<varlist> ::= ε | id ( , id )*
	'''

	if(idtk == 'ALNUM_ID'):
		entity = lookup_current_scope(tokentk)
		if(not entity_exists(entity)):
			if(not equal_to_scope_name(tokentk)):
				insert_entity(Variable(tokentk, "Regular", symbol_table[nesting_level].framelength))
				lex() # outer ALNUM_ID lex() call
				while(idtk == 'COMMA_ID'):
					lex()
					if(idtk == 'ALNUM_ID'):
						entity = lookup_current_scope(tokentk)
						if(not entity_exists(entity)):
							if(not equal_to_scope_name(tokentk)):
								insert_entity(Variable(tokentk, "Regular", symbol_table[nesting_level].framelength))
								lex() # inner ALNUM_ID lex() call
							else:
								error_handler('SEM_MODE', 'VARLIST_FUNC', 'USED_FOR_FUNC', {'var_name' : tokentk})		
						else:
							error_handler('SEM_MODE', 'VARLIST_FUNC', 'REDECLARED_VAR', {'redeclared_var' : tokentk,
																							'scope_type' : get_scope_type(),
																							'scope_name' : symbol_table[nesting_level].name})
					else:
						error_handler('SYNTAX_MODE', 'VARLIST_FUNC', 'ALNUM_ID', {'var_name' : tokentk})	
			else:
				error_handler('SEM_MODE', 'VARLIST_FUNC', 'USED_FOR_FUNC', {'var_name' : tokentk})
		else:
			error_handler('SEM_MODE', 'VARLIST_FUNC', 'REDECLARED_VAR', {'redeclared_var' : tokentk,
																		'scope_type' : get_scope_type(),
																		'scope_name' : symbol_table[nesting_level].name})

def subprograms():

	'''
		<subprograms> ::= (<subprogram>)*
	'''

	while(idtk == 'FUNCTION_ID'):
		subprogram()

def subprogram():
	
	'''
		<subprogram> ::= function id <funcbody> endfunction
	'''

	if(idtk == 'FUNCTION_ID'):
		lex()
		if(idtk == 'ALNUM_ID'):
			func_name = tokentk
			entity = lookup_current_scope(func_name)
			if(not entity_exists(entity)):
				func_entity = Function(func_name, None, [], 0)
				insert_entity(func_entity)
				insert_scope(Scope(func_name, [], STD_FRAMELENGTH))
				lex() # ALNUM_ID lex() call
				return_list = [False]
				funcbody(func_name, return_list)
				if(idtk == 'ENDFUNCTION_ID'):
					lex()
					if(return_list[0] == False):
						error_handler('SEM_MODE', 'SUBPROGRAM_FUNC', 'NO_RETURN', {'func_name' : func_name})
					else:
						# Update function's framelength
						func_entity.framelength = symbol_table[nesting_level].framelength
						delete_scope()
				else:
					er_line_count = get_error_line()
					er_tokentk = tokentk
					er_idtk = idtk
					if(terminal_keyword_exists('FUNCTION_ID', 'ENDFUNCTION_ID')):
						if(is_valid_stat(er_idtk, er_tokentk)):
							error_handler('SYNTAX_MODE', 'SUBPROGRAM_FUNC', 'SEMICOLON_ID', {'error_line' : er_line_count})
						else:
							error_handler('SYNTAX_MODE', 'SUBPROGRAM_FUNC', 'UNEXPECTED_ID', {'unexp_token' : er_tokentk,
																								'error_line' : er_line_count})
					else:
						error_handler('SYNTAX_MODE', 'SUBPROGRAM_FUNC', 'ENDFUNCTION_ID', {'error_line' : er_line_count})
			else:
				if(is_var_par(entity)):
					error_handler('SEM_MODE', 'SUBPROGRAM_FUNC', 'REDECLARED_VAR', {'redeclared_var' : func_name,
																					'scope_type' : get_scope_type(),
																					'scope_name' : symbol_table[nesting_level].name})
				elif(is_function(entity)):
					error_handler('SEM_MODE', 'SUBPROGRAM_FUNC', 'REDECLARED_FUNC', {'redeclared_func' : func_name,
																						'scope_type' : get_scope_type(),
																						'scope_name' : symbol_table[nesting_level].name})
		else:
			error_handler('SYNTAX_MODE', 'SUBPROGRAM_FUNC', 'ALNUM_ID', {'sub_prog_name' : tokentk})

def funcbody(func_name, return_list):

	'''
		<funcbody> ::= <formalpars> <block>
	'''

	formalpars(func_name)
	block(func_name, return_list)

def formalpars(func_name):

	'''
		<formalpars> ::= ( <formalparlist> )
	'''

	if(idtk == 'PARENTHESIS_OPEN_ID'):
		lex()
		formalparlist(func_name)
		if(idtk == 'PARENTHESIS_CLOSE_ID'):
			lex()
		else:
			error_handler('SYNTAX_MODE', 'FORMALPARS_FUNC', 'PARENTHESIS_CLOSE_ID', {'func_name' : func_name})
	else:
		error_handler('SYNTAX_MODE', 'FORMALPARS_FUNC', 'PARENTHESIS_OPEN_ID', {'func_name' : func_name})

def formalparlist(func_name):

	'''
		<formalparlist> ::= <formalparitem> ( , <formalparitem> )* | ε
	'''

	if (idtk != 'PARENTHESIS_CLOSE_ID'):
		entity = lookup_enclosing_scopes(func_name)
		formalparitem(entity)
		while(idtk == 'COMMA_ID'):
			lex()
			formalparitem(entity)

def formalparitem(func_entity):

	'''
		<formalparitem> ::= in id | inout id | inandout id
	'''

	par_mode = tokentk
	if(idtk == 'IN_ID'):
		lex()
		par_name = tokentk
		if(idtk == 'ALNUM_ID'):
			lex()
		else:
			error_handler('SYNTAX_MODE', 'FORMALPARITEM_FUNC', 'ALNUM_ID', {'par_name' : par_name})
	elif(idtk == 'INOUT_ID'):
		lex()
		par_name = tokentk
		if(idtk == 'ALNUM_ID'):
			lex()
		else:
			error_handler('SYNTAX_MODE', 'FORMALPARITEM_FUNC', 'ALNUM_ID', {'par_name' : par_name})
	elif(idtk == 'INANDOUT_ID'):
		lex()
		par_name = tokentk
		if(idtk == 'ALNUM_ID'):
			lex()
		else:
			error_handler('SYNTAX_MODE', 'FORMALPARITEM_FUNC', 'ALNUM_ID', {'par_name' : par_name})
	else:
		error_handler('SYNTAX_MODE', 'FORMALPARITEM_FUNC', 'OTHER_ID', {'func_name' : func_entity.name})
	entity = lookup_current_scope(par_name)
	if(not entity_exists(entity)):
		if(not equal_to_scope_name(par_name)):
			insert_entity(Parameter(par_name, par_mode, symbol_table[nesting_level].framelength))
			func_entity.arguments.append(Argument(par_mode))
		else:
			error_handler('SEM_MODE', 'FORMALPARITEM_FUNC', 'USED_FOR_FUNC', {'par_name' : par_name})
	else:
		error_handler('SEM_MODE', 'FORMALPARITEM_FUNC', 'REDECLARED_PAR', {'redeclared_par' : par_name,
																			'scope_type' : get_scope_type(),
																			'scope_name' : symbol_table[nesting_level].name})
	
def statements(exit_list = None, return_list = None):

	'''
		<statements> ::= <statement> ( ; <statement> )*
	'''

	statement(exit_list, return_list)
	while(idtk == 'SEMICOLON_ID'):
		lex()
		statement(exit_list, return_list)

def statement(exit_list = None, return_list = None):

	''' 
		<statement> ::= ε | <assignment-stat> | <if-stat> | <while-stat> |
							<do-while-stat> | <loop-stat> | <exit-stat> | 
							<forcase-stat> | <incase-stat> | <return-stat> |
							<input-stat> | <print-stat>
	'''

	if(idtk == 'ALNUM_ID'): assignment_stat()
	elif(idtk == 'IF_ID'): if_stat(exit_list, return_list)
	elif(idtk == 'WHILE_ID'): while_stat(exit_list, return_list)
	elif(idtk == 'DOWHILE_ID'): do_while_stat(exit_list, return_list)
	elif(idtk == 'LOOP_ID'): loop_stat(return_list)
	elif(idtk == 'EXIT_ID'): exit_stat(exit_list)
	elif(idtk == 'FORCASE_ID'): forcase_stat(exit_list, return_list)
	elif(idtk == 'INCASE_ID'): incase_stat(exit_list, return_list)
	elif(idtk == 'RETURN_ID'): return_stat(return_list)
	elif(idtk == 'INPUT_ID'): input_stat()
	elif(idtk == 'PRINT_ID'): print_stat()

def assignment_stat():
	
	'''
		<assignment-stat> ::= id := <expression>
	'''

	if(idtk == 'ALNUM_ID'):
		var_name = tokentk
		entity = lookup_enclosing_scopes(var_name)
		if(entity_exists(entity) and is_var_par(entity)):
			lex()
			if(idtk == 'ASSIGN_ID'): 
				lex()
				e1 = expression()
				genquad(":=",e1,"_",var_name)
			else:
				error_handler('SYNTAX_MODE', 'ASSIGNMENT_STAT_FUNC', 'ASSIGN_ID', {'unexp_token' : tokentk})
		else:
			error_handler('SEM_MODE', 'ASSIGNMENT_STAT_FUNC', 'UNDECLARED_VAR', {'undeclared_var' : var_name,
																				'scope_type' : get_scope_type(),
																				'scope_name' : symbol_table[nesting_level].name})
		
def if_stat(exit_list, return_list):

	'''
		<if-stat> ::= if (<condition>) then <statements> <elsepart> endif
	'''

	if(idtk == 'IF_ID'):
		lex()
		if(idtk == 'PARENTHESIS_OPEN_ID'):
			lex()
			cond_lists = condition()
			if (idtk == 'PARENTHESIS_CLOSE_ID'):
				lex()
				if(idtk == 'THEN_ID'):
					lex()
					backpatch(cond_lists[0],nextquad())
					statements(exit_list, return_list)
					if_list = makelist(nextquad())
					genquad("jump","_","_","_")
					backpatch(cond_lists[1],nextquad())
					elsepart(exit_list, return_list)
					if(idtk == 'ENDIF_ID'):
						lex()
						backpatch(if_list,nextquad())
					else:
						er_line_count = get_error_line()
						er_tokentk = tokentk
						er_idtk = idtk
						if(terminal_keyword_exists('IF_ID', 'ENDIF_ID')):
							if(is_valid_stat(er_idtk, er_tokentk)):
								error_handler('SYNTAX_MODE', 'IF_STAT_FUNC', 'SEMICOLON_ID', {'error_line' : er_line_count})
							else:
								error_handler('SYNTAX_MODE', 'IF_STAT_FUNC', 'UNEXPECTED_ID', {'unexp_token' : er_tokentk,
																							'error_line' : er_line_count})
						else:
							error_handler('SYNTAX_MODE', 'IF_STAT_FUNC', 'ENDIF_ID', {'error_line' : er_line_count})
				else:
					er_line_count = get_error_line()
					er_tokentk = tokentk
					er_idtk = idtk
					if(terminal_keyword_exists('IF_ID', 'THEN_ID')):
						error_handler('SYNTAX_MODE', 'IF_STAT_FUNC', 'EXPECTED_THEN_ID', {'unexp_token' : er_tokentk,
																					'error_line' : er_line_count})
					else:
						error_handler('SYNTAX_MODE', 'IF_STAT_FUNC', 'THEN_ID', {'error_line' : er_line_count})
			else:
				error_handler('SYNTAX_MODE', 'IF_STAT_FUNC', 'PARENTHESIS_CLOSE_ID', {})
		else:
			error_handler('SYNTAX_MODE', 'IF_STAT_FUNC', 'PARENTHESIS_OPEN_ID', {})

def elsepart(exit_list, return_list):
	
	'''
		<elsepart> ::= ε | else <statements>
	'''

	if(idtk == 'ELSE_ID'):
		lex()
		statements(exit_list, return_list)

def while_stat(exit_list, return_list):

	'''
		<while-stat> ::= while (<condition>) <statements> endwhile
	'''

	if(idtk == 'WHILE_ID'):
		lex()
		if(idtk == 'PARENTHESIS_OPEN_ID'):
			lex()
			first_cond_quad = str(nextquad())
			cond_lists = condition()
			if(idtk == 'PARENTHESIS_CLOSE_ID'):
				lex()
				backpatch(cond_lists[0],nextquad())
				statements(exit_list, return_list)
				if(idtk == 'ENDWHILE_ID'):
					lex()
					genquad("jump","_","_",first_cond_quad)
					backpatch(cond_lists[1],nextquad())
				else:
					er_line_count = get_error_line()
					er_tokentk = tokentk
					er_idtk = idtk
					if(terminal_keyword_exists('WHILE_ID', 'ENDWHILE_ID')):
						if(is_valid_stat(er_idtk, er_tokentk)):
							error_handler('SYNTAX_MODE', 'WHILE_STAT_FUNC', 'SEMICOLON_ID', {'error_line' : er_line_count})
						else:
							error_handler('SYNTAX_MODE', 'WHILE_STAT_FUNC', 'UNEXPECTED_ID', {'unexp_token' : er_tokentk,
																							'error_line' : er_line_count})
					else:
						error_handler('SYNTAX_MODE', 'WHILE_STAT_FUNC', 'ENDWHILE_ID', {'error_line' : er_line_count})
			else:
				error_handler('SYNTAX_MODE', 'WHILE_STAT_FUNC', 'PARENTHESIS_CLOSE_ID', {})
		else:
			error_handler('SYNTAX_MODE', 'WHILE_STAT_FUNC', 'PARENTHESIS_OPEN_ID', {})

def do_while_stat(exit_list, return_list):

	'''
		<do-while-stat> ::= dowhile <statements> enddowhile (<condition>)
	'''

	if(idtk == 'DOWHILE_ID'):
		lex()
		first_stat_quad = str(nextquad())
		statements(exit_list, return_list)
		if(idtk == 'ENDDOWHILE_ID'):
			lex()
			if(idtk == 'PARENTHESIS_OPEN_ID'):
				lex()
				cond_lists = condition()
				if(idtk == 'PARENTHESIS_CLOSE_ID'):
					lex()
					backpatch(cond_lists[0],first_stat_quad)
					backpatch(cond_lists[1],nextquad())
				else:
					error_handler('SYNTAX_MODE', 'DO_WHILE_STAT_FUNC', 'PARENTHESIS_CLOSE_ID', {})
			else:
				error_handler('SYNTAX_MODE', 'DO_WHILE_STAT_FUNC', 'PARENTHESIS_OPEN_ID', {})
		else:
			er_line_count = get_error_line()
			er_tokentk = tokentk
			er_idtk = idtk
			if(terminal_keyword_exists('DOWHILE_ID', 'ENDDOWHILE_ID')):
				if(is_valid_stat(er_idtk, er_tokentk)):
					error_handler('SYNTAX_MODE', 'DO_WHILE_STAT_FUNC', 'SEMICOLON_ID', {'error_line' : er_line_count})
				else:
					error_handler('SYNTAX_MODE', 'DO_WHILE_STAT_FUNC', 'UNEXPECTED_ID', {'unexp_token' : er_tokentk,
																					'error_line' : er_line_count})
			else:
				error_handler('SYNTAX_MODE', 'DO_WHILE_STAT_FUNC', 'ENDWHILE_ID', {'error_line' : er_line_count})

def loop_stat(return_list):

	'''
		<loop-stat> ::= loop <statements> endloop
	'''

	if(idtk == 'LOOP_ID'):
		lex()
		first_stat_quad = str(nextquad())
		exit_list = emptylist()
		statements(exit_list, return_list)
		if(idtk == 'ENDLOOP_ID'):
			lex()
			genquad("jump","_","_",first_stat_quad)
			if(exit_list):
				backpatch(exit_list,nextquad())
		else:
			er_line_count = get_error_line()
			er_tokentk = tokentk
			er_idtk = idtk
			if(terminal_keyword_exists('LOOP_ID', 'ENDLOOP_ID')):
				if(is_valid_stat(er_idtk, er_tokentk)):
					error_handler('SYNTAX_MODE', 'LOOP_STAT_FUNC', 'SEMICOLON_ID', {'error_line' : er_line_count})
				else:
					error_handler('SYNTAX_MODE', 'LOOP_STAT_FUNC', 'UNEXPECTED_ID', {'unexp_token' : er_tokentk,
																					'error_line' : er_line_count})
			else:
				error_handler('SYNTAX_MODE', 'LOOP_STAT_FUNC', 'ENDLOOP_ID', {'error_line' : er_line_count})

def exit_stat(exit_list):

	'''
		<exit-stat> ::= exit
	'''

	if(idtk == 'EXIT_ID'): 
		if(exit_list != None):
			lex()
			exit_quad_list = makelist(nextquad())
			exit_list[:]  = merge(exit_list,exit_quad_list) # Python's syntax
			genquad("jump","_","_","_")
		else:
			error_handler('SEM_MODE', 'EXIT_STAT_FUNC', 'NO_LOOP', {})

def forcase_stat(exit_list, return_list):

	'''
		<forcase-stat> ::= forcase 
								( when (<condition>) : <statements> )*
								default: <statements> enddefault
							endforcase
	'''

	if(idtk == 'FORCASE_ID'):
		lex()
		first_cond_quad = str(nextquad())
		jump_list = emptylist()
		while (idtk == 'WHEN_ID'):
			lex()
			if(idtk == 'PARENTHESIS_OPEN_ID'):
				lex()
				cond_lists = condition()
				if(idtk == 'PARENTHESIS_CLOSE_ID'):
					lex()
					if(idtk == 'COLON_ID'):
						lex()
						backpatch(cond_lists[0],nextquad())
						statements(exit_list, return_list)
						jump_quad_list = makelist(nextquad())
						jump_list = merge(jump_list,jump_quad_list)
						genquad("jump","_","_","_")
						backpatch(cond_lists[1],nextquad())
					else:
						error_handler('SYNTAX_MODE', 'FORCASE_STAT_FUNC', 'WCOLON_ID', {'unexp_token' : tokentk})
				else:
					error_handler('SYNTAX_MODE', 'FORCASE_STAT_FUNC', 'PARENTHESIS_CLOSE_ID', {})
			else:
				error_handler('SYNTAX_MODE', 'FORCASE_STAT_FUNC', 'PARENTHESIS_OPEN_ID', {})

		if(idtk == 'DEFAULT_ID'):
			lex()
			if(idtk == 'COLON_ID'):
				lex()
				statements(exit_list, return_list)
				if(idtk == 'ENDDEFAULT_ID'):
					lex()
					genquad("jump","_","_",first_cond_quad)
					if(idtk == 'ENDFORCASE_ID'):
						lex()
						backpatch(jump_list,nextquad())
					else:
						er_line_count = get_error_line()
						er_tokentk = tokentk
						er_idtk = idtk
						if(terminal_keyword_exists('FORCASE_ID', 'ENDFORCASE_ID')):
							error_handler('SYNTAX_MODE', 'FORCASE_STAT_FUNC', 'EXPECTED_ENDFORCASE_ID', {'unexp_token' : er_tokentk,
																						'error_line' : er_line_count})
						else:
							error_handler('SYNTAX_MODE', 'FORCASE_STAT_FUNC', 'ENDFORCASE_ID', {'error_line' : er_line_count})
				else:
					er_line_count = get_error_line()
					er_tokentk = tokentk
					er_idtk = idtk
					if(terminal_keyword_exists('DEFAULT_ID', 'ENDDEFAULT_ID')):
						if(is_valid_stat(er_idtk, er_tokentk)):
							error_handler('SYNTAX_MODE', 'FORCASE_STAT_FUNC', 'SEMICOLON_ID', {'error_line' : er_line_count})
						else:
							error_handler('SYNTAX_MODE', 'FORCASE_STAT_FUNC', 'UNEXPECTED_ID', {'unexp_token' : er_tokentk,
																						'error_line' : er_line_count})
					else:
						error_handler('SYNTAX_MODE', 'FORCASE_STAT_FUNC', 'ENDDEFAULT_ID', {'error_line' : er_line_count})
			else:
				error_handler('SYNTAX_MODE', 'FORCASE_STAT_FUNC', 'DCOLON_ID', {'unexp_token' : tokentk})
		else:
			er_line_count = get_error_line()
			er_tokentk = tokentk
			er_idtk = idtk
			if(terminal_keyword_exists('FORCASE_ID', 'DEFAULT_ID')):
				if(is_valid_stat(er_idtk, er_tokentk)):
					error_handler('SYNTAX_MODE', 'FORCASE_STAT_FUNC', 'SEMICOLON_ID', {'error_line' : er_line_count})
				else:
					error_handler('SYNTAX_MODE', 'FORCASE_STAT_FUNC', 'UNEXPECTED_ID', {'unexp_token' : er_tokentk,
																				'error_line' : er_line_count})
			else:
				error_handler('SYNTAX_MODE', 'FORCASE_STAT_FUNC', 'DEFAULT_ID', {'error_line' : er_line_count})

def incase_stat(exit_list, return_list):

	'''
		<incase-stat> ::= incase
							( when (<condition>) : <statements> )*
						endincase
	'''

	if(idtk == 'INCASE_ID'):
		lex()
		first_cond_quad = str(nextquad())
		incase_flag = newtemp()
		genquad(":=","0","_",incase_flag)
		while (idtk == 'WHEN_ID'):
			lex()
			if(idtk == 'PARENTHESIS_OPEN_ID'):
				lex()
				cond_lists = condition()
				if(idtk == 'PARENTHESIS_CLOSE_ID'):
					lex()
					if(idtk == 'COLON_ID'):
						lex()
						backpatch(cond_lists[0],nextquad())
						statements(exit_list, return_list)
						genquad(":=","1","_",incase_flag)
						backpatch(cond_lists[1],nextquad())
					else:
						error_handler('SYNTAX_MODE', 'INCASE_STAT_FUNC', 'COLON_ID', {'unexp_token' : tokentk})
				else:
					error_handler('SYNTAX_MODE', 'INCASE_STAT_FUNC', 'PARENTHESIS_CLOSE_ID', {})
			else:
				error_handler('SYNTAX_MODE', 'INCASE_STAT_FUNC', 'PARENTHESIS_OPEN_ID', {})

		if(idtk == 'ENDINCASE_ID'):
			lex()
			genquad("=",incase_flag,"1",first_cond_quad)
		else:
			er_line_count = get_error_line()
			er_tokentk = tokentk
			er_idtk = idtk
			if(terminal_keyword_exists('INCASE_ID', 'ENDINCASE_ID')):
				if(is_valid_stat(er_idtk, er_tokentk)):
					error_handler('SYNTAX_MODE', 'INCASE_STAT_FUNC', 'SEMICOLON_ID', {'error_line' : er_line_count})
				else:
					error_handler('SYNTAX_MODE', 'INCASE_STAT_FUNC', 'UNEXPECTED_ID', {'unexp_token' : er_tokentk,
																				'error_line' : er_line_count})
			else:
				error_handler('SYNTAX_MODE', 'INCASE_STAT_FUNC', 'ENDINCASE_ID', {'error_line' : er_line_count})

def return_stat(return_list):

	'''
		<return-stat> ::= return <expression>
	'''

	if(idtk == 'RETURN_ID'):
		if(return_list != None):
			return_list[:] = [True]
			lex()
			e1 = expression()
			genquad("retv",e1,"_","_")
		else:
			error_handler('SEM_MODE', 'RETURN_STAT_FUNC', 'NO_RETURN', {})

def input_stat():
	
	'''
		<input-stat> ::= input id
	'''

	if(idtk == 'INPUT_ID'):
		lex()
		var_name = tokentk
		if(idtk == 'ALNUM_ID'):
			entity = lookup_enclosing_scopes(var_name)
			if(entity_exists(entity) and is_var_par(entity)):
				lex()
				genquad("inp",var_name,"_","_")
			else:
				error_handler('SEM_MODE', 'INPUT_STAT_FUNC', 'UNDECLARED_VAR', {'undeclared_var' : var_name,
																				'scope_type' : get_scope_type(),
																				'scope_name' : symbol_table[nesting_level].name})
		else:
			error_handler('SYNTAX_MODE', 'INPUT_STAT_FUNC', 'ALNUM_ID', {'var_name' : var_name})

def print_stat():

	'''
		<print-stat> ::= print <expression>
	'''

	if(idtk == 'PRINT_ID'):
		lex()
		e1 = expression()
		genquad("out",e1,"_","_")

def actualpars(func_name):

	'''
		<actualpars> ::= ( <actualparlist> )
	'''
	
	if(idtk == 'PARENTHESIS_OPEN_ID'):
		lex()
		arg_list = emptylist()
		actualparlist(arg_list, func_name) # Fill the list with function's arguments
		if(idtk == 'PARENTHESIS_CLOSE_ID'):
			er_line_count = get_error_line()
			lex()
			func_entity = lookup_enclosing_scopes(func_name)
			if(have_equal_len(arg_list,func_entity.arguments)):
				pos = 1
				for arg_elem, argument in zip(arg_list, func_entity.arguments):
					if(arg_elem[1] == argument.par_mode):
						pos += 1
						genquad("par",arg_elem[0],par_mode_map[arg_elem[1]],"_")
					else:
						error_handler('SEM_MODE','ACTUALPARS_FUNC','NOT_EQUAL_MODE',{'func_name' : func_name,
																					'correct_pass_mode' : argument.par_mode,
																					'wrong_pass_mode' : arg_elem[1],
																					'arg_pos' : pos,
																					'error_line' : er_line_count})
				ret_var = newtemp()
				genquad("par",ret_var,"RET","_");		
				genquad("call",func_name,"_","_")
				return ret_var
			else:
				error_handler('SEM_MODE', 'ACTUALPARS_FUNC', 'NOT_EQUAL_LEN', {'func_name' : func_name,
																				'param_num' : len(func_entity.arguments),
																				'arg_num' : len(arg_list),
																				'tense_arg' : "argument" if (len(func_entity.arguments) == 1) else "arguments",
																				'tense_w' : "was" if (len(arg_list) == 1) else "were",
																				'error_line' : er_line_count})
		else:
			error_handler('SYNTAX_MODE', 'ACTUALPARS_FUNC', 'PARENTHESIS_CLOSE_ID', {'func_name' : func_name})
	else:
		error_handler('SYNTAX_MODE', 'ACTUALPARS_FUNC', 'PARENTHESIS_OPEN_ID', {'func_name' : func_name})

def actualparlist(arg_list, func_name):

	'''
		<actualparlist> ::= <actualparitem> ( , <actualparitem> )* | ε
	'''

	if (idtk != 'PARENTHESIS_CLOSE_ID'):
		actualparitem(arg_list, func_name)
		while(idtk == 'COMMA_ID'):
			lex()
			actualparitem(arg_list, func_name)

def actualparitem(arg_list, func_name):

	'''
		<actualparitem> ::= in <expression> | inout id | inandout id
	'''

	par_mode = tokentk
	if(idtk == 'IN_ID'):
		lex()
		var_name = expression()
	elif(idtk == 'INOUT_ID'):
		lex()
		if(idtk == 'ALNUM_ID'):
			var_name = tokentk
			entity = lookup_enclosing_scopes(var_name)
			if(entity_exists(entity) and is_var_par(entity)):
				lex()
			else:
				error_handler('SEM_MODE', 'ACTUALPARITEM_FUNC', 'UNDECLARED_VAR', {'undeclared_var' : var_name,
																					'scope_type' : get_scope_type(),
																					'scope_name' : symbol_table[nesting_level].name})
		else:
			error_handler('SYNTAX_MODE', 'ACTUALPARITEM_FUNC', 'ALNUM_ID', {'arg_name' : tokentk})
	elif(idtk == 'INANDOUT_ID'):
		lex()
		if(idtk == 'ALNUM_ID'):
			var_name = tokentk
			entity = lookup_enclosing_scopes(var_name)
			if(entity_exists(entity) and is_var_par(entity)):
				lex()
			else:
				error_handler('SEM_MODE', 'ACTUALPARITEM_FUNC', 'UNDECLARED_VAR', {'undeclared_var' : var_name,
																					'scope_type' : get_scope_type(),
																					'scope_name' : symbol_table[nesting_level].name})
		else:
			error_handler('SYNTAX_MODE', 'ACTUALPARITEM_FUNC', 'ALNUM_ID', {'arg_name' : tokentk})
	else:
		error_handler('SYNTAX_MODE', 'ACTUALPARITEM_FUNC', 'OTHER_ID', {'func_name' : func_name})
	arg_list.append([var_name,par_mode])

def condition():

	'''
		<condition> ::= <boolterm> (or <boolterm>)*
	'''

	cond_lists = boolterm()
	condtrue_list = cond_lists[0]
	while(idtk == 'OR_ID'):
		lex()
		backpatch(cond_lists[1],nextquad())
		cond_lists = boolterm()
		condtrue_list = merge(condtrue_list,cond_lists[0])
	return [condtrue_list,cond_lists[1]]

def boolterm():
	
	'''
		<boolterm> ::= <boolfactor> (and <boolfactor>)*
	'''

	bt_lists = boolfactor()
	btfalse_list = bt_lists[1]
	while(idtk == 'AND_ID'):
		lex()
		backpatch(bt_lists[0],nextquad())
		bt_lists = boolfactor()
		btfalse_list = merge(btfalse_list,bt_lists[1])
	return [bt_lists[0],btfalse_list]

def boolfactor():

	'''
		<boolfactor> ::= not [<condition>] | [<condition>] | <expression> <relational-oper> <expression> 
	'''

	if(idtk == 'NOT_ID'):
		lex()
		if(idtk == 'BRACKET_OPEN_ID'):
			lex()
			bf_lists = condition()
			if (idtk == 'BRACKET_CLOSE_ID'):
				lex()
				return [bf_lists[1],bf_lists[0]]
			else:
				error_handler('SYNTAX_MODE', 'BOOLFACTOR_FUNC', 'BRACKET_CLOSE_ID', {})
		else:
			error_handler('SYNTAX_MODE', 'BOOLFACTOR_FUNC', 'BRACKET_OPEN_ID', {})
	elif(idtk == 'BRACKET_OPEN_ID'):
		lex()
		bf_lists = condition()
		if(idtk == 'BRACKET_CLOSE_ID'):
			lex()
			return bf_lists
		else:
			error_handler('SYNTAX_MODE', 'BOOLFACTOR_FUNC', 'BRACKET_CLOSE_ID', {})
	else:
		e1 = expression()
		if(is_rel_oper(idtk)):
			oper = relational_oper()
			e2 = expression()
			bftrue_list = makelist(nextquad())
			genquad(oper,e1,e2,"_")
			bffalse_list = makelist(nextquad())
			genquad("jump","_","_","_")
			return [bftrue_list,bffalse_list]
		else:
			error_handler('SYNTAX_MODE', 'BOOLFACTOR_FUNC', 'NOT_REL_OPER_ID', {'rel_op' : tokentk})

def expression():

	'''
		<expression> ::= <optional-sign> <term> ( <add-oper> <term>)* 
	'''

	sign = optional_sign()
	t1 = term()
	if(sign != None):
		tmp_var = newtemp()
		genquad(sign,t1,"_",tmp_var)
		t1 = tmp_var
	while (idtk == 'ADD_ID' or idtk == 'MINUS_ID'):
		oper =  add_oper()
		t2 = term()
		tmp_var =  newtemp()
		genquad(oper,t1,t2,tmp_var)
		t1 = tmp_var
	return t1
	
def term():

	'''
		<term> ::= <factor> (<mul-oper> <factor>)*
	'''

	f1 = factor()
	while(idtk == 'MULT_ID' or idtk == 'DIV_ID'):
		oper = mul_oper()
		f2 = factor()
		tmp_var = newtemp()
		genquad(oper,f1,f2,tmp_var)
		f1 = tmp_var
	return f1

def factor():

	'''
		<factor> ::= constant | (<expression>) | id <idtail>
	'''

	if(idtk == 'DIGIT_ID'): 
		const = tokentk
		lex()
		return const # F.place = Constant
	elif(idtk == 'PARENTHESIS_OPEN_ID'):
		lex()
		tmp_e = expression() # F.place = E.place
		if(idtk == 'PARENTHESIS_CLOSE_ID'):
			lex()
			return tmp_e
		else:
			error_handler('SYNTAX_MODE', 'FACTOR_FUNC', 'PARENTHESIS_CLOSE_ID', {})
	elif(idtk == 'ALNUM_ID'):
		var_name = tokentk
		lex()
		return idtail(var_name) # F.place = IDT.place
	else:
		error_handler('SYNTAX_MODE', 'FACTOR_FUNC', 'OTHER_ID', {'factor' : tokentk})

def idtail(var_name):

	'''
		<idtail> ::=  ε | <actualpars>
	'''

	entity = lookup_enclosing_scopes(var_name)
	if(idtk == 'PARENTHESIS_OPEN_ID'):
		if(entity_exists(entity) and is_function(entity)):
			if(is_def_compl(entity) or is_recursive_func(entity)):
				return actualpars(var_name) # IDT.place = AP.place
			else:
				error_handler('SEM_MODE', 'IDTAIL_FUNC', 'UNCOMPLETED_FUNC', {'uncompleted_func' : var_name,
																			'scope_type' : get_scope_type(),
																			'scope_name' : symbol_table[nesting_level].name})
		else:
			error_handler('SEM_MODE', 'IDTAIL_FUNC', 'UNDECLARED_FUNC', {'undeclared_func' : var_name,
																			'scope_type' : get_scope_type(),
																			'scope_name' : symbol_table[nesting_level].name})
	else:
		if(entity_exists(entity) and is_var_par(entity)):
			return var_name
		else:
			error_handler('SEM_MODE', 'IDTAIL_FUNC', 'UNDECLARED_VAR', {'undeclared_var' : var_name,
																		'scope_type' : get_scope_type(),
																		'scope_name' : symbol_table[nesting_level].name})

def relational_oper():

	'''
		<relational-oper> ::= = | <= | >= | > | < | <>
	'''
	tmp_relop = tokentk
	lex()
	return tmp_relop

def add_oper():

	'''
		<add-oper> ::= + | -
	'''

	tmp_aop = tokentk
	lex()
	return tmp_aop

def mul_oper():

	'''
		<mul-oper> ::= * | /
	'''

	tmp_mop = tokentk
	lex()
	return tmp_mop

def optional_sign():

	'''
		<optional-sign> ::= ε | <add-oper> 
	'''

	if(idtk == 'ADD_ID' or idtk == 'MINUS_ID'):
		return add_oper()
	else:
		return None

'''
	====================================================================================================
										Intermediate-Code Generator's Functions											
	====================================================================================================
'''

def nextquad():
	return (latest_quad_label + 1)

def genquad(op, term0, term1, term2):
	global latest_quad_label
	latest_quad_label += 1
	uncompiled_quads.append(Quad(op, term0, term1, term2, str(latest_quad_label)))

def newtemp():
	global temp_count
	temp_count += 1
	temp_name = "T_" + str(temp_count)
	insert_entity(Variable(temp_name, "Temponary", symbol_table[nesting_level].framelength))
	return (temp_name) 

def emptylist():
	return []

def makelist(label):
	return [label]

def merge(list0,list1):
	mergedlist = list0 + list1
	del list0[:], list1[:]
	return mergedlist

def backpatch(list0,label):
	for quad in list0:
		uncompiled_quads[quad - compiled_quads].term2 = str(label)
	del list0[:]

def is_sign_quad(quad):
	return (quad.op in ['+','-'] and quad.term1 == '_')

'''
	====================================================================================================
										Symbol Table's Functions											
	====================================================================================================
'''

def insert_scope(scope):
	global nesting_level, symbol_table
	nesting_level += 1
	symbol_table.append(scope)
	if (debug_mode):
		print("-------------------- Insertion of %s Scope. --------------------" %(scope.to_string())) #Debugging

def delete_scope():
	global nesting_level, compiled_quads
	if (debug_mode):
		for entity in symbol_table[nesting_level].entities: print(entity.to_string()) #Debugging
		print("Framelength: %d" %(symbol_table[nesting_level].framelength)) #Debugging
		print("-------------------- Deletion of %s Scope. -------------------------\n" %(symbol_table[nesting_level].to_string())) #Debugging
	compiled_quads += len(uncompiled_quads)
	compile_quads()
	move_quads()
	del symbol_table[nesting_level]
	nesting_level -= 1

def insert_entity(entity):
	entity.nesting_level = nesting_level
	symbol_table[nesting_level].entities.append(entity)
	if(is_var_par(entity)):
		symbol_table[nesting_level].framelength += STD_INT_SIZE
		if(nesting_level == 0):
			main_vars.append(entity.name) # For C code

def insert_argument(function, argument):
	function.arguments.append(argument)

def lookup_current_scope(name):
	for entity in symbol_table[nesting_level].entities:
		if (entity.name == name):
			return entity
	return None

def lookup_enclosing_scopes(name):
	for scope in reversed(symbol_table):
		for entity in scope.entities:
			if (entity.name == name):
				return entity
	return None

def entity_exists(entity):
	return (entity != None)

def is_variable(entity):
	return (entity.type == "Variable")

def is_parameter(entity):
	return (entity.type == "Parameter")

def is_var_par(entity):
	return (is_variable(entity) or is_parameter(entity))

def is_function(entity):
	return (entity.type == "Function")

def is_def_compl(entity):
	return (entity.framelength != 0)

def is_recursive_func(entity):
	return (entity.name == symbol_table[nesting_level].name)

def have_equal_len(list0, list1):
	return (len(list0) == len(list1))

def get_scope_type():
	return ("function" if (nesting_level) else "program")

def is_program_scope():
	return (nesting_level == 0)

def equal_to_scope_name(name):
	return (name == symbol_table[nesting_level].name)

'''
	====================================================================================================
										Code Generator's Functions											
	====================================================================================================
'''

def gnvlcode(variable):

	'''
		$t0 = &(variable)
	'''

	entity = variable
	asm_instructions.append(gen_mips_instr('lw',['$t0', '-4', "$sp"]))
	current_func = lookup_enclosing_scopes(symbol_table[nesting_level].name)
	father_nesting_level = current_func.nesting_level
	for i in range(father_nesting_level, entity.nesting_level, -1):
		asm_instructions.append(gen_mips_instr('lw',['$t0', '-4', "$t0"]))
	asm_instructions.append(gen_mips_instr('addi',['$t0', '$t0', str(-entity.offset)]))

def loadvr(variable, register):

	'''
		register = variable
		Reading from MEM
	'''

	if (isinstance(variable, str) and variable.isdigit()):
		asm_instructions.append(gen_mips_instr('li', [register, variable]))
	else:
		entity = variable
		if (is_global_var(entity)):
			asm_instructions.append(gen_mips_instr('lw', [register, str(-entity.offset), '$s0']))
		elif (is_local(entity)):
			if (is_variable(entity) or (is_parameter(entity) and (is_cv_par(entity) or is_cp_par(entity)))):
				asm_instructions.append(gen_mips_instr('lw', [register, str(-entity.offset), '$sp']))
			elif (is_parameter(entity) and is_ref_par(entity)):
				asm_instructions.append(gen_mips_instr('lw', ['$t0', str(-entity.offset), '$sp']))
				asm_instructions.append(gen_mips_instr('lw', [register, '0', '$t0']))
		else:
			if (is_variable(entity) or (is_parameter(entity) and (is_cv_par(entity) or is_cp_par(entity)))):
				gnvlcode(entity)
				asm_instructions.append(gen_mips_instr('lw', [register, '0', '$t0']))
			elif (is_parameter(entity) and is_ref_par(entity)):
				gnvlcode(entity)
				asm_instructions.append(gen_mips_instr('lw', ['$t0', '0', '$t0']))
				asm_instructions.append(gen_mips_instr('lw', [register, '0', '$t0']))

def storerv(register, variable):
	
	'''
		variable = register
		Writing to MEM
	'''

	entity = variable
	if (is_global_var(entity)):
		asm_instructions.append(gen_mips_instr('sw', [register, str(-entity.offset), '$s0']))
	elif (is_local(entity)):
		if (is_variable(entity) or (is_parameter(entity) and (is_cv_par(entity) or is_cp_par(entity)))):
			asm_instructions.append(gen_mips_instr('sw', [register, str(-entity.offset), '$sp']))
		elif (is_parameter(entity) and is_ref_par(entity)):
			asm_instructions.append(gen_mips_instr('lw', ['$t0', str(-entity.offset), '$sp']))
			asm_instructions.append(gen_mips_instr('sw', [register, '0', '$t0']))
	else:
		if (is_variable(entity) or (is_parameter(entity) and (is_cv_par(entity) or is_cp_par(entity)))):
			gnvlcode(entity)
			asm_instructions.append(gen_mips_instr('sw', [register, '0', '$t0']))
		elif (is_parameter(entity) and is_ref_par(entity)):
			gnvlcode(entity)
			asm_instructions.append(gen_mips_instr('lw', ['$t0', '0', '$t0']))
			asm_instructions.append(gen_mips_instr('sw', [register, '0', '$t0']))

def load_term(name):

	if (isinstance(name, str) and name.isdigit()):
		return name
	else:
		return lookup_enclosing_scopes(name)

def compile_quads():
	par_quads = []
	par_cp_quads = []
	for quad in uncompiled_quads:
		quad_tokens = quad.to_string().split(", ")
		if(quad_tokens[0] == 'par'): # par gather
			par_quads.append(quad)
		else:
			if(quad_tokens[0] == 'call'): # call write
				for par_quad in par_quads:
					insert_quad_label(par_quad)
					if(par_quad.term1 == 'CP'):
						par_cp_quads.append([par_quad, par_quads.index(par_quad)])
					if(par_quads.index(par_quad) == 0):
						entity_callee = load_term(quad_tokens[1])
						asm_instructions.append(gen_mips_instr('addi', ['$fp', '$sp', str(entity_callee.framelength)]))
					compile_quad(par_quad, [par_quads.index(par_quad)])
			if((quad_tokens[0] == 'begin_block') and (is_program_scope())): #program's begin_block
				insert_main_label()
			if( not((quad_tokens[0] == 'end_block') and (is_program_scope())) ): #not program's end_block
				insert_quad_label(quad)
				if(quad_tokens[0] == 'call'):
					compile_quad(quad, [par_quads, par_cp_quads])
					par_quads = []
					par_cp_quads = []
				else:
					compile_quad(quad, None)

def compile_quad(quad, args):
	quad_tokens = quad.to_string().split(", ")
	if(quad_tokens[0] == ':='):
		entity_source = load_term(quad_tokens[1])
		entity_target = load_term(quad_tokens[3])
		loadvr(entity_source, '$t1')
		storerv('$t1', entity_target)
	elif(quad_tokens[0] in ['+', '-', '/', '*']):
		if(is_sign_quad(quad)):
			entity_source = load_term(quad_tokens[1])
			entity_target = load_term(quad_tokens[3])
			loadvr(entity_source, '$t1')
			if(quad_tokens[0] == '-'):
				asm_instructions.append(gen_mips_instr('subu', ['$t1', '$zero', '$t1']))
			else:
				asm_instructions.append(gen_mips_instr('add', ['$t1', '$zero', '$t1']))
			storerv('$t1', entity_target)
		else:
			entity_target = load_term(quad_tokens[3])
			entity_first_operand = load_term(quad_tokens[1])
			entity_second_operand = load_term(quad_tokens[2])
			loadvr(entity_first_operand, '$t1')
			loadvr(entity_second_operand, '$t2')
			asm_instructions.append(gen_mips_instr(mips_instr_map[quad_tokens[0]], ['$t1', '$t1', '$t2']))
			storerv('$t1', entity_target)
	elif(quad_tokens[0] in ['=', '>', '<', '>=', '<=', '<>']):
		target_label = quad_tokens[3]
		entity_first_operand = load_term(quad_tokens[1])
		entity_second_operand = load_term(quad_tokens[2])
		loadvr(entity_first_operand, '$t1')
		loadvr(entity_second_operand, '$t2')
		asm_instructions.append(gen_mips_instr(mips_instr_map[quad_tokens[0]], ['$t1', '$t2', 'L{}'.format(target_label)]))
	elif(quad_tokens[0] == 'inp'):
		entity_target = load_term(quad_tokens[1])
		asm_instructions.append(gen_mips_instr('li', ['$v0', '5']))
		asm_instructions.append(gen_mips_instr('syscall', None))
		storerv('$v0', entity_target)
	elif(quad_tokens[0] == 'out'):
		entity_target = load_term(quad_tokens[1])
		asm_instructions.append(gen_mips_instr('li', ['$v0', '1']))
		loadvr(entity_target, '$t1')
		asm_instructions.append(gen_mips_instr('move', ['$a0', '$t1']))
		asm_instructions.append(gen_mips_instr('syscall', None))
		# Print new line
		asm_instructions.append(gen_mips_instr('li', ['$v0', '4']))
		asm_instructions.append(gen_mips_instr('la', ['$a0', 'newline']))
		asm_instructions.append(gen_mips_instr('syscall', None))
	elif(quad_tokens[0] == 'jump'):
		target_label = quad_tokens[3]
		asm_instructions.append(gen_mips_instr('j', ['L{}'.format(target_label)]))
	elif(quad_tokens[0] == 'par'):
		entity_par = load_term(quad_tokens[1])
		par_mode = quad_tokens[2];
		if(par_mode in ['CV', 'CP']):
			loadvr(entity_par, '$t0')
			asm_instructions.append(gen_mips_instr('sw', ['$t0', str(-(STD_FRAMELENGTH + STD_INT_SIZE*args[0])), '$fp']))
		elif(par_mode == 'REF'):
			if(is_global_var(entity_par)):
				asm_instructions.append(gen_mips_instr('addi',['$t0', '$s0', str(-entity_par.offset)]))
				asm_instructions.append(gen_mips_instr('sw',['$t0', str(-(STD_FRAMELENGTH + STD_INT_SIZE*args[0])), '$fp']))
			elif(is_local(entity_par)):
				if (is_variable(entity_par) or (is_parameter(entity_par) and (is_cv_par(entity_par) or is_cp_par(entity_par)))):
					asm_instructions.append(gen_mips_instr('addi',['$t0', '$sp', str(-entity_par.offset)]))
					asm_instructions.append(gen_mips_instr('sw', ['$t0', str(-(STD_FRAMELENGTH + STD_INT_SIZE*args[0])), '$fp']))
				elif (is_parameter(entity_par) and is_ref_par(entity_par)):
					asm_instructions.append(gen_mips_instr('lw', ['$t0', str(-entity_par.offset), '$sp']))
					asm_instructions.append(gen_mips_instr('sw', ['$t0', str(-(STD_FRAMELENGTH + STD_INT_SIZE*args[0])), '$fp']))
			else:
				if (is_variable(entity_par) or (is_parameter(entity_par) and (is_cv_par(entity_par) or is_cp_par(entity_par)))):
					gnvlcode(entity_par)
					asm_instructions.append(gen_mips_instr('sw', ['$t0', str(-(STD_FRAMELENGTH + STD_INT_SIZE*args[0])), '$fp']))
				elif (is_parameter(entity_par) and is_ref_par(entity_par)):
					gnvlcode(entity_par)
					asm_instructions.append(gen_mips_instr('lw', ['$t0', '0', '$t0']))
					asm_instructions.append(gen_mips_instr('sw', ['$t0', str(-(STD_FRAMELENGTH + STD_INT_SIZE*args[0])), '$fp']))
		elif(par_mode == 'RET'):
			asm_instructions.append(gen_mips_instr('addi', ['$t0', '$sp', str(-entity_par.offset)]))
			asm_instructions.append(gen_mips_instr('sw', ['$t0', '-8', '$fp']))
	elif(quad_tokens[0] == 'retv'):
		entity_target = load_term(quad_tokens[1])
		loadvr(entity_target, '$t1')
		asm_instructions.append(gen_mips_instr('lw', ['$t0', '-8', '$sp']))
		asm_instructions.append(gen_mips_instr('sw', ['$t1', '0', '$t0']))
	elif(quad_tokens[0] == 'call'):
		entity_callee = load_term(quad_tokens[1])
		# Brother or Recursive
		if(entity_callee.nesting_level == (nesting_level - 1)):
			asm_instructions.append(gen_mips_instr('lw', ['$t0', '-4', '$sp']))
			asm_instructions.append(gen_mips_instr('sw', ['$t0', '-4', '$fp']))
		# Father
		else:
			asm_instructions.append(gen_mips_instr('sw', ['$sp', '-4', '$fp']))
		asm_instructions.append(gen_mips_instr('addi', ['$sp', '$sp', str(entity_callee.framelength)]))
		asm_instructions.append(gen_mips_instr('jal', ['L{}'.format(str(entity_callee.start_quad))]))
		if(len(args[1]) != 0):
			asm_instructions.append(gen_mips_instr('move', ['$s1', '$sp']))
		asm_instructions.append(gen_mips_instr('addi', ['$sp', '$sp', str(-entity_callee.framelength)]))
		for par_cp_quad, par_cp_index in args[1]:
			entity_par = load_term(par_cp_quad.term0)
			asm_instructions.append(gen_mips_instr('lw', ['$t1', str(-(STD_FRAMELENGTH + STD_INT_SIZE*par_cp_index)), '$s1']))
			storerv('$t1', entity_par)
	elif(quad_tokens[0] == 'begin_block' and (not is_program_scope())):
		asm_instructions.append(gen_mips_instr('sw', ['$ra', '0', '$sp']))
	elif(quad_tokens[0] == 'end_block' and (not is_program_scope())):
		asm_instructions.append(gen_mips_instr('lw', ['$ra', '0', '$sp']))
		asm_instructions.append(gen_mips_instr('jr', ['$ra']))
	elif(quad_tokens[0] == 'halt'):
		asm_instructions.append(gen_mips_instr('li', ['$v0', '10']))
		asm_instructions.append(gen_mips_instr('syscall', None))

def gen_mips_instr(op, terms):

	if (op in ['li', 'la', 'move', ]):
		return "{} {}, {}".format(op, terms[0], terms[1])
	elif (op in ['lw', 'sw']):
		return "{} {}, {}({})".format(op, terms[0], terms[1], terms[2])
	elif (op in ['add', 'addi', 'sub', 'subu', 'mul', 'div', 'beq', 'blt', 'bgt', 'ble', 'bge', 'bne']):
		return "{} {}, {}, {}".format(op, terms[0], terms[1], terms[2])
	elif (op in ['j', 'jal', 'jr']):
		return "{} {}".format(op, terms[0])
	elif (op in ['syscall']):
		return "{}".format(op)

def insert_main_label():
	asm_instructions.append("Lmain:")
	asm_instructions.append(gen_mips_instr('addi', ['$sp', '$sp', str(main_framelength)]))
	asm_instructions.append(gen_mips_instr('move', ['$s0', '$sp']))

def insert_quad_label(quad):
	asm_instructions.append("L{}:".format(quad.label))

def move_quads():
	global quads, uncompiled_quads
	quads = quads + uncompiled_quads
	uncompiled_quads.clear()

def is_global_var(entity):
	return (entity.nesting_level == 0)

def is_local(entity):
	return (entity.nesting_level == nesting_level)

def is_temponary_var(variable):
	return (variable.var_type == "Temponary")

def is_regular_var(variable):
	return (variable.var_type == "Regular")

def is_cv_par(parameter):
	return (parameter.par_mode == "in")

def is_cp_par(parameter):
	return (parameter.par_mode == "inandout")

def is_ref_par(parameter):
	return (parameter.par_mode == "inout")

'''
	====================================================================================================
										Output Functions													
	====================================================================================================
'''

def make_int_file():
	int_file = open(sys.argv[1][:-4]+".int", "w")
	i = 0
	for quad in quads:
		int_file.write(str(i) + ":  " + quad.to_string() + '\n')
		i += 1
	int_file.close()

def make_C_like_file():
	C_file = open(sys.argv[1][:-4]+".c", "w")
	C_file.write("#include <stdio.h>\n\n")
	C_file.write("int main()\n{\n")
	if(len(main_vars)):
		C_file.write("\tint ")
		for i in range(len(main_vars)):
			if(i == len(main_vars)-1):
				C_file.write(main_vars[i] + ";\n")
			else:
				C_file.write(main_vars[i] + ", ")
	for quad in quads:
		quad_tokens = quad.to_string().split(", ")
		out_str = ""
		if(quad_tokens[0] == ':='):
			out_str = ("{} {} {};".format(quad_tokens[3], C_oper_map[quad_tokens[0]], quad_tokens[1]))
		elif(quad_tokens[0] in ['+', '-', '/', '*']):
			if(is_sign_quad(quad)):
				out_str = ("{} = {}{};".format(quad_tokens[3], quad_tokens[0], quad_tokens[1]))
			else:
				out_str = ("{} = {} {} {};".format(quad_tokens[3], quad_tokens[1], quad_tokens[0], quad_tokens[2]))
		elif(quad_tokens[0] in ['=', '>', '<', '>=', '<=', '<>']):
			out_str = ("if ({} {} {}) goto L_{};".format(quad_tokens[1], C_oper_map[quad_tokens[0]], quad_tokens[2], quad_tokens[3]))
		elif(quad_tokens[0] in ['inp', 'out']):
			out_str = ("{}{});".format(C_oper_map[quad_tokens[0]], quad_tokens[1]))			
		elif(quad_tokens[0] == 'jump'):
			out_str = ("goto L_{};").format(quad_tokens[3])
		elif(quad_tokens[0] == 'begin_block'):
			out_str = " "
		elif(quad_tokens[0] == 'halt'):
			out_str = "{}"
		if(out_str):
			C_file.write("\tL_" + quad.label + ": " + str(out_str) + " //" + quad.to_string() + "\n")
	C_file.write("}\n")
	C_file.close()

def make_asm_file():
	asm_file = open(sys.argv[1][:-4]+".asm", "w")
	asm_file.write(STD_ASM_HEADER)
	for instruction in asm_instructions:
		if(not instruction[len(instruction)-1] == ':'):
			asm_file.write('\t')
		asm_file.write('{}\n'.format(instruction))
	asm_file.write(STD_ASM_COPYRIGHT)
	asm_file.close()

'''
	====================================================================================================
										Main Function													
	====================================================================================================
'''

tokentk = idtk = ""
debug_mode = False
line_count = char_count = main_framelength = compiled_quads = 0
latest_quad_label = temp_count = nesting_level = -1
uncompiled_quads = []
quads = []
symbol_table = []
asm_instructions = ['L:','j Lmain']
main_vars = []

if (len(sys.argv) == 3):
	if (sys.argv[2] != '-d'):
		print('Invalid Input!')
		exit()
	debug_mode = True
elif (len(sys.argv) != 2):
	print('Invalid Input!')
	exit()

if (sys.argv[1][-4:] != '.stl'):
	print('Invalid File Type!')
	exit()

try:
	stl_file = open(sys.argv[1])
	program()
	stl_file.close()
	make_int_file()
	make_C_like_file()
	make_asm_file()
except FileNotFoundError:
	print('File Not Found!')
	exit()

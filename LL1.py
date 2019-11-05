from definitions import lexemes, key_words, nonterminal_symbols
from tree import Tree, Node

class Analyser(object):
    """LL1 syntax analyser"""
    def __init__(self, scanner):
        self.scanner = scanner
        self.table = Tree() # Compiler's table
        self.table.set_current(self.table)
        self.scopes = list()
        self.type = None # type of a varibale or an argument that's being inserted
        self.variables = list() # list of variables after 'int', 'boolean', or 'identifier' keywords
        self.number_of_arguments = None # num of args of a function that's being inserted
        self.address = None # field's or variable's address for . operators, as in 'class.subclass.field = 5;'
        self.triads = list() # list of triads
        self.r = list() # stack 'r'
        self.rememembering = True # flag that signals whether the variables that are being read should be stored for
        # insertion into the tree
        self.last_var = None
        self.is_left_part_of_assignment = True
        self.is_a_call = False # indicates wheter args should be pushed into stack
        self.to_call = [] # list of functions to call
        self.is_expression = False # workaround
        self.args = [] # a list of args to pass to a function
        self.is_true = [] # results of if expressions
        self.incomplete_ifs = [] # a stack of incomplete if triads
        self.incomplete_thens = []

    
    def epsilon(self):
        """Handle rules with an empty right part"""
        self.stack_pointer -= 1

    def next_lexeme(self):
        """Get the next lexeme from input"""
        lexeme = self.scanner.next_lexeme()
        value_of_lexeme = lexeme[0]
        type_of_lexeme = lexeme[1]
        return value_of_lexeme, type_of_lexeme

    def check_next_lexeme(self):
        """Get the next lexeme and restore scanner's pointer"""
        saved_position = self.scanner.get_pointer()
        lexeme = self.scanner.next_lexeme()
        value_of_lexeme = lexeme[0]
        type_of_lexeme = lexeme[1]
        self.scanner.set_pointer(saved_position)
        return value_of_lexeme, type_of_lexeme

    def check_next_next_lexeme(self):
        """Get the next lexeme after the next lexeme and restore scanner's pointer"""
        saved_position = self.scanner.get_pointer()
        lexeme = self.scanner.next_lexeme()
        lexeme = self.scanner.next_lexeme()
        value_of_lexeme = lexeme[0]
        type_of_lexeme = lexeme[1]
        self.scanner.set_pointer(saved_position)
        return value_of_lexeme, type_of_lexeme

    def scan_past_variable(self):
        """Keep scanning until = or ; is found

        Return: "H" - if '=' was found
                "B" - if ';' was found
        """
        saved_position = self.scanner.get_pointer()
        lexeme = self.scanner.next_lexeme()
        type_of_lexeme = lexeme[1]
        while type_of_lexeme not in ["TAssign", "TSemicolon"]:
            lexeme = self.scanner.next_lexeme()
            type_of_lexeme = lexeme[1]
        self.scanner.set_pointer(saved_position)
        if type_of_lexeme == "TAssign":
            return "H"
        else:
            return "B"

    def print_error(self, msg):
        """Print an error and terminate execution"""
        self.scanner.print_error(msg)

    def ins_table(self, value, obj_type):
        print("Inserting \'%s\' of type \'%s\' into the tree" % (value, obj_type))
        pointer = self.table.include(value, obj_type)
        return pointer

    def ret_ptr(self, pointer):
        self.table.set_current(pointer)

    def gen_fun(self, name):
        triad = ("proc", name, "")
        self.triads.append(triad)

    def gen_prolog(self):
        triad = ("prolog", "?", "")
        self.triads.append(triad)

    def gen_epilog(self):
        triad = ("epilog", "?", "")
        self.triads.append(triad)

    def remember_variable(self, var):
        print("Remembered variable \'%s\'" % var)
        if self.rememembering:
            self.variables.append(var)
        if self.last_var is None:
            self.last_var = self.table.find_up(var, self.table.current)
        else:
            self.last_var = self.table.contains(identifier=var, node=self.last_var)
        print("variables = %s" % str(self.variables))


    def ins_vars(self):
        for variable in self.variables:
            #print("Inserting variable \'%s\' of type \'%s\'" % (variable, self.type))
            var = self.ins_table(variable, self.type)
            parents = self.table.find_parents(var)
            var = ".".join([parent for parent in parents])
            self.gen_alloc(var)
        self.variables = []
        self.rememembering = False


    def gen_alloc(self, var):
        triad = ('alloc', var, self.type)
        self.triads.append(triad)

    def ins_argument(self, arg):
        if not self.is_a_call:
            print("Inserting argument \'%s\' of type \'%s\'" % (arg, self.type))
            self.ins_table(arg, self.type)

    def add_parameter(self):
        if self.number_of_arguments is not None:
            self.number_of_arguments += 1
        else:
            self.number_of_arguments = 1
    
    def set_num_of_args(self):
        print("Setting number of args = %d" % self.number_of_arguments)
        self.table.set_parameters(self.scopes[-1], self.number_of_arguments)
        self.number_of_arguments = None


    def find_class(self, name):
        # Crutch
        if self.is_a_call:
            result = self.table.find_up(name, self.table.current)
            print("find %s" % name)
            print(result)
            if result is not None:
                if result.root.type == "ObjClass":
                    self.print_error("Class's fields and methods are not static")
            else:
                self.print_error("Object not found")
        if self.is_left_part_of_assignment:
            self.address = self.table.find_up(name, self.table.current)
            if self.address is not None:
                print("find_class %s - found %s" % (name, self.address.root))
            else:
                print("find_class %s - not found" % name)

    def find_class_or_field(self, name):
        if self.is_left_part_of_assignment:
            self.address = self.table.contains(identifier=name, node=self.address)
            if self.address is not None:
                print("find_class_or_field %s - found %s" % (name, self.address.root))
            else:
                print("find_class_or_field %s - not found" % name)

    def ins_assignment(self):
        value = self.r.pop()
        if self.address is None:
            self.print_error("Variable or field has not been declared!")
        else:
            print("Assignment: %s = %s" % (self.address.root, value))
            self.address.root.value = value
        self.gen_assignment(self.address, value)

    def gen_not(self):
        value = self.r.pop()
        if self.get_type(value) == "ObjBoolean":
            self.triads.append(('!', value, ""))
            self.r.append(["<%d>" % len(self.triads), "ObjBoolean"])
        else:
            self.print_error("Type error, only type 'boolean' is allowed for ! operator")

    def const_to_r(self, const):
        print("Const %s appended to r" % const)
        self.r.append(const)

    def var_to_r(self):
        if self.last_var is None:
            self.print_error("Variable or field has not been declared")
        else:
            print("Variable %s appended to r" % self.last_var.root)
            self.r.append(self.last_var)
            self.last_var = None

    def erase_last_var(self):
        self.last_var = None

    def change_side_of_assignment(self):
        self.is_left_part_of_assignment = not self.is_left_part_of_assignment
        if self.is_left_part_of_assignment:
            print("Changed side of assignment to LEFT")
        else:
            print("Changed side of assignment to RIGHT")

    def gen_assignment(self, var, new_value):
        if var.root.type == self.get_type(new_value):
            parents = self.table.find_parents(var)
            var = ".".join([parent for parent in parents])
            if isinstance(new_value, Tree):
                parents = self.table.find_parents(new_value)
                new_value = ".".join([parent for parent in parents])
            triad = ('=', var, new_value)
            self.triads.append(triad)
        else:
            self.print_error("Type mismatch in expression '%s' = '%s'" % (var.root.type, self.get_type(new_value)))

    def is_int(self, string):
        try: 
            int(string)
            return True
        except ValueError:
            return False
        except TypeError:
            return False

    def get_type(self, obj):
        #print("get_type", obj)
        if isinstance(obj, Tree):
            return obj.root.type
        elif isinstance(obj, list):
            return obj[1]
        elif obj in ["true", "false"]:
            return "ObjBoolean"
        elif self.is_int(obj):
            return "ObjInt"
        else:
            return "TYPE_UNKNOWN"


    def gen_binary(self, operation):
        print("gen_binary: %s" % str(self.r))
        fisrt_operand = self.r.pop()
        triad_type = None

        if isinstance(fisrt_operand, list):
            triad_type = fisrt_operand[1]
            fisrt_operand = fisrt_operand[0]
        second_operand = self.r.pop()

        if isinstance(second_operand, list):
            second_operand = second_operand[0]
        if triad_type is None:
            if self.get_type(fisrt_operand) == "ObjInt" or self.is_int(fisrt_operand):
                triad_type = "ObjInt"
            else:
                triad_type = "ObjBoolean"
        if isinstance(fisrt_operand, Tree):
            parents = self.table.find_parents(fisrt_operand)
            fisrt_operand = ".".join([parent for parent in parents])
        if isinstance(second_operand, Tree):
            parents = self.table.find_parents(second_operand)
            second_operand = ".".join([parent for parent in parents])
        if operation == "==" or operation == "!=":
            triad_type = "ObjBoolean"
            # operation = "cmp"
        triad = (operation, fisrt_operand, second_operand)
        self.triads.append(triad)
        self.r.append(["<%d>" % len(self.triads), triad_type])
        print(self.r)

    def gen_logical_or(self):
        if self.get_type(self.r[-1]) == "ObjBoolean" and self.get_type(self.r[-2]) == "ObjBoolean":
            self.gen_binary('||')
        else:
            self.print_error("Type error, only type 'boolean' is allowed for || operator")

    def gen_logical_and(self):
        if self.get_type(self.r[-1]) == "ObjBoolean" and self.get_type(self.r[-2]) == "ObjBoolean":
            self.gen_binary('&&')
        else:
            self.print_error("Type error, only type 'boolean' is allowed for && operator")

    def gen_xor(self):
        if self.get_type(self.r[-1]) == "ObjInt" and self.get_type(self.r[-2]) == "ObjInt":
            self.gen_binary('^')
        else:
            self.print_error("Type error, only type 'int' is allowed for ^ operator")

    def gen_equal_to(self):
        fisrt_operand = self.get_type(self.r[-1])
        second_operand = self.get_type(self.r[-2])
        if (fisrt_operand == "ObjBoolean" and second_operand == "ObjBoolean") or \
            (fisrt_operand == "ObjInt" and second_operand == "ObjInt"):
            self.gen_binary('==')
        else:
            self.print_error("Type error, both operands must be the same type for == operator")

    def gen_not_equal_to(self):
        fisrt_operand = self.get_type(self.r[-1])
        second_operand = self.get_type(self.r[-2])
        if (fisrt_operand == "ObjBoolean" and second_operand == "ObjBoolean") or \
            (fisrt_operand == "ObjInt" and second_operand == "ObjInt"):
            self.gen_binary('!=')
        else:
            self.print_error("Type error, both operands must be the same type for != operator")

    def gen_multiplication(self):
        if self.get_type(self.r[-1]) == "ObjInt" and self.get_type(self.r[-2]) == "ObjInt":
            self.gen_binary('*')
        else:
            self.print_error("Type error, only type 'int' is allowed for * operator")

    def gen_division(self):
        print(self.r)
        self.print_triads()
        if self.get_type(self.r[-1]) == "ObjInt" and self.get_type(self.r[-2]) == "ObjInt":
            self.gen_binary('/')
        else:
            self.print_error("Type error, only type 'int' is allowed for / operator")

    def gen_modulus(self):
        if self.get_type(self.r[-1]) == "ObjInt" and self.get_type(self.r[-2]) == "ObjInt":
            self.gen_binary('%')
        else:
            self.print_error("Type error, only type 'int' is allowed for %% operator")

    def gen_addition(self):
        if self.get_type(self.r[-1]) == "ObjInt" and self.get_type(self.r[-2]) == "ObjInt":
            self.gen_binary('+')
        else:
            self.print_error("Type error, only type 'int' is allowed for + operator")

    def gen_substraction(self):
        if self.get_type(self.r[-1]) == "ObjInt" and self.get_type(self.r[-2]) == "ObjInt":
            self.gen_binary('-')
        else:
            self.print_error("Type error, only type 'int' is allowed for - operator")

    def gen_call(self):
        function = self.to_call.pop()
        address = self.table.find_function(function)
        print("calling %s" % function)
        print(self.variables)
        if self.table.compare_parameters(address, self.args, self.scanner) == False:
            self.print_error("Wrong number of arguments for a function '%s': %d given, while %d expected" %\
                                                        (function, len(self.args), address.root.parameters))
        self.args = []
        triad = ("call", function, "")
        self.triads.append(triad)
        self.is_a_call = False

    def gen_push(self):
        arg = self.r.pop()
        self.args.append([self.get_type(arg)])
        if isinstance(arg, str):
            triad = ("push", arg, "")
        else:
            parents = self.table.find_parents(arg)
            arg = ".".join([parent for parent in parents])
            triad = ("push", arg, "")
        self.triads.append(triad)

    def add_to_queue(self, function):
        self.to_call.append(function)

    def check_if(self):
        arg = self.r.pop()
        arg_type = self.get_type(arg)
        if arg_type != "ObjBoolean":
            self.print_error("Expression must be of type 'boolean'")
        if isinstance(arg, list):
            arg = arg[0]
        else:
            if arg not in ["true", "false"]:
                parents = self.table.find_parents(arg)
                arg = ".".join([parent for parent in parents])
        triad = ("cmp", arg, "true")
        self.triads.append(triad)
        triad = ("if", "<" + str(len(self.triads)+2) + ">", "?")
        self.triads.append(triad)
        self.incomplete_ifs.append(len(self.triads)-1)

    def continue_else(self):
        triad = self.triads[self.incomplete_ifs[-1]]
        self.triads[self.incomplete_ifs[-1]] = (triad[0], triad[1], "<" + str(len(self.triads)+1) + ">")

    def finish_else(self):
        print(self.incomplete_thens)
        triad = ("nop", "", "")
        self.triads.append(triad)
        self.incomplete_ifs.pop(-1)
        triad = self.triads[self.incomplete_thens[-1]]
        self.triads[self.incomplete_thens.pop(-1)] = (triad[0], "<" + str(len(self.triads)) + ">", "")
        # triad = ("nop", "", "")
        # self.triads.append(triad)
        # triad = self.triads[self.incomplete_ifs[-1]]
        # self.triads[self.incomplete_ifs[-1]] = (triad[0], triad[1], "<" + str(len(self.triads)) + ">")

    def finish_without_else(self):
        triad = self.triads[self.incomplete_ifs.pop(-1)]
        self.triads[self.incomplete_ifs[-1]] = (triad[0], triad[1], "<" + str(len(self.triads)) + ">")
        triad = self.triads[self.incomplete_thens.pop(-1)]
        self.triads[self.incomplete_thens[-1]] = (triad[0], "<" + str(len(self.triads)) + ">", "")

    def finish_then(self):
        triad = ("jmp", "?", "")
        self.triads.append(triad)
        self.incomplete_thens.append(len(self.triads)-1)

    def print_triads(self):
        for i in range(len(self.triads)):
            triad = self.triads[i]
            operation = triad[0]
            fisrt_operand = triad[1]
            if isinstance(fisrt_operand, Tree):
                fisrt_operand = fisrt_operand.root.id
            elif isinstance(fisrt_operand, list):
                fisrt_operand = fisrt_operand[0]
            second_operand = triad[2]
            if isinstance(second_operand, Tree):
                second_operand = second_operand.root.id
            elif isinstance(second_operand, list):
                second_operand = second_operand[0]
            print(('%3d) %10s | %50s | %50s |' % (i + 1, operation, fisrt_operand, second_operand)).replace('\'',''))

    def analyse(self):
        """Analyse syntax. Raise an error if one of the rules is violated"""
        stack = []
        terminate = False
        stack.append(nonterminal_symbols["S"])

        value_of_lexeme, type_of_lexeme = self.next_lexeme()
        while terminate is not True:
            top = stack[-1]
            # If a function is at the top of the stack, then execute it
            if callable(top):
                if top == self.ins_table:
                    if type_of_lexeme == "TClass":
                        # Insert class into the tree
                        val, _ = self.check_next_lexeme()
                        ptr = self.ins_table(val, "ObjClass")
                        self.scopes.append(ptr)
                    elif type_of_lexeme == "TVoid":
                        # Insert function into the tree
                        val, _ = self.check_next_lexeme()
                        ptr = top(val, "ObjFun")
                        self.gen_fun(val)
                        self.gen_prolog()
                        self.scopes.append(ptr)
                    elif type_of_lexeme == "TLeftBrace":
                        # Insert block into the tree
                        self.table.current.set_left(Node())
                        self.table.set_current(self.table.current.left)
                        return_point = self.table.get_current()
                        self.scopes.append(return_point)
                        self.table.current.set_right(Node())
                        self.table.set_current(self.table.current.right)
                elif top == self.ret_ptr:
                    ptr = self.scopes.pop()
                    top(ptr)
                elif top == self.remember_variable:
                    self.remember_variable(value_of_lexeme)
                elif top == self.ins_vars:
                    self.ins_vars()
                elif top == self.ins_argument:
                    self.ins_argument(value_of_lexeme)
                elif top == self.add_parameter:
                    self.add_parameter()
                elif top == self.set_num_of_args:
                    self.set_num_of_args()
                elif top == self.find_class:
                    self.find_class(value_of_lexeme)
                elif top == self.find_class_or_field:
                    self.find_class_or_field(value_of_lexeme)
                elif top == self.const_to_r:
                    self.const_to_r(value_of_lexeme)
                elif top == self.var_to_r:
                    self.var_to_r()
                elif top == self.ins_assignment:
                    self.ins_assignment()
                elif top == self.erase_last_var:
                    self.erase_last_var()
                elif top == self.change_side_of_assignment:
                    self.change_side_of_assignment()
                elif top == self.gen_logical_or:
                    self.gen_logical_or()
                elif top == self.gen_logical_and:
                    self.gen_logical_and()
                elif top == self.gen_xor:
                    self.gen_xor()
                elif top == self.gen_equal_to:
                    self.gen_equal_to()
                elif top == self.gen_not_equal_to:
                    self.gen_not_equal_to()
                elif top == self.gen_multiplication:
                    self.gen_multiplication()
                elif top == self.gen_division:
                    self.gen_division()
                elif top == self.gen_modulus:
                    self.gen_modulus()
                elif top == self.gen_addition:
                    self.gen_addition()
                elif top == self.gen_substraction:
                    self.gen_substraction()
                elif top == self.gen_not:
                    self.gen_not()
                elif top == self.gen_epilog:
                    self.gen_epilog()
                elif top == self.add_to_queue:
                    self.add_to_queue(value_of_lexeme)
                elif top == self.gen_call:
                    self.gen_call()
                elif top == self.gen_push:
                    self.gen_push()
                elif top == self.check_if:
                    self.check_if()
                elif top == self.continue_else:
                    self.continue_else()
                elif top == self.finish_else:
                    self.finish_else()
                elif top == self.finish_then:
                    self.finish_then()
                elif top == self.finish_without_else:
                    self.finish_without_else()
                stack.pop(-1)
            # If a symbol at the top of the stack is a terminal symbol
            elif not top in nonterminal_symbols.values():
                # If scanned terminal symbol equals to what is at the top
                # of the stack
                if top == type_of_lexeme:
                    # If EOF was the symbol then termanite the analysis
                    if type_of_lexeme == "TEnd":
                        terminate = True
                    # Else scan next lexeme and update the stack
                    else:
                        value_of_lexeme, type_of_lexeme = self.next_lexeme()
                        stack.pop(-1)
                else:
                    self.print_error("Unexpected symbol %s found while %s was expected!" % (value_of_lexeme, top))
            # If a symbol at the top of the stack is a nonterminal symbol
            else:
                if top == nonterminal_symbols["S"]:
                    # S -> C
                    print("S")
                    stack.pop(-1)
                    stack.append("TEnd")
                    stack.append(nonterminal_symbols["C"])
                elif top == nonterminal_symbols["C"]:
                    # C -> class Identifier{A}
                    print("C")
                    stack.pop(-1)
                    stack.append(self.ret_ptr)
                    stack.append("TRightBrace")
                    stack.append(nonterminal_symbols["A"])
                    stack.append("TLeftBrace")
                    stack.append("TIdentifier")
                    stack.append("TClass")
                    stack.append(self.ins_table)
                elif top == nonterminal_symbols["A"]:
                    # A -> CA|UA|BA|eps
                    print("A")
                    stack.pop(-1)
                    value_of_next_lexeme, type_of_next_lexeme = self.check_next_next_lexeme()
                    if type_of_lexeme == "TClass":
                        stack.append(nonterminal_symbols["A"])
                        stack.append(nonterminal_symbols["C"])
                    elif type_of_lexeme == "TVoid":
                        stack.append(nonterminal_symbols["A"])
                        stack.append(nonterminal_symbols["U"])
                    elif type_of_lexeme in ["TIdentifier", "TBoolean", "TInt"]:
                        stack.append(nonterminal_symbols["A"])
                        stack.append(nonterminal_symbols["B"])
                    elif type_of_lexeme == "TSemicolon":
                        stack.append(nonterminal_symbols["A"])
                        stack.append("TSemicolon")
                    else:
                        pass
                elif top == nonterminal_symbols["B"]:
                    # B -> RT;
                    print("B")
                    stack.pop(-1)
                    stack.append(self.ins_vars)
                    stack.append("TSemicolon")
                    stack.append(nonterminal_symbols["T"])
                    stack.append(nonterminal_symbols["R"])
                elif top == nonterminal_symbols["D"]:
                    # D -> {E}
                    print("D")
                    stack.pop(-1)
                    stack.append(self.ret_ptr)
                    stack.append("TRightBrace")
                    
                    stack.append(nonterminal_symbols["E"])
                    stack.append("TLeftBrace")
                    stack.append(self.ins_table)
                elif top == nonterminal_symbols["E"]:
                    # E -> FE|BE|CE|eps
                    print("E")
                    stack.pop(-1)
                    value_of_next_lexeme, type_of_next_lexeme = self.check_next_lexeme()
                    if type_of_lexeme == "TIf":
                        stack.append(nonterminal_symbols["E"])
                        stack.append(nonterminal_symbols["F"])
                    elif type_of_lexeme == "TLeftBrace":
                        stack.append(nonterminal_symbols["E"])
                        stack.append(nonterminal_symbols["F"])
                    elif type_of_lexeme == "TRightBrace":
                        pass
                    elif type_of_lexeme == "TSemicolon":
                        stack.append(nonterminal_symbols["E"])
                        stack.append(nonterminal_symbols["F"])
                    elif type_of_lexeme == "TClass":
                        stack.append(nonterminal_symbols["E"])
                        stack.append(nonterminal_symbols["C"])
                    elif type_of_next_lexeme == "TLeftParenthesis":
                        stack.append(nonterminal_symbols["E"])
                        stack.append(nonterminal_symbols["F"])
                    elif self.scan_past_variable() == "H":
                        stack.append(nonterminal_symbols["E"])
                        stack.append(nonterminal_symbols["F"])
                    elif self.scan_past_variable() == "B":
                        stack.append(nonterminal_symbols["E"])
                        stack.append(nonterminal_symbols["B"])
                    else:
                        pass
                elif top == nonterminal_symbols["F"]:
                    # F -> H|G|D|Y|;
                    print("F")
                    stack.pop(-1)
                    if type_of_lexeme == "TSemicolon":
                        stack.append("TSemicolon")
                    elif type_of_lexeme == "TIf":
                        stack.append(nonterminal_symbols["Y"])
                    elif type_of_lexeme == "TLeftBrace":
                        stack.append(nonterminal_symbols["D"])
                    else:
                        value_of_next_lexeme, type_of_next_lexeme = self.check_next_lexeme()
                        if type_of_next_lexeme == "TLeftParenthesis":
                            stack.append(nonterminal_symbols["G"])
                        else:
                            stack.append(nonterminal_symbols["H"])
                elif top == nonterminal_symbols["G"]:
                    # G -> Identifier (G1
                    print("G")
                    self.is_a_call = True
                    stack.pop(-1)
                    stack.append(self.gen_call)
                    stack.append(nonterminal_symbols["G1"])
                    stack.append("TLeftParenthesis")
                    stack.append("TIdentifier")
                    stack.append(self.add_to_queue)
                elif top == nonterminal_symbols["G1"]:
                    # G1 -> Z); | );
                    print("G1")
                    stack.pop(-1)
                    if type_of_lexeme == "TRightParenthesis":
                        stack.append("TSemicolon")
                        stack.append("TRightParenthesis")
                    else:
                        stack.append("TSemicolon")
                        stack.append("TRightParenthesis")
                        stack.append(nonterminal_symbols["Z"])
                elif top == nonterminal_symbols["Z"]:
                    # Z -> W1 Z1
                    print("Z")
                    stack.pop(-1)
                    stack.append(nonterminal_symbols["Z1"])
                    stack.append(self.gen_push)
                    stack.append(nonterminal_symbols["W1"])
                elif top == nonterminal_symbols["Z1"]:
                    # Z1 -> ,W1 Z1 | eps
                    print("Z1")
                    value_of_next_lexeme, type_of_next_lexeme = self.check_next_lexeme()
                    stack.pop(-1)
                    if type_of_lexeme == "TComma":
                        stack.append(nonterminal_symbols["Z1"])
                        stack.append(self.gen_push)
                        stack.append(nonterminal_symbols["W1"])
                        stack.append("TComma")
                    elif type_of_lexeme == "TRightParenthesis":
                        pass
                    else:
                        self.print_error("RULE Z1. ) expected but %s found" % value_of_lexeme)
                elif top == nonterminal_symbols["H"]:
                    # H -> P = W1;
                    print("H")
                    stack.pop(-1)
                    if type_of_lexeme == "TIdentifier":
                        stack.append(self.change_side_of_assignment)
                        stack.append("TSemicolon")
                        stack.append(self.ins_assignment)
                        stack.append(nonterminal_symbols["W1"])
                        stack.append("TAssign")
                        stack.append(self.erase_last_var)
                        stack.append(self.change_side_of_assignment)
                        stack.append(nonterminal_symbols["P"])
                    else:
                        self.print_error("RULE H. Identifier expected but %s found" % type_of_lexeme)
                elif top == nonterminal_symbols["P"]:
                    # P -> Identifier P1
                    print("P")
                    stack.pop(-1)
                    if type_of_lexeme == "TIdentifier":
                        stack.append(nonterminal_symbols["P1"])
                        stack.append("TIdentifier")
                        stack.append(self.remember_variable)
                        stack.append(self.find_class)
                    else:
                        self.print_error("Identifier expected but %s found" % type_of_lexeme)
                elif top == nonterminal_symbols["P1"]:
                    # P1 -> .Identifier P1 | eps
                    print("P1")
                    stack.pop(-1)
                    if type_of_lexeme == "TPeriod":
                        stack.append(nonterminal_symbols["P1"])
                        stack.append("TIdentifier")
                        stack.append(self.remember_variable)
                        stack.append(self.find_class_or_field)
                        stack.append("TPeriod")
                    elif type_of_lexeme == "TRightParenthesis":
                        pass
                    elif type_of_lexeme == "TPeriod":
                        pass
                    elif type_of_lexeme == "TAssign":
                        pass
                    elif type_of_lexeme == "TSemicolon":
                        pass
                elif top == nonterminal_symbols["T"]:
                    # T -> PT1
                    print("T")
                    stack.pop(-1)
                    if type_of_lexeme == "TIdentifier":
                        stack.append(nonterminal_symbols["T1"])
                        stack.append(nonterminal_symbols["P"])
                    """else:
                        self.print_error("RULE T. Identifier expected but %s found" % type_of_lexeme)"""
                elif top == nonterminal_symbols["T1"]:
                    # T1 -> ,PT1 | eps
                    print("T1")
                    stack.pop(-1)
                    if type_of_lexeme == "TComma":
                        stack.append(nonterminal_symbols["T1"])
                        stack.append(nonterminal_symbols["P"])
                        stack.append("TComma")
                    elif type_of_lexeme == "TRightBrace":
                        pass
                    elif type_of_lexeme == "TComma":
                        pass
                    elif type_of_lexeme == "TSemicolon":
                        pass
                    else:
                        self.print_error("RULE T1. Only , } and ; are allowed but %s found" % value_of_lexeme)
                elif top == nonterminal_symbols["U"]:
                    # U -> void Identifier(X) D
                    print("U")
                    stack.pop(-1)
                    self.is_a_call = False
                    value_of_next_lexeme, type_of_next_lexeme = self.check_next_lexeme()
                    if type_of_lexeme == "TVoid":
                        if type_of_next_lexeme == "TIdentifier":
                            stack.append(self.ret_ptr)
                            stack.append(self.gen_epilog)
                            stack.append(nonterminal_symbols["D"])
                            stack.append("TRightParenthesis")
                            stack.append(self.set_num_of_args)
                            stack.append(nonterminal_symbols["X"])
                            stack.append("TLeftParenthesis")
                            stack.append("TIdentifier")
                            stack.append("TVoid")
                            stack.append(self.ins_table)
                        elif type_of_next_lexeme == "TMain":
                            stack.append(self.ret_ptr)
                            stack.append(self.gen_epilog)
                            stack.append(nonterminal_symbols["D"])
                            stack.append(self.set_num_of_args)
                            stack.append("TRightParenthesis")
                            stack.append(nonterminal_symbols["X"])
                            stack.append("TLeftParenthesis")
                            stack.append("TMain")
                            stack.append("TVoid")
                            stack.append(self.ins_table)
                    else:
                        self.print_error("RULE U. 'void' expected but %s found" % value_of_lexeme)
                elif top == nonterminal_symbols["R"]:
                    # R -> Int | Boolean | Identifier
                    print("R")
                    stack.pop(-1)
                    self.rememembering = True
                    if type_of_lexeme == "TInt":
                        self.type = "ObjInt"
                        print("Saved type ObjInt")
                        stack.append("TInt")
                    elif type_of_lexeme == "TBoolean":
                        self.type = "ObjBoolean"
                        print("Saved type ObjBoolean")
                        stack.append("TBoolean")
                    elif type_of_lexeme == "TIdentifier":
                        print("Saved type %s" % value_of_lexeme)
                        self.type = value_of_lexeme
                        stack.append("TIdentifier")
                    else:
                        msg = "RULE R. Only Integers, Booleans and Identifiers are allowed but %s found" % value_of_lexeme
                        self.print_error(msg)
                elif top == nonterminal_symbols["X"]:
                    # X -> R Identifier X1
                    print("X")
                    stack.pop(-1)
                    if type_of_lexeme in ["TInt", "TBoolean", "TIdentifier"]:
                        stack.append(nonterminal_symbols["X1"])
                        stack.append("TIdentifier")
                        stack.append(self.ins_argument)
                        stack.append(self.add_parameter)
                        stack.append(nonterminal_symbols["R"])
                    elif type_of_lexeme == "TIntegerConstant":
                        stack.append(nonterminal_symbols["X1"])
                        stack.append("TIntegerConstant")
                    else:
                        msg = "RULE X. Only Integers, Booleans, Constants and Identifiers are allowed but %s found" % value_of_lexeme
                        self.print_error(msg)
                elif top == nonterminal_symbols["X1"]:
                    # X1 -> ,R Identifier X1 | ,const X1 | eps
                    print("X1")
                    value_of_next_lexeme, type_of_next_lexeme = self.check_next_lexeme()
                    stack.pop(-1)
                    if type_of_lexeme == "TComma":
                        if type_of_next_lexeme == "TIntegerConstant":
                            stack.append(nonterminal_symbols["X1"])
                            stack.append("TIntegerConstant")
                            stack.append("TComma")
                        else:
                            stack.append(nonterminal_symbols["X1"])
                            stack.append("TIdentifier")
                            stack.append(self.ins_argument)
                            stack.append(self.add_parameter)
                            stack.append(nonterminal_symbols["R"])
                            stack.append("TComma")
                    elif type_of_lexeme == "TRightParenthesis":
                        pass
                    else:
                        self.print_error("RULE X1. ) or 'ARGUMENT' expected but %s found" % value_of_lexeme)
                elif top == nonterminal_symbols["Y"]:
                    # Y -> if (W1) F Y1
                    print("Y")
                    stack.pop(-1)
                    if type_of_lexeme == "TIf":
                        stack.append(nonterminal_symbols["Y1"])
                        stack.append(self.finish_then)
                        stack.append(nonterminal_symbols["F"])
                        stack.append("TRightParenthesis")

                        stack.append(self.check_if)
                        stack.append(nonterminal_symbols["W1"])
                        stack.append("TLeftParenthesis")
                        stack.append("TIf")
                    else:
                        self.print_error("RULE Y. if expected but %s found" % value_of_lexeme)
                elif top == nonterminal_symbols["Y1"]:
                    # Y1 -> else F | eps
                    print("Y1")
                    stack.pop(-1)
                    if type_of_lexeme == "TElse":
                        stack.append(self.finish_else)
                        stack.append(nonterminal_symbols["F"])
                        stack.append(self.continue_else)
                        stack.append("TElse")
                    elif type_of_lexeme in ["TClass", "TInt", "TBoolean", "TIdentifier",
                                            "TLeftBrace", "TRightBrace",
                                            "Tsemicolon", "TIf"]:
                        stack.append(self.finish_without_else)
                    else:
                        msg = "RULE Y1. TElse or (TClass, types, ...) expected but %s found"% value_of_lexeme
                        self.print_error(msg)
                elif top == nonterminal_symbols["W1"]:
                    # W1 -> !W1 | W2
                    print("W1")
                    stack.pop(-1)
                    self.is_expression = True
                    if type_of_lexeme == "TLogicalNot":
                        stack.append(self.gen_not)
                        stack.append(nonterminal_symbols["W1"])
                        stack.append("TLogicalNot")
                    else:
                        stack.append(nonterminal_symbols["W2"])
                elif top == nonterminal_symbols["W2"]:
                    # W2 -> W3W21
                    print("W2")
                    stack.pop(-1)
                    stack.append(nonterminal_symbols["W21"])
                    stack.append(nonterminal_symbols["W3"])
                elif top == nonterminal_symbols["W21"]:
                    # W21 -> + W3W21 | - W3W21 | eps
                    print("W21")
                    stack.pop(-1)
                    if type_of_lexeme == "TSubstraction":
                        stack.append(nonterminal_symbols["W21"])
                        stack.append(self.gen_substraction)
                        stack.append(nonterminal_symbols["W3"])
                        stack.append("TSubstraction")
                    elif type_of_lexeme == "TAddition":
                        stack.append(nonterminal_symbols["W21"])
                        stack.append(self.gen_addition)
                        stack.append(nonterminal_symbols["W3"])
                        stack.append("TAddition")
                    else:
                        pass
                elif top == nonterminal_symbols["W3"]:
                    # W3 -> W4W31
                    print("W3")
                    stack.pop(-1)
                    stack.append(nonterminal_symbols["W31"])
                    stack.append(nonterminal_symbols["W4"])
                elif top == nonterminal_symbols["W31"]:
                    # W31 -> * W4W31 | / W4W31 | % W4W31 | eps
                    print("W31")
                    stack.pop(-1)
                    if type_of_lexeme == "TMultiplication":
                        stack.append(nonterminal_symbols["W31"])
                        stack.append(self.gen_multiplication)
                        stack.append(nonterminal_symbols["W4"])
                        stack.append("TMultiplication")
                    elif type_of_lexeme == "TDivision":
                        stack.append(nonterminal_symbols["W31"])
                        stack.append(self.gen_division)
                        stack.append(nonterminal_symbols["W4"])
                        stack.append("TDivision")
                    elif type_of_lexeme == "TModulus":
                        stack.append(nonterminal_symbols["W31"])
                        stack.append(self.gen_modulus)
                        stack.append(nonterminal_symbols["W4"])
                        stack.append("TModulus")
                    else:
                        pass
                elif top == nonterminal_symbols["W4"]:
                    # W4 -> W5W41
                    print("W4")
                    stack.pop(-1)
                    stack.append(nonterminal_symbols["W41"])
                    stack.append(nonterminal_symbols["W5"])
                elif top == nonterminal_symbols["W41"]:
                    # W41 -> == W5W41 | != W5W41 | eps
                    print("W41")
                    stack.pop(-1)
                    if type_of_lexeme == "TEqualTo":
                        stack.append(nonterminal_symbols["W41"])
                        stack.append(self.gen_equal_to)
                        stack.append(nonterminal_symbols["W5"])
                        stack.append("TEqualTo")
                    elif type_of_lexeme == "TNotEqualTo":
                        stack.append(nonterminal_symbols["W41"])
                        stack.append(self.gen_not_equal_to)
                        stack.append(nonterminal_symbols["W5"])
                        stack.append("TNotEqualTo")
                    else:
                        pass
                elif top == nonterminal_symbols["W5"]:
                    # W5 -> W6W51
                    print("W5")
                    stack.pop(-1)
                    stack.append(nonterminal_symbols["W51"])
                    stack.append(nonterminal_symbols["W6"])
                elif top == nonterminal_symbols["W51"]:
                    # W51 -> ^ W6W51 | eps
                    print("W51")
                    stack.pop(-1)
                    if type_of_lexeme == "TBitwiseXor":
                        stack.append(nonterminal_symbols["W51"])
                        stack.append(self.gen_xor)
                        stack.append(nonterminal_symbols["W6"])
                        stack.append("TBitwiseXor")
                    else:
                        pass
                elif top == nonterminal_symbols["W6"]:
                    # W6 -> W7W61
                    print("W6")
                    stack.pop(-1)
                    stack.append(nonterminal_symbols["W61"])
                    stack.append(nonterminal_symbols["W7"])
                elif top == nonterminal_symbols["W61"]:
                    # W61 -> && W7W61 | eps
                    print("W61")
                    stack.pop(-1)
                    if type_of_lexeme == "TLogicalAnd":
                        stack.append(nonterminal_symbols["W61"])
                        stack.append(self.gen_logical_and)
                        stack.append(nonterminal_symbols["W7"])
                        stack.append("TLogicalAnd")
                    else:
                        pass
                elif top == nonterminal_symbols["W7"]:
                    # W7 -> W8W71
                    print("W7")
                    stack.pop(-1)
                    stack.append(nonterminal_symbols["W71"])
                    stack.append(nonterminal_symbols["W8"])
                elif top == nonterminal_symbols["W71"]:
                    # W71 -> || W8W71 | eps
                    print("W71")
                    stack.pop(-1)
                    if type_of_lexeme == "TLogicalOr":
                        stack.append(nonterminal_symbols["W71"])
                        stack.append(self.gen_logical_or)
                        stack.append(nonterminal_symbols["W8"])
                        stack.append("TLogicalOr")
                    else:
                        pass
                elif top == nonterminal_symbols["W8"]:
                    # W8 -> P | const | (W1)
                    print("W8")
                    stack.pop(-1)
                    if type_of_lexeme == "TIdentifier":
                        stack.append(self.var_to_r)
                        stack.append(nonterminal_symbols["P"])
                    elif type_of_lexeme == "TIntegerConstant":
                        stack.append("TIntegerConstant")
                        stack.append(self.const_to_r)
                    elif type_of_lexeme == "TTrue":
                        stack.append("TTrue")
                        stack.append(self.const_to_r)
                    elif type_of_lexeme == "TFalse":
                        stack.append("TFalse")
                        stack.append(self.const_to_r)
                    elif type_of_lexeme == "TLeftParenthesis":
                        stack.append("TRightParenthesis")
                        stack.append(nonterminal_symbols["W1"])
                        stack.append("TLeftParenthesis")
                    else:
                        self.print_error("Wrong expression")
                    self.is_expression = False
            #print(stack)
        self.table.write_tree('tree')
        self.print_triads()

        # Set tree's current pointer to root
        while self.table.current.parent is not None:
            self.table.current = self.table.current.parent

        return self.triads, self.table
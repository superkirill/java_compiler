from tree import Tree, Node
import sys

class Generator(object):
    """Assembler code generator"""
    def __init__(self, triads, tree):
        self.triads = triads
        self.tree = tree
        self.data = ""
        self.text = ""
        self.asm = "" # Resulting asm code
        self.last_function_name = ""
        self.local_vars = list()
        self.function_args = list()

    def print_error(self, message):
        print("\n\n\nError! %s" % message)
        sys.exit(0)

    def calc_required_space(self, num_of_triad):
        """Calculate how much space needs to be allocated for
            function's data"""
        allocate = 0
        operation = 'prolog'
        while operation != 'epilog':
            triad = self.triads[num_of_triad]
            operation = triad[0]
            arg1 = triad[1]
            arg2 = triad[2]
            if operation == "alloc":
                if self.get_type(arg1) == "ObjInt":
                    size = 4
                elif self.get_type(arg1) == "ObjBoolean":
                    size = 1
                else:
                    self.print_error("Unknown type in triad %d" % num_of_triad)
                allocate += size
            num_of_triad += 1
        return allocate

    def get_type(self, var):
        """Return type of a variable"""
        route = var.split('.')
        root = self.tree.current
        for node in route:
            if '(' in node:
                node = node[:node.index('(')]
            self.tree.current = self.tree.find_from(self.tree.current, node)
        result = self.tree.current.root.type
        self.tree.current = root
        return result

    def gen_data(self):
        self.data += '.data\n'
        is_global = True
        for triad in self.triads:
            operation = triad[0]
            arg1 = triad[1]
            arg2 = triad[2]
            if operation == 'proc':
                is_global = False
            elif operation == 'epilog':
                is_global = True
            if is_global is True and operation == 'alloc':
                if arg2 == 'ObjBoolean':
                    size = 'db'
                elif arg2 == 'ObjInt':
                    size = 'dd'
                self.data += '\t' + arg1.replace('.','@') + ': ' + size + " 0\n"

    def get_var(self, arg):
        if isinstance(arg, list):
            return 'ebx'
        if arg[0] == '<':
            return 'ebx'
        else:
            if '.' in arg:
                route = arg.split('.')
                is_a_parameter = False
                function = self.tree.find_by_id(route[-2])
                if function is not None and function.root.type == 'ObjFun':
                    is_a_parameter = True
                if is_a_parameter is True:
                    num_of_params = function.root.parameters
                    temp = function.right
                    for i in range(num_of_params):
                        temp = temp.left
                        if temp.root.id == route[-1]:
                            param_type = self.get_type(arg)
                            if param_type == 'ObjBoolean':
                                offset = -1
                            else:
                                offset = -4
                            return '[%d]' % offset
            if arg.replace('.','@') + ':' in self.data:
                return '[%s]' % arg.replace('.','@')
            else:
                offset = 0
                # print(self.local_vars)
                for var in self.local_vars:
                    if var[0] == arg:
                        return '[%d]' % offset
                    else:
                        offset += var[1]
        if arg == 'false':
            return 0
        if arg == 'true':
            return 1
        return arg

    def gen_text(self):
        self.text = '.text\n'
        self.text += '\tglobal _main\n'
        is_local = False
        function_args_size = 0
        for i in range(len(self.triads)):
            triad = self.triads[i]
            operation = triad[0]
            arg1 = triad[1]
            arg2 = triad[2]
            if operation == 'proc':
                # Function declaration
                self.text += "_" + arg1 + "\n"
                self.last_function_name = arg1
                function = self.tree.find_by_id(arg1)
                return_point = self.tree.current
                # print(function)
                self.tree.current = function.right
                for i in range(function.root.parameters):
                    self.tree.current = self.tree.current.left
                    if self.tree.current.root.type == 'ObjBoolean':
                        arg_type = 1
                    else:
                        arg_type = 4
                    self.function_args.append(arg_type)
                self.tree.current = return_point
                # print(self.function_args)
            elif operation == 'prolog':
                # Function's prolog
                is_local = True
                self.local_vars = list()
                self.text += "\tpush ebp"  + "".join([" " for i in range(20)]) + ";prolog\n"
                self.text += "\tmov ebp, esp\n"
                allocate = self.calc_required_space(i)
                if allocate != 0:
                    self.text += "\tsub esp, %d\n" % allocate
                self.text += "\tpush ebx\n"
                self.text += "\tpush esi\n"
                self.text += "\tpush edi\n"
            elif operation == 'epilog':
                # Function's epilog
                self.text += "\tpop edi" + "".join([" " for i in range(21)]) + ";epilog\n"
                self.text += "\tpop esi\n"
                self.text += "\tpop ebx\n"
                self.text += "\tmov esp, ebp\n"
                self.text += "\tpop ebp\n"
                self.text += "\tret\n"
                self.function_args = list()
                is_local = False
            elif operation == '&&':
                # Logical and
                var1 = self.get_var(arg1)
                var2 = self.get_var(arg2)
                self.text += '\tmov eax, %s\n' % str(var1)
                self.text += '\tand eax, %s\n' % str(var2)
                self.text += '\tmov ebx, eax\n'
            elif operation == '||':
                # Logical and
                var1 = self.get_var(arg1)
                var2 = self.get_var(arg2)
                self.text += '\tmov eax, %s\n' % str(var1)
                self.text += '\tor eax, %s\n' % str(var2)
                self.text += '\tmov ebx, eax\n'
            elif operation == 'alloc' and is_local is True:
                if arg2 == 'ObjBoolean':
                    size = 1
                else:
                    size = 4
                self.local_vars.append((arg1,size))
            elif operation == '+':
                # Addition
                var1 = self.get_var(arg1)
                var2 = self.get_var(arg2)
                self.text += '\tmov eax, %s\n' % str(var1)
                self.text += '\tadd eax, %s\n' % str(var2)
                self.text += '\tmov ebx, eax\n'
            elif operation == '=':
                # Assignment
                var1 = self.get_var(arg1)
                var2 = self.get_var(arg2)
                self.text += '\tmov eax, %s\n' % var2
                self.text += '\tmov %s, eax\n' % var1
            elif operation == '-':
                # Substraction
                var1 = self.get_var(arg1)
                var2 = self.get_var(arg2)
                self.text += '\tmov eax, %s\n' % str(var1)
                self.text += '\tsub eax, %s\n' % str(var2)
                self.text += '\tmov ebx, eax\n'
            elif operation == '^':
                # Bitwise xor
                var1 = self.get_var(arg1)
                var2 = self.get_var(arg2)
                self.text += '\tmov eax, %s\n' % str(var1)
                self.text += '\txor eax, %s\n' % str(var2)
                self.text += '\tmov ebx, eax\n'
            elif operation == '*':
                # Multiplication
                var1 = self.get_var(arg1)
                var2 = self.get_var(arg2)
                self.text += '\tmov eax, %s\n' % str(var1)
                self.text += '\tmov ecx, %s\n' % str(var2)
                self.text += '\tmul ecx\n'
                self.text += '\tmov ebx, eax\n'
            elif operation == '/':
                # Multiplication
                var1 = self.get_var(arg1)
                var2 = self.get_var(arg2)
                self.text += '\txor edx, edx\n'
                self.text += '\tmov eax, %s\n' % str(var1)
                self.text += '\tmov ecx, %s\n' % str(var2)
                self.text += '\tdiv ecx\n'
                self.text += '\tmov ebx, eax\n'
            elif operation == '%':
                # Modulus
                var1 = self.get_var(arg1)
                var2 = self.get_var(arg2)
                self.text += '\txor edx, edx\n'
                self.text += '\tmov eax, %s\n' % str(var1)
                self.text += '\tmov ecx, %s\n' % str(var2)
                self.text += '\tdiv ecx\n'
                self.text += '\tmov ebx, edx\n'
            elif operation == '!':
                # Logical not
                var1 = self.get_var(arg1)
                self.text += '\tmov eax, %s\n' % str(var1)
                self.text += '\txor eax, 1\n'
                self.text += '\tmov ebx, eax\n'
            elif operation == 'push':
                # Pass args to a function
                var1 = self.get_var(arg1)
                var_type = self.get_type(arg1)
                if var_type == 'ObjBoolean':
                    size = 1
                else:
                    size = 4
                function_args_size += size
                self.text += '\tpush %s\n' % str(var1)
            elif operation == 'call':
                var1 = self.get_var(arg1)
                self.text += '\tcall %s\n' % str(var1)
                self.text += '\tadd esp, %s\n' % str(function_args_size)
                function_args_size = 0
        # self.text = self.text.replace('\tmov ebx, eax\n\tmov eax, ebx\n', '')

    def generate(self):
        self.gen_data()
        self.gen_text()
        self.asm = self.data + self.text
        print(self.asm)

        
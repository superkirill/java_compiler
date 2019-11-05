from tree import Tree, Node

class Optimizer(object):
    """Optimizer"""
    def __init__(self, triads):
        self.triads = triads
        self.used_variables = list()
        self.all_variables = list()

    def is_constant(self, expr):
        if expr in ['true', 'false']:
            return True
        try: 
            int(expr)
            return True
        except ValueError:
            return False
        except TypeError:
            return False

    def find_dependencies(self, triad_num):
        """Find all variables used in an expression"""
        dependecies = list()
        for arg_num in range(1,3):
            arg = self.triads[triad_num][arg_num]
            if self.is_constant(arg) is False:
                if arg != '' and arg != '?':
                    if isinstance(arg, list):
                        if arg[0][0] == '<':
                            # print(arg)
                            dependecies += self.find_dependencies(int(arg[0][1:-1])-1)
                    else:
                        if isinstance(arg, Tree) is False:
                            if arg[0] == '<':
                                # print(arg)
                                dependecies += self.find_dependencies(int(arg[1:-1])-1)
                            else:
                                dependecies.append(arg)
                        else:
                            dependecies.append(arg.root.id)
        return dependecies

    def find_triad(self, operation, arg1=None, arg2=None, is_reversed=False, start_at=0, until=None):
        """Find a triad that satisfies a given form (operation, arg1, arg2) and return its number"""
        if until is None:
            until = len(self.triads)
        if is_reversed == True:
            triads = list(reversed(self.triads[start_at:until]))
        else:
            triads = self.triads[start_at:until]
        for i in range(len(triads)):
            found = True
            triad = triads[i]
            if triad[0] != operation:
                found = False    
            if arg1 is not None:
                if triad[1] != arg1:
                    found = False
            if arg2 is not None:
                if triad[2] != arg2:
                    found = False
            if found is True:
                if is_reversed:
                    return len(triads) - 1 - i
                else:
                    return i
        return -1

    def optimize(self):
        """Remove unused variables"""
        last_reference = dict()
        for i in range(len(self.triads)):
            triad = self.triads[i]
            if triad[0] in ['push', 'cmp']:
                self.used_variables.append(triad[1])
                last_reference[triad[1]] = i
                self.all_variables.append(triad[1])
            elif triad[0] not in ['proc', 'prolog', 'epilog', 'call']:
                if self.is_constant(triad[1]) is False and  triad[1] != '' and  triad[1][0] not in ['<', '?'] \
                    and isinstance(triad[1], list) is False and triad[1] != 'ObjBoolean' and triad[1] != 'ObjInt':
                    self.all_variables.append(triad[1])
                    last_reference[triad[1]] = i
                if self.is_constant(triad[2]) is False and  triad[2] != '' and triad[2][0] not in ['<', '?']\
                    and isinstance(triad[2], list) is False and triad[2] != 'ObjBoolean' and triad[2] != 'ObjInt':
                    self.all_variables.append(triad[2])
                    last_reference[triad[2]] = i

        depended_variables = list()
        for used_variable in self.used_variables:
            if self.is_constant(used_variable) is False:
                to_check = [used_variable]
                dependecies = list()
                triad_num = self.find_triad(operation='=', arg1=used_variable, is_reversed=True)
                while len(to_check) > 0:
                    var = to_check.pop()
                    triad_num = self.find_triad(operation='=', arg1=var, is_reversed=True, until=triad_num+1)
                    result = [dependency for dependency in self.find_dependencies(triad_num) if dependency != var]
                    to_check += result
                    dependecies += result
                depended_variables += [dependency for dependency in dependecies if dependency != used_variable]
        for dependency in depended_variables:
            if dependency not in self.used_variables:
                self.used_variables.append(dependency)
        for var in self.used_variables:
            if self.is_constant(var) is True:
                self.used_variables.remove(var)
        for var in self.all_variables:
            if self.is_constant(var) is True:
                self.all_variables.remove(var)
        self.used_variables = list(set(self.used_variables))
        self.all_variables = list(set(self.all_variables))
        unused_variables = list(set(self.all_variables)-set(self.used_variables))
        # print(self.used_variables)
        # print(self.all_variables)
        # print(unused_variables)
        # print(last_reference)

        to_clear = list()
        for i in range(len(self.triads)):
            triad = self.triads[i]
            for var in self.used_variables:
                if triad[1] == var and last_reference[var] < i:
                    self.triads[i] = tuple(('nop', '', ''))
                if triad[2] == var and last_reference[var] < i:
                    self.triads[i] = tuple(('nop', '', ''))
            if triad[1] in unused_variables or triad[2] in unused_variables:
                if triad[2] != '' and triad[2][0]=='<':
                    to_clear.append(int(triad[2][1:-1])-1)
                if triad[1] != '' and triad[1][0]=='<':
                    to_clear.append(int(triad[1][1:-1])-1)
                self.triads[i] = tuple(('nop', '', ''))
        # print('\n\n\n' + str(to_clear) + '\n\n\n')
        for index in to_clear:
            if self.triads[index][1] != '' and self.triads[index][1][0]=='<':
                to_clear.append(int(self.triads[index][1][1:-1])-1)
            if self.triads[index][2] != '' and self.triads[index][2][0]=='<':
                to_clear.append(int(self.triads[index][2][1:-1])-1)
        for index in to_clear:
            self.triads[index] = tuple(('nop', '', ''))
        self.print_triads()
        return self.triads


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
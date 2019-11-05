import numpy as np
import sys, os
from definitions import object_type, MAX_NODES
from copy import deepcopy

class Node(object):
    """Tree's Node"""
    def __init__(self, id_lex=None, data_type=None, value=None, parameters=None, user=None):
        self.id = id_lex # Object's identifier
        self.type = data_type # Value type
        self.value = value # Object's value or None
        self.parameters = parameters # Number of function's parameters
        self.user_type = user
    
    def __str__(self):
        """String Representation"""
        if self.type == "ObjFun":
            string = "%s(%s), parameters = %d, text_ptr = %s" % (self.id, self.type, self.parameters, self.value)
        else:
            string = "%s(%s), value = %s" % (self.id, self.type, str(self.value))
        return string


class Tree(object):
    """Binary Tree"""
    def __init__(self, data=None, left_subtree=None, right_subtree=None, parent=None):
        if type(data) == Node:
            self.root = data
        else:
            self.root = Node() if data is None else Node(data[0], data[1])
        self.left = left_subtree
        self.right = right_subtree
        self.parent = parent
        self.current = None
        self.invisible_node_id = np.random.randint(1000000) # Used for graphviz

    def __str__(self):
        if self.root is not None:
            if self.root.type == "ObjFun":
                string = "%s(%s), parameters = %d, text_ptr = %s" % (self.root.id, self.root.type, self.root.parameters, self.root.value)
            else:
                string = "%s(%s), value = %s" % (self.root.id, self.root.type, str(self.root.value))
            return string

    def set_current(self, node):
        self.current = node

    def get_current(self):
        return self.current

    def is_present(self, identifier, from_node):
        """Check if object with identifier 'a' has previously
        been defined within the 'from_node' nesting level"""
        if self.find_up_one_level(identifier, from_node):
            return True
        else:
            return False


    def include(self, lexeme, object_type):
        """Add object into the tree"""
        if self.is_present(lexeme, self.current):
            print("\n\n\nError! Attempt to define an object (%s) that has already been defined!" % lexeme)
            sys.exit(0)
        if object_type == "ObjInt" or object_type == "ObjBoolean":
            # Insert a node of type 'variable' into the tree
            self.current.set_left(Node(id_lex=lexeme, data_type=object_type, parameters=0))
            self.current = self.current.left
            return self.current
        elif object_type == "ObjFun":
            # Insert a node of type 'function' into the tree
            self.current.set_left(Node(id_lex=lexeme, data_type=object_type, parameters=0))
            self.current = self.current.left
            # Save point of return

            return_point = self.current

            # # Insert an empty node into the tree (right child of function's 
            # # declaration node)
            self.current.set_right(Node(parameters=0))
            self.current = self.current.right
            return return_point
            # return self.current
        elif object_type == "ObjClass":
            # Insert a node of type 'class' into the tree
            self.current.set_left(Node(id_lex=lexeme, data_type=object_type, parameters=0))
            self.current = self.current.left
            # Save point of return
            return_point = self.current

            # Insert an empty node into the tree (right child of class's 
            # declaration node)
            self.current.set_right(Node(parameters=0))
            self.current = self.current.right
            return return_point    
        else:
            # Insert a node of type 'variable' into the tree
            # print("Class: %s, object: %s" % (object_type, lexeme))
            self.find_class(object_type)
            self.current.set_left(Node(id_lex=lexeme, data_type=object_type, parameters=0))
            self.current = self.current.left
            self.copy_subtree(self.find_class(object_type))
            return self.current   

    def copy_subtree(self, reference):
        """Copy the subtree found at a given reference"""
        return_point = self.current
        self.current.right = deepcopy(reference.right)
        self.update_parent_references(self.current)

    def update_parent_references(self, subtree):
        if subtree.left is not None:
            subtree.left.parent = subtree
            self.update_parent_references(subtree.left)
        if subtree.right is not None:
            subtree.right.parent = subtree
            self.update_parent_references(subtree.right)



    def set_left(self, node):
        self.left = Tree(data=node, parent=self)

    def set_right(self, node):
        self.right = Tree(data=node,parent=self)

    def set_type(self, node, new_type):
        node.root.type = new_type

    def set_parameters(self, node, new_parameters):
        node.root.parameters = new_parameters

    def compare_number_of_parameters(self, node, number):
        """Check if a function is called with the same amount of
        parameters that has been set in its declaration"""
        if number != node.root.parameters:
            print("\n\n\nError! Wrong number of parameters, function: \'%s\'!" % node.root)
            sys.exit(0)

    def compare_parameters(self, node, params, scanner):
        """Check if a function is called with the same amount and
        types of parameters that have been set in its declaration"""
        if len(params) != node.root.parameters:
            return False
        return_point = self.current
        self.current = node.right
        for i in range(node.root.parameters):
            self.current = self.current.left
            if self.current.root.type != params[i][0]:
                msg = "\n\n\nFunction called: %s\n" % node.root.id
                msg += "Parameter No. %d has a wrong type. Expected: %s, got: %s" % (i+1, self.current.root.type, params[i][0]) 
                scanner.print_error(msg)
        self.current = return_point
        return True

    def contains(self, node, identifier):
        """Return a reference to 'identifier'"""
        temp = node.right.left
        while not temp is None:
            # print(temp.root)
            if temp.root.id == identifier:
                return temp
            temp = temp.left
        return None

    def find_variable(self, identifier):
        """Return node containing variable with identifier = 'identifier'"""
        result = self.find_up(identifier, self.current).root
        if result is None:
            print("\n\n\nError! Variable \'%s\' has not been declared!" % identifier)
            sys.exit(0)
        elif result.type == "ObjFun":
            print("\n\n\nError! Wrong usage of function \'%s\' !" % identifier)
            sys.exit(0)
        elif result.type == "ObjClass":
            print("\n\n\nError! Wrong usage of class \'%s\' !" % identifier)
            sys.exit(0)
        return result

    def find_function(self, identifier):
        """Return node containing variable with identifier = 'identifier'"""
        result = self.find_up(identifier, self.current)
        if result is None:
            print("\n\n\nError! Function \'%s\' has not been declared!" % identifier)
            sys.exit(0)
        elif result.root.type == "ObjVar":
            print("\n\n\nError! \'%s\' is not a variable!" % identifier)
            sys.exit(0)
        elif result.root.type == "ObjClass":
            print("\n\n\nError! \'%s\' is not a class!" % identifier)
            sys.exit(0)
        return result

    def find_class(self, identifier):
        """Return node containing variable with identifier = 'identifier'"""
        result = self.find_up(identifier, self.current)
        if result is None:
            print("\n\n\nError! Class \'%s\' has not been declared!" % identifier)
            sys.exit(0)
        elif result.root.type == "ObjFun":
            print("\n\n\nError! \'%s\' is not a function!" % identifier)
            sys.exit(0)
        elif result.root.type == "ObjVar":
            print("\n\n\nError! \'%s\' is not a variable!" % identifier)
            sys.exit(0)
        elif result.root.type != "ObjClass":
            print("\n\n\nError! \'%s\' is not a class!" % identifier)
            sys.exit(0)
        return result

    def find_parents(self, node):
        """Return a list of parents of a node 'node'"""
        parents = [node.root.id]
        i = 0
        local_argument = False
        while i < 20 and node.parent is not None:
            print(node.root)
            if local_argument is False and node.parent.root.type == "ObjFun" and node.parent.right == node:
                local_argument = True
                parents.append(node.parent.root.id)
                node = node.parent
            elif node.parent.root.type == "ObjClass" and node.parent.right == node:
                parents.append(node.parent.root.id)
                node = node.parent
            elif node.parent.root.type not in ["ObjClass", "ObjFun"] and isinstance(node.parent.root.type, str) and node.parent.right == node:
                parents.append(str(node.parent.root.id) + "(" + str(node.parent.root.type) + ")")
                node = node.parent
            else:
                node = node.parent
            # else:
            #     if node.root.type in ["ObjClass"]:
            #         parents.append(node.root.id)
            #         node = node.parent
            #     else:
            #         node = node.parent
            i += 1
        return list(reversed(parents))

    def find_by_id(self, identifier):
        """Find a node in the tree by its identifier, starting from root"""
        if self.root.id == identifier:
            return self
        else:
            result = None
            if not self.left is None:
                result = self.left.find_by_id(identifier)
            if not result is None:
                return result
            if not self.right is None:
                result = self.right.find_by_id(identifier)
            if not result is None:
                return result
        return None

    def find_from(self, node, identifier):
        """Return a reference to 'identifier'"""
        temp = node
        if temp is not None:
            if temp.root.id == identifier:
                return temp
            if temp.left is not None:
                result = self.find_from(temp.left, identifier)
                if result is not None:
                    return result
            if temp.right is not None:
                result = self.find_from(temp.right, identifier)
                if result is not None:
                    return result
        return None

    def find_up(self, identifier, from_node):
        """Find a node in the tree by its identifier, starting from 'from_node'
        and going upwards"""
        temp = from_node
        while not temp is None and identifier != temp.root.id:
            temp = temp.parent
        if temp is None:
            return None
        elif temp.root.id == identifier:
            return temp
        else:
            return None

    def find_up_one_level(self, identifier, from_node):
        """Find a node in the tree by its identifier, starting from 'from_node'
        and going upwards and using left connections only"""
        temp = from_node
        while not temp is None and \
                not temp.parent is None and\
                not temp.parent.right is temp:
            if temp.root.id == identifier:
                return temp
            temp = temp.parent
        return None

    def _print_nodes(self):
        print("\nNode %s" % self.root)
        if not self.left is None:
            print("\tLeft child: %s" % id(self.left.root))

        if not self.right is None:
            print("\tRight child: %s" % id(self.right.root))

        if not self.left is None:
            self.left._print_nodes()

        if not self.right is None:
            self.right._print_nodes()

    def print_tree(self):
        """Print the tree"""
        print("Binary Tree")
        self._print_nodes()
        print("\n")

    def write_tree_as_dot(self, f):
        """Write the tree in the dot language format to f."""
        def node_id(node):
            """Return the node's id"""
            return 'N%d' % id(node)

        def visit_node(node):
            """Visit a node."""
            if node.root.type is None:
                f.write("  %s [label=\"\", shape=\"circle\", fixedsize=\"true\", size=\"12.4\", style=\"filled\", fillcolor=\"black\"];" % node_id(node.root))
            else:
                f.write("  %s [label=\"%s\", shape=\"box\"];" % (node_id(node.root), node.root))
            if not node.left is None:
                visit_node(node.left)
                f.write("  %s -> %s ;" % (node_id(node.root), node_id(node.left.root)))
            else:
                f.write(" %s [label=\"C\", style=invis]; %s -> %s [style=invis];" % (self.invisible_node_id,
                                                                        node_id(node.root),
                                                                        self.invisible_node_id))
                self.invisible_node_id += 1
            if not node.right is None:
                visit_node(node.right)
                f.write("  %s -> %s ;" % (node_id(node.root), node_id(node.right.root)))
            else:
                f.write(" %s [label=\"C\", style=invis]; %s -> %s [style=invis];" % (self.invisible_node_id,
                                                                        node_id(node.root),
                                                                        self.invisible_node_id))
                self.invisible_node_id += 1
        f.write("digraph b_tree {graph [ordering=\"out\"];")
        visit_node(self)
        f.write("}")

    def write_tree(self, filename):
        """Write the tree as a .gv file."""
        with open('%s.gv' % filename, 'w') as f:
            self.write_tree_as_dot(f)
        os.system(r'D:/"Program Files"/Graphviz2.38/bin/dot.exe -Tjpg -o %s.jpg %s.gv' % (filename, filename))

def main():
    binary_tree = Tree()
    
    binary_tree.set_current(binary_tree)

    binary_tree.include("function_example", "ObjFun")
    binary_tree.set_type(binary_tree.get_current(), "LALALAL")
    binary_tree.include("class_example", "ObjClass")
    binary_tree.print_tree()

    binary_tree.set_type(binary_tree.get_current(), "LALALAL")
    binary_tree.print_tree()
    binary_tree.write_tree("tree")

if __name__ == '__main__':
    main()
from __future__ import annotations

class ParseTree:
    """
    represents a node in a parse tree
    two types: terminal nodes (leaf with token) or non-terminal nodes (internal with children)
    """

    def __init__(self, name: str, token: tuple[str, str] = None):
        """
        initialize a parse tree node
        name: non-terminal name (like "expr") or token type (like "NUMBER")
        token: if set, this is a terminal/leaf node with (token_type, lexeme) pair
        """
        self.name = name  # node name (rule name or token type)
        self.children = []  # list of child ParseTree nodes
        self.token = token  # if not None, this is a terminal node (leaf)

    def add_children(self, child: ParseTree):
        """add a child node to this node's children list"""
        self.children.append(child)
    
    def to_string(self, indent_level=0):
        """
        convert parse tree to formatted string with indentation
        indent_level: current indentation level (0 = root, 1 = first level children, etc.)
        returns string representation with proper formatting
        """
        # calculate indentation string: 2 spaces per level (0 spaces, 2 spaces, 4 spaces, ...)
        indentation = " " * indent_level*2
        
        # case 1: terminal node (leaf node with actual token)
        # format: (TOKEN_TYPE: lexeme)
        if self.token:
            return f"{indentation}({self.token[0]}: {self.token[1]})"
        
        # case 2: non-terminal node (internal node with children)
        # need to handle three subcases for different formatting rules
        
        # subcase 2a: flatten wrapper nodes with single terminal child
        # if node only has one child and that child is a terminal, skip this node
        # example: instead of "rule\n  (ID: x)", just show "(ID: x)"
        if len(self.children)==1 and self.children[0].token:
            return self.children[0].to_string(indent_level)
        
        # subcase 2b: hide intermediate nodes (int_*) created during cnf conversion
        # these nodes are implementation details, not meaningful for users
        # show their children at the same indentation level (don't increase indent)
        if self.name.startswith("int_"):
            result = ""
            for child in self.children:
                result += "\n"+child.to_string(indent_level)
            return result[1:]
        
        # subcase 2c: regular non-terminal node
        # format: node_name followed by indented children (indent + 1)
        result = f"{indentation}{self.name}"
        for child in self.children:
            result+="\n"+child.to_string(indent_level+1)
        return result

    def __str__(self):
        """string representation: calls to_string() starting at indent level 0"""
        return self.to_string()
import ast

from pepgrave.transformers import ASTTransformer

ROMAN_LITERALS = {
    "I": 1,
    "V": 5,
    "X": 10,
    "L": 50,
    "C": 100,
    "D": 500,
    "M": 1000,
}


class PEP313Resolver(ASTTransformer):
    def visit_Name(self, node):
        if literal := self.roman_literal_check(node.id):
            constant = ast.Constant(literal)
            ast.copy_location(node, constant)
            return constant
        return self.generic_visit(node)

    @staticmethod
    def roman_literal_check(literal):
        # Adapted from old version of PEPGrave,
        # https://github.com/isidentical-archive/pepallow/blob/master/pepallow/romana.py
        try:
            literals = [ROMAN_LITERALS[lit] for lit in literal]
        except KeyError:
            return None

        result = literals.pop(0)

        for literal in literals:
            if literal > result:
                result = literal - result
            elif literal <= result:
                result += literal

        return result

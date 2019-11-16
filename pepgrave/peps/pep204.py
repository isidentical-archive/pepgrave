import io
import tokenize

from pepgrave.transformers import TokenTransformer, pattern


class PEP204Resolver(TokenTransformer):
    """
    >>> [:5]
    [0, 1, 2, 3, 4]
    >>> [1:10]
    [1, 2, 3, 4, 5, 6, 7, 8, 9]
    >>> [5:1:-1]
    [5, 4, 3, 2]
    """

    @pattern("lsqb", "colon", "number", "rsqb")
    def slice_type_range_transformer(self, *tokens):
        *_, finish, __ = tokens
        return self.quick_tokenize(repr(list(range(int(finish.string)))))

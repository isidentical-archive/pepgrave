import io
import tokenize

from pepgrave.transformers import TokenTransformer


class PEP204Resolver(TokenTransformer):
    """
    >>> [:5]
    [0, 1, 2, 3, 4]
    >>> [1:10]
    [1, 2, 3, 4, 5, 6, 7, 8, 9]
    >>> [5:1:-1]
    [5, 4, 3, 2]
    """

    def pattern_lsqb_colon_number_rsqb(self, _, __, finish, ___):
        literal_repr = repr(list(range(int(finish.string))))
        return list(
            tokenize.generate_tokens(io.StringIO(literal_repr).readline)
        )[:-1]

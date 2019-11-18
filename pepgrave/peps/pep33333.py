# This is just a PoC that PEPGrave can implement features from other languages

import token

from pepgrave.transformers import TokenTransformer, pattern
from pepgrave.untokenizer import untokenize


class PEP33333Resolver(TokenTransformer):
    # Just a placeholder PEP
    # Idea credits: waterymadman for elm features

    @pattern(
        "name",
        "name",
        "equal",
        "newline",
        "indent",
        "*(.*?)",
        "newline",
        "*nl",
        "dedent",
    )
    def elm_function_resolver(self, *tokens):
        stream_token = iter(tokens)
        function_name = next(stream_token)
        argument = next(stream_token)
        _, __ = next(stream_token), next(stream_token)
        indent = next(stream_token)
        return_value = []
        while (current := next(stream_token)).type != token.NEWLINE:
            return_value.append(current)
        nl = current
        *nls, ___ = stream_token
        return [
            *self.quick_tokenize(
                f"{function_name.string} = (lambda {argument.string}: {untokenize(return_value)})"
            ),
            nl,
        ]

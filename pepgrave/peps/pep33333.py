# This is just a PoC that PEPGrave can implement features from other languages

from pepgrave.transformers import TokenTransformer, pattern


class PEP33333Resolver(TokenTransformer):
    # Just a placeholder PEP
    # Idea credits: waterymadman for elm features

    @pattern(
        "name",
        "name",
        "equal",
        "newline",
        "*indent",
        "name",
        "newline",
        "dedent",
    )
    def elm_function_resolver(self, *tokens):
        (
            function_name,
            argument,
            _,
            __,
            *indents,
            return_value,
            nl,
            ___,
        ) = tokens
        return [
            *self.quick_tokenize(
                f"{function_name.string} = (lambda {argument.string}: {return_value.string})"
            ),
            nl,
        ]

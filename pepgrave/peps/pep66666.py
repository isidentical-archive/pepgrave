# This is just a PoC that PEPGrav0/can implement features from other languages

import token

from pepgrave.transformers import Priority, TokenTransformer, pattern
from pepgrave.untokenizer import untokenize


class PEP66666Resolver(TokenTransformer):
    # Just a placeholder PEP
    # Idea credits: @badem_bagetli for ruby functions

    @pattern(
        "number",
        "name",
        "name",
        "*( newline| nl)",
        "indent",
        "*(.*?)",
        "*( newline| nl)",
        "dedent",
        "name",
    )
    def ruby_times_resolver(self, *tokens):
        stream_token = iter(tokens)
        times = next(stream_token).string.replace(".", "", -1)
        if (
            next(stream_token).string != "times"
            or next(stream_token).string != "do"
        ):
            return
        next(stream_token)  # newline
        body = []
        while (current := next(stream_token)).type not in {
            token.NL,
            token.NEWLINE,
        }:
            body.append(current)
        *_, end = stream_token
        if end.string != "end":
            return
        return self.quick_tokenize(
            f"for _ in range({times}):\n{untokenize(body)}"
        )

    @pattern("name", "*(.*?)", "newline")
    @Priority.LAST
    def ruby_puts_resolver(self, name, *tokens):
        if name.string == "puts":
            *body, _ = tokens
            return self.quick_tokenize(f"print({untokenize(body)})")

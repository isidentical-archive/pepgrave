import token
from pepgrave.transformers import TokenTransformer, pattern


class PEP315Resolver(TokenTransformer):
    # do:
    #   <suite>
    # while:
    #

    @pattern("name", "colon", "newline", "indent", "(.*?)", "dedent", "name", "(.*?)", "colon", "newline", "indent", "(.*?)", "dedent")
    def indexing_transformer(self, *stream_tokens):
        stream_token = iter(stream_tokens)
        if next(stream_token).string != "do":
            return
        next(stream_token) # colon
        next(stream_token) # newline
        next(stream_token) # indent
        setup, dedent = self.until(token.DEDENT, stream_token)
        statement = next(stream_token)
        if statement.string != "while":
            return
        test, colon = self.until(token.COLON, stream_token)
        newline = next(stream_token)
        indent = next(stream_token)
        body, dedent = self.until(token.DEDENT, stream_token)
        return (*setup, statement, *test, colon, newline, indent, *body, *setup, dedent)


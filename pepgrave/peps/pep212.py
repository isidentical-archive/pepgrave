from pepgrave.transformers import TokenTransformer, pattern


class PEP212Resolver(TokenTransformer):
    # for i indexing e in sequence

    @pattern("name", "name", "name", "name", "name", "name")
    def indexing_transformer(self, *tokens):
        statement, indexer, indexing, iteration, keyword, iterable = tokens
        if statement.string == "for" and indexing.string == "indexing":
            return self.quick_tokenize(
                f"for {indexer.string}, {iteration.string} in enumerate({iterable.string})"
            )
        return tokens

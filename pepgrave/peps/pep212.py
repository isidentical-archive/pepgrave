from pepgrave.transformers import TokenTransformer


class PEP212Resolver(TokenTransformer):
    # for i indexing e in sequence

    def catch(self, *tokens):
        statement, indexer, indexing, iteration, keyword, iterable = tokens
        if statement.string == "for" and indexing.string == "indexing":
            return self.quick_tokenize(
                f"for {indexer.string}, {iteration.string} in enumerate({iterable.string})"
            )
        return tokens

    pattern_name_name_name_name_name_name = catch

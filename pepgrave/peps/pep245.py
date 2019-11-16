from pepgrave.transformers import TokenTransformer, pattern


class PEP245Resolver(TokenTransformer):
    # interface ColorFishInterface

    @pattern("name", "name", "colon")
    def interface_transformer(self, *tokens):
        interface, class_name, _ = tokens
        if interface.string == "interface":
            return self.quick_tokenize(
                f"class {class_name.string}(__import__('abc').ABC):"
            )
        return tokens

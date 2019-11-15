from pepgrave.transformers import TokenTransformer


class PEP245Resolver(TokenTransformer):
    # interface ColorFishInterface

    def pattern_name_name_colon(self, *tokens):
        interface, class_name, _ = tokens
        if interface.string == "interface":
            return self.quick_tokenize(
                f"class {class_name.string}(__import__('abc').ABC):"
            )
        return tokens

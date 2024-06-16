# stateless class
class Operation:
    @classmethod
    def name(cls):
        raise Exception("Not implemented")

    @classmethod
    def icon(cls):
        raise Exception("Not implemented")

    @classmethod
    def validate_selection(cls, use, sel):
        raise Exception("Not implemented")

    @classmethod
    def validate_and_parse(cls, form):
        raise Exception("Not implemented")

    @classmethod
    def apply(cls, mods):
        raise Exception("Not implemented")

    @classmethod
    def render(cls):
        raise Exception("Not implemented")

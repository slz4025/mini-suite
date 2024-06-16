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
    def apply(cls, form):
        raise Exception("Not implemented")

    @classmethod
    def render(cls):
        raise Exception("Not implemented")

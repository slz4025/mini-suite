# stateless class
class Selector:
    @classmethod
    def name(cls):
        raise Exception("Not implemented")

    @classmethod
    def validate_and_parse(cls, form):
        raise Exception("Not implemented")

    @classmethod
    def render(cls):
        raise Exception("Not implemented")

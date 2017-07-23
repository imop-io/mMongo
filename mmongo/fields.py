# coding: utf8


class Null(object):
    pass


class Field(object):

    def __init__(
        self,
        required=None,
        index=None,
        default=Null()
    ):
        self.required = required
        self.index = index
        self.default = default

    def validate(self, value):
        raise NotImplemented()

    @property
    def types(self):
        return self._types


class StringField(Field):
    _types = (str, bytes)

    def validate(self, value):
        if self.required:
            if isinstance(value, self._types):
                return True
            return False
        return True


class IntegerField(Field):
    _types = (int, )

    def validate(self, value):
        if not self.required:
            return True
        if not isinstance(value, self._types):
            return False
        return True


class FloatField(Field):
    _types = (float, )

    def validate(self, value):
        if not self.required:
            return True
        if not isinstance(value, self._types):
            return False
        return True


class NumericField(Field):
    _types = (int, float)

    def validate(self, value):
        if not self.required:
            return True
        if not isinstance(value, self._types):
            return False
        return True

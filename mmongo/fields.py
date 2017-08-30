# coding: utf8


class Null(object):
    pass


class Field(object):
    _types = None

    def __init__(self, required=None, index=None, default=Null()):
        self.required = required
        self.index = index
        self.default = default

    def validate(self, value):
        raise NotImplementedError()

    @property
    def types(self):
        return self._types

    def ensure_value(self, value):
        return value


class StringField(Field):
    _types = (str, bytes)

    def validate(self, value):
        if self.required:
            if isinstance(value, self.types):
                return True
            return False
        return True


class IntegerField(Field):
    _types = (int, )

    def validate(self, value):
        if not self.required:
            return True
        if not isinstance(value, self.types):
            return False
        return True


class FloatField(Field):
    _types = (float, )

    def validate(self, value):
        if not self.required:
            return True
        if not isinstance(value, self.types):
            return False
        return True


class NumericField(Field):
    _types = (int, float)

    def validate(self, value):
        if not self.required:
            return True
        if not isinstance(value, self.types):
            return False
        return True


class SequenceField(Field):

    _types = (list,)

    def __init__(self, required=None, index=None, default=Null(),
                 sub_fields=[]):
        super().__init__(required, index, default)
        self._sub_fields = sub_fields

    def validate(self, value):
        if not self.required:
            return True
        if not isinstance(value, self.types):
            return False
        for field, val in zip(self._sub_fields, value):
            if not isinstance(field, Field):
                return False
            if not field.validate(val):
                return False
        return True

    def ensure_value(self, value):
        return list(value)


class ComplexField(Field):
    _types = ()
    
    def validate(self, value):
        return True


class EnumField(Field):
    def __init__(self, enum, required=None, index=None, default=Null()):
        self._enum = enum
        super().__init__(required, index, default)

    def validate(self, value):
        if not self.required:
            return True
        if value in self._enum:
            return True
        return False


class BoolField(EnumField):
    def __init__(self, required=None, index=None, default=Null()):
        super().__init__((True, False), required, index, default)

    def validate(self, value):
        if not self.required:
            return True
        if bool(value) in self._enum:
            return True
        return False

    def ensure_value(self, value):
        return bool(value)

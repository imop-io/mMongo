# coding: utf8


class Null(object):
    pass


class Field(object):

    def __init__(self, required=None, index=None, default=Null()):
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
        self.sub_fields = sub_fields

    def validate(self, value):
        if not self.required:
            return True
        if not isinstance(value, self.types):
            return False
        for field, val in zip(self.sub_fields, value):
            if not isinstance(field, Field):
                return False
            if not field.validate(val):
                return False
        return True


class ComplexField(Field):
    _types = ()
    
    def validate(self, value):
        return True

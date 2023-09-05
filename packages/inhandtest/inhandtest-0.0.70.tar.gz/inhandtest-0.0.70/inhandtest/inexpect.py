# -*- coding: utf-8 -*-
# @Time    : 2023/8/31 16:02:16
# @Author  : Pane Li
# @File    : inexpect.py
"""
inexpect

"""
import typing
from inhandtest.tools import dict_in


class expect:
    def __init__(self, value, args=None, kwargs=None):
        self._value = value
        self._args = args
        self._kwargs = kwargs

    def to_eq(self, expect_value):
        """Value is equal， 非严格相同， 只要值相等即可，可以是列表也可以是元组和字典等类型
           ex: expect(1).to_eq(1).to_ne(2)
           a = [1, 2, 3]
           expect(a).to_eq([1, 2, 3])
           a = {"a": 1, "b": 2}
           expect(a).to_eq({"a": 1, "b": 2})
        """
        try:
            assert self._value == expect_value, f'expect {self._value} to be {expect_value}'
        except TypeError:
            raise
        return self

    def to_ne(self, expect_value):
        """Value is not equal
           ex: expect(1).to_ne(2).to_eq(1)
        """
        try:
            assert self._value != expect_value, f'expect {self._value} not to be {expect_value}'
        except TypeError:
            raise
        return self

    def to_lt(self, expect_value):
        """Value is less than
           ex: expect(1).to_lt(2).to_gt(0)
        """
        try:
            assert self._value < expect_value, f'expect {self._value} to less than {expect_value}'
        except TypeError:
            raise
        return self

    def to_gt(self, expect_value):
        """Value is more than
           ex: expect(2).to_gt(1).to_lt(3)
        """
        try:
            assert self._value > expect_value, f'expect {self._value} to more than {expect_value}'
        except TypeError:
            raise
        return self

    def to_le(self, expect_value):
        """Value is less than or equal
           ex: expect(1).to_le(1).to_ge(1)
        """
        try:
            assert self._value <= expect_value, f'expect {self._value} to less than or equal {expect_value}'
        except TypeError:
            raise
        return self

    def to_ge(self, expect_value):
        """Value is more than or equal
           ex: expect(1).to_ge(1).to_le(1)
        """
        try:
            assert self._value >= expect_value, f'expect {self._value} to more than or equal {expect_value}'
        except TypeError:
            raise
        return self

    def to_be(self, expect_value):
        """Value is the same, 严格相同
           ex: expect(1).to_be(1).to_not_be(2), expect('1').to_be('1').to_not_be('2')
        """
        try:
            assert self._value is expect_value, f'expect {self._value} to be {expect_value}'
        except TypeError:
            raise
        return self

    def to_be_false(self):
        """Value is False  False|0|''|[]|{}|None|()"""
        try:
            assert not self._value, f'expect {self._value} to be False'
        except TypeError:
            raise
        return self

    def to_be_true(self):
        """Value is True  True|1|'1'|[1]|{"a": 1}|(1, )"""
        try:
            assert self._value, f'expect {self._value} to be True'
        except TypeError:
            raise
        return self

    def to_not_be(self, expect_value):
        """Value is not the same
           ex: expect(1).to_not_be(2).to_be(1), expect('1').to_not_be('2').to_be('1')
        """
        try:
            assert self._value is not expect_value, f'expect {self._value} to be not {expect_value}'
        except TypeError:
            raise
        return self

    def to_be_empty(self):
        """Value is empty  |''|[]|{}|()"""
        try:
            assert len(self._value) == 0, f'expect {self._value} to be empty'
        except TypeError:
            raise
        return self

    def to_contain(self, expect_value):
        """Value contains
        value = 'Hello, World'
        expect(value).to_contain('Hello')
        value = [1, 2, 3]
        expect(value).to_contain(1)
        """
        try:
            assert expect_value in self._value, f'expect {self._value} to contain {expect_value}'
        except TypeError:
            raise
        return self

    def to_not_contain(self, expect_value):
        """Value not contains
        value = 'Hello, World'
        expect(value).to_not_contain('hello')
        value = [1, 2, 3]
        expect(value).to_not_contain(4)
        """
        try:
            assert expect_value not in self._value, f'expect {self._value} to not contain {expect_value}'
        except TypeError:
            raise
        return self

    def to_have_length(self, expect_value):
        """Array or string has length
           ex: expect('Hello, World').toHaveLength(12)
           expect([1, 2, 3]).toHaveLength(3)
        """
        try:
            assert len(self._value) == expect_value, f'expect {self._value} to have length {expect_value}'
        except TypeError:
            raise
        return self

    def to_have_property(self, expect_key: str, expect_value: typing.Any = None):
        """dict has a property  or list contain dict has a property
            ex:
            value = {a: {b: [42]}, c: True}
            expect(value).to_have_property('a.b')
            expect(value).to_have_property('a.b', [42])
            expect(value).to_have_property('a.b[0]', 42)
            expect(value).to_have_property('c')
            expect(value).toHaveProperty('c', true)
            value = [{a: 1}, {a: 2}]
            expect(value).to_have_property('[0].a', 1)
        """
        try:
            keys = expect_key.split('.')
            expression = 'self._value'
            for key in keys:
                if key.startswith('['):
                    expression += f'{key}'
                else:
                    key_ = key.split('[', 1)[0]
                    try:
                        key_list = key.split('[', 1)[1]
                        expression += f'.get("{key_}")[{key_list}'
                    except IndexError:
                        expression += f'.get("{key_}")'
            if expect_value is None:
                assert eval(expression,
                            {'self': self}) is not None, f'expect {self._value} to have property {expect_key}'
            else:
                assert eval(expression, {'self': self}) is expect_value, \
                    f'expect {self._value} to have property {expect_key} is {expect_value}'
        except TypeError:
            raise
        return self

    def to_match(self, expect_value: str or typing.Pattern):
        """string value matches a regular expression
           ex:
           expect('Hello, World').to_match(r'Hello')
           expect('Hello, World').to_match(re.compile(r'^Hello.*'))
        """
        import re
        try:
            assert re.match(expect_value, self._value), f'expect {self._value} to match {expect_value}'
        except TypeError:
            raise
        return self

    def to_dict_contain(self, expect_value: dict):
        """dict value is in a dict
           ex:
            value = {a: 1, b: 2, c: True,}
            expect(value).to_dict_contain({a: 1, b: 2})
        """
        try:
            dict_in(self._value, expect_value)
        except TypeError:
            raise
        return self

    def to_throw(self, expect_value=Exception, message: str = None):
        """function throws an exception
           ex:
           def add(a, b):
               assert a + b != a + b
           expect(add, args=(1, 2)).to_throw(AssertionError)
        """
        try:
            self._value(self._args, self._kwargs)
        except expect_value as e:
            if message is not None:
                assert message in str(e), f'expect {self._value} to throw {expect_value} with message {message}'
        return self

    def to_be_instance_of(self, expect_value):
        """Value is instance of
            ex:
            value = [1, 2, 3]
            expect(value).to_be_instance_of(list)
        """
        try:
            assert isinstance(self._value, expect_value), f'expect {self._value} to be instance of {expect_value}'
        except TypeError:
            raise
        return self


class raises:

    def __init__(self, expected_exception, match=None):
        if not issubclass(expected_exception, BaseException):
            raise TypeError(f"expected_exception must be classes, not {expected_exception.__name__}")
        if not isinstance(match, (str, typing.Pattern, type(None))):
            raise TypeError(f"match must be str or typing.Pattern")
        self.expected_exception = expected_exception
        self.match = match

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type is not None:
            if not issubclass(exc_type, self.expected_exception):
                return False
            if self.match is not None:
                if isinstance(self.match, str):
                    if self.match not in str(exc_value):
                        return False
                else:
                    if not self.match.search(str(exc_value)):
                        return False
            # 返回True表示异常已被处理，否则异常将继续传播
            return True
        else:
            raise Exception(f"DID NOT RAISE {self.expected_exception.__name__}")


if __name__ == '__main__':
    import re
    with raises(AssertionError):
        x = {"a": 1, "b": 2}
        expect(x).to_eq({"a": 1, "b": 2, "c": 3})

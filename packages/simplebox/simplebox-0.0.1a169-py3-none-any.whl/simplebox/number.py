#!/usr/bin/env python
# -*- coding:utf-8 -*-

from decimal import Decimal, ROUND_HALF_UP
from functools import reduce
from math import factorial
from typing import Iterator

from ._handler._number_handler._compare import _Compare, _T
from .collection.arraylist import ArrayList
from .exceptions import raise_exception


def _check_number(number):
    def is_number(num):
        # noinspection PyBroadException
        try:
            tmp = eval(num)
            return tmp
        except BaseException:
            return False

    if isinstance(number, (int, float)):
        return number
    else:
        n = is_number(number)
        if n is False:
            raise ValueError(f"Excepted a number, got a '{number}'")
        else:
            return n


def _add(x, y):
    x_ = _check_number(x)
    y_ = _check_number(y)
    return x_ + y_


def _sub(x, y):
    x_ = _check_number(x)
    y_ = _check_number(y)
    return x_ - y_


def _mul(x, y):
    x_ = _check_number(x)
    y_ = _check_number(y)
    return x_ * y_


def _div(x, y):
    x_ = _check_number(x)
    y_ = _check_number(y)
    if y_ == 0:
        raise ValueError(f"The divisor cannot be 0, but got '{y_}'")
    return x_ / y_


class Float(float, _Compare):
    """
    A subclass of float.
    Some tool methods are provided
    """

    def __new__(cls, num: _T = 0):
        if issubclass(type(num), str) and not num.isdigit():
            raise_exception(ValueError(f"The string '{num}' is not a valid number"))
        return float.__new__(cls, num)

    def __init__(self, num: _T = 0):
        self.__num = num

    def round(self, accuracy: int = None) -> 'Float':
        """
        Rounds floating-point types
        """
        if isinstance(accuracy, int) and accuracy >= 0:
            return Float(
                Decimal(self.__num).quantize(Decimal(f'0.{"0" * accuracy}'), rounding=ROUND_HALF_UP).__float__())
        return self

    def integer(self) -> 'Integer':
        """
        Output as Integer type
        """
        return Integer(self.__num)

    def add(self, *numbers) -> 'Float':
        """
        Accumulates the numbers in the current instance and numbers
        :param numbers: The number that is accumulated
        :return:
        """
        tmp = [self]
        tmp.extend(numbers)
        return Float(reduce(_add, tmp))

    def sub(self, *numbers) -> 'Float':
        """
        Decrements the current number and numbers
        :param numbers: The number that is decremented
        :return:
        """
        tmp = [self]
        tmp.extend(numbers)
        return Float(reduce(_sub, tmp))

    def mul(self, *numbers) -> 'Float':
        """
        Multiplies the numbers in the current number and numbers
        :param numbers: The number to be multiplied
        :return:
        """
        tmp = [self]
        tmp.extend(numbers)
        return Float(reduce(_mul, tmp))

    def div(self, *numbers) -> 'Float':
        """
        Divides the current number by the number in numbers
        :param numbers: The number to be accumulated
        :return:
        """

        tmp = [self]
        tmp.extend(numbers)
        return Float(reduce(_div, tmp))

    def factorial(self) -> 'Integer':
        """
        factorial function, cast to int type is calculated in calculation.
        :return:
        """
        return Integer(factorial(int(self)))

    def fibonacci(self) -> ArrayList['Float']:
        """
        Generate a Fibonacci sequence
        """

        def _fibonacci() -> Iterator[Float]:
            n = self
            a, b = 0, 1
            while n > 0:
                a, b = b, a + b
                n -= 1
                yield Float(a)

        return ArrayList.of_item(_fibonacci())


class Integer(int, _Compare):
    """
    A subclass of int.
    Some tool methods are provided
    """

    def __new__(cls, num: _T = 0, base=10):
        if base not in [2, 8, 10, 16]:
            raise_exception(ValueError(f"base error: {base}"))
        if base != 10:
            return int.__new__(cls, num, base=base)
        if issubclass(type(num), str) and not num.isdigit():
            raise_exception(ValueError(f"The string '{num}' is not a valid number"))
        return int.__new__(cls, num)

    def __init__(self, num: _T = 0, base=10):
        self.__num = num
        self.__base = base

    def float(self) -> Float:
        """
        Output as Float type
        """
        return Float(self)

    def is_odd(self) -> bool:
        """
        The check is an odd number
        """
        return not self.is_even()

    def is_even(self) -> bool:
        """
        The check is an even number
        """
        return self & 1 == 0

    def to_bin(self) -> str:
        """
        Convert to binary (string)
        """
        return bin(self)

    def to_oct(self) -> str:
        """
        Convert to octal (string)
        """
        return oct(self)

    def to_hex(self) -> str:
        """
        Convert to hexadecimal (string)
        """
        return hex(self)

    def add(self, *numbers) -> Float:
        """
        Accumulates the numbers in the current instance and numbers
        :param numbers: The number that is accumulated
        :return:
        """
        tmp = [self]
        tmp.extend(numbers)
        return Float(reduce(_add, tmp))

    def sub(self, *numbers) -> Float:
        """
        Decrements the current number and numbers
        :param numbers: The number that is decremented
        :return:
        """
        tmp = [self]
        tmp.extend(numbers)
        return Float(reduce(_sub, tmp))

    def mul(self, *numbers) -> Float:
        """
        Multiplies the numbers in the current number and numbers
        :param numbers: The number to be multiplied
        :return:
        """
        tmp = [self]
        tmp.extend(numbers)
        return Float(reduce(_mul, tmp))

    def div(self, *numbers) -> Float:
        """
        Divides the current number by the number in numbers
        :param numbers: The number to be accumulated
        :return:
        """

        tmp = [self]
        tmp.extend(numbers)
        return Float(reduce(_div, tmp))

    def factorial(self) -> 'Integer':
        """
        factorial function
        :return:
        """
        return Integer(factorial(self))

    def fibonacci(self) -> ArrayList['Integer']:
        """
        Generate a Fibonacci sequence
        """

        def _fibonacci() -> Iterator[Integer]:
            n = self
            a, b = 0, 1
            while n > 0:
                a, b = b, a + b
                n -= 1
                yield Integer(a)

        return ArrayList.of_item(_fibonacci())

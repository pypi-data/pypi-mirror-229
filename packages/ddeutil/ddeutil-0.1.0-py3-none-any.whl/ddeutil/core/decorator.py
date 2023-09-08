import contextlib
import copy
from functools import wraps
from time import time


def deepcopy(func):
    """Deep copy method

    .. usage::
        >>> @deepcopy
        ... def foo(a, b, c=None):
        ...     c = c or {}
        ...     a[1] = 3
        ...     b[2] = 4
        ...     c[3] = 5
        ...     return a, b, c
        >>> aa = {1: 2}
        >>> bb = {2: 3}
        >>> cc = {3: 4}
        >>> foo(aa, bb, cc)
        ({1: 3}, {2: 4}, {3: 5})

        >>> (aa, bb, cc)
        ({1: 2}, {2: 3}, {3: 4})

    """

    def func_get(*args, **kwargs):
        return func(
            *(copy.deepcopy(x) for x in args),
            **{k: copy.deepcopy(v) for k, v in kwargs.items()},
        )

    return func_get


def deepcopy_args(func):
    """Deep copy method

    .. usage::
        >>> class Foo:
        ...
        ...     @deepcopy_args
        ...     def foo(self, a, b=None):
        ...         b = b or {}
        ...         a[1] = 4
        ...         b[2] = 5
        ...         return a, b
        >>>
        >>> aa = {1: 2}
        >>> bb = {2: 3}
        >>> Foo().foo(aa, bb)
        ({1: 4}, {2: 5})

        >>> (aa, bb)
        ({1: 2}, {2: 3})

    """

    def func_get(self, *args, **kwargs):
        return func(
            self,
            *(copy.deepcopy(x) for x in args),
            **{k: copy.deepcopy(v) for k, v in kwargs.items()},
        )

    return func_get


class classproperty:
    """Decorator that converts a method with a single cls argument
    into a property that can be accessed directly from the class.

    .. usage::

        >>> class Car:
        ...     wheel: int = 4
        ...     @classproperty
        ...     def foo(cls):
        ...         return "Foo" + str(cls.wheel)
        >>> Car.foo
        'Foo4'
    """

    def __init__(self, cls=None):
        self.fget = cls

    def __get__(self, instance, cls=None):
        return self.fget(cls)

    def getter(self, method):
        self.fget = method
        return self


class ClassPropertyDescriptor:
    def __init__(self, fget, fset=None):
        self.fget = fget
        self.fset = fset

    def __get__(self, obj, klass=None):
        if klass is None:
            klass = type(obj)
        return self.fget.__get__(obj, klass)()

    def __set__(self, obj, value):
        if not self.fset:
            raise AttributeError("can't set attribute")
        type_ = type(obj)
        return self.fset.__get__(obj, type_)(value)

    def setter(self, func):
        if not isinstance(func, (classmethod, staticmethod)):
            func = classmethod(func)
        self.fset = func
        return self


def class_property(func):
    """
    .. usage::

        >>> class Car:
        ...     wheel: int = 4
        ...     @class_property
        ...     def foo(cls):
        ...         return "Foo" + str(cls.wheel)
        >>> Car.foo
        'Foo4'
    """
    if not isinstance(func, (classmethod, staticmethod)):
        func = classmethod(func)
    return ClassPropertyDescriptor(func)


def timing(name):
    """
    .. usage::
        >>> import time
        >>> @timing("Sleep")
        ... def will_sleep():
        ...     time.sleep(2)
        ...     return
        >>> will_sleep()
        Sleep ....................................................... 2.01s
    """

    def timing_internal(func):
        @wraps(func)
        def wrap(*args, **kw):
            ts = time()
            result = func(*args, **kw)
            te = time()
            padded_name = f"{name} ".ljust(60, ".")
            padded_time = f" {(te - ts):0.2f}".rjust(6, ".")
            print(f"{padded_name}{padded_time}s", flush=True)
            return result

        return wrap

    return timing_internal


@contextlib.contextmanager
def timer_perf(title):
    """
    :usage:
        >>> import time
        >>> with timer_perf('Sleep'):
        ...     time.sleep(2)
        Sleep ....................................................... 2.00s
    """
    ts = time()
    yield
    te = time()
    padded_name = f"{title} ".ljust(60, ".")
    padded_time = f" {(te - ts):0.2f}".rjust(6, ".")
    print(f"{padded_name}{padded_time}s", flush=True)

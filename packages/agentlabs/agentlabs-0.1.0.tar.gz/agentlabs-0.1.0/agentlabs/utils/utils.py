import inspect


def internal_use(func):
    def wrapper(self, *args, **kwargs):
        caller_frame = inspect.currentframe().f_back
        caller_method = caller_frame.f_code.co_name
        if caller_method.startswith("__") and caller_method.endswith("__"):
            raise TypeError("The method is for internal use only!")
        return func(self, *args, **kwargs)

    return wrapper

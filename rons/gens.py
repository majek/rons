import functools

KEY = '_rons_generator'

def save_generator(fun):
    @functools.wraps(fun)
    def wrapper(self, *args, **kwargs):
        assert not hasattr(self, KEY), "Tornado runs one handler per instance, right?"
        gen = fun(self, *args, **kwargs)
        setattr(self, KEY, gen)
        return gen
    return wrapper

def stop_generator(self):
    if hasattr(self, KEY):
        getattr(self, KEY).close()

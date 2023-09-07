class SingletonMeta(type):
    _instances = {}

    def __getattr__(cls, name):
        if cls not in cls._instances:
            cls._instances[cls] = super(SingletonMeta, cls).__call__()
        return getattr(cls._instances[cls], name)


class BaseSingleton(metaclass=SingletonMeta):
    pass

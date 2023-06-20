class SingletonMetaClass(type):
    """
    Singleton metaclass: only one instance of the class can be created.
    """

    _instances: dict = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]

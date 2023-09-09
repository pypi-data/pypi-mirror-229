

class ServiceManager:
    def __init__(self):
        self.__managed__ = {}

    def manage(self, cls):
        cls.__new__ = self.__manage_new__(cls.__new__)
        cls.__init__ = self.__manage_init__(cls.__init__)
        return cls

    def __manage_new__(self, __new__):
        def __managed__new__(cls, gam_id, *args, **kwds):
            if gam_id not in self.__managed__:
                self.__managed__[gam_id] = {"instance": __new__(cls)}
            return self.__managed__[gam_id]["instance"]
        return __managed__new__

    def __manage_init__(self, __init__):
        def __managed__init__(instance, gam_id, *args, **kwds):
            if not self.__managed__[gam_id].get("init", False):
                __init__(instance, gam_id, *args, **kwds)
                self.__managed__[gam_id]["init"] = True
        return __managed__init__

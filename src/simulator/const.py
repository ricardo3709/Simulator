class _const:
    """常量数据类"""
    class ConstError(TypeError):
        """修改常量抛出此错误"""
        pass

    __PROPERTY_PATH = './translator.properties'

    def __setattr__(self, name, value):
        if name in self.__dict__:
            raise self.ConstError("Can't rebind const instance attribute ({})".format(name))

        self.__dict__[name] = value

import sys
sys.modules[__name__] = _const()
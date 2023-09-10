import logging
from types import ModuleType
from typing import Optional
from importlib import import_module


class LazyLoader(ModuleType):
    """模块延迟加载"""

    def __init__(
        self,
        local_name: str,
        parent_module_globals: dict,
        name: Optional[str] = None,
        warning: Optional[str] = None
    ):
        """模块延迟加载

        :param local_name: 模块引用名称
        :param parent_module_globals: 全局变量
        :param name: 导入模块名称
        :param warning: 警告信息
        """
        if not isinstance(local_name, str):
            raise TypeError(f"'local_name' type must be a str, got: {type(local_name)}")

        if not isinstance(name, str):
            if name is None:
                name = local_name
            else:
                raise TypeError(f"'name' type must be a str, got: {type(name)}")

        self._local_name = local_name
        self._parent_module_globals = parent_module_globals
        self._warning = warning
        super().__init__(name)

    def _load(self):
        """加载模块并将其插入父模块的全局变量中"""
        # 导入模块
        module = import_module(self.__name__)
        self._parent_module_globals[self._local_name] = module

        # 如果指定了警告，则发出警告
        if self._warning:
            logging.warning(self._warning)
            # 确保只警告一次
            self._warning = None

        # 将模块的方法和变量注册到当前对象下
        self.__dict__.update(module.__dict__)
        return module

    def __getattr__(self, item):
        module = self._load()
        return getattr(module, item)

    def __dir__(self):
        module = self._load()
        return dir(module)

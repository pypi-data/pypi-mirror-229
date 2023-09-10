from typing import (
    IO,
    Any,
    Union,
    Optional,
    Callable,
    Generator,
    Dict,
    List,
    Iterable,
    AsyncGenerator
)
from pathlib import Path as _Path

from pyxk.lazy_loader import LazyLoader
from pyxk.utils.typedef import MD5, Time, Units, Number, Rename

_re = LazyLoader("_re", globals(), "re")
_io = LazyLoader("_io", globals(), "io")
_time = LazyLoader("_time", globals(), "time")
_copy = LazyLoader("_copy", globals(), "copy")
_difflib = LazyLoader("_difflib", globals(), "difflib")
_hashlib = LazyLoader("_hashlib", globals(), "hashlib")
_aiofiles = LazyLoader("_aiofiles", globals(), "aiofiles")
_functools = LazyLoader("_functools", globals(), "functools")
_itertools = LazyLoader("_itertools", globals(), "itertools")


__all__ = [
    "md5",
    "path",
    "time_format",
    "number",
    "mdopen",
    "rename",
    "convert_units",
    "convert_str_to_number",
    "convert_lazy_loader",
    "convert_lazy_loader_with_file",
    "open_generator",
    "open_async_generator",
    "human_time",
    "rtime",
    "rtime_of_coro",
    "allowed",
    "fuzzy_match",
]


def allowed(
    allowable: dict,
    callback: Optional[Callable[[str, Any], None]] = None,
    raise_exception: bool = True,
    **kwargs: Dict[str, Any]
) -> Dict[str, bool]:
    """检测允许的数据类型, 其他类型抛出

    :param allowable: 变量类型判断的依据
        {"name": str, "age": (int, float)}
    :param callback: 对每项数据进行回调
        def callback(key, value, allowable, **cb_kwargs):
            ...
    :param raise_exception: 是否抛出异常, 若为False则返回bool值

    explain:

        allowed(
            allowable={"name": str, "age": (int, float)},
            name="xxx", age="18"
        )

        >>> TypeError: 'age' type must ba a 'int' or 'float', got: <class 'str'>
    """
    if not kwargs or not allowable:
        return

    if not isinstance(allowable, dict):
        raise TypeError(f"'allowable' type must be a dict. got: {type(allowable)}")

    # prompt: 字典中的键必须是字符
    if not all(isinstance(x, str) for x in allowable):
        raise ValueError("'allowable' key-words type must be a str.")

    # prompt: 字典中的值必须是元组
    for key, value in allowable.items():
        # type(value) is type
        if isinstance(value, type):
            allowable[key] = (value, )
        # type(value) is list
        elif isinstance(value, list):
            allowable[key] = tuple(value)
        # type(value) is not tuple
        elif not isinstance(value, tuple):
            raise ValueError(f"'allowable' dictionary-value type must be a tuple. got: {type(value)}")
        # 判断元组数据是否为 type
        for item in allowable[key]:
            if not isinstance(item, type):
                raise ValueError(f"'allowable' dictionary-value(tuple) each value type must be a class. got: {type(item)}")

    # 判断数据类型
    allowed_result = {}
    for key, value in kwargs.items():
        # 键是否存在
        if key not in allowable:
            expected_key = tuple(allowable)
            raise ValueError(f"key:{key!r} is not in the {expected_key}")

        # 类型是否合法
        if not isinstance(value, allowable[key]):
            if raise_exception:
                expected_type = ' or '.join(f"{x.__name__!r}" for x in allowable[key])
                raise ValueError(f"{key!r} type must be a {expected_type}. got: {type(value)}")
            allowed_result[key] = False
            continue

        # 回调
        if callable(callback):
            callback(key, value)
        allowed_result[key] = True
    return allowed_result


def fuzzy_match(
    word: str,
    possibilities: Iterable,
    n: int = 3,
    cutoff: float = 0.6,
    default: Optional[str] = None,
) -> List[str]:
    """返回最佳匹配列表(模糊匹配)

    :param word: 需要接近匹配的序列
    :param possibilities: 要匹配单词的序列列表(通常是字符串列表)
    :param n: 接近匹配的最大匹配次数. n必须大于0(默认为3)
    :param cutoff: 得分至少不那么接近的词会被忽略. cutoff是[0,1]中的浮点数(默认0.6)
    :param default: 如果匹配为空返回default(必须为字符串)
    :return: List[str]
    """
    from collections.abc import Iterable as _Iterable

    allowed(
        dict(
            word=(_Iterable,),
            possibilities=(_Iterable,),
            n=(int,),
            cutoff=(float,),
            default=(str, type(None))
        ),
        word=word,
        possibilities=possibilities,
        n=n,
        cutoff=cutoff,
        default=default
    )
    result = _difflib.get_close_matches(word, possibilities, n, cutoff)

    # default
    if (
        not result
        and default is not None
    ):
        result.append(default)
    return result


def convert_str_to_number(target: Union[str, int, float], default: Any = None) -> Number:
    """字符串转换数字

    :param target: 转换目标
    :param default: 不是数字则返回默认值
    :return: namedtuple
    """
    # 本身即是数字，直接返回
    if isinstance(target, (int, float)):
        return Number(target, target, True)
    # 格式有误，返回默认值
    if not isinstance(target, str):
        return Number(default, target, False)
    # 正则表达式匹配数字
    pattern = _re.compile(
        r"""^\s*[-+]?            # 符号位置
            (\d+(\.\d*)?|\.\d+)  # 整数和小数部分
            ([eE][-+]?\d+)?\s*$  # 科学计数法部分""",
        _re.X
    )
    ret = pattern.match(target)

    # 不能转化数字，返回默认值
    if not ret:
        return Number(default, target, False)
    # float
    if (
        ret.group().find(".") != -1
        or ret.group().find("e") != -1
        or ret.group().find("E") != -1
    ):
        return Number(float(target), target, True)
    # int
    return Number(int(target), target, True)


number = convert_str_to_number


def _mdopen(func: Callable):
    """io.open装饰器 写入模式下自动创建文件夹"""

    @_functools.wraps(func)
    def wrapper(
        file: str,
        mode: str = "r",
        buffering: int = -1,
        encoding: Optional[str] = None,
        **kwargs,
    ) -> IO[Any]:
        # mode数据格式
        if not isinstance(file, (str, _Path)):
            raise TypeError(f"{func.__name__}() argument the 'file' type must be str, got: {type(file)}")

        if not isinstance(mode, str):
            raise TypeError(f"{func.__name__}() argument the 'mode' type must be str, got: {type(mode)}")

        # 创建文件夹
        _all_mode = [i+j for j in ["b", "b+", "", "+"] for i in ["w", "a"]]
        if mode in _all_mode:
            _Path(file).parent.mkdir(parents=True, exist_ok=True)
        # 二进制模式下 encoding=None
        if "b" in mode:
            encoding = None

        return func(file, mode, buffering, encoding, **kwargs)
    return wrapper


mdopen = _mdopen(_io.open)


def rtime(func: Callable):
    """装饰器: 计算函数运行时间"""

    @_functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = _time.perf_counter()
        try:
            result = func(*args, **kwargs)
        finally:
            end_time = _time.perf_counter()
            print(f"{func.__name__!r} running time: {end_time-start_time}")
        return result
    return wrapper


def rtime_of_coro(func: Callable):
    """装饰器: 计算异步函数运行时间"""

    @_functools.wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = _time.perf_counter()
        try:
            result = await func(*args, **kwargs)
        finally:
            end_time = _time.perf_counter()
            print(f"{func.__name__!r} running time: {end_time-start_time}")
        return result
    return wrapper


def time_format(second: Union[str, int]) -> Time:
    """返回时间格式(hour. minute. second. positive)

    :param second: 时间(秒)
    :return: Time(hour, minute, second, positive)
    """
    ret = convert_str_to_number(second)
    # 不是数字
    if not ret.is_number:
        return Time(0, 0, 0, None)

    second = round(ret.number)
    # 记录正负数
    positive = second >= 0

    hour, second = divmod(abs(second), 3600)
    minute, second = divmod(second, 60)

    return Time(hour, minute, second, positive)


def human_time(second: Union[str, int], default: Any = None) -> Union[str, Any]:
    """人类直观时间展示

    :param second: 时间(秒)
    :param default: 无效时间则返回默认值
    :return: str
    """
    ret = time_format(second)
    # 无效时间
    if ret.positive is None:
        return default
    return f"{'' if ret.positive else '-'}{ret.hour}:{ret.minute:0>2}:{ret.second:0>2}"


def path(*_path, strict: bool = False, exits_name: bool = False) -> _Path:
    """获取一个 pathlib.Path

    :param *_path: path
    :param strict: 严格的(路径不存在会抛出)
    :param exits_name: 是否存在 base_name
    """
    # 没有path传入，返回当前工作目录
    if not _path:
        return _Path.cwd()
    # 格式检测
    if not all(isinstance(x, (str, _Path)) for x in _path):
        raise TypeError(
            "'_path' type must be a str or pathlib.Path. "
            f"got: {set(type(x) for x in _path)}"
        )
    # 获取绝对路径
    parse_path = _Path(*_path).resolve(strict=strict)
    # 是否存在name
    if exits_name and not parse_path.name:
        raise ValueError(f"{parse_path.as_posix()!r} has an empty name")
    return parse_path


def rename(
    *_path,
    is_dir: bool = False,
    suffix: Optional[str] = None,
    create: bool = False,
) -> Rename:
    """重命名 文件 or 目录 路径

    :param *_path: 文件 or 目录路径
    :param is_dir: 是否是目录(default: False)
    :param suffix: 文件后缀名
    :param create: 是否创建 文件 or 目录
    :return: namedtuple
    """
    parse_path = path(*_path, exits_name=True)
    allowed(
        allowable=dict(
            is_dir=(bool,), suffix=(str, type(None)), create=(bool,)
        ),
        is_dir=is_dir, suffix=suffix, create=create
    )

    # 解析suffix
    if not suffix:
         suffix = parse_path.suffix
    else:
         suffix = "." + suffix.strip().strip(".").strip()
         if suffix != parse_path.suffix:
             suffix = parse_path.suffix + suffix
    # 完整路径
    parse_path = parse_path.with_suffix(suffix)

    # 创建和返回path
    def create_path(rename_path: _Path):
        """创建path 和 返回数据"""
        if create:
            if is_dir:
                rename_path.mkdir(parents=True, exist_ok=True)
            else:
                rename_path.touch()
        return Rename(rename_path, rename_path.parent, rename_path.name)

    # 文件或目录不存在 直接返回
    if not parse_path.exists():
        return create_path(parse_path)

    # 重命名已经存在的文件或文件夹
    for index in _itertools.count(1):
        if is_dir:
            temp = parse_path.with_name(f"{parse_path.name}({index})")
        else:
            temp = parse_path.with_stem(f"{parse_path.stem}({index})")
        # 退出循环条件
        if not temp.exists():
            parse_path = temp
            break
    return create_path(parse_path)


def open_generator(
    file: str,
    mode: str = "r",
    encoding: Optional[str] = None,
    *,
    chunk_size: int = 1024,
    **kwargs
) -> Generator:
    """基于生成器的文件读取

    :param file: file path
    :param mode: file open mode
    :param encoding: encoding
    :param chunk_size: chunk size
    :return: Generator
    """
    if not isinstance(file, (str, _Path)):
        raise TypeError(f"'file' type must be a str or pathlib.Path, got: {type(file)}")

    if not isinstance(mode, str):
        raise TypeError(f"'mode' type must be a str, got: {type(mode)}")

    # 已二进制模式打开文件 encoding=None
    if mode.find("b") != -1:
        encoding = None

    with open(file=file, mode=mode, encoding=encoding, **kwargs) as read_file_obj:
        while True:
            chunk = read_file_obj.read(chunk_size)
            if not chunk:
                return
            yield chunk


async def open_async_generator(
    file: str,
    mode: str = "r",
    encoding: Optional[str] = None,
    *,
    chunk_size: int = 1024,
    **kwargs
) -> AsyncGenerator:
    """基于异步生成器的文件读取 note: 不知道为什么还没有同步(open)速度快

    :param file: file path
    :param mode: file open mode
    :param encoding: encoding
    :param chunk_size: chunk size
    :return: AsyncGenerator
    """
    if not isinstance(file, (str, _Path)):
        raise TypeError(f"'file' type must be a str or pathlib.Path, got: {type(file)}")

    if not isinstance(mode, str):
        raise TypeError(f"'mode' type must be a str, got: {type(mode)}")

    async with _aiofiles.open(file, mode, encoding=encoding, **kwargs) as read_file_obj:
        while True:
            chunk = await read_file_obj.read(chunk_size)
            if not chunk:
                return
            yield chunk


def md5(byte_str: Union[str, bytes, bytearray]) -> MD5:
    """MD5加密"""
    # str
    if isinstance(byte_str, str):
        byte_str = bytearray(byte_str.encode())
    # bytes
    elif isinstance(byte_str, bytes):
        byte_str = bytearray(byte_str)
    # != bytearray
    elif not isinstance(byte_str, bytearray):
        raise TypeError(f"'byte_str' type must be a str or bytes or bytearray, got: {type(byte_str)}")

    return MD5(byte_str, _hashlib.md5(byte_str).hexdigest())


def convert_lazy_loader(pycode: str) -> str:
    """转换为懒加载模块"""
    if not isinstance(pycode, str):
        raise TypeError(f"'pycode' type must be a str, got: {type(pycode)}")

    pattern = _re.compile(
        r"""^(import                      # import
            |from\s+(?P<from>[\w.]+)      # from 'module' import
            \s+import)
            \s+((?P<import>[\w.]+))       # import 'module'
            (\s+as\s+(?P<alias>\w+))?     # as 'alias'
            \s*$""",
        _re.X|_re.M
    )

    def repl(match):
        _from, _import, _alias = match.groupdict()["from"], match.groupdict()["import"], match.groupdict()["alias"]
        if _import == "LazyLoader":
            return match.group()
        name = _alias if _alias else _import.replace(".", "_")
        loader = f"{_from}.{_import}" if _from else _import
        return f'{name} = LazyLoader("{name}", globals(), "{loader}")'

    return pattern.sub(repl, pycode)


def convert_lazy_loader_with_file(file: str, encoding: str = "utf-8") -> None:
    """转换懒加载到文件"""
    file = path(file, strict=True, exits_name=True)
    pycode = file.read_text(encoding=encoding)
    file.write_text(
        data=convert_lazy_loader(pycode), encoding=encoding
    )


def convert_units(target: Union[str, int, float]) -> Units:
    """字节单位自动换算"""
    num = convert_str_to_number(target)

    if not num.is_number:
        return Units(None, target, None, None)

    num, current_units = abs(num.number), "Bytes"
    units_dict = {
        "KB": 1024, "MB": 1024, "GB": 1024,
        "TB": 1024, "PB": 1024, "EB": 1024,
        "ZB": 1024, "YB": 1024, "BB": 1024,
    }

    for units, rate in units_dict.items():
        if num >= rate:
            num, current_units = num / rate, units
            continue
        break
    num = round(num, 2)
    return Units(num, target, current_units, f"{num}{current_units}")

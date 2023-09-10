"""随机获取UserAgent

from pyxk import get_headers, get_user_agent, UserAgnets

ua = UserAgnets()

user_agent = ua.user_agent(os="android", use_faker=True)
user_agent = get_user_agent()

>>>
    Mozilla/5.0 (Linux; Android 5.1.1) AppleWebKit/531.0 (KHTML,like Gecko) Chrome/16.0.888.0 Safari/531.0
"""
from typing import Any, List, Optional, Dict

from pyxk.lazy_loader import LazyLoader
from pyxk.utils.main import allowed, fuzzy_match
from pyxk.utils.typedef import UserAgentNamedTuple

faker = LazyLoader("faker", globals(), "faker")
random = LazyLoader("random", globals(), "random")
multidict = LazyLoader("multidict", globals(), "multidict")
_user_agents = LazyLoader("_user_agents", globals(), "user_agents")


__all__ = ["user_agents", "UserAgnets", "get_headers", "get_user_agent"]

user_agents = UserAgentNamedTuple(
    ios="Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1",
    mac="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36",
    linux="Mozilla/5.0 (X11; Linux i686; rv:1.9.5.20) Gecko/6619-04-25 11:19:32 Firefox/3.8",
    android="Mozilla/5.0 (Linux; Android 8.1.0; 16th Build/OPM1.171019.026) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.110 Mobile Safari/537.36",
    windows="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36"
)


class UserAgnets:
    """随机获取UserAgent

    from pyxk import get_headers, get_user_agent, UserAgnets

    ua = UserAgnets()

    user_agent = ua.user_agent(os="android", use_faker=True)
    user_agent = get_user_agent()

    >>>
        Mozilla/5.0 (Linux; Android 5.1.1) AppleWebKit/531.0 (KHTML,like Gecko) Chrome/16.0.888.0 Safari/531.0
    """
    def __init__(self):
        self._faker = None
        self._all_user_agents = {k: [v] for k, v in user_agents._asdict().items()}

    def user_agent(self, os: Optional[str] = None, use_faker: bool = False) -> str:
        """获取随机UserAgent

        :param os: 指定UserAgent操作系统
        :param use_faker: 是否使用模块faker
        :return: str
        """
        self._allowed(os=os, use_faker=use_faker)

        # 获取 operating system
        os = os.lower() if os else random.choice(self.operating_system)
        if os not in self.operating_system:
            os = fuzzy_match(os.lower(), self.operating_system, 1, 0.5, "android")[0]

        # user_agent
        if not use_faker:
            return random.choice(self.all_user_agents[os])

        user_agent = self._use_faker(os)
        self._all_user_agents[os].append(user_agent)
        return user_agent

    def user_agent_of_ios(self, use_faker: bool = False) -> str:
        """基于 ios 系统的 user_agent"""
        return self.user_agent(os="ios", use_faker=use_faker)

    def user_agent_of_mac(self, use_faker: bool = False) -> str:
        """基于 mac 系统的 user_agent"""
        return self.user_agent(os="mac", use_faker=use_faker)

    def user_agent_of_linux(self, use_faker: bool = False) -> str:
        """基于 linux 系统的 user_agent"""
        return self.user_agent(os="linux", use_faker=use_faker)

    def user_agent_of_android(self, use_faker: bool = False) -> str:
        """基于 android 系统的 user_agent"""
        return self.user_agent(os="android", use_faker=use_faker)

    def user_agent_of_windows(self, use_faker: bool = False) -> str:
        """基于 windows 系统的 user_agent"""
        return self.user_agent(os="windows", use_faker=use_faker)

    def _use_faker(self, os: Optional[str]) -> str:
        """使用faker获取UserAgent"""
        self._allowed(os=os)
        if os not in self.operating_system:
            raise ValueError(f"os not in {self.operating_system}. got: {os!r}")

        while True:
            user_agent = _user_agents.parse(self.faker.user_agent())
            get_os = fuzzy_match(
                user_agent.os.family.split(" ", 1)[0].lower(),
                self.operating_system,
                n=1,
                cutoff=0.5,
                default=""
            )[0]

            # 老子不喜欢 IE浏览器
            if user_agent.browser.family.lower() == "ie":
                continue

            # 获取指定操作系统的user_agent
            if not os:
                return user_agent.ua_string
            if os != get_os:
                continue
            return user_agent.ua_string

    @staticmethod
    def _allowed(**kwargs: Dict[str, Any]) -> None:
        """检测数据类型"""
        allowable = dict(
            os=(str, type(None)),
            use_faker=(bool,)
        )
        allowed(allowable, **kwargs)

    @property
    def faker(self):
        """faker.Faker"""
        if not self._faker:
            self._faker = faker.Factory.create()
        return self._faker

    @property
    def operating_system(self) -> str:
        """UserAgent的全部操作系统"""
        return tuple(self._all_user_agents.keys())

    @property
    def all_user_agents(self) -> Dict[str, List[str]]:
        """全部UserAgent"""
        return self._all_user_agents


def get_user_agent(os: Optional[str] = None, use_faker: bool = False) -> str:
    """随机获取一个指定操作系统的 User_Agent

    :param os: User_Agent 的操作系统类型
    :param use_faker: 是否使用 faker.Factory.create
    :return: str
    """
    user_agent = UserAgnets()
    return user_agent.user_agent(os, use_faker)


def get_headers(
    os: Optional[str] = "android",
    use_faker: bool = False,
    **kwargs: Dict[str, Any]
) -> Dict[str, Any]:
    """获取 Headers - UserAgent

    :param os: User_Agent 的操作系统类型
    :param use_faker: 是否使用 faker.Factory.create
    :return: dict
    """
    _headers = multidict.CIMultiDict(kwargs)
    _headers["User-Agent"] = get_user_agent(os, use_faker)
    return dict(_headers)

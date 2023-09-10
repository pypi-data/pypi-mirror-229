from pathlib import Path
from typing import  Optional, Union, NamedTuple, Dict, List

from rich.live import Live
from rich.table import Table
from rich.progress import Task, Progress


Store = Union[str, Path]
Output = Union[str, Path]
Content = Union[str, bytes]


class ParseResult(NamedTuple):
    url: Optional[str]
    keys: Dict[str, Dict[str, bytes]]
    segments: List[tuple]
    durations: float


class RichResult(NamedTuple):
    live: Live
    table: Table
    progress: Progress
    task: Task

from typing import Optional

from rich import progress
from rich.console import Console


__all__ = ["tasks_progress", "download_progress"]


def download_progress(
    transient: bool = False,
    console: Optional[Console] = None,
    text_column: Optional[str] = "[progress.description]{task.description}",
    task_progress_column: Optional[str] = "[progress.percentage]{task.percentage:>6.2f}%",
    show_transfer_speed: bool = True
) -> progress.Progress:
    """rich.progress.Progress - 下载进度条

    :param transient: 转瞬即逝
    :param console: rich.console.Console
    :param text_column: text column 文本格式 [progress.description]{task.description}
    :param task_progress_column: 任务进度格式 [progress.percentage]{task.percentage:>6.2f}%
    :param show_transfer_speed: 显示任务下载速度
    """
    columns = [
        progress.TextColumn(text_column),
        progress.TaskProgressColumn(task_progress_column),
        progress.BarColumn(),
        progress.DownloadColumn(),
        progress.TransferSpeedColumn(),
        progress.TimeElapsedColumn()
    ]
    # 不显示下载速度
    if not show_transfer_speed:
        columns.pop(-2)
    return progress.Progress(*columns, transient=transient, console=console)


def tasks_progress(
    transient: bool = False,
    console: Optional[Console] = None,
    text_column: Optional[str] = "[progress.description]{task.description}",
    task_progress_column: Optional[str] = "[progress.percentage]{task.percentage:>6.2f}%",
    task_progress_column_2: Optional[str] = "[cyan]{task.completed}/{task.total}[/]",
    show_transfer_speed: bool = False
) -> progress.Progress:
    """rich.progress.Progress - 任务进度条

    :param transient: 转瞬即逝
    :param console: rich.console.Console
    :param text_column: text column 文本格式 [progress.description]{task.description}
    :param task_progress_column: 任务进度格式 [progress.percentage]{task.percentage:>6.2f}%
    :param task_progress_column_2: 任务进度格式 [cyan]{task.completed}/{task.total}[/]
    :param show_transfer_speed: 显示任务下载速度
    """
    columns = [
        progress.TextColumn(text_column),
        progress.TaskProgressColumn(task_progress_column),
        progress.BarColumn(),
        progress.TaskProgressColumn(task_progress_column_2),
        progress.TimeElapsedColumn(),
    ]
    # 显示下载速度
    if show_transfer_speed:
        columns.insert(-1, progress.TransferSpeedColumn())
    return progress.Progress(*columns, transient=transient, console=console)

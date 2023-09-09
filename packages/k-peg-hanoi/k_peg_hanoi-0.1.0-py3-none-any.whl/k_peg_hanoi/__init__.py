from functools import lru_cache
from typing import Generator, List, Tuple

import fire


def main():
    fire.Fire(show_hanoi)


@lru_cache(maxsize=1024)
def nmove(m: int, n: int) -> float:
    """minimum number of moves

    :param m: number of disks
    :param n: number of rods
    :return: minimum number of moves
    """
    n = min(m + 1, n)
    if n == 2:
        return 1 if m == 1 else float("inf")
    elif n == 3:
        return 2**m - 1
    elif n == m + 1:
        return 2 * m - 1
    return min(nmove(i, n) * 2 + nmove(m - i, n - 1) for i in range(1, m))


def hanoi(m: int, pos: List[int]) -> Generator[Tuple[int, int], None, None]:
    """Moves of Tower of Hanoi

    :param m: number of disks
    :param n: number of rods
    :return: from, to
    """
    if m == 1:
        yield pos[0], pos[-1]
        return
    n = len(pos)
    assert n > 2, "Too few len(pos)"
    mn = min((nmove(i, n) * 2 + nmove(m - i, n - 1), i) for i in range(1, m))[1]
    yield from hanoi(mn, [pos[0]] + pos[2:] + [pos[1]])
    yield from hanoi(m - mn, [pos[0]] + pos[2:-1] + [pos[-1]])
    yield from hanoi(mn, pos[1:-1] + [pos[0], pos[-1]])


def _show(towers, count):
    height = max(len(tower) for tower in towers)
    width = max(max(tower, default=0) for tower in towers)
    for i in range(height - 1, -1, -1):
        for tower in towers:
            n = tower[i] if i < len(tower) else 0
            s = "=" * (n * 2 - 1)
            print(f"{s:^{width * 2 - 1}}", end=" ")
        print()
    print(f"{count:-<{width * 2 * len(towers) - 1}}\n")


def show_hanoi(m: int, n: int = 3, text: bool = False):
    """Show move of Tower of Hanoi

    :param m: number of disks
    :param n: number of rods, default 3
    :param text: show with text, default False
    """
    towers = [list(range(m, 0, -1))] + [[] for _ in range(n - 1)]
    if not text:
        _show(towers, 0)
    for i, (fr, to) in enumerate(hanoi(m, list(range(n))), 1):
        towers[to].append(towers[fr].pop())
        if text:
            print(f"#{i} disk {towers[to][-1]} from {fr} to {to}")
        else:
            _show(towers, i)

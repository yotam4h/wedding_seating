from __future__ import annotations

from typing import Any

import matplotlib.pyplot as plt

from .types import Tables


def plot_seating_chart(tables: Tables) -> None:
    ax: Any
    _fig: Any
    _fig, ax = plt.subplots()  # type: ignore[call-overload]
    for idx, table in enumerate(tables):
        x = list(range(len(table)))
        y = [idx] * len(table)
        names = [guest['name'] for guest in table]
        ax.scatter(x, y)
        for xi, yi, name in zip(x, y, names):
            ax.text(xi, yi, name, fontsize=10, ha='center', va='bottom')
    ax.set_yticks(range(len(tables)))
    ax.set_yticklabels([f'Table {i+1}' for i in range(len(tables))])
    ax.set_xlabel("Seats")
    ax.set_title("Wedding Seating Chart")
    plt.show()  # type: ignore[call-overload]

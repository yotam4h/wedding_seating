import pytest

from wedding_seating.visualization import plot_seating_chart


def test_plot_seating_chart_raises_runtime_error() -> None:
    with pytest.raises(RuntimeError, match="Visualization support has been removed"):
        plot_seating_chart([])

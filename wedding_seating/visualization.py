"""Visualization support was removed from the public API."""


def plot_seating_chart(*_: object, **__: object) -> None:  # pragma: no cover - shim
    """Legacy stub retained for backward compatibility.

    The function raises at runtime to surface the removal rather than failing at
    import time.
    """
    raise RuntimeError(
        "Visualization support has been removed from wedding_seating."
    )

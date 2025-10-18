"""Helper exports for the `scripts` package used by suite automation."""

try:  # pragma: no cover - convenience re-export for autorunners
    from .autofetch import AutoFetchConfig, autofetch  # noqa: F401
except ModuleNotFoundError:  # pragma: no cover
    AutoFetchConfig = None  # type: ignore[assignment]
    autofetch = None  # type: ignore[assignment]

__all__ = [
    "AutoFetchConfig",
    "autofetch",
]

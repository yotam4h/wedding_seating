import argparse
import sys
from typing import Iterable, Iterator, Optional

from .core import WeddingSeating
from .utils import import_guest_list_csv


def _positive_int(value: str) -> int:
    try:
        parsed = int(value)
    except ValueError as exc:  # pragma: no cover - argparse surfaces error
        raise argparse.ArgumentTypeError(f"Expected an integer, received '{value}'") from exc
    if parsed <= 0:
        raise argparse.ArgumentTypeError("Value must be greater than zero")
    return parsed


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="wedding-seating",
        description="Optimize a wedding seating chart from a CSV guest list.",
    )
    parser.add_argument(
        "guest_list",
        help="Path to the guest CSV file."
    )
    parser.add_argument(
        "--table-size",
        type=_positive_int,
        default=8,
        help="Maximum number of guests per table (default: 8).",
    )
    parser.add_argument(
        "--vip-tables",
        type=_positive_int,
        default=1,
        help="Number of tables reserved for VIP guests (default: 1).",
    )
    parser.add_argument(
        "--max-iter",
        type=_positive_int,
        default=100,
        help="Maximum iterations for local optimization swaps (default: 100).",
    )
    parser.add_argument(
        "--export-prefix",
        help="File prefix to export the seating chart (omit extension).",
    )
    parser.add_argument(
        "--export-format",
        action="append",
        choices=["csv", "pdf"],
        help=(
            "Export format to use when --export-prefix is supplied. Repeat the flag "
            "to write multiple formats (default: csv)."
        ),
    )
    parser.add_argument(
        "--visualize",
        action="store_true",
        help="Render the seating chart with matplotlib.",
    )
    parser.add_argument(
        "--no-print",
        action="store_true",
        help="Suppress printing table assignments to stdout.",
    )
    return parser


def _unique_ordered(values: Iterable[str]) -> Iterator[str]:
    seen: set[str] = set()
    for value in values:
        if value not in seen:
            seen.add(value)
            yield value


def main(argv: Optional[Iterable[str]] = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(list(argv) if argv is not None else None)

    try:
        guest_list = import_guest_list_csv(args.guest_list)
    except FileNotFoundError:
        print(f"Error: guest list not found at '{args.guest_list}'.", file=sys.stderr)
        return 1
    except Exception as exc:  # pragma: no cover - defensive, reported to user
        print(f"Error reading guest list: {exc}", file=sys.stderr)
        return 1

    if not guest_list:
        print("Error: guest list CSV did not contain any guests.", file=sys.stderr)
        return 1

    planner = WeddingSeating(
        guest_list,
        table_size=args.table_size,
        vip_tables=args.vip_tables,
        max_iter=args.max_iter,
    )

    tables = planner.optimize()

    if not args.no_print:
        for idx, table in enumerate(tables, start=1):
            names = ", ".join(guest["name"] for guest in table)
            print(f"Table {idx}: {names}")

    if args.export_prefix:
        formats = list(_unique_ordered(args.export_format or ["csv"]))
        for fmt in formats:
            try:
                planner.export(str(args.export_prefix), fmt)
            except Exception as exc:  # pragma: no cover - defensive export error
                print(f"Error exporting {fmt.upper()} file: {exc}", file=sys.stderr)
                return 1

    if args.visualize:
        planner.visualize()

    return 0


if __name__ == "__main__":  # pragma: no cover - entry point
    sys.exit(main())

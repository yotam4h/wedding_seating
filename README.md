# Wedding Seating Planner

Plan stress-free receptions by automatically arranging guests into balanced tables while respecting VIPs, friendships, and conflicts. This lightweight library provides seating optimization and data import/export helpers so you can iterate on layouts with confidence.

## Features

- **Smart assignment** – group families, seat VIPs first, and iteratively swap guests to improve satisfaction.
- **Conflict awareness** – honor `avoid` relationships and encourage friends or shared groups to sit together.
- **One-stop workflow** – import guests from CSV, optimize a layout, and export the final plan to CSV or PDF.

## Installation

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

The library depends on `pandas` and `reportlab`. If you prefer to install directly, run:

```bash
pip install pandas reportlab
```

## Guest list format

Provide your guest list as a CSV file with the following columns:

| column   | required | description |
|----------|----------|-------------|
| `name`   | ✅        | Guest display name. |
| `group`  | optional | Family or cohort label to keep together when possible. |
| `vip`    | optional | Boolean (`True`/`False` or `1`/`0`) marking VIP status. |
| `avoid`  | optional | Comma-separated list of guests they should not sit with. |
| `friends`| optional | Comma-separated list of seatmates they'd enjoy. |

Missing optional columns are treated as empty lists/false values automatically.

## Quick start

```python
from wedding_seating.core import WeddingSeating
from wedding_seating.utils import import_guest_list_csv

guest_list = import_guest_list_csv("guests.csv")

planner = WeddingSeating(
	guest_list,
	table_size=8,
	vip_tables=2,
	max_iter=200,
)

tables = planner.optimize()
planner.export("seating", "csv")  # write seating.csv
planner.export("seating", "pdf")  # write seating.pdf

for idx, table in enumerate(tables, start=1):
	print(f"Table {idx}: {[guest['name'] for guest in table]}")
```

Run the example script under `examples/example_usage.py` for an end-to-end demonstration once you supply a `guests.csv` file in the same directory.

## Command-line runner

Optimize a seating plan directly from the terminal:

```bash
python -m wedding_seating guests.csv \
	--table-size 8 \
	--vip-tables 2 \
	--max-iter 200 \
	--export-prefix seating_plan \
	--export-format csv \
	--no-print
```

- `guests.csv` is your input file following the schema above.
- Use `--export-prefix` to write `seating_plan.csv` (and `.pdf` if you add `--export-format pdf`).
- Drop the `--no-print` flag to see each table listed in the console.

## How it works

1. VIP guests are placed first across the designated VIP tables.
2. Guests sharing a `group` label are seated together whenever space allows.
3. Remaining guests are assigned based on a scoring heuristic that rewards friends and penalizes conflicts.
4. A local search loop performs beneficial swaps to further improve satisfaction.

## Development

Install the project dependencies and add `pytest` for the test suite:

```bash
pip install -r requirements.txt
pip install pytest
```

Run the automated tests after making changes:

```bash
pytest
```

Feel free to extend the optimization strategy or hook in alternative scoring rules.

## License

This project is licensed under the [MIT License](./LICENSE). You are free to use, modify, and distribute the code with minimal restrictions—just retain the original copyright and license notice.

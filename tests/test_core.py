import csv
from pathlib import Path
from typing import List

import pytest

from wedding_seating.core import WeddingSeating
from wedding_seating.types import Guest, Tables
from wedding_seating.utils import import_guest_list_csv, save_csv, save_pdf


@pytest.fixture
def guest_list() -> List[Guest]:
    return [
        {
            "name": "Alice",
            "group": None,
            "vip": True,
            "avoid": [],
            "friends": ["Bob"],
        },
        {
            "name": "Bob",
            "group": None,
            "vip": False,
            "avoid": [],
            "friends": ["Alice"],
        },
        {
            "name": "Carol",
            "group": "Family1",
            "vip": False,
            "avoid": [],
            "friends": [],
        },
        {
            "name": "Dave",
            "group": "Family1",
            "vip": False,
            "avoid": ["Eve"],
            "friends": [],
        },
        {
            "name": "Eve",
            "group": None,
            "vip": False,
            "avoid": [],
            "friends": [],
        },
    ]


def test_optimize_respects_constraints(guest_list: List[Guest]) -> None:
    planner = WeddingSeating(guest_list, table_size=3, vip_tables=1, max_iter=20)
    tables = planner.optimize()

    assigned_names = [guest["name"] for table in tables for guest in table]
    assert sorted(assigned_names) == sorted(guest["name"] for guest in guest_list)

    assert all(len(table) <= 3 for table in tables)

    for table in tables:
        table_names = {guest["name"] for guest in table}
        for guest in table:
            for avoid in guest.get("avoid", []):
                assert avoid not in table_names, (
                    f"Guest {guest['name']} should not be seated with {avoid}"
                )


def test_export_dispatches_formats(tmp_path: Path, guest_list: List[Guest], monkeypatch: pytest.MonkeyPatch) -> None:
    planner = WeddingSeating(guest_list, table_size=3, vip_tables=1, max_iter=20)
    planner.optimize()

    captured: dict[str, tuple[Tables, str]] = {}

    def fake_save_csv(tables: Tables, filename: str) -> None:
        captured["csv"] = (tables, filename)
        Path(filename).write_text("Table,Seat,Name\n")

    def fake_save_pdf(tables: Tables, filename: str) -> None:
        captured["pdf"] = (tables, filename)
        Path(filename).write_bytes(b"%PDF-1.4 test")

    monkeypatch.setattr("wedding_seating.core.save_csv", fake_save_csv)
    monkeypatch.setattr("wedding_seating.core.save_pdf", fake_save_pdf)

    base_path = tmp_path / "layout"

    planner.export(str(base_path), "csv")
    assert "csv" in captured
    assert Path(captured["csv"][1]).exists()

    planner.export(str(base_path), "pdf")
    assert "pdf" in captured
    assert Path(captured["pdf"][1]).exists()

    with pytest.raises(ValueError):
        planner.export(str(base_path), "txt")


def test_save_csv_creates_expected_output(tmp_path: Path, guest_list: List[Guest]) -> None:
    tables: Tables = [guest_list[:3], guest_list[3:]]
    csv_path = tmp_path / "seating.csv"
    save_csv(tables, csv_path)

    with csv_path.open() as handle:
        reader = csv.DictReader(handle)
        rows = list(reader)

    assert len(rows) == len(guest_list)
    assert {row["Name"] for row in rows} == {guest["name"] for guest in guest_list}


def test_save_pdf_creates_file(tmp_path: Path, guest_list: List[Guest]) -> None:
    tables: Tables = [guest_list[:2]]
    pdf_path = tmp_path / "seating.pdf"
    save_pdf(tables, pdf_path)
    assert pdf_path.exists()
    assert pdf_path.stat().st_size > 0


def test_import_guest_list_csv(tmp_path: Path) -> None:
    csv_content = (
        "name,group,vip,avoid,friends\n"
        'Alice,FamilyA,1,"Bob, Eve","Carol"\n'
        "Bob,,0,,\n"
    )
    csv_path = tmp_path / "guests.csv"
    csv_path.write_text(csv_content)

    guests = import_guest_list_csv(csv_path)

    assert len(guests) == 2
    assert guests[0]["name"] == "Alice"
    assert guests[0].get("vip") is True
    assert guests[0].get("avoid") == ["Bob", "Eve"]
    assert guests[0].get("friends") == ["Carol"]
    assert guests[1].get("vip") is False
    assert guests[1].get("avoid") == []
    assert guests[1].get("friends") == []


def test_local_optimize_swaps_to_improve_friend_satisfaction() -> None:
    guests: List[Guest] = [
        {"name": "VIP_Alice", "group": None, "vip": True, "avoid": [], "friends": ["Carol"]},
        {"name": "VIP_Bob", "group": None, "vip": True, "avoid": [], "friends": ["Dave"]},
        {"name": "Carol", "group": None, "vip": False, "avoid": [], "friends": ["VIP_Alice"]},
        {"name": "Dave", "group": None, "vip": False, "avoid": [], "friends": ["VIP_Bob"]},
    ]

    planner = WeddingSeating(guests, table_size=2, vip_tables=1, max_iter=10)
    tables = planner.optimize()

    assert any(
        {guest["name"] for guest in table} == {"VIP_Alice", "Carol"}
        for table in tables
    )
    assert any(
        {guest["name"] for guest in table} == {"VIP_Bob", "Dave"}
        for table in tables
    )

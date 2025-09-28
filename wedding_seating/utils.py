from __future__ import annotations

from pathlib import Path
from typing import List, Union

import pandas as pd
from reportlab.platypus import SimpleDocTemplate, Table

from .types import Guest, Tables

PathLike = Union[str, Path]


def import_guest_list_csv(filename: PathLike) -> List[Guest]:
    df = pd.read_csv(filename)  # type: ignore[call-overload]
    guest_list: List[Guest] = []
    for _, row in df.iterrows():
        guest_list.append(
            {
                'name': row['name'],
                'group': row.get('group', None),
                'vip': bool(row.get('vip', False)),
                'avoid': [] if pd.isna(row.get('avoid')) else [x.strip() for x in str(row['avoid']).split(',')],
                'friends': [] if pd.isna(row.get('friends')) else [x.strip() for x in str(row['friends']).split(',')],
            }
        )
    return guest_list


def save_csv(tables: Tables, filename: PathLike) -> None:
    data: List[List[object]] = []
    for idx, table in enumerate(tables):
        for seat, guest in enumerate(table, 1):
            data.append([f'Table {idx+1}', seat, guest['name']])
    df = pd.DataFrame(data, columns=['Table', 'Seat', 'Name'])
    df.to_csv(str(filename), index=False)


def save_pdf(tables: Tables, filename: PathLike) -> None:
    doc = SimpleDocTemplate(str(filename))
    data: List[List[str]] = []
    for idx, table in enumerate(tables):
        row = [guest['name'] for guest in table]
        data.append([f'Table {idx+1}'] + row)
    report_table = Table(data)
    doc.build([report_table])

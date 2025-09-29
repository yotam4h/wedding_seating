from __future__ import annotations

from typing import Dict, Iterable, List, Optional, Set

from .types import Guest, Table, Tables
from .utils import save_csv, save_pdf

class WeddingSeating:
    def __init__(
        self,
        guest_list: Iterable[Guest],
        table_size: int = 8,
        vip_tables: int = 1,
        max_iter: int = 100,
    ) -> None:
        """
        guest_list: list of dicts with keys:
            'name', 'group', 'vip' (bool), 'avoid' (list), 'friends' (list)
        table_size: maximum guests per table
        vip_tables: number of tables reserved for VIPs
        max_iter: max iterations for local optimization
        """
        self.guest_list: List[Guest] = list(guest_list)
        self.table_size: int = table_size
        self.vip_tables: int = vip_tables
        self.max_iter: int = max_iter
        self.tables: Tables = []

    def optimize(self) -> Tables:
        n_guests = len(self.guest_list)
        n_tables = (n_guests + self.table_size - 1) // self.table_size
        self.tables = [[] for _ in range(n_tables)]

        # --- Step 1: Place VIPs ---
        vip_guests = [guest for guest in self.guest_list if guest.get('vip')]
        non_vip_guests = [guest for guest in self.guest_list if not guest.get('vip')]

        table_idx = 0
        for guest in vip_guests:
            while len(self.tables[table_idx]) >= self.table_size:
                table_idx += 1
            self.tables[table_idx].append(guest)
            if table_idx >= self.vip_tables:
                table_idx = 0  # VIPs distributed among VIP tables

        # --- Step 2: Place groups/families ---
        groups: Dict[str, List[Guest]] = {}
        for guest in non_vip_guests:
            group = guest.get('group')
            if group:
                existing = groups.get(group)
                if existing is None:
                    groups[group] = [guest]
                else:
                    existing.append(guest)

        placed_guests: Set[str] = set()
        for group_guests in groups.values():
            # Find table with enough space
            table_idx = self._find_table_for_group(len(group_guests))
            if table_idx is not None:
                self.tables[table_idx].extend(group_guests)
                placed_guests.update(member['name'] for member in group_guests)
            else:
                # If no table can fit all, split
                for member in group_guests:
                    self._place_guest_best_fit(member)
                    placed_guests.add(member['name'])

        # --- Step 3: Place remaining guests ---
        for guest in non_vip_guests:
            if guest['name'] not in placed_guests:
                self._place_guest_best_fit(guest)

        # --- Step 4: Local optimization (swap friends) ---
        self._local_optimize()

        return self.tables

    # --- Helper methods ---
    def _find_table_for_group(self, group_size: int) -> Optional[int]:
        for idx, table in enumerate(self.tables):
            if len(table) + group_size <= self.table_size:
                return idx
        return None

    def _place_guest_best_fit(self, guest: Guest) -> None:
        best_table: Optional[int] = None
        best_score = -float('inf')
        for idx, table in enumerate(self.tables):
            if len(table) >= self.table_size:
                continue
            score = self._table_score(table, guest)
            if score > best_score:
                best_score = score
                best_table = idx
        if best_table is not None:
            self.tables[best_table].append(guest)
        else:
            # Should not happen, but fallback
            self.tables[0].append(guest)

    def _table_score(self, table: Table, guest: Guest) -> int:
        score = 0
        table_names = [g['name'] for g in table]
        # Avoid conflicts
        for avoid in guest.get('avoid', []):
            if avoid in table_names:
                score -= 100
        # Friend bonus
        for friend in guest.get('friends', []):
            if friend in table_names:
                score += 5
        # Group bonus
        if guest.get('group'):
            group_count = sum(1 for g in table if g.get('group') == guest.get('group'))
            score += group_count
        return score

    def _local_optimize(self) -> None:
        for _ in range(self.max_iter):
            improved = False
            for i in range(len(self.tables)):
                swap_made = False
                for j in range(i + 1, len(self.tables)):
                    table1 = self.tables[i]
                    table2 = self.tables[j]

                    for idx1, guest1 in enumerate(list(table1)):
                        for idx2, guest2 in enumerate(list(table2)):
                            old_score = self._table_score(table1, guest1) + self._table_score(table2, guest2)

                            swapped_table1 = table1[:idx1] + [guest2] + table1[idx1 + 1:]
                            swapped_table2 = table2[:idx2] + [guest1] + table2[idx2 + 1:]
                            new_score = self._table_score(swapped_table1, guest2) + self._table_score(swapped_table2, guest1)

                            if new_score > old_score:
                                table1[idx1] = guest2
                                table2[idx2] = guest1
                                improved = True
                                swap_made = True
                                break
                        if swap_made:
                            break
                    if swap_made:
                        break
                if swap_made:
                    break
            if not improved:
                break

    # --- Output methods ---
    def export(self, filename: str = 'seating', filetype: str = 'csv') -> None:
        if filetype == 'csv':
            save_csv(self.tables, filename + '.csv')
        elif filetype == 'pdf':
            save_pdf(self.tables, filename + '.pdf')
        else:
            raise ValueError("Unsupported filetype. Use 'csv' or 'pdf'.")

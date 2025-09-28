from wedding_seating.core import WeddingSeating
from wedding_seating.utils import import_guest_list_csv

# Import guests from CSV
guest_list = import_guest_list_csv("guests.csv")

# Create seating arrangement
seating = WeddingSeating(guest_list, table_size=10, vip_tables=3)
seating.optimize()

# Visualize
seating.visualize()

# Export to CSV and PDF
seating.export("wedding_seating", "csv")
seating.export("wedding_seating", "pdf")

"""
Plots the data from the futek loadcell readings
"""
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

# Load the data
path = Path("data") / "Run.xlsx"
df = pd.read_excel(path, index_col=0)

# Inspect column names and first few rows
print("Columns:", list(df.columns))
print(df.head())

# Assume columns 2-4 are load cells and column 5 is time.
# Adjust if the file has different column names/order.
load_cells = df.iloc[:, 0:3]
time = df.iloc[:, 3]

# Convert time to elapsed time (assuming it's in seconds)
elapsed = time - time.iloc[0]

# Plot all three load cells on one chart
plt.figure(figsize=(10, 6))
for col in load_cells.columns:
    plt.plot(elapsed, load_cells[col], label=col)

plt.xlabel("Elapsed time")
plt.ylabel("Pressure (N)")
plt.title("Loadcell Pressures vs Elapsed Time")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig("plot.png", format="png", dpi=500)
plt.show()  



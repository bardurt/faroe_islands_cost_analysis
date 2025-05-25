import pandas as pd
import matplotlib.pyplot as plt
import argparse
import os
from datetime import datetime

COLOR_GROUP_GREEN_DARK = '#58d68d'  
COLOR_GROUP_GREEN_LIGHT = '#abebc6'  
COLOR_GROUP_YELLOW = '#f9e79f'       
COLOR_GROUP_RED_LIGHT = '#f5b7b1'  
COLOR_GROUP_RED_DARK = '#ec7063'    

def calculate_municipal_tax(income, tax_rate):
    threshold = 30000
    if income <= threshold:
        return 0.0
    taxable_income = income - threshold
    return taxable_income * tax_rate

def calculate_church_tax(income, tax_rate):
    threshold = 30000
    if income <= threshold:
        return 0.0
    taxable_income = income - threshold
    return taxable_income * tax_rate

def calculate_federal_tax(income):
    brackets = [
        (0, 65000,     0,        0,      0.00),
        (65000, 180000, 0,        65000,  0.13),
        (180000, 330000, 14950,   180000, 0.15),
        (330000, 450000, 37450,   330000, 0.20),
        (450000, 600000, 61450,   450000, 0.25),
        (600000, float('inf'), 98950, 600000, 0.30)
    ]
    for lower, upper, base_tax, threshold, rate in brackets:
        if income < upper:
            return base_tax + (income - threshold) * rate
    return 0

def calculate_total_tax(income, municipal_rate, church_rate):
    municipal_tax = calculate_municipal_tax(income, municipal_rate)
    church_tax = calculate_church_tax(income, church_rate)
    federal_tax = calculate_federal_tax(income)
    total_tax = municipal_tax + church_tax + federal_tax
    return round(total_tax, 2)

# --- Argument Parsing ---
parser = argparse.ArgumentParser(description="Plot municipal tax data for a given year.")
parser.add_argument("year", nargs='?', type=int, default=datetime.now().year,
                    help="Year of the data to visualize (default: current year)")
args = parser.parse_args()

year = args.year
file_path = f"../data/{year}.csv"

if not os.path.exists(file_path):
    raise FileNotFoundError(f"No data file found for year {year} at {file_path}")

df = pd.read_csv(file_path)

FIXED_INCOME = 400_000
df["Total Tax (400,000kr)"] = df.apply(
    lambda row: calculate_total_tax(
        income=FIXED_INCOME,
        municipal_rate=row["tax"] / 100,
        church_rate=row["churchtax"] / 100
    ),
    axis=1
)

numeric_cols = df.select_dtypes(include='number').columns
averages = df[numeric_cols].mean().round(2)

average_row = {col: averages[col] if col in averages else '' for col in df.columns}
average_row['municipal'] = 'Average'
df_with_avg = pd.concat([df, pd.DataFrame([average_row])], ignore_index=True)

n_rows, n_cols = df_with_avg.shape
fig_width = max(15, n_cols * 2.2)
fig_height = max(5, n_rows * 0.6)
fig, ax = plt.subplots(figsize=(fig_width, fig_height))
ax.axis('off')
ax.axis('tight')

table_data = df_with_avg.astype(str).values

custom_labels = {
    'municipal': 'Municipality',
    'tax': 'Tax Rate (%)',
    'churchtax': 'Church Tax Rate (%)',
    'child_deduction': 'Child Deduction',
    'connected_to_center': 'Connected to Center',
    'distance_to_center': 'Distance to Center\n(1 - 5)',
    'cost_group': 'Cost Group\n(1 - 5)',
    'Total Tax (400,000kr)': 'Total Tax\nfor 400,000 kr'
}
col_labels = [custom_labels.get(col, col) for col in df_with_avg.columns.tolist()]

table = ax.table(cellText=table_data,
                 colLabels=col_labels,
                 loc='center',
                 cellLoc='center',
                 bbox=[0, 0, 1, 1])

table.scale(1.2, 1.5)
header_row = 0
for col_idx in range(n_cols):
    header_cell = table[header_row, col_idx]
    header_cell.set_text_props(weight='bold')
    header_cell.set_facecolor('#d9d9d9')
    header_cell.set_height(header_cell.get_height() * 1.5)

last_row_idx = len(df)
for col_idx in range(n_cols):
    cell = table[last_row_idx + 1, col_idx]
    cell.set_facecolor('#f2f2f2')
    cell.set_text_props(weight='bold')

def color_cell_standard(row_idx, col_name):
    col_index = df_with_avg.columns.get_loc(col_name)
    if col_name not in averages:
        return
    avg_value = averages[col_name]
    try:
        value = float(df_with_avg.iloc[row_idx][col_name])
        cell = table[row_idx + 1, col_index]
        if value < avg_value:
            cell.set_facecolor(COLOR_GROUP_GREEN_DARK)
        elif value > avg_value:
            cell.set_facecolor(COLOR_GROUP_RED_DARK)
        else:
            cell.set_facecolor(COLOR_GROUP_YELLOW)
    except:
        pass

def color_cell_reversed(row_idx, col_name):
    col_index = df_with_avg.columns.get_loc(col_name)
    if col_name not in averages:
        return
    avg_value = averages[col_name]
    try:
        value = float(df_with_avg.iloc[row_idx][col_name])
        cell = table[row_idx + 1, col_index]
        if value > avg_value:
            cell.set_facecolor(COLOR_GROUP_GREEN_DARK)
        elif value < avg_value:
            cell.set_facecolor(COLOR_GROUP_RED_DARK)
        else:
            cell.set_facecolor(COLOR_GROUP_YELLOW)
    except:
        pass

def color_cell_direct_center(row_idx, col_name):
    col_index = df_with_avg.columns.get_loc(col_name)
    try:
        value = int(df_with_avg.iloc[row_idx][col_name])
        cell = table[row_idx + 1, col_index]
        if value == 1:
            cell.set_facecolor(COLOR_GROUP_GREEN_DARK)
        else:
            cell.set_facecolor(COLOR_GROUP_RED_DARK)
    except:
        pass

def color_cell_distance_center(row_idx, col_name):
    col_index = df_with_avg.columns.get_loc(col_name)
    try:
        value = float(df_with_avg.iloc[row_idx][col_name])
        cell = table[row_idx + 1, col_index]
        if value < 3:
            cell.set_facecolor(COLOR_GROUP_GREEN_DARK)
        elif value == 3:
            cell.set_facecolor(COLOR_GROUP_YELLOW)
        else:
            cell.set_facecolor(COLOR_GROUP_RED_DARK)
    except:
        pass

def color_cell_cost_group(row_idx, col_name):
    col_index = df_with_avg.columns.get_loc(col_name)
    color_map = {
        1: COLOR_GROUP_GREEN_DARK,
        2: COLOR_GROUP_GREEN_LIGHT,
        3: COLOR_GROUP_YELLOW,
        4: COLOR_GROUP_RED_LIGHT,
        5: COLOR_GROUP_RED_DARK,
    }
    try:
        value = int(df_with_avg.iloc[row_idx][col_name])
        cell = table[row_idx + 1, col_index]
        cell.set_facecolor(color_map.get(value, '#ffffff'))
    except:
        pass

for row_idx in range(len(df)):
    color_cell_standard(row_idx, 'tax')
    color_cell_standard(row_idx, 'churchtax')
    color_cell_reversed(row_idx, 'child_deduction')
    color_cell_direct_center(row_idx, 'connected_to_center')
    color_cell_distance_center(row_idx, 'distance_to_center')
    color_cell_cost_group(row_idx, 'cost_group')

table.auto_set_font_size(False)
table.set_fontsize(10)
table.scale(1.2, 1.5)

for key, cell in table.get_celld().items():
    cell.set_text_props(va='center')


plt.title(f'Municipal Tax & Cost Matrix – {year}', fontsize=16, pad=20)
plt.tight_layout()
plt.show()

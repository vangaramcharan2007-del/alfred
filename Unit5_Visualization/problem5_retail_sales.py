"""
Unit 5 - Problem 5: Retail Company Monthly Sales Data
Tasks:
- Line plot: Monthly revenue trends
- Grouped bar chart: Sales & Profit across product categories
- Scatter plot: Discount % vs Profit
- Heatmap: Correlations among revenue, qty, discount, profit
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
import os

np.random.seed(99)
months = pd.date_range('2024-01', periods=12, freq='MS').strftime('%b %Y').tolist()
categories = ['Electronics', 'Clothing', 'Food', 'Furniture', 'Books']

# Monthly revenue
revenue_data = {
    'Electronics': np.random.randint(80000, 150000, 12),
    'Clothing':    np.random.randint(40000, 80000,  12),
    'Food':        np.random.randint(30000, 60000,  12),
    'Furniture':   np.random.randint(25000, 55000,  12),
    'Books':       np.random.randint(10000, 25000,  12),
}
df_rev = pd.DataFrame(revenue_data, index=months)

# Transaction-level data
n = 500
cat_arr = np.random.choice(categories, n)
qty      = np.random.randint(1, 50, n)
unit_px  = {'Electronics': 5000, 'Clothing': 800, 'Food': 200, 'Furniture': 3000, 'Books': 300}
discount = np.random.uniform(0, 40, n).round(1)
revenue  = np.array([qty[i] * unit_px[cat_arr[i]] * (1 - discount[i]/100) for i in range(n)])
profit   = revenue * np.random.uniform(0.05, 0.35, n) - discount * 100
df_tx = pd.DataFrame({'Category': cat_arr, 'Quantity': qty, 'Discount': discount,
                      'Revenue': revenue.round(2), 'Profit': profit.round(2)})

fig, axes = plt.subplots(2, 2, figsize=(18, 12))
fig.suptitle('Retail Company – Sales Analytics Dashboard', fontsize=18, fontweight='bold')

# ── Line plot: Monthly revenue ──
ax = axes[0, 0]
palette = sns.color_palette('tab10', len(categories))
for i, cat in enumerate(categories):
    ax.plot(months, df_rev[cat], marker='o', label=cat, color=palette[i], linewidth=2)
ax.set_title('Monthly Revenue Trends by Category', fontsize=13, fontweight='bold')
ax.set_xlabel('Month'); ax.set_ylabel('Revenue (₹)')
ax.tick_params(axis='x', rotation=45)
ax.legend(fontsize=8); ax.grid(alpha=0.35)

# ── Grouped bar chart: Sales & Profit per category ──
ax = axes[0, 1]
cat_summary = df_tx.groupby('Category')[['Revenue', 'Profit']].sum().reset_index()
x = np.arange(len(cat_summary))
w = 0.35
ax.bar(x - w/2, cat_summary['Revenue'], width=w, label='Revenue', color='steelblue', edgecolor='black')
ax.bar(x + w/2, cat_summary['Profit'],  width=w, label='Profit',  color='coral',     edgecolor='black')
ax.set_xticks(x)
ax.set_xticklabels(cat_summary['Category'], rotation=15, fontsize=9)
ax.set_title('Total Revenue vs Profit per Category\n(Grouped Bar Chart)', fontsize=13, fontweight='bold')
ax.set_ylabel('Amount (₹)'); ax.legend(); ax.grid(axis='y', alpha=0.35)

# ── Scatter: Discount vs Profit ──
ax = axes[1, 0]
sns.scatterplot(data=df_tx, x='Discount', y='Profit', hue='Category',
                palette='tab10', alpha=0.6, ax=ax, s=50)
m, b = np.polyfit(df_tx['Discount'], df_tx['Profit'], 1)
xs = np.linspace(df_tx['Discount'].min(), df_tx['Discount'].max(), 100)
ax.plot(xs, m * xs + b, 'k--', lw=2, label='Trend line')
ax.set_title('Discount (%) vs Profit\n(Scatter Plot)', fontsize=13, fontweight='bold')
ax.set_xlabel('Discount (%)'); ax.set_ylabel('Profit (₹)')
ax.legend(fontsize=8, bbox_to_anchor=(1.01, 1)); ax.grid(alpha=0.35)

# ── Heatmap: correlations ──
corr = df_tx[['Quantity', 'Discount', 'Revenue', 'Profit']].corr()
sns.heatmap(corr, annot=True, fmt='.2f', cmap='coolwarm', center=0,
            linewidths=0.5, ax=axes[1, 1], annot_kws={'size': 11})
axes[1, 1].set_title('Correlation Heatmap\n(Revenue, Qty, Discount, Profit)', fontsize=13, fontweight='bold')

plt.tight_layout()
out_path = os.path.join(os.path.dirname(__file__), 'output_problem5_retail_sales.png')
plt.savefig(out_path, dpi=150, bbox_inches='tight')
print(f"[✓] Saved → {out_path}")
plt.close()

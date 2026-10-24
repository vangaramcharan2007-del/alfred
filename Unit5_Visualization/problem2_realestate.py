"""
Unit 5 - Problem 2: Real-Estate Dataset (Area, Price, City, Bedrooms)
a) Seaborn scatter plot – Area vs Price
b) Box plot – Price across Cities
c) Categorical vs Categorical plot
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
import os

np.random.seed(7)
n = 200
cities = ['Mumbai', 'Delhi', 'Bangalore', 'Chennai', 'Hyderabad']
data = {
    'Area':      np.random.randint(500, 3500, n),
    'Bedrooms':  np.random.choice([1, 2, 3, 4, 5], n),
    'City':      np.random.choice(cities, n),
}
# Price correlated with Area + city multiplier
city_mult = {'Mumbai': 12000, 'Delhi': 10000, 'Bangalore': 9000, 'Chennai': 7500, 'Hyderabad': 7000}
data['Price'] = [
    data['Area'][i] * city_mult[data['City'][i]] + np.random.randint(-500000, 500000)
    for i in range(n)
]
df = pd.DataFrame(data)
df['Price_Lakhs'] = df['Price'] / 1e5

fig, axes = plt.subplots(1, 2, figsize=(15, 6))
fig.suptitle('Real-Estate Market Analysis', fontsize=16, fontweight='bold')

# ── (a) Scatter plot ──
sns.scatterplot(data=df, x='Area', y='Price_Lakhs', hue='City', size='Bedrooms',
                sizes=(40, 200), alpha=0.7, palette='tab10', ax=axes[0])
axes[0].set_title('(a) Area vs Price by City & Bedrooms', fontsize=13, fontweight='bold')
axes[0].set_xlabel('Area (sq ft)', fontsize=11)
axes[0].set_ylabel('Price (Lakhs ₹)', fontsize=11)
axes[0].legend(title='City / Bedrooms', bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=8)
axes[0].grid(alpha=0.3)

# ── (b) Box plot ──
palette = sns.color_palette('Set2', len(cities))
sns.boxplot(data=df, x='City', y='Price_Lakhs', palette='Set2', ax=axes[1],
            order=sorted(cities))
axes[1].set_title('(b) Price Distribution by City (Box Plot)', fontsize=13, fontweight='bold')
axes[1].set_xlabel('City', fontsize=11)
axes[1].set_ylabel('Price (Lakhs ₹)', fontsize=11)
axes[1].tick_params(axis='x', rotation=15)
axes[1].grid(axis='y', alpha=0.4)

fig.text(0.5, -0.04,
         '(c) For a Categorical vs Categorical relationship → Use a Seaborn heatmap with crosstab, '
         'a grouped bar chart, or a mosaic/stacked bar chart.',
         ha='center', fontsize=10, style='italic',
         bbox=dict(boxstyle='round,pad=0.4', facecolor='lightyellow', edgecolor='gray'))

plt.tight_layout()
out_path = os.path.join(os.path.dirname(__file__), 'output_problem2_realestate.png')
plt.savefig(out_path, dpi=150, bbox_inches='tight')
print(f"[✓] Saved → {out_path}")
plt.close()

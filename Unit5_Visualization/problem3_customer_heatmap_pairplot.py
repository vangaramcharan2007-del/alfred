"""
Unit 5 - Problem 3: Customer Dataset – Heatmap & Pairplot
a) Heatmap of correlation matrix
b) Pairplot for multivariate analysis
c) Two factors for choosing graph type
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
import os

np.random.seed(21)
n = 150
age        = np.random.randint(18, 70, n)
income     = age * 800 + np.random.randint(5000, 50000, n)
spend      = income * np.random.uniform(0.1, 0.5, n)
credit     = (income / 1000).astype(int) + np.random.randint(-5, 15, n)
loyalty_yr = np.random.randint(0, 15, n)
df = pd.DataFrame({
    'Age': age,
    'Annual Income (K)': (income / 1000).round(1),
    'Spending Score': spend.round(1),
    'Credit Score': credit.clip(300, 850),
    'Loyalty (yrs)': loyalty_yr,
})
corr = df.corr()

# ── (a) Heatmap ──
fig1, ax1 = plt.subplots(figsize=(8, 6))
mask = np.triu(np.ones_like(corr, dtype=bool))
sns.heatmap(corr, annot=True, fmt='.2f', cmap='coolwarm', center=0,
            linewidths=0.5, linecolor='white', mask=mask,
            annot_kws={'size': 11}, ax=ax1)
ax1.set_title('(a) Correlation Heatmap – Customer Attributes\n'
              'How to read: Values near +1 = strong positive, near -1 = strong negative correlation',
              fontsize=11, fontweight='bold')
plt.tight_layout()
out1 = os.path.join(os.path.dirname(__file__), 'output_problem3a_heatmap.png')
fig1.savefig(out1, dpi=150, bbox_inches='tight')
print(f"[✓] Saved → {out1}")
plt.close(fig1)

# ── (b) Pairplot ──
df['Segment'] = pd.cut(df['Annual Income (K)'], bins=3, labels=['Low', 'Mid', 'High'])
pp = sns.pairplot(df.drop(columns=['Segment']), diag_kind='kde',
                  plot_kws={'alpha': 0.5, 'color': 'steelblue'},
                  diag_kws={'color': 'steelblue', 'fill': True})
pp.fig.suptitle('(b) Pairplot – Multivariate Analysis of Customer Data\n'
                'Shows: pairwise scatter plots + KDE on diagonal for distributions & relationships',
                y=1.02, fontsize=11, fontweight='bold')

fig2 = pp.fig
fig2.text(0.5, -0.03,
          '(c) Two factors for choosing graph type:\n'
          '1. Nature of data – categorical vs continuous   |   2. Purpose – comparison, distribution, relationship, or trend',
          ha='center', fontsize=10, style='italic',
          bbox=dict(boxstyle='round,pad=0.4', facecolor='lightyellow', edgecolor='gray'))
out2 = os.path.join(os.path.dirname(__file__), 'output_problem3b_pairplot.png')
fig2.savefig(out2, dpi=120, bbox_inches='tight')
print(f"[✓] Saved → {out2}")
plt.close(fig2)

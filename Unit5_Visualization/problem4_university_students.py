"""
Unit 5 - Problem 4: University Student Records
Tasks:
- Bar chart: Average marks per department
- Histogram: Distribution of student marks
- Seaborn Box plot: Marks across departments (outliers)
- Heatmap: Correlations among attendance, internal, external marks
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
import os

np.random.seed(55)
n = 300
depts = ['CSE', 'ECE', 'MECH', 'CIVIL', 'IT']
dept_base = {'CSE': 75, 'ECE': 70, 'MECH': 65, 'CIVIL': 60, 'IT': 72}
semesters = [1, 2, 3, 4, 5, 6, 7, 8]

rows = []
for i in range(n):
    dept = np.random.choice(depts)
    sem  = np.random.choice(semesters)
    base = dept_base[dept]
    internal  = int(np.clip(np.random.normal(base * 0.4, 5), 0, 40))
    external  = int(np.clip(np.random.normal(base * 0.6, 10), 0, 60))
    attendance= round(float(np.clip(np.random.normal(78, 12), 40, 100)), 1)
    rows.append({'StudentID': f'S{1000+i}', 'Department': dept, 'Semester': sem,
                 'Internal': internal, 'External': external, 'Attendance': attendance})
df = pd.DataFrame(rows)
df['TotalMarks'] = df['Internal'] + df['External']
df['Grade'] = pd.cut(df['TotalMarks'],
                     bins=[0,40,50,60,70,80,100],
                     labels=['F','D','C','B','A','A+'])

fig, axes = plt.subplots(2, 2, figsize=(16, 12))
fig.suptitle('University Student Academic Analysis', fontsize=18, fontweight='bold')

# ── Bar chart: avg marks per dept ──
avg_marks = df.groupby('Department')['TotalMarks'].mean().sort_values(ascending=False)
colors = sns.color_palette('viridis', len(avg_marks))
bars = axes[0, 0].bar(avg_marks.index, avg_marks.values, color=colors, edgecolor='black')
for bar in bars:
    axes[0, 0].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.3,
                    f'{bar.get_height():.1f}', ha='center', va='bottom', fontweight='bold', fontsize=10)
axes[0, 0].set_title('Average Marks per Department', fontsize=13, fontweight='bold')
axes[0, 0].set_xlabel('Department'); axes[0, 0].set_ylabel('Average Total Marks')
axes[0, 0].set_ylim(0, 110); axes[0, 0].grid(axis='y', alpha=0.4)

# ── Histogram: marks distribution ──
axes[0, 1].hist(df['TotalMarks'], bins=15, color='coral', edgecolor='black', alpha=0.85)
axes[0, 1].axvline(df['TotalMarks'].mean(), color='navy', linestyle='--', lw=2,
                   label=f"Mean={df['TotalMarks'].mean():.1f}")
axes[0, 1].axvline(df['TotalMarks'].median(), color='green', linestyle='-.', lw=2,
                   label=f"Median={df['TotalMarks'].median():.1f}")
axes[0, 1].set_title('Distribution of Student Marks (Histogram)', fontsize=13, fontweight='bold')
axes[0, 1].set_xlabel('Total Marks (out of 100)'); axes[0, 1].set_ylabel('Frequency')
axes[0, 1].legend(); axes[0, 1].grid(axis='y', alpha=0.4)

# ── Box plot: marks across depts ──
sns.boxplot(data=df, x='Department', y='TotalMarks', palette='Set2',
            order=sorted(depts), ax=axes[1, 0], linewidth=1.2)
axes[1, 0].set_title('Marks Distribution by Department (Box Plot)', fontsize=13, fontweight='bold')
axes[1, 0].set_xlabel('Department'); axes[1, 0].set_ylabel('Total Marks')
axes[1, 0].grid(axis='y', alpha=0.4)

# ── Heatmap: correlations ──
corr_df = df[['Attendance', 'Internal', 'External', 'TotalMarks']].corr()
sns.heatmap(corr_df, annot=True, fmt='.2f', cmap='RdYlGn', center=0,
            linewidths=0.5, ax=axes[1, 1], annot_kws={'size': 11})
axes[1, 1].set_title('Correlation Heatmap\n(Attendance, Internal, External, Total)', fontsize=13, fontweight='bold')

plt.tight_layout()
out_path = os.path.join(os.path.dirname(__file__), 'output_problem4_university_students.png')
plt.savefig(out_path, dpi=150, bbox_inches='tight')
print(f"[✓] Saved → {out_path}")
plt.close()

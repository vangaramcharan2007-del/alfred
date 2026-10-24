"""
Unit 5 - Problem 1: School Exam Results (100 Students)
a) Histogram of marks
b) Bar chart for number of students per grade
c) One advantage of data visualization
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import os

# ---------- Generate sample data ----------
np.random.seed(42)
marks = np.random.normal(loc=65, scale=15, size=100).clip(0, 100).astype(int)

# Assign grades
def assign_grade(m):
    if m >= 90: return 'A+'
    elif m >= 80: return 'A'
    elif m >= 70: return 'B'
    elif m >= 60: return 'C'
    elif m >= 50: return 'D'
    else: return 'F'

grades = [assign_grade(m) for m in marks]
grade_labels = ['A+', 'A', 'B', 'C', 'D', 'F']
grade_counts = {g: grades.count(g) for g in grade_labels}

# ---------- Create figure ----------
fig, axes = plt.subplots(1, 2, figsize=(14, 6))
fig.suptitle('School Exam Results Analysis – 100 Students', fontsize=16, fontweight='bold', y=1.02)

# ── (a) Histogram ──
ax1 = axes[0]
n, bins, patches = ax1.hist(marks, bins=10, color='steelblue', edgecolor='black', alpha=0.85)
# Color-code bars by grade
colors = ['#2ecc71','#27ae60','#f39c12','#e67e22','#e74c3c','#c0392b']
for i, patch in enumerate(patches):
    bin_center = (bins[i] + bins[i+1]) / 2
    if bin_center >= 90:   patch.set_facecolor('#2ecc71')
    elif bin_center >= 80: patch.set_facecolor('#27ae60')
    elif bin_center >= 70: patch.set_facecolor('#f39c12')
    elif bin_center >= 60: patch.set_facecolor('#e67e22')
    elif bin_center >= 50: patch.set_facecolor('#e74c3c')
    else:                  patch.set_facecolor('#c0392b')

ax1.set_title('(a) Histogram of Student Marks', fontsize=13, fontweight='bold')
ax1.set_xlabel('Marks (out of 100)', fontsize=11)
ax1.set_ylabel('Number of Students', fontsize=11)
ax1.axvline(np.mean(marks), color='navy', linestyle='--', linewidth=2, label=f'Mean = {np.mean(marks):.1f}')
ax1.legend(fontsize=10)
ax1.grid(axis='y', alpha=0.4)

# ── (b) Bar chart ──
ax2 = axes[1]
bar_colors = ['#2ecc71','#27ae60','#f39c12','#e67e22','#e74c3c','#c0392b']
bars = ax2.bar(grade_labels, [grade_counts[g] for g in grade_labels],
               color=bar_colors, edgecolor='black', linewidth=0.8)
for bar, label in zip(bars, grade_labels):
    height = bar.get_height()
    ax2.text(bar.get_x() + bar.get_width()/2., height + 0.3, str(int(height)),
             ha='center', va='bottom', fontweight='bold', fontsize=12)

ax2.set_title('(b) Number of Students per Grade', fontsize=13, fontweight='bold')
ax2.set_xlabel('Grade', fontsize=11)
ax2.set_ylabel('Number of Students', fontsize=11)
ax2.grid(axis='y', alpha=0.4)

# Annotation – c)
fig.text(0.5, -0.04,
         '(c) Advantage of Data Visualization: It transforms complex numerical data into intuitive visual\n'
         'patterns, enabling faster identification of trends, outliers, and distributions.',
         ha='center', fontsize=10, style='italic',
         bbox=dict(boxstyle='round,pad=0.4', facecolor='lightyellow', edgecolor='gray'))

plt.tight_layout()
out_path = os.path.join(os.path.dirname(__file__), 'output_problem1_school_exam.png')
plt.savefig(out_path, dpi=150, bbox_inches='tight')
print(f"[✓] Saved → {out_path}")
plt.close()

"""
Unit 5 Visualization - Master Runner
Executes all 6 problems and saves output PNG images.
"""

import subprocess, sys, os

scripts = [
    'problem1_school_exam.py',
    'problem2_realestate.py',
    'problem3_customer_heatmap_pairplot.py',
    'problem4_university_students.py',
    'problem5_retail_sales.py',
    'problem6_weather.py',
]

base = os.path.dirname(os.path.abspath(__file__))
print("=" * 60)
print("  Unit 5 - Visualization (Matplotlib & Seaborn)")
print("  Running all problems ...")
print("=" * 60)

for script in scripts:
    path = os.path.join(base, script)
    print("\n>> Running " + script + " ...")
    result = subprocess.run([sys.executable, path], capture_output=True, text=True)
    if result.stdout:
        print(result.stdout.strip())
    if result.stderr:
        print("[STDERR]", result.stderr.strip()[:300])
    if result.returncode != 0:
        print("  FAILED: " + script)
    else:
        print("  OK: " + script)

print("\n" + "=" * 60)
print("  All outputs saved in: " + base)
print("=" * 60)
outputs = [f for f in os.listdir(base) if f.startswith('output_') and f.endswith('.png')]
print("\n  Generated " + str(len(outputs)) + " image(s):")
for f in sorted(outputs):
    print("    [PNG]  " + f)

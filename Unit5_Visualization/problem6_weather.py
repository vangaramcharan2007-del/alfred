"""
Unit 5 - Problem 6: Meteorological Weather Data
Tasks:
- Line plot: Daily temperature over a month
- Histogram: Rainfall distribution
- Scatter plot: Humidity vs Temperature
- Heatmap: Correlations (Temperature, Humidity, Rainfall, Wind Speed)
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
import os

np.random.seed(77)
dates = pd.date_range('2024-07-01', periods=30, freq='D')
temp       = 30 + 5 * np.sin(np.linspace(0, 2 * np.pi, 30)) + np.random.normal(0, 1.5, 30)
humidity   = 60 + 20 * np.cos(np.linspace(0, 2 * np.pi, 30)) + np.random.normal(0, 5, 30)
rainfall   = np.abs(np.random.exponential(3, 30))
wind_speed = np.abs(np.random.normal(12, 4, 30))

# Introduce a few NaN values to demonstrate handling
temp[5]      = np.nan
humidity[14] = np.nan
rainfall[22] = np.nan

df = pd.DataFrame({'Date': dates, 'Temperature': temp, 'Humidity': humidity,
                   'Rainfall': rainfall, 'WindSpeed': wind_speed})
df.set_index('Date', inplace=True)

# Fill NaN with interpolation
df.interpolate(method='linear', inplace=True)

fig, axes = plt.subplots(2, 2, figsize=(16, 11))
fig.suptitle('Meteorological Department – Weather Data Analysis (July 2024)', fontsize=17, fontweight='bold')

# ── Line plot: Daily temperature ──
ax = axes[0, 0]
ax.plot(df.index, df['Temperature'], color='orangered', marker='o', markersize=4, linewidth=2)
ax.fill_between(df.index, df['Temperature'].min(), df['Temperature'], alpha=0.15, color='orangered')
ax.set_title('Daily Temperature Changes Over July 2024', fontsize=13, fontweight='bold')
ax.set_xlabel('Date'); ax.set_ylabel('Temperature (°C)')
ax.tick_params(axis='x', rotation=45); ax.grid(alpha=0.35)

# ── Histogram: Rainfall ──
ax = axes[0, 1]
ax.hist(df['Rainfall'], bins=10, color='royalblue', edgecolor='black', alpha=0.8)
ax.axvline(df['Rainfall'].mean(), color='red', linestyle='--', lw=2,
           label=f"Mean = {df['Rainfall'].mean():.1f} mm")
ax.set_title('Rainfall Distribution (Histogram)', fontsize=13, fontweight='bold')
ax.set_xlabel('Rainfall (mm)'); ax.set_ylabel('Days')
ax.legend(); ax.grid(axis='y', alpha=0.4)

# ── Scatter: Humidity vs Temperature ──
ax = axes[1, 0]
sc = ax.scatter(df['Humidity'], df['Temperature'],
                c=df['Rainfall'], cmap='Blues', s=70, alpha=0.8, edgecolors='gray', lw=0.5)
plt.colorbar(sc, ax=ax, label='Rainfall (mm)')
m, b = np.polyfit(df['Humidity'], df['Temperature'], 1)
xs = np.linspace(df['Humidity'].min(), df['Humidity'].max(), 100)
ax.plot(xs, m * xs + b, 'r--', lw=2, label='Trend')
ax.set_title('Humidity vs Temperature\n(Scatter Plot, colored by Rainfall)', fontsize=13, fontweight='bold')
ax.set_xlabel('Humidity (%)'); ax.set_ylabel('Temperature (°C)')
ax.legend(); ax.grid(alpha=0.35)

# ── Heatmap: correlations ──
corr = df[['Temperature', 'Humidity', 'Rainfall', 'WindSpeed']].corr()
sns.heatmap(corr, annot=True, fmt='.2f', cmap='vlag', center=0,
            linewidths=0.6, linecolor='white', ax=axes[1, 1], annot_kws={'size': 12})
axes[1, 1].set_title('Correlation Heatmap\n(Temperature, Humidity, Rainfall, Wind Speed)',
                      fontsize=13, fontweight='bold')

plt.tight_layout()
out_path = os.path.join(os.path.dirname(__file__), 'output_problem6_weather.png')
plt.savefig(out_path, dpi=150, bbox_inches='tight')
print(f"[✓] Saved → {out_path}")
plt.close()

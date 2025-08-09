import matplotlib.pyplot as plt
import numpy as np

# Medianwerte aus deinen Reports
data = {
    'hint':    {'GR': 0.0001376, 'SR': 0.0001511, 'GR*SR': 0.0001890, 'Seg': 0.0001255, 'perf': 0.912},
    'deltaM':  {'GR': 0.0688306, 'SR': 0.0002473, 'GR*SR': 0.00028128, 'Seg': 0.00028128, 'perf': 0.004086},
    'hybrid':  {'GR': 0.0688306, 'SR': 0.0002473, 'GR*SR': 0.00028128, 'Seg': 0.00028129, 'perf': 0.004087},
}

models = ['GR', 'SR', 'GR*SR', 'Seg']
modes = list(data.keys())
colors = {'hint': 'tab:blue', 'deltaM': 'tab:orange', 'hybrid': 'tab:green'}

x = np.arange(len(models))
width = 0.25

fig, ax = plt.subplots(figsize=(10,6))

for i, mode in enumerate(modes):
    vals = [data[mode][m] for m in models]
    bars = ax.bar(x + i*width - width, vals, width, label=mode, color=colors[mode])
    # Label nur über Seg-Balken
    seg_idx = models.index('Seg')
    ax.text(x[seg_idx] + i*width - width, vals[seg_idx]*1.1,
            f"{data[mode]['perf']:.3f}×", ha='center', va='bottom', fontsize=9)

ax.set_yscale('log')
ax.set_ylabel('Median |Δz|')
ax.set_title('Vergleich GR, SR, GR*SR, Seg – alle Modi')
ax.set_xticks(x)
ax.set_xticklabels(models)
ax.legend(title='Modus')
ax.grid(True, which="both", axis='y', linestyle='--', alpha=0.5)

plt.tight_layout()
plt.show()

import matplotlib.pyplot as plt
import numpy as np

# Medianwerte aus deinen Reports (gerundet wie besprochen)
med = {
    'hint':   {'GR': 1.376e-4, 'SR': 1.511e-4, 'GR*SR': 1.890e-4, 'Seg': 1.255e-4, 'perf': 0.912},
    'deltaM': {'GR': 6.88306e-2, 'SR': 2.473303e-4, 'GR*SR': 2.812762e-4, 'Seg': 2.812854e-4, 'perf': 0.004086},
    'hybrid': {'GR': 6.883062e-2, 'SR': 2.473303e-4, 'GR*SR': 2.812762e-4, 'Seg': 2.812854e-4, 'perf': 0.004087},
}
modes   = ['hint','deltaM','hybrid']
models  = ['GR','SR','GR*SR','Seg']
colors  = {'hint':'tab:blue','deltaM':'tab:orange','hybrid':'tab:green'}

# Datenmatrizen
Y = np.array([[med[m][k] for k in models] for m in modes])  # shape (3,4)
perf = np.array([med[m]['perf'] for m in modes])

# Figure
fig = plt.figure(figsize=(12,5))
gs = fig.add_gridspec(1,2, width_ratios=[2.4,1.0], wspace=0.25)

# --- (A) Median |Δz| je Modell & Modus ---
ax1 = fig.add_subplot(gs[0,0])
x = np.arange(len(models))
W = 0.24
for i,mode in enumerate(modes):
    vals = Y[i]
    ax1.bar(x + (i-1)*W, vals, W, color=colors[mode], label=mode)
    # Label nur auf Seg-Balken
    si = models.index('Seg')
    ax1.text(x[si] + (i-1)*W, vals[si]*1.15, f"{med[mode]['perf']:.3f}× vs GR",
             ha='center', va='bottom', fontsize=9, color=colors[mode])

ax1.set_yscale('log')
ax1.set_xticks(x)
ax1.set_xticklabels(models)
ax1.set_ylabel('Median |Δz| (log)')
ax1.set_title('Medianfehler pro Modell (alle Modi)')
ax1.grid(True, which='both', axis='y', ls='--', alpha=0.4)
ax1.legend(title='Modus', ncol=3, loc='upper right')

# --- (B) Performance vs GR (nur Seg) ---
ax2 = fig.add_subplot(gs[0,1])
xb = np.arange(len(modes))
bars = ax2.bar(xb, perf, color=[colors[m] for m in modes])
for i,v in enumerate(perf):
    ax2.text(i, v*1.25, f"{v:.4f}×", ha='center', va='bottom', fontsize=10)
ax2.set_yscale('log')
ax2.set_xticks(xb)
ax2.set_xticklabels(modes)
ax2.set_ylabel('Seg / GR (Median)')
ax2.set_title('Performance-Faktor (Seg vs GR)')
ax2.grid(True, which='both', axis='y', ls='--', alpha=0.4)

fig.suptitle('Segmented Spacetime – Vergleich über alle Modi', fontsize=13)
plt.tight_layout()
plt.savefig('segspace_comparison.png', dpi=200)
plt.savefig('segspace_comparison.svg')
plt.show()

from scipy.constants import h, c, m_e
f_emit = 1.384e14  # Hz
f_obs  = 1.349e14  # Hz

# Lokale Segmentierungsdichte
alpha = 1 - f_obs / f_emit

# Gebundene Masse
m_bound = (f_emit * h) / (alpha * c**2)

# Bestätige gebundene Photonenenergie
E_gamma = alpha * m_bound * c**2

print(f"α = {alpha:.8f}")
print(f"m_e (bound) = {m_bound:.4e} kg")
print(f"E_gamma = {E_gamma:.4e} J")

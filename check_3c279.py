import pandas as pd
df = pd.read_csv('data/real_data_emission_lines_clean.csv')
row = df[df['case'].str.contains('3C279', na=False)].iloc[0]
print('3C279_jet data:')
print(f'  case = {row["case"]}')
print(f'  z_obs = {row["z"]}')
print(f'  z_geom_hint = {row.get("z_geom_hint", "N/A")}')
print(f'  v_tot = {row["v_tot_mps"]/299792458:.4f}c')
print(f'  v_los = {row["v_los_mps"]/299792458:.4f}c')
print(f'  M_solar = {row["M_solar"]:.2e}')
print(f'  r_emit_m = {row["r_emit_m"]:.2e}')

# Calculate r_s
G = 6.67430e-11
C = 299792458
M_kg = row["M_solar"] * 1.98847e30
r_s = 2 * G * M_kg / (C**2)
x = row["r_emit_m"] / r_s
print(f'  r_s = {r_s:.2e} m')
print(f'  x = r/r_s = {x:.4f}')

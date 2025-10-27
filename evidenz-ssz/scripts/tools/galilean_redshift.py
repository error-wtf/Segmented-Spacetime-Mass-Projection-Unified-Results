import pandas as pd
import matplotlib.pyplot as plt

# 1. Daten laden
df = pd.read_csv("real_data_emission_lines_best.csv")

# 2. Lichtgeschwindigkeit in km/s
c_kms = 299792.458

# 3. Galilei-Vorhersagefunktion
def galilean_redshift(row):
    v = row['v_los']  # line-of-sight velocity in km/s
    return v / c_kms  # classical approximation

# 4. Berechnung und Fehleranalyse
df["z_galilean"] = df.apply(galilean_redshift, axis=1)
df["abs_error"] = (df["z_obs"] - df["z_galilean"]).abs()

# 5. Fehlerstatistiken ausgeben
print("Mean absolute error:", df["abs_error"].mean())
print("Max error:", df["abs_error"].max())

# 6. Plot erzeugen
plt.plot(df["z_obs"], 'ko-', label="Observed z")
plt.plot(df["z_galilean"], 'r--', label="Galilean model (z = v/c)")
plt.xlabel("Object index")
plt.ylabel("Redshift z")
plt.title("Observed vs Galilean-Predicted Redshift")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()

import pandas as pd
import plotly.express as px

# 1) Cargar df_final
df = pd.read_csv("data/df_final.csv")

# 2) Crear df_subeje
df_subeje = df.dropna(subset=["Sub Eje"])

# ============================
# ANALISIS A: SubEje GENERAL
# ============================

subeje_counts = df_subeje["Sub Eje"].value_counts().reset_index()
subeje_counts.columns = ["SubEje", "Cantidad"]
subeje_counts["Porcentaje"] = subeje_counts["Cantidad"] / subeje_counts["Cantidad"].sum() * 100

print(subeje_counts.head(20))

# ============================
# ANALISIS B: SubEje POR Eje
# ============================

subeje_por_eje = df_subeje.groupby(["Eje", "Sub Eje"]).size().reset_index(name="Cantidad")
print(subeje_por_eje.head(20))

# Ejemplo: graficar solo Encuentro
df_encuentro = subeje_por_eje[subeje_por_eje["Eje"] == "Encuentro"]

fig = px.bar(
    df_encuentro,
    x="Sub Eje",
    y="Cantidad",
    title="SubEjes del Eje Encuentro",
    text="Cantidad"
)
fig.update_layout(xaxis_tickangle=45)
fig.show()



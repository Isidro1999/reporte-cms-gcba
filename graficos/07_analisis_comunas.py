import pandas as pd
import plotly.express as px

# Cargar dataset final limpio
df_final = pd.read_csv("data/df_final.csv")

# Asegurar normalización
df_final["Comuna"] = df_final["Comuna"].astype(str).str.replace("Comuna ", "").str.strip()
df_final["Comuna"] = df_final["Comuna"].replace(["nan", "None", "", "0"], None)

# Filtrar filas válidas
df_comunas = df_final.dropna(subset=["Comuna"])

# ============================
# 1) Total de materiales por Comuna
# ============================

conteo_comuna = df_comunas["Comuna"].value_counts().reset_index()
conteo_comuna.columns = ["Comuna", "Cantidad"]

print("\n=== Cantidad total de materiales por Comuna ===\n")
print(conteo_comuna)

fig = px.bar(
    conteo_comuna,
    x="Comuna",
    y="Cantidad",
    text="Cantidad",
    title="Cantidad de materiales por Comuna (últimos 2 años)",
)
fig.update_traces(textposition="outside")
fig.show()

# ============================
# 2) Ejes por Comuna
# ============================

pivot_ejes = df_comunas.pivot_table(
    index="Comuna",
    columns="Eje",
    values="Material ID",
    aggfunc="count",
    fill_value=0
)

print("\n=== Distribución de Ejes por Comuna ===\n")
print(pivot_ejes)

fig = px.bar(
    pivot_ejes,
    barmode="stack",
    title="Distribución de Ejes por Comuna (stacked)",
)
fig.show()

# ============================
# 3) SubEjes más frecuentes por Comuna
# ============================

subejes_por_comuna = df_comunas.groupby(["Comuna", "Sub Eje"]).size().reset_index(name="Cantidad")

top_subejes = subejes_por_comuna.groupby("Comuna").apply(lambda x: x.nlargest(5, "Cantidad")).reset_index(drop=True)

print("\n=== Top SubEjes por Comuna ===\n")
print(top_subejes)

fig = px.bar(
    top_subejes,
    x="Comuna",
    y="Cantidad",
    color="Sub Eje",
    title="Top SubEjes por Comuna (últimos 2 años)",
    text="Cantidad"
)
fig.update_traces(textposition="outside")
fig.show()

res = df_comunas.groupby("Comuna").agg({
    "Eje": "nunique",
    "Sub Eje": "nunique",
    "Tema": "nunique",
    "Subtema": "nunique",
    "Material ID": "count"
})
print(res)

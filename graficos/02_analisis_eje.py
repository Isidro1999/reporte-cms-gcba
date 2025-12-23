import pandas as pd
import plotly.express as px

df = pd.read_csv("data/df_final.csv")

# DISTRIBUCIÓN POR EJE
eje_counts = df["Eje"].value_counts().reset_index()
eje_counts.columns = ["Eje", "Cantidad"]
eje_counts["Porcentaje"] = eje_counts["Cantidad"] / eje_counts["Cantidad"].sum() * 100

print(eje_counts)

# GRÁFICO
fig = px.bar(
    eje_counts,
    x="Eje",
    y="Cantidad",
    text="Cantidad",
    title="Cantidad de materiales por Eje (últimos 2 años)"
)
fig.show()

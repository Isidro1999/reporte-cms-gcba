import pandas as pd
import plotly.express as px

df = pd.read_csv("data/df_final.csv")

df_subeje = df.dropna(subset=["Sub Eje"])

# Agrupación jerárquica
subeje_por_eje = df_subeje.groupby(["Eje", "Sub Eje"]).size().reset_index(name="Cantidad")


def graficar_subejes(eje):
    df_eje = subeje_por_eje[subeje_por_eje["Eje"] == eje].sort_values("Cantidad", ascending=False)
    
    fig = px.bar(
        df_eje,
        x="Sub Eje",
        y="Cantidad",
        title=f"SubEjes del Eje {eje}",
        text="Cantidad"
    )
    fig.update_layout(xaxis_tickangle=45)
    fig.update_traces(textposition="outside")
    
    fig.show()

subeje_por_eje[subeje_por_eje["Eje"] == "Orden"].sort_values("Cantidad", ascending=False).head(10)


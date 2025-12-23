import pandas as pd
import plotly.express as px

df = pd.read_csv("data/df_final.csv")

df_subeje = df.dropna(subset=["Sub Eje"])



# Top global de SubEjes
top_subejes = df_subeje["Sub Eje"].value_counts().reset_index()
top_subejes.columns = ["SubEje", "Cantidad"]

print(top_subejes.head(20))


fig = px.bar(
    top_subejes.head(20),
    x="SubEje",
    y="Cantidad",
    title="Top 20 SubEjes globales (últimos 2 años)",
    text="Cantidad"
)

fig.update_layout(xaxis_tickangle=45)
fig.update_traces(textposition="outside")
fig.show()

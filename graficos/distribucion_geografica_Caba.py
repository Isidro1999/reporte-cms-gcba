import pandas as pd
import plotly.express as px
import json

# -------------------------------
# 1) Cargar DF final + recuento
# -------------------------------
df = pd.read_csv("data/df_final.csv")

df_comuna = df.groupby("Comuna").size().reset_index(name="Cantidad")

# Aseguramos que Comuna sea numérica
df_comuna["Comuna"] = df_comuna["Comuna"].astype(float)

# -------------------------------
# 2) Cargar GeoJSON de comunas
# -------------------------------
with open("geo/comunas_caba.geojson", "r") as f:
    comunas_geo = json.load(f)

# -------------------------------
# 3) Choropleth Map
# -------------------------------
fig = px.choropleth_mapbox(
    df_comuna,
    geojson=comunas_geo,
    locations="Comuna",
    featureidkey="properties.comuna",
    color="Cantidad",
    color_continuous_scale="Blues",
    mapbox_style="carto-positron",
    zoom=10,
    center={"lat": -34.61, "lon": -58.44},
    opacity=0.6,
    hover_name="Comuna",
    hover_data={"Cantidad": True}
)

fig.update_layout(
    title="Mapa: Cantidad de materiales por Comuna (últimos 2 años)",
    margin={"r":0, "t":30, "l":0, "b":0}
)

fig.show()


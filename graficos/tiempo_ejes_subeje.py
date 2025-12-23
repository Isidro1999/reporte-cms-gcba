import pandas as pd
import plotly.express as px

# ================================
# 1) Cargar y preparar dataset
# ================================
df = pd.read_csv("data/df_final.csv")

# Asegurar formato consistente
df["Eje"] = df["Eje"].astype(str).str.strip()
df["Sub Eje"] = df["Sub Eje"].astype(str).str.strip()
df["Mes"] = df["Mes"].astype(str).str.lower().str.strip()

# Mapa mes español → número
mes_map = {
    "enero": 1, "febrero": 2, "marzo": 3, "abril": 4,
    "mayo": 5, "junio": 6, "julio": 7, "agosto": 8,
    "septiembre": 9, "setiembre": 9,
    "octubre": 10, "noviembre": 11, "diciembre": 12
}

df["Mes_num"] = df["Mes"].map(mes_map)
df["Año"] = pd.to_numeric(df["Año"], errors="coerce")

# Filtrar filas válidas
df = df.dropna(subset=["Año", "Mes_num"])

# Construir fecha exacta
df["Fecha"] = pd.to_datetime(
    df["Año"].astype(int).astype(str) + "-" +
    df["Mes_num"].astype(int).astype(str) + "-01"
)

# ================================
# 2) Filtrar últimos 2 años
# ================================
fecha_max = df["Fecha"].max()
limite = fecha_max - pd.DateOffset(years=2)

df_2y = df[df["Fecha"] >= limite]

print("\nRango temporal analizado:")
print(df_2y["Fecha"].min(), "→", df_2y["Fecha"].max())

# ================================
# 3) Evolución mensual por EJE
# ================================
df_eje = (
    df_2y.groupby(["Fecha", "Eje"])
    .size()
    .reset_index(name="Cantidad")
)

print("\nVista previa por Eje:")
print(df_eje.head())

fig = px.line(
    df_eje,
    x="Fecha",
    y="Cantidad",
    color="Eje",
    markers=True,
    title="📈 Evolución mensual por Eje (últimos 2 años)"
)

fig.update_layout(
    xaxis_title="Fecha",
    yaxis_title="Cantidad",
    hovermode="x unified",
    template="simple_white"
)

fig.show()


# ================================
# 4) Evolución mensual por SUBEJE
# ================================
df_subeje = (
    df_2y.groupby(["Fecha", "Sub Eje"])
    .size()
    .reset_index(name="Cantidad")
)

print("\nVista previa por SubEje:")
print(df_subeje.head())

fig2 = px.line(
    df_subeje,
    x="Fecha",
    y="Cantidad",
    color="Sub Eje",
    markers=True,
    title="📈 Evolución mensual por SubEje (últimos 2 años)",
)

fig2.update_layout(
    xaxis_title="Fecha",
    yaxis_title="Cantidad",
    hovermode="x unified",
    template="simple_white"
)

fig2.show()



print("\n=== Gráfico acumulado por Eje ===")

df_area = df_eje.copy()

fig_area = px.area(
    df_area,
    x="Fecha",
    y="Cantidad",
    color="Eje",
    title="📌 Evolución acumulada por Eje (Stacked Area – últimos 2 años)",
)

fig_area.update_layout(
    xaxis_title="Fecha",
    yaxis_title="Cantidad de materiales",
    template="simple_white",
    hovermode="x unified"
)

fig_area.show()


print("\n=== Comparación Año vs Año por Eje ===")

df_eje["Año"] = df_eje["Fecha"].dt.year
df_eje["Mes"] = df_eje["Fecha"].dt.month

df_yoy = (
    df_eje.groupby(["Año", "Mes", "Eje"])
    .agg({"Cantidad": "sum"})
    .reset_index()
)

fig_yoy = px.line(
    df_yoy,
    x="Mes",
    y="Cantidad",
    color="Eje",
    line_dash="Año",
    title="📊 Comparativa Año vs Año por Eje (YoY)",
    markers=True
)

fig_yoy.update_layout(
    xaxis_title="Mes",
    yaxis_title="Cantidad de materiales",
    template="simple_white",
    hovermode="x unified"
)

fig_yoy.show()


print("\n=== Media móvil por Eje (tendencia suavizada) ===")

df_roll = df_eje.copy()
df_roll = df_roll.sort_values("Fecha")

# Aplicar rolling 3 meses por EJE
df_roll["Suavizado"] = (
    df_roll.groupby("Eje")["Cantidad"]
    .transform(lambda s: s.rolling(window=3, min_periods=1).mean())
)

fig_roll = px.line(
    df_roll,
    x="Fecha",
    y="Suavizado",
    color="Eje",
    title="📈 Tendencia suavizada por Eje (Media móvil 3 meses)",
    markers=False
)

fig_roll.update_layout(
    xaxis_title="Fecha",
    yaxis_title="Cantidad (media móvil)",
    template="simple_white",
    hovermode="x unified"
)

fig_roll.show()

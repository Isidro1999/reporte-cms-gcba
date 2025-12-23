import ast
import pandas as pd
import streamlit as st
import plotly.express as px
import os

def check_password():
    # Cambiá esta pass por la tuya momentáneamente
    PASSWORD = "gcba2025"

    if "password_ok" not in st.session_state:
        st.session_state.password_ok = False

    if not st.session_state.password_ok:
        st.markdown("### 🔐 Acceso restringido")
        password = st.text_input("Ingresá la contraseña", type="password")

        if st.button("Entrar"):
            if password == PASSWORD:
                st.session_state.password_ok = True
                st.rerun()
            else:
                st.error("Contraseña incorrecta")

        st.stop()

check_password()
st.image("data/logo_gcba.png", width=280)
st.image("data/logo_feater.png", width=180)



PALETA_PLOTLY = ["#800008", "#5B0C11", "#989898", "#FFFFFF", "#C55A5A", "#7A7A7A"]

def aplicar_tema_plotly(fig):
    fig.update_layout(
        plot_bgcolor="#000000",
        paper_bgcolor="#000000",
        font=dict(color="#FFFFFF"),
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            font=dict(color="#FFFFFF")
        ),
        coloraxis_colorbar=dict(
            bgcolor="#000000",
            tickfont=dict(color="#FFFFFF")
        )
    )

    try:
        fig.update_traces(marker=dict(colors=PALETA_PLOTLY), selector=dict(type="bar"))
    except:
        pass

    fig.update_layout(colorway=PALETA_PLOTLY)

    return fig


# =====================================================
# 0. CONFIG STREAMLIT
# =====================================================
st.set_page_config(
    page_title="Reporte Analítico CMS GCBA",
    layout="wide"
)



st.markdown("""
<style>

body, .stApp {
    background-color: #000000 !important;
    color: #FFFFFF !important;
}

/* TITULOS */
h1, h2, h3, h4, h5, h6, label {
    color: #FFFFFF !important;
    font-weight: 600;
}

/* SIDEBAR */
section[data-testid="stSidebar"] {
    background-color: #5B0C11 !important;
    border-right: 1px solid #800008 !important;
}

/* INPUTS */
div[data-baseweb="select"] {
    background-color: #5B0C11 !important;
    color: #FFFFFF !important;
}

.stSelectbox, .stMultiSelect {
    background-color: #5B0C11 !important;
}

/* KPI CARDS */
.kpi-card {
    padding: 15px;
    background-color: #800008;
    border-radius: 12px;
    border: 1px solid #5B0C11;
    text-align: center;
    margin-bottom: 10px;
}
.kpi-title {
    font-size: 16px;
    color: #D3D3D3;
}
.kpi-value {
    font-size: 26px;
    font-weight: bold;
    color: #FFFFFF;
}

/* FOOTER */
.footer {
    text-align: center;
    margin-top: 50px;
    padding: 15px;
    color: #AAAAAA;
    font-size: 14px;
}

</style>
""", unsafe_allow_html=True)


# =====================================================
# 1. CARGA Y PREPARACIÓN DE DATOS
# =====================================================

@st.cache_data
def load_data():
    df = pd.read_csv("data/df_final.csv")

    df["Eje"] = df["Eje"].astype(str).str.strip()
    df["Sub Eje"] = df["Sub Eje"].astype(str).str.strip()
    df["Tema"] = df["Tema"].astype(str).str.strip()
    df["Subtema"] = df["Subtema"].astype(str).str.strip()
    df["Mes"] = df["Mes"].astype(str).str.lower().str.strip()
    df["Comuna"] = pd.to_numeric(df["Comuna"], errors="coerce")
    df["Tipo de material"] = df["Tipo de material"].astype(str).str.strip()

    df = df[df["Comuna"].between(1, 15)]

    meses = {"enero":1,"febrero":2,"marzo":3,"abril":4,"mayo":5,"junio":6,
             "julio":7,"agosto":8,"septiembre":9,"setiembre":9,"octubre":10,
             "noviembre":11,"diciembre":12}
    df["Mes_num"] = df["Mes"].map(meses)
    df["Año"] = pd.to_numeric(df["Año"], errors="coerce")

    df = df.dropna(subset=["Año", "Mes_num"])
    df["Fecha"] = pd.to_datetime(
        df["Año"].astype(int).astype(str) + "-" +
        df["Mes_num"].astype(int).astype(str) + "-01"
    )

    def parse_tags(x):
        if isinstance(x, list): return x
        if isinstance(x, str):
            try: return ast.literal_eval(x)
            except: return []
        return []
    df["Tags_list"] = df.get("Tags_list", []).apply(parse_tags)

    def extraer_subtipos(tags):
        sub = []
        for t in tags:
            if isinstance(t, str) and t.startswith("Material - "):
                stp = t.replace("Material - ", "").strip().lower()
                sub.append(stp.capitalize())
        return sub

    df["Subtipos_material"] = df["Tags_list"].apply(extraer_subtipos)
    return df

df = load_data()

# Fechas
fecha_max = df["Fecha"].max()
limite_2y = fecha_max - pd.DateOffset(years=2)

# =====================================================
# 2. SIDEBAR
# =====================================================
st.sidebar.header("Filtros")

from datetime import date

fecha_inicio_default = date(2024, 1, 1)
fecha_fin_default = date.today()

rango_fechas = st.sidebar.date_input(
    "Rango de fechas",
    value=(fecha_inicio_default, fecha_fin_default),
    min_value=fecha_inicio_default,
    max_value=fecha_fin_default
)

inicio, fin = rango_fechas


ejes_disp = sorted(df["Eje"].unique())
ejes_sel = st.sidebar.multiselect("Ejes", ejes_disp, default=ejes_disp)

tipos_disp = sorted(df["Tipo de material"].unique())
tipos_sel = st.sidebar.multiselect("Tipo de material", tipos_disp, default=tipos_disp)

subtipos_disp = sorted(df.explode("Subtipos_material")["Subtipos_material"].dropna().unique())
subtipos_sel = st.sidebar.multiselect("Subtipos", subtipos_disp, default=subtipos_disp)

mask = (
    (df["Fecha"].dt.date >= inicio) &
    (df["Fecha"].dt.date <= fin) &
    (df["Eje"].isin(ejes_sel)) &
    (df["Tipo de material"].isin(tipos_sel))
)

df_filtrado = df[mask].copy()

# =====================================================
# 3. KPIs
# =====================================================
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total materiales", f"{len(df_filtrado):,}".replace(",", "."))
col2.metric("Ejes activos", df_filtrado["Eje"].nunique())
col3.metric("Comunas alcanzadas", df_filtrado["Comuna"].nunique())
col4.metric("Último mes cargado", df_filtrado["Fecha"].max().strftime("%m/%Y"))

st.markdown("---")

# =====================================================
# 4. TABS
# =====================================================
tab_resumen, tab_ejes, tab_territorio, tab_materiales, tab_insights = st.tabs([
    "📌 Resumen", "🏛️ Ejes & Temas", "🗺️ Territorio", "🎥 Materiales", "🧠 Insights"
])

# -----------------------------------------------------
# 🟦 TAB RESUMEN
# -----------------------------------------------------
with tab_resumen:
    st.subheader("Distribución general por Eje")

    df_eje = df_filtrado.groupby("Eje").size().reset_index(name="Cantidad")
    fig_eje = aplicar_tema_plotly(px.bar(df_eje, x="Eje", y="Cantidad", text="Cantidad"))
    st.plotly_chart(fig_eje, use_container_width=True)

    st.subheader("Evolución mensual total")
    df_mes = df_filtrado.groupby("Fecha").size().reset_index(name="Cantidad")
    fig_total = aplicar_tema_plotly(px.line(df_mes, x="Fecha", y="Cantidad", markers=True))
    st.plotly_chart(fig_total, use_container_width=True)

# -----------------------------------------------------
# 🟩 TAB EJES & TEMAS
# -----------------------------------------------------
with tab_ejes:

    # Sunburst
    st.subheader("Jerarquía Eje → SubEje → Tema → Subtema")
    df_h = df_filtrado[["Eje", "Sub Eje", "Tema", "Subtema"]].fillna("Sin dato")
    fig_sun = aplicar_tema_plotly(
        px.sunburst(df_h, path=["Eje", "Sub Eje", "Tema", "Subtema"])
    )
    st.plotly_chart(fig_sun, use_container_width=True)

    # Evolución por eje
    st.subheader("Evolución mensual por Eje")
    df_eje_tiempo = df_filtrado.groupby(["Fecha", "Eje"]).size().reset_index(name="Cantidad")
    fig_eje_tiempo = aplicar_tema_plotly(px.line(df_eje_tiempo, x="Fecha", y="Cantidad", color="Eje", markers=True))
    st.plotly_chart(fig_eje_tiempo, use_container_width=True)

    # Top subejes
    st.subheader("Top 20 SubEjes")
    df_subeje = df_filtrado.groupby("Sub Eje").size().reset_index(name="Cantidad").nlargest(20, "Cantidad")
    fig_subeje = aplicar_tema_plotly(px.bar(df_subeje, x="Sub Eje", y="Cantidad", text="Cantidad"))
    st.plotly_chart(fig_subeje, use_container_width=True)

    # Heatmaps
    st.subheader("Heatmap — Eje vs Mes")
    df_heat_eje = df_filtrado.groupby(["Eje", "Mes_num"]).size().reset_index(name="Cantidad")
    heat_eje = df_heat_eje.pivot(index="Eje", columns="Mes_num", values="Cantidad")
    fig_heat1 = aplicar_tema_plotly(px.imshow(heat_eje, color_continuous_scale="Blues"))
    st.plotly_chart(fig_heat1, use_container_width=True)

    st.subheader("Heatmap — SubEje vs Mes")
    df_heat_subeje = df_filtrado.groupby(["Sub Eje", "Mes_num"]).size().reset_index(name="Cantidad")
    heat_subeje = df_heat_subeje.pivot(index="Sub Eje", columns="Mes_num", values="Cantidad")
    fig_heat2 = aplicar_tema_plotly(px.imshow(heat_subeje, color_continuous_scale="Reds"))
    st.plotly_chart(fig_heat2, use_container_width=True)

    # YoY
    st.subheader("Comparativa Año vs Año por Eje (YoY)")
    ejes_yoy_disponibles = sorted(df_filtrado["Eje"].unique())

    eje_yoy = st.selectbox(
        "Seleccioná un Eje:",
        options=ejes_yoy_disponibles,
        index=0
    )

    df_yoy = df_filtrado[df_filtrado["Eje"] == eje_yoy]
    df_yoy = df_yoy.groupby(["Año", "Mes_num"]).size().reset_index(name="Cantidad")

    fig_yoy_single = aplicar_tema_plotly(
        px.line(df_yoy, x="Mes_num", y="Cantidad", color="Año", markers=True)
    )
    st.plotly_chart(fig_yoy_single, use_container_width=True)



# -----------------------------------------------------
# 🟧 TAB TERRITORIO
# -----------------------------------------------------
with tab_territorio:

    st.subheader("Materiales por Comuna")

    df_com = df_filtrado.groupby("Comuna").size().reset_index(name="Cantidad")
    fig_com = aplicar_tema_plotly(px.bar(df_com, x="Comuna", y="Cantidad", text="Cantidad"))
    st.plotly_chart(fig_com, use_container_width=True)

    st.subheader("Mapa territorial")

    import geopandas as gpd
    import json

    try:
        gdf = gpd.read_file("data/comunas_caba.geojson")
        gdf["comuna"] = gdf["comuna"].astype(int)

        df_map = df_filtrado.groupby("Comuna").size().reset_index(name="Cantidad")
        gdf_merge = gdf.merge(df_map, left_on="comuna", right_on="Comuna", how="left").fillna(0)

        fig_map = px.choropleth_mapbox(
            gdf_merge,
            geojson=json.loads(gdf.to_json()),
            locations="comuna",
            color="Cantidad",
            center={"lat": -34.61, "lon": -58.44},
            zoom=10.3,
            mapbox_style="carto-positron"
        )
        
        fig_map = aplicar_tema_plotly(fig_map)
        st.plotly_chart(fig_map, use_container_width=True)

    except Exception as e:
        st.error("No se pudo cargar el mapa")
        st.code(str(e))

# -----------------------------------------------------
# 🟪 TAB MATERIALES
# -----------------------------------------------------
with tab_materiales:
    st.subheader("Distribución por tipo de material")


    df_tipo = df_filtrado.groupby("Tipo de material").size().reset_index(name="Cantidad")
    fig_tipo = aplicar_tema_plotly(px.pie(df_tipo, names="Tipo de material", values="Cantidad", hole=0.4))
    st.plotly_chart(fig_tipo, use_container_width=True)

    st.subheader("Evolución por Subtipo")

    df_sub = df_filtrado.explode("Subtipos_material")
    df_sub = df_sub[df_sub["Subtipos_material"].isin(subtipos_sel)]
    df_sub = df_sub.groupby(["Fecha","Subtipos_material"]).size().reset_index(name="Cantidad")

    fig_evo_sub = aplicar_tema_plotly(px.line(df_sub, x="Fecha", y="Cantidad", color="Subtipos_material", markers=True))
    st.plotly_chart(fig_evo_sub, use_container_width=True)

# -----------------------------------------------------
# 🧠 TAB INSIGHTS
# -----------------------------------------------------
with tab_insights:
    st.subheader("Insights automáticos")

    try:
        top_eje = df_filtrado["Eje"].value_counts().idxmax()
        top_subeje = df_filtrado["Sub Eje"].value_counts().idxmax()
        top_mes = df_filtrado["Mes_num"].value_counts().idxmax()
        pico = df_filtrado["Fecha"].dt.to_period("M").value_counts().idxmax()

        st.markdown(f"""
        ### Conclusiones principales  
        - 🔹 **Eje más activo:** {top_eje}  
        - 🔹 **SubEje líder:** {top_subeje}  
        - 🔹 **Mes con mayor carga:** {top_mes}  
        - 🔹 **Pico de actividad:** {pico}  
        """)
    except:
        st.info("No hay suficientes datos para generar insights.")






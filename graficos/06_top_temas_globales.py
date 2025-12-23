import pandas as pd
import plotly.express as px

# ===========================================
# 1) Cargar el dataset final limpio
# ===========================================
df_final = pd.read_csv("data/df_final.csv")

# Aseguramos que las columnas clave existan y estén limpias
for col in ["Tema", "Subtema"]:
    df_final[col] = df_final[col].astype(str).str.strip()
    df_final[col] = df_final[col].replace("nan", None)

# ===========================================
# 2) TOP TEMAS (conteo global)
# ===========================================
print("\n=== TOP 20 TEMAS ===\n")
top_temas = df_final["Tema"].value_counts().reset_index()
top_temas.columns = ["Tema", "Cantidad"]
print(top_temas.head(20))

fig = px.bar(
    top_temas.head(20),
    x="Tema",
    y="Cantidad",
    text="Cantidad",
    title="Top 20 Temas globales (últimos 2 años)"
)
fig.update_traces(textposition="outside")
fig.update_layout(xaxis_tickangle=45)
fig.show()

# ===========================================
# 3) TOP SUBTEMAS
# ===========================================
print("\n=== TOP 20 SUBTEMAS ===\n")
top_subtemas = df_final["Subtema"].value_counts().reset_index()
top_subtemas.columns = ["Subtema", "Cantidad"]
print(top_subtemas.head(20))

fig = px.bar(
    top_subtemas.head(20),
    x="Subtema",
    y="Cantidad",
    text="Cantidad",
    title="Top 20 Subtemas globales (últimos 2 años)"
)
fig.update_traces(textposition="outside")
fig.update_layout(xaxis_tickangle=45)
fig.show()

# ===========================================
# 4) JERARQUÍA COMPLETA (Eje → SubEje → Tema → Subtema)
# ===========================================

df_hierarchy = df_final[["Eje", "Sub Eje", "Tema", "Subtema"]].copy()

# --- Normalización de texto ---
for col in ["Eje", "Sub Eje", "Tema", "Subtema"]:
    df_hierarchy[col] = df_hierarchy[col].astype(str).str.strip()
    df_hierarchy[col] = df_hierarchy[col].replace(
        ["nan", "None", "NaN", "NULL", "-", ""], None
    )

# --- Reglas obligatorias ---

# 1) El Eje no puede ser nulo → eliminar filas inválidas
df_hierarchy = df_hierarchy.dropna(subset=["Eje"])

# 2) Sub Eje vacío → "Sin SubEje"
df_hierarchy["Sub Eje"] = df_hierarchy["Sub Eje"].fillna("Sin SubEje")

# 3) Tema vacío → "Sin Tema"
df_hierarchy["Tema"] = df_hierarchy["Tema"].fillna("Sin Tema")

# 4) Subtema vacío SIEMPRE debe tener valor
df_hierarchy["Subtema"] = df_hierarchy["Subtema"].fillna("No especificado")

# Además: si queda algún string vacío después de reemplazos → cubrirlos
df_hierarchy.loc[df_hierarchy["Subtema"].astype(str).str.strip() == "", "Subtema"] = "No especificado"

# Verificación fuerte: imprimir filas problemáticas (debería dar 0)
problemas = df_hierarchy[
    (df_hierarchy["Subtema"].isna()) |
    (df_hierarchy["Subtema"].astype(str).str.strip() == "")
]

print("\nFILA(S) PROBLEMÁTICAS DETECTADAS PARA SUNBURST:")
print(problemas.head())
print(f"Total problematicas: {len(problemas)}")

# ===========================================
# Construcción del sunburst
# ===========================================

fig = px.sunburst(
    df_hierarchy,
    path=["Eje", "Sub Eje", "Tema", "Subtema"],
    color="Eje",
    color_discrete_sequence=px.colors.qualitative.Set3,
    title="Distribución jerárquica Eje → SubEje → Tema → Subtema (últimos 2 años)"
)

fig.update_traces(textinfo="label+value")
fig.show()





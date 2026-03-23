# ================================================
#  COMO USAR EL PROGRAMA
# INICIAR EL ENTORNO VISUAL. PEGAR ESTE CODIGO EN LA TERMINAL Y DEBERIA FUNCIONAR.
# .\.venv\Scripts\activate
# python -m streamlit run app.py
# ===================================================
import streamlit as st
import pandas as pd
import plotly.express as px
import requests

# =========================================================
# CONFIG
# =========================================================
st.set_page_config(
    page_title="SECLA Futsal Dashboard",
    page_icon="⚽",
    layout="wide"
)

archivo = "data/SECLA_Sistema_Datos.xlsx"
url_tabla = "https://parenlapelotafutsal.com.ar/fem/primeraA/primera"
ruta_escudo = "assets/escudo_secla.png"

# =========================================================
# ESTILO RESPONSIVE FINAL
# =========================================================
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(180deg, #08111f 0%, #0b1220 100%);
    }

    .block-container {
        padding-top: 1rem;
        padding-bottom: 1.5rem;
        max-width: 1450px;
    }

    h1, h2, h3, h4, h5, h6, p, label, div {
        color: white;
    }

    section[data-testid="stSidebar"] {
        background-color: #0f172a;
        border-right: 1px solid #1f2937;
    }

    .header-box {
        background: linear-gradient(180deg, #111827 0%, #0f172a 100%);
        border: 1px solid #1f2937;
        border-radius: 20px;
        padding: 14px 18px;
        box-shadow: 0 10px 26px rgba(0,0,0,0.28);
        margin-bottom: 16px;
    }

    .section-title {
        font-size: 1.15rem;
        font-weight: 800;
        margin-bottom: 10px;
    }

    .card {
        background: linear-gradient(180deg, #111827 0%, #0f172a 100%);
        padding: 16px;
        border-radius: 16px;
        border: 1px solid #1f2937;
        box-shadow: 0 8px 24px rgba(0,0,0,0.25);
        text-align: center;
        min-height: 115px;
    }

    .card h3 {
        margin: 0;
        font-size: 1.15rem;
        line-height: 1.2;
    }

    .card p {
        color: #93c5fd;
        font-weight: 700;
        font-size: 0.95rem;
        margin-top: 10px;
    }

    .kpi-card {
        background: linear-gradient(180deg, #111827 0%, #0f172a 100%);
        border: 1px solid #1f2937;
        border-radius: 16px;
        padding: 14px;
        box-shadow: 0 8px 24px rgba(0,0,0,0.22);
        min-height: 90px;
    }

    .kpi-label {
        color: #93c5fd;
        font-size: 0.85rem;
        font-weight: 700;
    }

    .kpi-value {
        font-size: 1.6rem;
        font-weight: 900;
        line-height: 1.1;
        margin-top: 6px;
    }

    @media (max-width: 768px) {
        .block-container {
            padding-top: 0.7rem;
            padding-left: 0.8rem;
            padding-right: 0.8rem;
            padding-bottom: 1.2rem;
        }

        .header-box {
            padding: 12px 14px;
            border-radius: 16px;
        }

        .section-title {
            font-size: 1rem;
            margin-bottom: 8px;
        }

        .card {
            min-height: 95px;
            padding: 12px;
            border-radius: 14px;
        }

        .card h3 {
            font-size: 1rem;
        }

        .card p {
            font-size: 0.9rem;
            margin-top: 8px;
        }

        .kpi-card {
            padding: 12px;
            border-radius: 14px;
            min-height: 82px;
        }

        .kpi-label {
            font-size: 0.78rem;
        }

        .kpi-value {
            font-size: 1.3rem;
        }
    }
</style>
""", unsafe_allow_html=True)

# =========================================================
# FUNCIONES
# =========================================================
def tarjeta_kpi(label, value):
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}</div>
    </div>
    """, unsafe_allow_html=True)

def titulo(txt):
    st.markdown(f'<div class="section-title">{txt}</div>', unsafe_allow_html=True)

def buscar_hoja(nombre_buscado: str, hojas):
    nombre_buscado = nombre_buscado.strip().lower()
    for hoja in hojas:
        if hoja.strip().lower() == nombre_buscado:
            return hoja
    raise ValueError(f"No encontré una hoja llamada '{nombre_buscado}' en: {hojas}")

def asegurar_columnas(df: pd.DataFrame, columnas: list[str]) -> pd.DataFrame:
    for col in columnas:
        if col not in df.columns:
            if col in ["Goles", "Asistencias", "Minutos", "Amarillas", "Rojas", "ID_Jugadora", "ID_Partido", "Orden"]:
                df[col] = 0
            else:
                df[col] = ""
    return df

# =========================================================
# LEER HOJAS
# =========================================================
xls = pd.ExcelFile(archivo)
sheet_names = xls.sheet_names

hoja_jugadoras = buscar_hoja("Jugadoras", sheet_names)
hoja_partidos = buscar_hoja("Partidos", sheet_names)
hoja_stats = buscar_hoja("Stats_Jugadora_Partido", sheet_names)
hoja_fixture = buscar_hoja("FIXTURE", sheet_names)

# =========================================================
# CARGA DE DATOS
# =========================================================
@st.cache_data
def cargar_datos():
    jugadoras = pd.read_excel(archivo, sheet_name=hoja_jugadoras)
    partidos = pd.read_excel(archivo, sheet_name=hoja_partidos)
    stats = pd.read_excel(archivo, sheet_name=hoja_stats)
    fixture = pd.read_excel(archivo, sheet_name=hoja_fixture)

    jugadoras.columns = jugadoras.columns.str.strip()
    partidos.columns = partidos.columns.str.strip()
    stats.columns = stats.columns.str.strip()
    fixture.columns = fixture.columns.str.strip()

    return jugadoras, partidos, stats, fixture

@st.cache_data(ttl=1800)
def cargar_tabla_posiciones():
    tablas = []

    try:
        tablas = pd.read_html(url_tabla)
    except Exception:
        tablas = []

    if not tablas:
        headers = {"User-Agent": "Mozilla/5.0"}
        r = requests.get(url_tabla, headers=headers, timeout=20)
        r.raise_for_status()
        tablas = pd.read_html(r.text)

    if not tablas:
        raise ValueError("No se encontraron tablas en la página.")

    tabla_posiciones = None

    for tabla in tablas:
        tabla.columns = [str(c).strip() for c in tabla.columns]
        cols_upper = [c.upper() for c in tabla.columns]
        if "POS" in cols_upper and "EQUIPO" in cols_upper and "PTS" in cols_upper:
            tabla_posiciones = tabla.copy()
            break

    if tabla_posiciones is None:
        raise ValueError("No encontré una tabla con columnas Pos / Equipo / PTS.")

    tabla_posiciones.columns = [str(c).strip() for c in tabla_posiciones.columns]

    renombrar = {}
    for col in tabla_posiciones.columns:
        c = col.upper()
        if c == "POS":
            renombrar[col] = "Pos"
        elif c == "EQUIPO":
            renombrar[col] = "Equipo"
        elif c == "PJ":
            renombrar[col] = "PJ"
        elif c == "G":
            renombrar[col] = "G"
        elif c == "E":
            renombrar[col] = "E"
        elif c == "P":
            renombrar[col] = "P"
        elif c == "GF":
            renombrar[col] = "GF"
        elif c == "GC":
            renombrar[col] = "GC"
        elif c == "DG":
            renombrar[col] = "DG"
        elif c == "PTS":
            renombrar[col] = "PTS"

    tabla_posiciones = tabla_posiciones.rename(columns=renombrar)

    if "Pos" in tabla_posiciones.columns:
        tabla_posiciones["Pos"] = pd.to_numeric(tabla_posiciones["Pos"], errors="coerce")
        tabla_posiciones = tabla_posiciones.sort_values("Pos")

    columnas_visibles = [c for c in ["Pos", "Equipo", "PJ", "GF", "GC", "DG", "PTS"] if c in tabla_posiciones.columns]
    return tabla_posiciones[columnas_visibles]

jugadoras, partidos, stats, fixture = cargar_datos()

# =========================================================
# NORMALIZAR
# =========================================================
jugadoras = asegurar_columnas(jugadoras, ["ID_Jugadora", "Nombre", "Apellido"])
partidos = asegurar_columnas(partidos, ["ID_Partido"])
stats = asegurar_columnas(stats, ["ID_Jugadora", "ID_Partido", "Minutos", "Goles", "Asistencias", "Amarillas", "Rojas"])
fixture = asegurar_columnas(fixture, ["Orden", "Rival", "Local_Visitante"])

jugadoras["Jugador"] = (
    jugadoras["Nombre"].fillna("").astype(str) + " " + jugadoras["Apellido"].fillna("").astype(str)
).str.strip()

stats = stats.merge(
    jugadoras[["ID_Jugadora", "Jugador"]],
    on="ID_Jugadora",
    how="left"
)
stats["Jugador"] = stats["Jugador"].fillna("Sin nombre")

# =========================================================
# CREAR NOMBRE DE PARTIDO AMIGABLE
# =========================================================
fixture["Orden"] = pd.to_numeric(fixture["Orden"], errors="coerce")

if "Orden" in partidos.columns:
    partidos["Orden"] = pd.to_numeric(partidos["Orden"], errors="coerce")
    partidos = partidos.merge(
        fixture[["Orden", "Rival", "Local_Visitante"]],
        on="Orden",
        how="left",
        suffixes=("", "_fix")
    )
else:
    partidos["Rival"] = ""
    partidos["Local_Visitante"] = ""

if "Rival" not in partidos.columns:
    if "Rival_fix" in partidos.columns:
        partidos["Rival"] = partidos["Rival_fix"]
    else:
        partidos["Rival"] = ""

if "Local_Visitante" not in partidos.columns:
    if "Local_Visitante_fix" in partidos.columns:
        partidos["Local_Visitante"] = partidos["Local_Visitante_fix"]
    else:
        partidos["Local_Visitante"] = ""

partidos["Rival"] = partidos["Rival"].fillna("")
partidos["Local_Visitante"] = partidos["Local_Visitante"].fillna("")

partidos["Nombre_Partido"] = partidos.apply(
    lambda row: (
        f"{row['Rival']} ({str(row['Local_Visitante'])[:1].upper()})"
        if str(row["Rival"]).strip() != ""
        else str(row["ID_Partido"])
    ),
    axis=1
)

# =========================================================
# SIDEBAR
# =========================================================
st.sidebar.title("🎛️ Panel")

lista_jugadoras = sorted([j for j in jugadoras["Jugador"].dropna().tolist() if str(j).strip() != ""])
jugadora_sel = st.sidebar.selectbox("Jugadora", ["Todas"] + lista_jugadoras)

lista_partidos = sorted([p for p in partidos["Nombre_Partido"].dropna().tolist() if str(p).strip() != ""])
partido_sel = st.sidebar.selectbox("Partido", ["Todos"] + lista_partidos)

st.sidebar.markdown("---")

comp_options = sorted([j for j in jugadoras["Jugador"].dropna().tolist() if str(j).strip() != ""])
comp1 = st.sidebar.selectbox("Comparar 1", ["Ninguna"] + comp_options)
comp2 = st.sidebar.selectbox("Comparar 2", ["Ninguna"] + comp_options)

# =========================================================
# FILTROS
# =========================================================
stats_f = stats.copy()
partido_info = None

if jugadora_sel != "Todas":
    stats_f = stats_f[stats_f["Jugador"] == jugadora_sel]

if partido_sel != "Todos":
    fila = partidos.loc[partidos["Nombre_Partido"] == partido_sel]
    if not fila.empty:
        partido_info = fila.iloc[0]
        id_p = partido_info["ID_Partido"]
        stats_f = stats_f[stats_f["ID_Partido"] == id_p]

# =========================================================
# HEADER
# =========================================================
st.markdown('<div class="header-box">', unsafe_allow_html=True)

c1, c2 = st.columns([1, 6])
with c1:
    st.image(ruta_escudo, width=80)
with c2:
    st.markdown("""
    <div style="padding-top: 4px;">
        <h1 style="margin:0; font-size:2rem;">SECLA FUTSAL DASHBOARD</h1>
        <p style="margin-top:6px; color:#94a3b8; font-size:0.95rem;">
            Análisis completo del equipo
        </p>
    </div>
    """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# =========================================================
# KPIs
# =========================================================
titulo("📊 Estadísticas")

c1, c2, c3, c4 = st.columns(4)
with c1:
    tarjeta_kpi("Goles", int(pd.to_numeric(stats_f["Goles"], errors="coerce").fillna(0).sum()))
with c2:
    tarjeta_kpi("Asistencias", int(pd.to_numeric(stats_f["Asistencias"], errors="coerce").fillna(0).sum()))
with c3:
    tarjeta_kpi("Amarillas", int(pd.to_numeric(stats_f["Amarillas"], errors="coerce").fillna(0).sum()))
with c4:
    tarjeta_kpi("Rojas", int(pd.to_numeric(stats_f["Rojas"], errors="coerce").fillna(0).sum()))

# =========================================================
# PRÓXIMOS PARTIDOS
# =========================================================
titulo("📅 Próximos partidos")

try:
    fecha_actual_df = pd.read_excel(
        archivo,
        sheet_name=hoja_fixture,
        usecols="F",
        header=None
    )
    fecha_actual = int(fecha_actual_df.iloc[1, 0])
except Exception:
    fecha_actual = 0

proximos = fixture[fixture["Orden"] > fecha_actual].sort_values("Orden").head(3)

cols = st.columns(3)
if proximos.empty:
    st.info("No hay próximos partidos para mostrar.")
else:
    for pos, (_, row) in enumerate(proximos.iterrows()):
        condicion = "🏠 Local" if str(row["Local_Visitante"]).strip().lower() == "local" else "✈️ Visitante"
        with cols[pos]:
            st.markdown(f"""
            <div class="card">
                <h3>⚽ {row['Rival']}</h3>
                <p>{condicion}</p>
            </div>
            """, unsafe_allow_html=True)

# =========================================================
# TABLA POSICIONES
# =========================================================
titulo("🏆 Tabla de posiciones")

try:
    tabla_posiciones = cargar_tabla_posiciones()

    def resaltar_secla(fila):
        equipo = str(fila.get("Equipo", "")).upper()
        if "SECLA" in equipo:
            return ["background-color: #1d4ed8; color: white; font-weight: bold;"] * len(fila)
        return [""] * len(fila)

    st.dataframe(
        tabla_posiciones.style.apply(resaltar_secla, axis=1).hide(axis="index"),
        use_container_width=True
    )
except Exception as e:
    st.warning(f"No se pudo cargar la tabla de posiciones: {e}")

# =========================================================
# RENDIMIENTO PARTIDO
# =========================================================
if partido_sel != "Todos" and partido_info is not None:
    titulo(f"🆚 Rendimiento del partido: {partido_sel}")

    cc1, cc2, cc3 = st.columns(3)
    with cc1:
        tarjeta_kpi("Rival", partido_info.get("Rival", ""))
    with cc2:
        tarjeta_kpi("Condición", partido_info.get("Local_Visitante", ""))
    with cc3:
        fecha_txt = partido_info["Orden"] if "Orden" in partido_info.index and pd.notnull(partido_info["Orden"]) else "-"
        tarjeta_kpi("Fecha", fecha_txt)

# =========================================================
# GRÁFICO GOLES
# =========================================================
titulo("⚽ Goles por jugadora")

df = stats_f.groupby("Jugador", as_index=False)["Goles"].sum()

if df.empty:
    st.info("Todavía no hay datos cargados.")
else:
    fig = px.bar(df, x="Jugador", y="Goles", text="Goles")
    fig.update_layout(
        plot_bgcolor="#0b1220",
        paper_bgcolor="#0b1220",
        font_color="white",
        margin=dict(l=10, r=10, t=40, b=10)
    )
    fig.update_traces(marker_color="#3b82f6", textposition="outside")
    st.plotly_chart(fig, use_container_width=True)

# =========================================================
# RESUMEN
# =========================================================
titulo("📋 Resumen por jugadora")

resumen = stats_f.groupby("Jugador", as_index=False).agg({
    "Minutos": "sum",
    "Goles": "sum",
    "Asistencias": "sum",
    "Amarillas": "sum",
    "Rojas": "sum"
})

if resumen.empty:
    st.info("Todavía no hay estadísticas cargadas.")
else:
    resumen["Impacto"] = resumen["Goles"] + resumen["Asistencias"]
    st.dataframe(
        resumen[["Jugador", "Minutos", "Goles", "Asistencias", "Impacto", "Amarillas", "Rojas"]],
        use_container_width=True,
        hide_index=True
    )

# =========================================================
# COMPARACIÓN
# =========================================================
if comp1 != "Ninguna" and comp2 != "Ninguna" and comp1 != comp2:
    titulo("⚔️ Comparación")

    comp_stats = stats.copy()

    if partido_sel != "Todos" and partido_info is not None:
        comp_stats = comp_stats[comp_stats["ID_Partido"] == partido_info["ID_Partido"]]

    d1 = comp_stats[comp_stats["Jugador"] == comp1]
    d2 = comp_stats[comp_stats["Jugador"] == comp2]

    comp = pd.DataFrame({
        "Métrica": ["Goles", "Asistencias", "Minutos"],
        comp1: [
            pd.to_numeric(d1["Goles"], errors="coerce").fillna(0).sum(),
            pd.to_numeric(d1["Asistencias"], errors="coerce").fillna(0).sum(),
            pd.to_numeric(d1["Minutos"], errors="coerce").fillna(0).sum()
        ],
        comp2: [
            pd.to_numeric(d2["Goles"], errors="coerce").fillna(0).sum(),
            pd.to_numeric(d2["Asistencias"], errors="coerce").fillna(0).sum(),
            pd.to_numeric(d2["Minutos"], errors="coerce").fillna(0).sum()
        ]
    })

    st.dataframe(comp, use_container_width=True, hide_index=True)

    fig2 = px.bar(
        comp.melt(id_vars="Métrica"),
        x="Métrica",
        y="value",
        color="variable",
        barmode="group"
    )
    fig2.update_layout(
        plot_bgcolor="#0b1220",
        paper_bgcolor="#0b1220",
        font_color="white",
        legend_title_text="",
        margin=dict(l=10, r=10, t=40, b=10)
    )
    st.plotly_chart(fig2, use_container_width=True)
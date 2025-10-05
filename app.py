# app.py

import os
import streamlit as st
import folium
from streamlit_folium import st_folium
import pandas as pd
import matplotlib.pyplot as plt
import geopandas as gpd
import gdown

# -------------------------------
# CONFIGURACIÓN
# -------------------------------
st.set_page_config(page_title="Plataforma Pasivos Ambientales", layout="wide")

# Crear carpeta para data
os.makedirs("data", exist_ok=True)

# -------------------------------
# FUNCIONES
# -------------------------------
def descargar_archivo(id_drive, nombre_salida):
    """Descarga archivo desde Google Drive por ID"""
    url = f"https://drive.google.com/uc?id={id_drive}"
    output = os.path.join("data", nombre_salida)
    if not os.path.exists(output):
        gdown.download(url, output, quiet=False)
    return output

def cargar_csv(path):
    try:
        return pd.read_csv(path)
    except Exception as e:
        st.error(f"Error cargando {path}: {e}")
        return None

def mostrar_grafico_barras(df, columna, titulo):
    fig, ax = plt.subplots(figsize=(6, 4))
    df[columna].value_counts().plot(kind="bar", ax=ax)
    ax.set_title(titulo)
    st.pyplot(fig)

# -------------------------------
# ARCHIVOS DESDE GOOGLE DRIVE
# (Reemplaza los IDs con los tuyos)
# -------------------------------
archivos_drive = {
    "pasivos.csv": "1blChzXrT4RWEAZq6qvxHHp6PYH77X0Ux",        # Lista de pasivos ambientales
    "provincias.shp": "1tbJCXkdvPcIslDIpB9nFOiB0QkKaQ1dY",     # Provincias
    "poblacion.tif": "1tbJCXkdvPcIslDIpB9nFOiB0QkKaQ1dY"       # Población raster
}

rutas = {}
for nombre, file_id in archivos_drive.items():
    rutas[nombre] = descargar_archivo(file_id, nombre)

# -------------------------------
# CARGAR BASE DE DATOS DE PASIVOS
# -------------------------------
df_pasivos = cargar_csv(rutas["pasivos.csv"])
if df_pasivos is not None:
    st.subheader("📋 Lista de Pasivos Ambientales")
    st.dataframe(df_pasivos.head())

    # Selección de pasivo
    pasivo_sel = st.selectbox("🔎 Selecciona un pasivo:", df_pasivos["nombre"].unique())

    datos_pasivo = df_pasivos[df_pasivos["nombre"] == pasivo_sel].iloc[0]

    st.write("### 🏭 Información del pasivo seleccionado")
    st.write(f"**ID:** {datos_pasivo['id']}")
    st.write(f"**Provincia:** {datos_pasivo['provincia']}")
    st.write(f"**Latitud:** {datos_pasivo['lat']}")
    st.write(f"**Longitud:** {datos_pasivo['lon']}")
    st.write(f"**Radio de dispersión estimado:** {datos_pasivo['radio_m']} m")
    st.write(f"**Centro poblado más cercano:** {datos_pasivo['centro_poblado']}")

    # -------------------------------
    # MAPA FOLIUM
    # -------------------------------
    m = folium.Map(location=[datos_pasivo['lat'], datos_pasivo['lon']], zoom_start=12)
    folium.Marker(
        [datos_pasivo['lat'], datos_pasivo['lon']],
        popup=f"Pasivo: {datos_pasivo['nombre']}",
        tooltip="Pasivo Ambiental",
        icon=folium.Icon(color="red")
    ).add_to(m)

    # Círculo de dispersión
    folium.Circle(
        radius=datos_pasivo["radio_m"],
        location=[datos_pasivo['lat'], datos_pasivo['lon']],
        color="blue",
        fill=True,
        fill_opacity=0.3
    ).add_to(m)

    st_folium(m, width=700, height=500)

    # -------------------------------
    # GRAFICO DE BARRAS
    # -------------------------------
    st.subheader("📊 Distribución de pasivos por provincia")
    mostrar_grafico_barras(df_pasivos, "provincia", "Cantidad de pasivos por provincia")

    # -------------------------------
    # ENLACES DE REFERENCIA
    # -------------------------------
    st.subheader("📚 Recursos")
    st.markdown("""
    - [Manual de gestión de pasivos ambientales mineros - MINAM Perú](https://www.gob.pe/minam)
    - [NASA EarthData (datos satelitales de contaminación y población)](https://earthdata.nasa.gov/)
    - [WorldPop datos de población](https://www.worldpop.org/)
    - [Centros médicos cercanos - Google Maps](https://maps.google.com)
    """)

else:
    st.warning("No se pudo cargar el archivo `pasivos.csv`. Verifica tu Google Drive.")

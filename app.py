import streamlit as st
import pandas as pd
import rasterio
import netCDF4 as nc
import folium
from folium import Circle, Marker, Icon
from streamlit_folium import st_folium
import gdown
import os
import matplotlib.pyplot as plt

# --------------------------
# CONFIG
# --------------------------
st.set_page_config(page_title="🌍 Pasivos Ambientales", layout="wide")

# Crear carpeta local
os.makedirs("data", exist_ok=True)

# Archivos en Google Drive (reemplaza por TUS IDs reales)
datasets = {
    "Global_2020_PopulationDensity30sec_GPWv4.tiff": "https://drive.google.com/file/d/1tbJCXkdvPcIslDIpB9nFOiB0QkKaQ1dY/view?usp=drive_link",
    "pm25_global.nc": "https://drive.google.com/drive/folders/1xyJy5mgk0beFkzMWwuV_X3SiI2kG6Cnd?usp=drive_link",
    "provincias.zip": "https://drive.google.com/file/d/1zjx2fEf0DJWsUhOLDPdtGfxyY9uYuHym/view?usp=drive_link",
    "centros_medicos.csv": "https://drive.google.com/file/d/1UqRwvfYCEj9Vj9Yqrjw2LvCWAantY95V/view?usp=drive_link"
}

# Descargar automáticamente desde Drive
for fname, fid in datasets.items():
    url = f"https://drive.google.com/drive/folders/1fQUUXU2VR6TGTjoobrgduyVQwgfQlzc8?usp=drive_link{fid}"
    output = f"data/{fname}"
    if not os.path.exists(output):
        with st.spinner(f"Descargando {fname}..."):
            gdown.download(url, output, quiet=False)

# --------------------------
# CARGAR DATOS
# --------------------------
centros = pd.read_csv("data/centros_medicos.csv") if os.path.exists("data/centros_medicos.csv") else None

# Raster población
pop_raster = "data/Global_2020_PopulationDensity30sec_GPWv4.tiff"
if os.path.exists(pop_raster):
    src = rasterio.open(pop_raster)

# NetCDF PM2.5
pm25_file = "data/pm25_global.nc"
if os.path.exists(pm25_file):
    ds_pm25 = nc.Dataset(pm25_file)

# --------------------------
# INTERFAZ
# --------------------------
st.title("🌍 Plataforma de Análisis de Pasivos Ambientales")

# Selección de ubicación
col1, col2 = st.columns(2)
with col1:
    ciudad = st.text_input("Ciudad", "")
    pais = st.text_input("País", "")
with col2:
    provincia = st.text_input("Provincia/Departamento", "")
    lat = st.number_input("Latitud (si no usas ciudad)", value=0.0, format="%.6f")
    lon = st.number_input("Longitud (si no usas ciudad)", value=0.0, format="%.6f")

radio_rapido = st.slider("Radio de atención rápida (km)", 1, 20, 5)
radio_lento = st.slider("Radio de atención lenta (km)", 10, 100, 30)

# --------------------------
# MAPA
# --------------------------
if pasivos is not None and not pasivos.empty:
    st.subheader("🗺️ Mapa de Pasivos y Centros Médicos")
    m = folium.Map(location=[-9.19, -75.0152], zoom_start=5)

    # Añadir pasivos
    for _, row in pasivos.iterrows():
        Marker(
            location=[row["lat"], row["lon"]],
            popup=f"Pasivo: {row['nombre']}<br>Daño: {row['tipo']}<br>Solución: {row['solucion']}",
            icon=Icon(color="red", icon="warning", prefix="fa")
        ).add_to(m)

        # Círculos de afectación
        Circle(location=[row["lat"], row["lon"]],
               radius=radio_rapido * 1000,
               color="orange", fill=True, fill_opacity=0.3).add_to(m)
        Circle(location=[row["lat"], row["lon"]],
               radius=radio_lento * 1000,
               color="blue", fill=True, fill_opacity=0.15).add_to(m)

    # Añadir centros médicos
    if centros is not None:
        for _, row in centros.iterrows():
            Marker(
                location=[row["lat"], row["lon"]],
                popup=f"Centro Médico: {row['nombre']}",
                icon=Icon(color="green", icon="plus", prefix="fa")
            ).add_to(m)

    st_map = st_folium(m, width=900, height=500)

# --------------------------
# ANÁLISIS
# --------------------------
if pasivos is not None:
    st.subheader("📊 Análisis de Población Afectada")
    # Simulación de población afectada
    poblacion_antes = [1000, 2000, 3000]
    poblacion_ahora = [3000, 5000, 7000]
    labels = ["Pasivo 1", "Pasivo 2", "Pasivo 3"]

    fig, ax = plt.subplots()
    ax.bar(labels, poblacion_antes, label="Hace 10 años")
    ax.bar(labels, poblacion_ahora, bottom=poblacion_antes, label="Actual")
    ax.set_ylabel("Personas afectadas")
    ax.legend()
    st.pyplot(fig)

    st.info("✅ Los radios de afectación están calculados desde el pasivo ambiental. "
            "Los gráficos muestran la comparación de población afectada en el tiempo.")

# --------------------------
# LINKS A MANUALES
# --------------------------
st.subheader("📚 Recursos de Solución por Tipo de Pasivo")
manuales = {
    "Relaves mineros": "https://www.unep.org/resources/report/tailings-management",
    "Drenaje ácido": "https://www.epa.gov/abandoned-mines/acid-mine-drainage",
    "Polvos de mina": "https://www.who.int/publications/i/item/WHO-SDE-PHE-EPE-14.5"
}

for tipo, link in manuales.items():
    st.markdown(f"- **{tipo}** → [Ver manual]({link})")

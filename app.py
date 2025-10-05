
st.set_page_config(page_title="Plataforma Pasivos Ambientales", layout="wide")
os.makedirs("data", exist_ok=True)

# Archivos en Google Drive (REEMPLAZA LOS IDs CON LOS DE TUS ARCHIVOS)
datasets = {
    "pasivos.csv": "TU_ID_P",
    "centros_medicos.csv": "1UqRwvfYCEj9Vj9Yqrjw2LvCWAantY95V",
    "Global_2020_PopulationDensity30sec_GPWv4.tiff": "1tbJCXkdvPcIslDIpB9nFOiB0QkKaQ1dY",
    "pm25_global.nc": "1x7aPFPN4VtmR4cRlcQM2ZdFiPTfv4Qjc",
    "provincias.zip": "1zjx2fEf0DJWsUhOLDPdtGfxyY9uYuHym"
}
for fname, fid in datasets.items():
    url = f"https://drive.google.com/uc?id={fid}"
    output = f"data/{fname}"
    if not os.path.exists(output):
        try:
            st.write(f"📥 Descargando {fname} ...")
            gdown.download(url, output, quiet=False)
        except Exception as e:
            st.warning(f"No se pudo descargar {fname}: {e}")

pasivos = pd.read_csv("data/pasivos.csv") if os.path.exists("data/pasivos.csv") else None
centros = pd.read_csv("data/centros_medicos.csv") if os.path.exists("data/centros_medicos.csv") else None

# ===============================
# 3. INTERFAZ DE USUARIO
# ===============================
st.title("🌍 Plataforma de Análisis de Pasivos Ambientales")

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
# ===============================
# 4. MAPA
# ===============================
if pasivos is not None and not pasivos.empty:
    st.subheader("🗺️ Mapa de Pasivos y Centros Médicos")
    m = folium.Map(location=[-9.19, -75.0152], zoom_start=5)

    # Pasivos
    for _, row in pasivos.iterrows():
        Marker(
            location=[row["lat"], row["lon"]],
            popup=f"<b>Pasivo:</b> {row['nombre']}<br><b>Daño:</b> {row['tipo']}<br><b>Solución:</b> {row['solucion']}",
            icon=Icon(color="red", icon="warning", prefix="fa")
        ).add_to(m)

        # Círculos de afectación
        Circle(location=[row["lat"], row["lon"]],
               radius=radio_rapido * 1000,
               color="orange", fill=True, fill_opacity=0.3).add_to(m)
        Circle(location=[row["lat"], row["lon"]],
               radius=radio_lento * 1000,
               color="blue", fill=True, fill_opacity=0.15).add_to(m)

    # Centros médicos
    if centros is not None:
        for _, row in centros.iterrows():
            Marker(
                location=[row["lat"], row["lon"]],
                popup=f"<b>Centro Médico:</b> {row['nombre']}",
                icon=Icon(color="green", icon="plus", prefix="fa")
            ).add_to(m)

    st_map = st_folium(m, width=900, height=500)

# ===============================
# 5. ANÁLISIS
# ===============================
if pasivos is not None:
    st.subheader("📊 Análisis de Población Afectada")
    # Ejemplo de simulación
    poblacion_antes = [1000, 2000, 3000]
    poblacion_ahora = [3000, 5000, 7000]
    labels = [f"Pasivo {i+1}" for i in range(len(poblacion_antes))]

    fig, ax = plt.subplots()
    ax.bar(labels, poblacion_antes, label="Hace 10 años")
    ax.bar(labels, poblacion_ahora, bottom=poblacion_antes, label="Actual")
    ax.set_ylabel("Personas afectadas")
    ax.legend()
    st.pyplot(fig)

    st.info("✅ Los radios de afectación se calculan desde el pasivo ambiental. "
            "Los gráficos comparan la población afectada en el tiempo.")

# ===============================
# 6. LINKS A MANUALES
# ===============================
st.subheader("📚 Recursos de Solución por Tipo de Pasivo")
manuales = {
    "Relaves mineros": "https://www.unep.org/resources/report/tailings-management",
    "Drenaje ácido": "https://www.epa.gov/abandoned-mines/acid-mine-drainage",
    "Polvos de mina": "https://www.who.int/publications/i/item/WHO-SDE-PHE-EPE-14.5"
}
for tipo, link in manuales.items():
    st.markdown(f"- **{tipo}** → [Ver manual]({link})")
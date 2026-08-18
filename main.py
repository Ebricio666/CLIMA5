import streamlit as st
import pandas as pd
import requests
import io  # Importar StringIO desde io
import os  # Asegurar la importación de os

import requests
import streamlit as st

# Listas de claves
claves_colima = [
        "C06001", "C06049", "C06076", "C06074", "C06006", "C06040", "C06010", "C06015",
        "C06024", "C06043", "C06071", "C06062", "C06014", "ARMCM", "C06008", "C06075",
        "C06056", "C06020", "C06002", "C06009", "C06041", "C06021", "C06073", "C06012",
        "C06042", "C06016", "CHNCM", "CSTCM", "LPSCM", "ASLCM", "ORTCM", "RDRCM", 
        "CMLCM", "PNTCM", "SCHCM", "CQMCM", "LAECM", "CMTCM", "C06063", "C06004",
        "C06060", "C06064", "C06068", "C06036", "C06054", "C06018", "C06051", "C06069",
        "C06070", "C06025", "BVSCM", "CUACM", "TRPCM", "C06066", "C06039", "C06030",
        "C06048", "C06061", "C06003", "C06005", "C06053", "C06011", "C06013", "C06059",
        "C06067", "C06017", "C06022", "C06023", "C06058", "C06007", "C06052", "C06065",
        "IXHCM", "ACMCM", "CMDCM", "MNZCM", "SNTCM", "MINCM", "CLRCM", "CLLCM", 
        "CDOCM", "LDACM", "DJLCM", "TCMCM"]

claves_colima_cerca = [
        "C14008", "C14018", "MRZJL", "C14019", "C14046", "C14390", "ELCJL", "TMLJL", "C14027", "CHFJL",
        "C14148", "C14112", "C14029", "C14094", "C14043", "C14343", "C14050", "BBAJL", "C14051", "C14315",
        "VIHJL", "C14348", "C14011", "C14042", "C14086", "C14099", "C14336", "C14109", "TRJCM", "C14031",
        "C14368", "C14034", "ECAJL", "C14141", "C14095", "C14052", "NOGJL", "C14142", "C14184", "TAPJL",
        "C14005", "SLTJL", "C14322", "C14311", "C14151", "C14190", "C14024", "CPEJL", "CP4JL", "CP3JL",
        "CP1JL", "C14067", "HIGJL", "RTOJL", "C14387", "C14350", "C14155", "C14022", "C14118", "C14342",
        "ALCJL", "C14395", "IVAJL", "C14197", "C14158", "C14007", "C14079", "C14117", "C14166", "C14170",
        "C14120", "C14352", "C14030", "CGZJL"
    ]

claves_jalisco = {'BBAJL', 'C14008', 'C14018', 'C14019', 'C14027', 'C14029', 'C14043',
                      'C14046', 'C14050', 'C14051', 'C14094', 'C14112', 'C14148', 'C14343',
                      'C14390', 'CHFJL', 'ELCJL', 'MRZJL', 'TMLJL'}
claves_michoacan = {'ALCJL', 'C14005', 'C14007', 'C14011', 'C14022', 'C14024', 'C14030',
                        'C14031', 'C14034', 'C14042', 'C14052', 'C14067', 'C14079', 'C14086',
                        'C14095', 'C14099', 'C14109', 'C14117', 'C14118', 'C14120', 'C14141',
                        'C14142', 'C14151', 'C14155', 'C14158', 'C14166', 'C14170', 'C14184',
                        'C14190', 'C14197', 'C14311', 'C14315', 'C14322', 'C14336', 'C14342',
                        'C14348', 'C14350', 'C14352', 'C14368', 'C14387', 'C14395', 'CGZJL',
                        'CP1JL', 'CP3JL', 'CP4JL', 'CPEJL', 'ECAJL', 'HIGJL', 'IVAJL', 'NOGJL',
                        'RTOJL', 'SLTJL', 'TAPJL', 'TRJCM', 'VIHJL'}


# Combinar todas las claves
claves = claves_colima + claves_colima_cerca

# Columnas numéricas disponibles
columnas_numericas = [
    'Precipitación(mm)', 'Temperatura Media(ºC)', 
    'Temperatura Máxima(ºC)', 'Temperatura Mínima(ºC)', 'Evaporación(mm)'
]



# URL base del repositorio
#github_base_url = "https://api.github.com/repos/SArcD/MapasClimaticosIA/contents/"


# Configuración general de la aplicación
st.set_page_config(
    page_title="ClimaPredictor Colima",
    page_icon="🌦️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Sidebar para navegación
st.sidebar.markdown("## 🌦️ ClimaPredictor")
st.sidebar.caption("Mapas climatológicos y predicción temporal para apoyar decisiones territoriales.")
seccion = st.sidebar.radio(
    "Navegación",
    ["Inicio", "Mapas Climatológicos", "Predicción con Prophet"]
)

if seccion == "Inicio":
    st.markdown("""
    <style>
    .hero {
        padding: 2.1rem 2.3rem;
        border-radius: 22px;
        background: linear-gradient(135deg, #eef7ff 0%, #f7fbf5 55%, #fff8ec 100%);
        border: 1px solid #dce8ef;
        margin-bottom: 1.2rem;
    }
    .hero h1 {margin:0; color:#12345b; font-size:2.55rem; line-height:1.08;}
    .hero p {font-size:1.08rem; color:#3d5266; max-width:980px; margin-top:.8rem;}
    .pill {display:inline-block; padding:.34rem .72rem; border-radius:999px; background:#ffffff; border:1px solid #d7e4ea; margin:.2rem .25rem .2rem 0; color:#24445f; font-weight:600;}
    .card {padding:1.15rem 1.25rem; border-radius:18px; border:1px solid #e1e8ed; background:#ffffff; min-height:175px;}
    .card h3 {margin-top:0; color:#173d67;}
    .flow {padding:1rem; border-radius:16px; background:#f7f9fb; border:1px solid #e5eaee; text-align:center; font-weight:650; color:#274861;}
    .muted {color:#617283; font-size:.95rem;}
    </style>

    <div class="hero">
      <span class="pill">Código abierto</span>
      <span class="pill">Python + Streamlit</span>
      <span class="pill">Colima, México</span>
      <h1>Aplicación para la generación de mapas climatológicos</h1>
      <p>
      Una herramienta para transformar registros meteorológicos dispersos en información espacial útil.
      Integra datos históricos de estaciones, variables geofísicas y técnicas de interpolación para estimar
      condiciones climáticas en zonas sin medición directa y apoyar decisiones de planeación territorial.
      </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### ¿Qué problema buscamos resolver?")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("""
        <div class="card">
        <h3>📍 Medimos en puntos</h3>
        <p>Las estaciones meteorológicas registran el clima únicamente en ubicaciones específicas. Una red suficientemente densa implica costos de instalación, mantenimiento y operación.</p>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown("""
        <div class="card">
        <h3>🗺️ Decidimos sobre territorios</h3>
        <p>La planeación agrícola, ambiental y energética necesita información continua del territorio, incluso donde no existe una estación activa.</p>
        </div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown("""
        <div class="card">
        <h3>🧠 Estimamos entre mediciones</h3>
        <p>La interpolación permite estimar variables climáticas en ubicaciones sin medición directa utilizando la información disponible en estaciones cercanas.</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("### Propuesta")
    st.markdown("""
    <div class="flow">
    Registros históricos de estaciones &nbsp; → &nbsp; Preparación de datos &nbsp; → &nbsp;
    Interpolaciones múltiples &nbsp; → &nbsp; Comparación mediante RMSE &nbsp; → &nbsp;
    Mapa climatológico para la zona de interés
    </div>
    """, unsafe_allow_html=True)

    st.write("")
    a, b = st.columns([1.05, 1])
    with a:
        st.markdown("#### 🌐 Mapas Climatológicos")
        st.write(
            "Explora temperatura, precipitación y evaporación por año o mes. "
            "La aplicación aprovecha registros históricos de CONAGUA, incorpora información de elevación "
            "y genera superficies continuas mediante diferentes estrategias de interpolación."
        )
        st.info("**Idea central:** más información espacial, no necesariamente más estaciones.")

    with b:
        st.markdown("#### 🔮 Predicción con Prophet")
        st.write(
            "Carga manualmente uno o varios CSV de estaciones y utiliza su serie histórica diaria para estimar "
            "una variable climática en una fecha futura específica. El resultado incluye valor esperado e intervalo predictivo."
        )
        st.info("**Dos preguntas complementarias:** interpolación responde *¿dónde?* y Prophet ayuda a explorar *¿cuándo?*")

    st.markdown("### ¿Para qué puede servir?")
    u1, u2, u3, u4 = st.columns(4)
    u1.metric("🌱", "Agricultura")
    u2.metric("🏙️", "Planeación territorial")
    u3.metric("🌿", "Gestión ambiental")
    u4.metric("☀️", "Tecnologías pasivas")

    st.caption(
        "Propuesta exploratoria desarrollada como herramienta de apoyo a la toma de decisiones. "
        "No sustituye la red de monitoreo meteorológico ni un pronóstico oficial."
    )

elif seccion == "Mapas Climatológicos":


    # Carga manual de CSV para la demostración / uso portátil
    st.subheader("📂 Cargar datos de estaciones meteorológicas")
    st.caption("Carga aquí los archivos CSV de las estaciones que quieras usar. Los mismos archivos alimentan los mapas climatológicos; en el módulo Prophet puedes volver a cargarlos para el pronóstico temporal.")

    archivos_mapa = st.file_uploader(
        "Selecciona uno o varios CSV de estaciones",
        type=["csv"],
        accept_multiple_files=True,
        key="csv_mapas_upload"
    )

    if not archivos_mapa:
        st.info("Carga al menos un archivo CSV para comenzar. Para interpolar se recomiendan varias estaciones con Latitud y Longitud.")
        st.stop()

    # Guardar temporalmente los archivos durante la sesión. No se requiere subirlos a GitHub.
    import tempfile
    output_dir_manual = os.path.join(tempfile.gettempdir(), "climapredictor_csv_manual")
    os.makedirs(output_dir_manual, exist_ok=True)

    # Limpiar CSV de sesiones/selecciones anteriores para evitar mezclar estaciones.
    for nombre_previo in os.listdir(output_dir_manual):
        if nombre_previo.lower().endswith(".csv"):
            try:
                os.remove(os.path.join(output_dir_manual, nombre_previo))
            except OSError:
                pass

    claves_cargadas = []
    for archivo_subido in archivos_mapa:
        nombre = os.path.basename(archivo_subido.name)
        ruta = os.path.join(output_dir_manual, nombre)
        with open(ruta, "wb") as f:
            f.write(archivo_subido.getbuffer())
        clave = nombre[:-7] if nombre.lower().endswith("_df.csv") else os.path.splitext(nombre)[0]
        claves_cargadas.append(clave)

    output_dir_colima = output_dir_manual
    output_dir_cerca = output_dir_manual
    st.success(f"{len(archivos_mapa)} archivo(s) cargado(s).")


    @st.cache_data
    # Descargar archivos desde enlaces utilizando requests
    def download_files_from_links(file_links, output_dir):
        os.makedirs(output_dir, exist_ok=True)
        with open(file_links, "r") as f:
            links = f.readlines()
        for link in links:
            link = link.strip()
            if link:
                # Extraer el ID o el nombre del archivo del enlace
                file_name = link.split("id=")[-1] if "id=" in link else os.path.basename(link)
                output_file = os.path.join(output_dir, file_name)
                if not os.path.exists(output_file):
                    try:
                        st.write(f"Descargando {file_name}...")
                        response = requests.get(link, stream=True)
                        response.raise_for_status()  # Levantar excepción para códigos de estado HTTP 4xx/5xx
                        with open(output_file, "wb") as f:
                            for chunk in response.iter_content(chunk_size=8192):
                                f.write(chunk)
                        st.success(f"Archivo descargado: {file_name}")
                    except Exception as e:
                        st.error(f"Error al descargar {link}: {e}")
                else:
                    st.write(f"Archivo ya existe: {file_name}")

    import numpy as np
    import streamlit as st
    import requests
    import os

    #############import requests
    import numpy as np
    import os
    import streamlit as st
    import requests

    # URL del archivo en Dropbox
    dropbox_url = "https://www.dropbox.com/scl/fi/y61orc7bzt2p2d22sxtcu/Colima_ACE2.ace2?rlkey=8asyjm6pjqjo0z02gofpg9l2b&st=eqnn71an&dl=1"
    file_path = "Colima_ACE2.ace2"

    # Descargar el archivo ACE2 si no existe
    if not os.path.exists(file_path):
        st.write("Descargando el archivo ACE2 desde Dropbox...")
        try:
            response = requests.get(dropbox_url, stream=True)
            response.raise_for_status()
            with open(file_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            st.success("Archivo ACE2 descargado correctamente.")
        except Exception as e:
            st.error(f"Error al descargar el archivo ACE2: {e}")
            st.stop()

    @st.cache_data
    # Diagnóstico de archivo
    def diagnosticar_archivo(file_path):
        """
        Verifica el tamaño del archivo y calcula dimensiones potenciales.
        """
        try:
            # Tamaño del archivo en bytes
            file_size_bytes = os.path.getsize(file_path)
            #st.write(f"Tamaño del archivo: {file_size_bytes} bytes")

            # Verificar divisibilidad por el tamaño de float32 (4 bytes)
            if file_size_bytes % 4 != 0:
                st.error("El tamaño del archivo no es divisible por 4. Puede estar corrupto o no ser un archivo válido.")
                return None

            # Calcular número total de elementos
            num_elements = file_size_bytes // 4
            #st.write(f"Número total de elementos (float32): {num_elements}")

            # Buscar dimensiones cuadradas o rectangulares
            possible_dims = []
            for rows in range(1, int(np.sqrt(num_elements)) + 1):
                if num_elements % rows == 0:
                    cols = num_elements // rows
                    possible_dims.append((rows, cols))

            #st.write(f"Dimensiones posibles: {possible_dims}")
            return possible_dims
        except Exception as e:
            st.error(f"Error al diagnosticar el archivo: {e}")
            return None


    @st.cache_data
    # Leer y calcular dimensiones automáticamente
    def read_ace2(file_path, selected_dims):
        """
        Lee el archivo ACE2 y lo convierte a una matriz según las dimensiones seleccionadas.
        """
        try:
            data = np.fromfile(file_path, dtype=np.float32)
            st.write(f"Archivo leído con {data.size} elementos.")

            # Convertir los datos a la matriz con las dimensiones seleccionadas
            rows, cols = selected_dims
            return data.reshape((rows, cols))
        except Exception as e:
            st.error(f"Error al procesar el archivo ACE2: {e}")
            return None

    # Diagnosticar el archivo
    dimensiones_posibles = diagnosticar_archivo(file_path)

    # Si se encuentran dimensiones válidas
    if dimensiones_posibles:
        # Permitir que el usuario seleccione dimensiones
        seleccion = st.selectbox("Seleccione las dimensiones para el archivo:", dimensiones_posibles)
        st.session_state.elevation_data = read_ace2(file_path, seleccion)
        #elevation_data = read_ace2(file_path, seleccion)
        elevation_data = st.session_state.elevation_data
        if elevation_data is not None:
            st.session_state.tile_size = elevation_data.shape    
            #tile_size = elevation_data.shape
            tile_size = st.session_state.tile_size
            st.success(f"Archivo procesado correctamente con dimensiones: {tile_size}.")
    else:
        st.error("No se pudieron determinar dimensiones válidas para el archivo.")

## Usar dimensiones por defecto (6000x6000)
#dim_por_defecto = (5760, 5420)

#############

    # Listas de claves
    claves_colima = [
        "C06001", "C06049", "C06076", "C06074", "C06006", "C06040", "C06010", "C06015",
        "C06024", "C06043", "C06071", "C06062", "C06014", "ARMCM", "C06008", "C06075",
        "C06056", "C06020", "C06002", "C06009", "C06041", "C06021", "C06073", "C06012",
        "C06042", "C06016", "CHNCM", "CSTCM", "LPSCM", "ASLCM", "ORTCM", "RDRCM", 
        "CMLCM", "PNTCM", "SCHCM", "CQMCM", "LAECM", "CMTCM", "C06063", "C06004",
        "C06060", "C06064", "C06068", "C06036", "C06054", "C06018", "C06051", "C06069",
        "C06070", "C06025", "BVSCM", "CUACM", "TRPCM", "C06066", "C06039", "C06030",
        "C06048", "C06061", "C06003", "C06005", "C06053", "C06011", "C06013", "C06059",
        "C06067", "C06017", "C06022", "C06023", "C06058", "C06007", "C06052", "C06065",
        "IXHCM", "ACMCM", "CMDCM", "MNZCM", "SNTCM", "MINCM", "CLRCM", "CLLCM", 
        "CDOCM", "LDACM", "DJLCM", "TCMCM"]

    claves_colima_cerca = [
        "C14008", "C14018", "MRZJL", "C14019", "C14046", "C14390", "ELCJL", "TMLJL", "C14027", "CHFJL",
        "C14148", "C14112", "C14029", "C14094", "C14043", "C14343", "C14050", "BBAJL", "C14051", "C14315",
        "VIHJL", "C14348", "C14011", "C14042", "C14086", "C14099", "C14336", "C14109", "TRJCM", "C14031",
        "C14368", "C14034", "ECAJL", "C14141", "C14095", "C14052", "NOGJL", "C14142", "C14184", "TAPJL",
        "C14005", "SLTJL", "C14322", "C14311", "C14151", "C14190", "C14024", "CPEJL", "CP4JL", "CP3JL",
        "CP1JL", "C14067", "HIGJL", "RTOJL", "C14387", "C14350", "C14155", "C14022", "C14118", "C14342",
        "ALCJL", "C14395", "IVAJL", "C14197", "C14158", "C14007", "C14079", "C14117", "C14166", "C14170",
        "C14120", "C14352", "C14030", "CGZJL"
    ]

    claves_jalisco = {'BBAJL', 'C14008', 'C14018', 'C14019', 'C14027', 'C14029', 'C14043',
                      'C14046', 'C14050', 'C14051', 'C14094', 'C14112', 'C14148', 'C14343',
                      'C14390', 'CHFJL', 'ELCJL', 'MRZJL', 'TMLJL'}
    claves_michoacan = {'ALCJL', 'C14005', 'C14007', 'C14011', 'C14022', 'C14024', 'C14030',
                        'C14031', 'C14034', 'C14042', 'C14052', 'C14067', 'C14079', 'C14086',
                        'C14095', 'C14099', 'C14109', 'C14117', 'C14118', 'C14120', 'C14141',
                        'C14142', 'C14151', 'C14155', 'C14158', 'C14166', 'C14170', 'C14184',
                        'C14190', 'C14197', 'C14311', 'C14315', 'C14322', 'C14336', 'C14342',
                        'C14348', 'C14350', 'C14352', 'C14368', 'C14387', 'C14395', 'CGZJL',
                        'CP1JL', 'CP3JL', 'CP4JL', 'CPEJL', 'ECAJL', 'HIGJL', 'IVAJL', 'NOGJL',
                        'RTOJL', 'SLTJL', 'TAPJL', 'TRJCM', 'VIHJL'}



    st.session_state.claves_colima = claves_colima

    # Combinar todas las claves
    # Para esta versión portátil, solo se procesan las estaciones cargadas manualmente.
    claves = list(dict.fromkeys(claves_cargadas))

    # Columnas numéricas disponibles
    columnas_numericas = [
        'Precipitación(mm)', 'Temperatura Media(ºC)', 
        'Temperatura Máxima(ºC)', 'Temperatura Mínima(ºC)', 'Evaporación(mm)'
    ]

    @st.cache_data
    # Función para obtener años disponibles
    def obtener_anos_disponibles(claves, output_dirs):
        anos_disponibles = set()
        for output_dir in output_dirs:
            for clave in claves:
                archivo = os.path.join(output_dir, f"{clave}_df.csv")
                if os.path.exists(archivo):
                    df = pd.read_csv(archivo)
                    df['Fecha'] = pd.to_datetime(df['Fecha'], format='%Y/%m/%d', errors='coerce')
                    anos = df['Fecha'].dt.year.dropna().unique()
                    anos_disponibles.update(anos)
        return sorted(anos_disponibles)

# Función para obtener la elevación desde el archivo ACE2
#def obtener_elevacion(lat, lon, tile_size, elevation_data):
#    """
#    Obtiene la elevación en kilómetros desde el archivo ACE2 usando latitud y longitud.
#    """
#    # Calcular índices en la matriz ACE2 basados en la latitud y longitud
#    lat_idx = int(max(0, min((30 - lat) * tile_size[0] / 15, tile_size[0] - 1)))  # Ajusta para el rango ACE2
#    lon_idx = int(max(0, min((lon + 105) * tile_size[1] / 15, tile_size[1] - 1)))  # Ajusta para el rango ACE2
#    elevacion = elevation_data[lat_idx, lon_idx] / 1000  # Convertir de metros a kilómetros
#    return max(0, elevacion)  # Evitar valores negativos

    @st.cache_data
    def obtener_elevacion(lat, lon, tile_size, elevation_data):
        """
        Obtiene la elevación en kilómetros desde el archivo ACE2 usando latitud y longitud.
        """
        try:
            # Validar dimensiones de tile_size con elevation_data
            if elevation_data.shape != tile_size:
                raise ValueError(f"Las dimensiones de elevation_data {elevation_data.shape} no coinciden con tile_size {tile_size}")
        
            # Calcular índices en la matriz ACE2 basados en la latitud y longitud
            lat_idx = int((30 - lat) * tile_size[0] / 15)  # Ajusta para el rango ACE2
            lon_idx = int((lon + 105) * tile_size[1] / 15)  # Ajusta para el rango ACE2

            # Asegurar que los índices están dentro del rango válido
            lat_idx = np.clip(lat_idx, 0, tile_size[0] - 1)
            lon_idx = np.clip(lon_idx, 0, tile_size[1] - 1)

            # Obtener elevación
            elevacion = elevation_data[lat_idx, lon_idx] / 1000  # Convertir de metros a kilómetros

        # Depuración opcional: verificar índices y elevación calculada
        # st.write(f"Lat: {lat}, Lon: {lon}, Indices: ({lat_idx}, {lon_idx}), Elevación: {elevacion} km")

            return max(0, elevacion)  # Evitar valores negativos
        except Exception as e:
            raise RuntimeError(f"Error al calcular elevación para lat={lat}, lon={lon}: {e}")

    @st.cache_data
    def procesar_datos(ano, mes, claves, output_dirs):
        datos_procesados = []

        for output_dir in output_dirs:
            for clave in claves:
                archivo = os.path.join(output_dir, f"{clave}_df.csv")
                if os.path.exists(archivo):
                    df = pd.read_csv(archivo) #aqui se agrego un eliminador de espacios
                    df.columns = df.columns.str.strip()
                    df['Fecha'] = pd.to_datetime(df['Fecha'], format='%Y/%m/%d', errors='coerce')
                    df['ano'] = df['Fecha'].dt.year
                    df['mes'] = df['Fecha'].dt.month

                    # Filtrar por año y mes
                    df_filtrado = df[df['ano'] == ano]
                    if mes and mes != 0:  # Si se selecciona un mes específico
                        df_filtrado = df_filtrado[df_filtrado['mes'] == mes]

                    # Si no hay datos para el año (o mes) seleccionado, omitir esta estación
                    if df_filtrado.empty:
                        continue

                    # Limpiar columnas numéricas y calcular promedios
                    promedios = {}
                    for col in columnas_numericas:
                        if col in df_filtrado.columns:
                            df_filtrado[col] = pd.to_numeric(df_filtrado[col].astype(str).str.replace('[^0-9.]', '', regex=True), errors='coerce')
                            promedios[col] = df_filtrado[col].mean()

                    # Obtener latitud y longitud
                    if 'Latitud' in df.columns and 'Longitud' in df.columns:
                        latitud = df['Latitud'].iloc[0]
                        longitud = df['Longitud'].iloc[0]
                        elevacion = obtener_elevacion(latitud, longitud, tile_size, elevation_data)
                    else:
                        latitud = np.nan
                        longitud = np.nan
                        elevacion = np.nan

                    # Determinar el estado de la estación
                    if clave in claves_colima:
                        estado = "Colima"
                    elif clave in claves_jalisco:
                        estado = "Jalisco"
                    elif clave in claves_michoacan:
                        estado = "Michoacán"
                    else:
                        estado = "Desconocido"

                    # Agregar datos al resultado
                    estacion_data = {
                        'Clave': clave,
                        'Estado': estado,
                        'Latitud': latitud,
                        'Longitud': longitud,
                        'Elevación (km)': elevacion  # Agregar elevación
                    }
                    estacion_data.update(promedios)
                    datos_procesados.append(estacion_data)

        return pd.DataFrame(datos_procesados)



    # Configuración de Streamlit
    st.title("Análisis de Datos Meteorológicos")

    st.markdown("""
    <div style="text-align: justify;">
    <h3>Mapas Meteorológicos del Estado de Colima</h3>

    <p>En esta sección se generan mapas climatológicos para el estado de Colima a partir de registros históricos de estaciones meteorológicas y una corrección geofísica por elevación. El objetivo es estimar variables en zonas donde no existe medición directa y comparar distintas estrategias de interpolación.</p>

    <ul>
      <li><b>Datos Meteorológicos:</b> Los datos de precipitación (medida en milímetros), temperatura (medida en grados Celsius) y evaporación (medida en milímetros) se obtuvieron de la base de datos de estaciones meteorológicas de la 
      <a href="https://sih.conagua.gob.mx/climas.html" target="_blank">Comisión Nacional del Agua (CONAGUA)</a>.</li>
      <li><b>Elevación sobre el Nivel del Mar:</b> La elevación sobre el nivel del mar (medida en kilómetros) se obtuvo del 
      <a href="https://sedac.ciesin.columbia.edu/mapping/ace2/?_ga=2.64821862.877322575.1732493587-819847203.1710446044" target="_blank">Modelo Digital de Elevación Global de la NASA</a>.</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style="text-align: justify;">
    <p>Seleccione el mes y año para visualizar los valores promedio de temperatura, precipitación y evaporación. Para consultar el promedio anual, seleccione <b>"Todo el año"</b>. Los resultados pueden descargarse como CSV desde la tabla o mediante el botón de descarga.</p>
    </div>
    """, unsafe_allow_html=True)

    # Directorios de entrada    
    st.session_state.output_dirs = [output_dir_manual] 
    #output_dirs = [output_dir_colima, output_dir_cerca]
    output_dirs = st.session_state.output_dirs
    # Obtener años disponibles
    anos_disponibles = obtener_anos_disponibles(claves, output_dirs)
    if not anos_disponibles:
        st.error("No se encontraron datos disponibles.")
        st.stop()

    # Menú desplegable para seleccionar año y mes
    ano = st.selectbox("Selecciona el año", options=anos_disponibles)
    meses = {0: "Todo el año", 1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril", 5: "Mayo", 6: "Junio",
             7: "Julio", 8: "Agosto", 9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"}    
    mes = st.selectbox("Selecciona el mes", options=list(meses.keys()), format_func=lambda x: meses[x])

    # Procesar datos seleccionados
    df_resultado = procesar_datos(ano, mes if mes != 0 else None, claves, output_dirs)
    df_resultado.columns = df_resultado.columns.str.strip()

    # Parámetros para radiación solar
    S0 = 1361  # Constante solar (W/m²)
    Ta = 0.75  # Transmisión atmosférica promedio
    k = 0.12   # Incremento de radiación por km de altitud


    @st.cache_data
    def calculate_annual_radiation(latitude, altitude):
        """Calcular radiación solar promedio anual considerando declinación solar y ángulo horario."""
        total_radiation = 0
        for day in range(1, 366):
            # Calcular declinación solar
            declination = 23.45 * np.sin(np.radians((360 / 365) * (day - 81)))
            declination_rad = np.radians(declination)
        
            # Convertir latitud a radianes
            latitude_rad = np.radians(latitude)
        
            # Calcular ángulo horario del amanecer/atardecer
            h_s = np.arccos(-np.tan(latitude_rad) * np.tan(declination_rad))
        
            # Calcular radiación diaria
            daily_radiation = (
                S0 * Ta * (1 + k * altitude) * 
                (np.cos(latitude_rad) * np.cos(declination_rad) * np.sin(h_s) +
                 h_s * np.sin(latitude_rad) * np.sin(declination_rad))
            )
        
            total_radiation += max(0, daily_radiation)  # Evitar valores negativos

        return total_radiation / 365  # Promedio anual


    @st.cache_data
    def calculate_monthly_radiation(latitude, altitude, days_in_month):
        """Calcular radiación solar promedio mensual."""
        total_radiation = 0
        for day in range(1, days_in_month + 1):
            declination = 23.45 * np.sin(np.radians((360 / 365) * (day - 81)))
            declination_rad = np.radians(declination)
            latitude_rad = np.radians(latitude)
            h_s = np.arccos(-np.tan(latitude_rad) * np.tan(declination_rad))
            daily_radiation = (
                S0 * Ta * (1 + k * altitude) *
                (np.cos(latitude_rad) * np.cos(declination_rad) * np.sin(h_s) +
                 h_s * np.sin(latitude_rad) * np.sin(declination_rad))
            )
            total_radiation += max(0, daily_radiation)  # Evitar valores negativos
        return total_radiation / days_in_month

    # Actualizar el DataFrame con la radiación solar
    if not df_resultado.empty:
        radiaciones = []
        for _, row in df_resultado.iterrows():
            latitud = row['Latitud']
            elevacion = row['Elevación (km)']
            if mes == 0:  # Todo el año
                radiacion = calculate_annual_radiation(latitud, elevacion)
            else:  # Mes específico
                # Días en cada mes (no considera años bisiestos)
                dias_por_mes = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
                dias_mes = dias_por_mes[mes - 1]
                radiacion = calculate_monthly_radiation(latitud, elevacion, dias_mes)
            radiaciones.append(radiacion)

        # Agregar la columna de radiación al DataFrame
        df_resultado['Radiación Solar Promedio (W/m²)'] = radiaciones


    # Parámetros para corrección
    gradiente_temperatura = -6.5  # °C/km, gradiente ambiental típico

    # Corregir valores de radiación y temperatura en función de la elevación
    if not df_resultado.empty:
        temperaturas_corregidas = []
        radiaciones_corregidas = []

        for _, row in df_resultado.iterrows():
            elevacion = row['Elevación (km)']

            # Corregir temperatura media
            temp_media_original = row['Temperatura Media(ºC)'] if 'Temperatura Media(ºC)' in row else np.nan
            temp_media_corregida = temp_media_original + (elevacion * gradiente_temperatura) if not pd.isna(temp_media_original) else np.nan
            temperaturas_corregidas.append(temp_media_corregida)

            # Corregir radiación solar
            radiacion_original = row['Radiación Solar Promedio (W/m²)'] if 'Radiación Solar Promedio (W/m²)' in row else np.nan
            radiacion_corregida = radiacion_original * (1 + k * elevacion) if not pd.isna(radiacion_original) else np.nan
            radiaciones_corregidas.append(radiacion_corregida)

        df_resultado['Radiación Solar Corregida (W/m²)'] = radiaciones_corregidas
        df_2=df_resultado.copy()


    # Mostrar resultados
    if not df_resultado.empty:
        st.write(f"Datos procesados para {meses[mes]} del año {ano}:")
        st.dataframe(df_resultado)
    else:
        st.write("No se encontraron datos para el período seleccionado.")


    # Determinar el nombre del archivo
    if mes:  # Si hay un mes seleccionado
        filename = f"datos_climaticos_para_{mes}_{ano}.csv"    
    else:  # Si es todo el año
        filename = f"datos_climaticos_para_{ano}.csv"

    # Botón de descarga
    csv = df_resultado.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Descargar",
        data=csv,
        file_name=filename,
        mime="text/csv"
    )

    import plotly.express as px
    import plotly.graph_objects as go
    import json
    import matplotlib as plt


    # Definir una escala coolwarm personalizada
    coolwarm_scale = [
        [0.0, 'rgb(59,76,192)'],  # Azul oscuro
        [0.35, 'rgb(116,173,209)'],  # Azul claro
        [0.5, 'rgb(221,221,221)'],  # Blanco/neutral
        [0.65, 'rgb(244,109,67)'],  # Naranja claro
        [1.0, 'rgb(180,4,38)']  # Rojo oscuro
    ]

    # Crear el esquema de colores 'coolwarm'
    coolwarm_colorscale = plt.cm.coolwarm(np.linspace(0, 1, 256))
    coolwarm_colorscale = [
        [i / 255.0, f"rgb({int(r * 255)}, {int(g * 255)}, {int(b * 255)})"]
        for i, (r, g, b, _) in enumerate(coolwarm_colorscale)
    ]

    # Cargar el archivo GeoJSON (Colima.JSON) para referencia del mapa
    try:
        with open('Colima.json', 'r', encoding='latin-1') as file:
            colima_geojson = json.load(file)
    except Exception as e:
        st.error(f"No se pudo cargar el archivo GeoJSON: {e}")
        st.stop()

    st.subheader("Mapa con datos de estaciones de la CONAGUA")

    st.markdown("""
    <div style="text-align: justify;">
    <p>En la siguiente gráfica se muestran las estaciones del estado de Colima y zonas circundantes que registraron datos climáticos para el periodo de tiempo seleccionado (los colores representan una aproximación al valor registrado por cada estación).</p>
    </div>
    """, unsafe_allow_html=True)

    import plotly.io as pio

    # Mostrar mapa con estaciones
    if not df_resultado.empty:
        # Menú desplegable para seleccionar la columna numérica a graficar
        columna_grafico = st.selectbox("Selecciona la columna para el color del mapa", options=columnas_numericas)

        # Filtrar estaciones con valores NaN en la columna seleccionada
        if columna_grafico in df_resultado.columns:
            df_filtrado = df_resultado.dropna(subset=[columna_grafico])
            #df_filtrado = df_resultado
            if not df_filtrado.empty:
                #c
                # Ajustar el título dinámicamente según la selección de mes
                if mes == 0:
                    titulo_mes = "Promedio Anual"
                else:
                    titulo_mes = f"Mes {mes}"

                # Crear el mapa base con las estaciones
                fig = px.scatter_mapbox(
                    df_filtrado,
                    lat="Latitud",
                    lon="Longitud",
                    color=columna_grafico,
                    hover_name="Clave",
                    hover_data=["Estado", columna_grafico],
                    title=f"Mapa de estaciones en Colima y alrededores ({columna_grafico.strip()} para el año {ano}, {titulo_mes})",
                    mapbox_style="carto-positron",
                    center={"lat": 19.0, "lon": -104.0},  # Ajusta el centro del mapa según sea necesario
                    zoom=8,
                    width=1000,
                    height=600,
                    color_continuous_scale=coolwarm_colorscale   # Usar escala coolwarm personalizada
                    )

                    # Configuración del diseño del gráfico
                fig.update_layout(
                    title=f"Mapa de estaciones en Colima y alrededores ({columna_grafico.strip()} para el año {ano}, {titulo_mes})",
                    margin=dict(l=0, r=0, t=50, b=0)
                    )

                # Cambiar tamaño de los puntos
                fig.update_traces(marker=dict(size=12))  # Ajusta el tamaño como desees
    
                # Añadir los polígonos de los municipios como trazas adicionales
                for feature in colima_geojson["features"]:
                    geometry = feature["geometry"]
                    properties = feature["properties"]

                    # Excluir islas si es necesario
                    if "isla" not in properties.get("name", "").lower():
                        if geometry["type"] == "Polygon":
                            for coordinates in geometry["coordinates"]:
                                x_coords, y_coords = zip(*coordinates)
                                fig.add_trace(
                                    go.Scattermapbox(
                                        lon=x_coords,
                                        lat=y_coords,
                                        mode="lines",
                                        line=dict(color="black", width=2),
                                        showlegend=False
                                    )
                                )
                        elif geometry["type"] == "MultiPolygon":
                            for polygon in geometry["coordinates"]:
                                for coordinates in polygon:
                                    x_coords, y_coords = zip(*coordinates)
                                    fig.add_trace(
                                        go.Scattermapbox(
                                            lon=x_coords,
                                            lat=y_coords,
                                            mode="lines",
                                            line=dict(color="black", width=2),
                                            showlegend=False
                                        )
                                    )


            
                    # Mostrar el mapa
                st.plotly_chart(fig, use_container_width=True)

            else:
                st.warning(f"No hay estaciones con datos válidos en la columna '{columna_grafico}'.")
        else:
            st.warning("La columna seleccionada no está disponible en el DataFrame.")
    else:
        st.write("No hay datos disponibles para mostrar en el mapa.")

#
#import streamlit as st
#import plotly.express as px
#import plotly.graph_objects as go
#import numpy as np
#import json
#import matplotlib.pyplot as plt

# Crear el esquema de colores 'coolwarm'
#coolwarm_colorscale = plt.cm.coolwarm(np.linspace(0, 1, 256))
#coolwarm_colorscale = [
#    [i / 255.0, f"rgb({int(r * 255)}, {int(g * 255)}, {int(b * 255)})"]
#    for i, (r, g, b, _) in enumerate(coolwarm_colorscale)
#]

## Cargar el archivo GeoJSON (Colima.JSON) para referencia del mapa
#try:
#    with open('Colima.JSON', 'r', encoding='latin-1') as file:
#        colima_geojson = json.load(file)
#except Exception as e:
#    st.error(f"No se pudo cargar el archivo GeoJSON: {e}")
#    st.stop()

## Mostrar mapa con estaciones
#if not df_resultado.empty:
#    # Menú desplegable para seleccionar la columna numérica a graficar
#    columna_grafico = st.selectbox("Selecciona columna para el color del mapa", options=columnas_numericas)

#    # Checkbox para mostrar u ocultar estaciones inactivas (valores NaN en la columna seleccionada)
#    mostrar_inactivas = st.checkbox("Mostrar estaciones inactivas (valores NaN)", value=True)

#    if columna_grafico in df_resultado.columns:
#        if mostrar_inactivas:
#            df_filtrado = df_resultado  # Incluir todas las estaciones
#        else:
#            df_filtrado = df_resultado.dropna(subset=[columna_grafico])  # Excluir estaciones inactivas

#        if not df_filtrado.empty:
#            # Crear el mapa base con las estaciones
#            fig = px.scatter_mapbox(
#                df_filtrado,
#                lat="Latitud",
#                lon="Longitud",
#                color=columna_grafico,
#                hover_name="Clave",
#                hover_data=["Estado", columna_grafico],
#                title=f"Mapa de estaciones en Colima y alrededores ({columna_grafico.strip()})",
#                mapbox_style="carto-positron",
#                center={"lat": 19.0, "lon": -104.0},  # Ajusta el centro del mapa según sea necesario
#                zoom=8,
#                width=1000,
#                height=600,
#                color_continuous_scale=coolwarm_colorscale  # Usar escala coolwarm personalizada
#            )

#            # Cambiar tamaño de los puntos
#            fig.update_traces(marker=dict(size=12))  # Ajusta el tamaño como desees

#            # Añadir los polígonos de los municipios como trazas adicionales
#            for feature in colima_geojson["features"]:
#                geometry = feature["geometry"]
#                properties = feature["properties"]

#                # Excluir islas si es necesario
#                if "isla" not in properties.get("name", "").lower():
#                    if geometry["type"] == "Polygon":
#                        for coordinates in geometry["coordinates"]:
#                            x_coords, y_coords = zip(*coordinates)
#                            fig.add_trace(
#                                go.Scattermapbox(
#                                    lon=x_coords,
#                                    lat=y_coords,
#                                    mode="lines",
#                                    line=dict(color="black", width=2),
#                                    showlegend=False
#                                )
#                            )
#                    elif geometry["type"] == "MultiPolygon":
#                        for polygon in geometry["coordinates"]:
#                            for coordinates in polygon:
#                                x_coords, y_coords = zip(*coordinates)
#                                fig.add_trace(
#                                    go.Scattermapbox(
#                                        lon=x_coords,
#                                        lat=y_coords,
#                                        mode="lines",
#                                        line=dict(color="black", width=2),
#                                        showlegend=False
#                                    )
#                                )

#            # Mostrar el mapa
#            st.plotly_chart(fig, use_container_width=True)
#        else:
#            st.warning(f"No hay estaciones con datos válidos en la columna '{columna_grafico}'.")
#    else:
#        st.warning("La columna seleccionada no está disponible en el DataFrame.")
#else:
#    st.write("No hay datos disponibles para mostrar en el mapa.")

#st.write("Columnas disponibles:", df_resultado.columns.tolist())
#st.write("Número total de filas:", len(df_resultado))
#st.write("Ejemplo de filas:", df_resultado[[columna_grafico, 'Latitud', 'Longitud']].dropna())


#
#latitudes = df_filtrado["Latitud"].values
#longitudes = df_filtrado["Longitud"].values

#st.write("Número total de estaciones:", len(df_resultado))
#st.write("Valores únicos de coordenadas:", len(np.unique(list(zip(longitudes, latitudes)), axis=0)))
#st.write("Valores NaN en columna seleccionada:", df_resultado[columna_grafico].isna().sum())
#st.write("Latitudes únicas:", np.unique(latitudes))
#st.write("Longitudes únicas:", np.unique(longitudes))
#st.write("Valores válidos:", len(valores))
#st.write("Shape grid_lon:", grid_lon.shape)



    import numpy as np
    from scipy.interpolate import griddata
    import plotly.graph_objects as go
    import json

    # Definir una escala coolwarm personalizada
    coolwarm_scale = [
        [0.0, 'rgb(59,76,192)'],  # Azul oscuro
        [0.35, 'rgb(116,173,209)'],  # Azul claro
        [0.5, 'rgb(221,221,221)'],  # Blanco/neutral
        [0.65, 'rgb(244,109,67)'],  # Naranja claro
        [1.0, 'rgb(180,4,38)']  # Rojo oscuro
    ]

    # Cargar el archivo GeoJSON (Colima.JSON) para referencia del mapa
    try:
        with open('Colima.json', 'r', encoding='latin-1') as file:
            colima_geojson = json.load(file)
    except Exception as e:
        st.error(f"No se pudo cargar el archivo GeoJSON: {e}")
        st.stop()

    st.subheader("Mapa con valores interpolados")

    st.markdown("""
    <div style="text-align: justify;">
    <p>Se utilizaron distintos métodos de interpolación para generar un mapa continuo del parámetro seleccionado. A continuación, puede seleccionar entre los distintos métodos y el mapa se generará a partir de la interpolación de los valores de las estaciones cercanas.</p>
    </div>
    """, unsafe_allow_html=True)


    # Mostrar mapa con estaciones
    if not df_resultado.empty:
        # Menú desplegable para seleccionar la columna numérica a graficar
        columna_grafico = st.selectbox("Selecciona el parámetro para graficar", options=columnas_numericas)

        # Filtrar estaciones con valores NaN en la columna seleccionada
        if columna_grafico in df_resultado.columns:
            df_filtrado = df_resultado.dropna(subset=[columna_grafico])

            if not df_filtrado.empty:
                # Preparar datos para interpolación
                latitudes = df_filtrado["Latitud"].values
                longitudes = df_filtrado["Longitud"].values
                valores = df_filtrado[columna_grafico].values

                margen_long = 0.08 * (longitudes.max() - longitudes.min())  # 5% del rango en longitud
                margen_lat = 0.08 * (latitudes.max() - latitudes.min())    # 5% del rango en latitud

                grid_lon, grid_lat = np.meshgrid(
                    np.linspace(longitudes.min() - margen_long, longitudes.max() + margen_long, 100),
                    np.linspace(latitudes.min() - margen_lat, latitudes.max() + margen_lat, 100)
                )

#            # Interpolar los datos
#            metodo_interpolacion = st.selectbox("Selecciona el método de interpolación", ["Linear", "Nearest", "IDW"])
#            if metodo_interpolacion in ["Linear", "Nearest"]:
#                interpolados = griddata(
#                    (longitudes, latitudes),
#                    valores,
#                    (grid_lon, grid_lat),
#                    method=metodo_interpolacion.lower()
#                )
#            elif metodo_interpolacion == "IDW":
#                # Implementación básica de IDW
#                def idw_interpolation(x, y, values, xi, yi):
#                    weights = 1 / np.sqrt((x - xi) ** 2 + (y - yi) ** 2 + 1e-10)
#                    return np.sum(weights * values) / np.sum(weights)

#                interpolados = np.zeros_like(grid_lon)
#                for i in range(grid_lon.shape[0]):
#                    for j in range(grid_lon.shape[1]):
#                        interpolados[i, j] = idw_interpolation(longitudes, latitudes, valores, grid_lon[i, j], grid_lat[i, j])

#bloque inicia
                # Interpolar los datos
                metodo_interpolacion = st.selectbox("Selecciona el método de interpolación", ["Linear", "Nearest", "IDW"])
                #columna = columna_grafico.strip()

                # 1. Filtrar valores válidos y sincronizar coordenadas
                mascara_validos = ~df_filtrado[columna_grafico].isna()
                longitudes = df_filtrado.loc[mascara_validos, "Longitud"].values
                latitudes = df_filtrado.loc[mascara_validos, "Latitud"].values
                valores = df_filtrado.loc[mascara_validos, columna_grafico].values

                # 2. Verificar si hay suficientes puntos para interpolar
                if len(valores) < 4:
                    st.warning("No hay suficientes estaciones con valores válidos para realizar la interpolación.")
                    st.stop()

                # 3. Interpolación
                if metodo_interpolacion in ["Linear", "Nearest"]:
                    try:
                        interpolados = griddata(
                            (longitudes, latitudes),
                            valores,
                            (grid_lon, grid_lat),
                            method=metodo_interpolacion.lower()
                        )
                    except Exception as e:
                        st.warning(f"Ocurrió un error con '{metodo_interpolacion}'. Usando 'nearest' como alternativa.")
                        interpolados = griddata(
                            (longitudes, latitudes),
                            valores,
                            (grid_lon, grid_lat),
                            method="nearest"
                        )

                elif metodo_interpolacion == "IDW":
                    # Implementación básica de IDW
                    def idw_interpolation(x, y, values, xi, yi):
                        weights = 1 / np.sqrt((x - xi) ** 2 + (y - yi) ** 2 + 1e-10)
                        return np.sum(weights * values) / np.sum(weights)

                    interpolados = np.zeros_like(grid_lon)
                    for i in range(grid_lon.shape[0]):
                        for j in range(grid_lon.shape[1]):
                            interpolados[i, j] = idw_interpolation(longitudes, latitudes, valores, grid_lon[i, j], grid_lat[i, j])
#bloque nuevo termina

            
#            # Crear la figura
#            fig = go.Figure()

#            # Añadir contornos de valores interpolados
#            fig.add_trace(
#                go.Contour(
#                    z=interpolados,
#                    x=grid_lon[0],
#                    y=grid_lat[:, 0],
#                    colorscale=coolwarm_colorscale,
#                    line=dict(color="black", width=1.0),  # Líneas más gruesas
#                    opacity=0.7,
#                    contours=dict(
#                        coloring="fill",  # Las zonas entre curvas tienen color
#                        showlabels=True,  # Mostrar etiquetas en los contornos
#                        labelfont=dict(size=10, color="black")
#                    ),
#                    colorbar=dict(
#                        title=f"{columna_grafico.strip()}",
#                        len=0.8  # Reducir la longitud de la barra de color
#                    ),
#                    name=f"Interpolación ({columna_grafico.strip()})"
#                )
#            )

#            # Añadir puntos de las estaciones
#            fig.add_trace(
#                go.Scatter(
#                    x=longitudes,
#                    y=latitudes,
#                    mode="markers",
 #                   marker=dict(
 #                       size=10,
 #                       color="black",
 #                       opacity=1.0,
 #                       #colorscale=coolwarm_scale,
 #                       showscale=False  # Ocultar barra de colores adicional
 #                   ),
 #                   text=df_filtrado["Clave"],
 #                   hoverinfo="text",
 #                   name="Estaciones"
 #               )
 #           )

 #           # Añadir contornos de los municipios
 #           for feature in colima_geojson["features"]:
 #               geometry = feature["geometry"]
 #               properties = feature["properties"]

 #               if "isla" not in properties.get("name", "").lower():
 #                   if geometry["type"] == "Polygon":
 #                       for coordinates in geometry["coordinates"]:
 #                           x_coords, y_coords = zip(*coordinates)
 #                           fig.add_trace(
 #                               go.Scatter(
  #                                  x=x_coords,
  #                                  y=y_coords,
  #                                  mode="lines",
  #                                  line=dict(color="black", width=2),
   #                                 showlegend=False
   #                             )
    #                        )
    #                elif geometry["type"] == "MultiPolygon":
    #                    for polygon in geometry["coordinates"]:
    #                        for coordinates in polygon:
 #                               x_coords, y_coords = zip(*coordinates)
 #                               fig.add_trace(
 #                                   go.Scatter(
 #                                       x=x_coords,
 #                                       y=y_coords,
 #                                       mode="lines",
 #                                       line=dict(color="black", width=2),
 #                                       showlegend=False
 #                                   )
 #                               )

            # Configuración del diseño
##            fig.update_layout(
###                title=f"Mapa de estaciones y contornos interpolados ({columna_grafico.strip()})",
##                xaxis_title="Longitud",
# #               yaxis_title="Latitud",
##                margin=dict(l=0, r=0, t=50, b=0)
##            )

#            #fig.update_layout(
#            #    xaxis=dict(
#            #        title="Longitud",
#            #        titlefont=dict(size=14, family="Arial"),
#            #        tickfont=dict(size=12, family="Arial"),
#            #        range=[-104.7, -103.3]  # Ajustar los límites iniciales del eje X (Longitud)
#            #    ),
#            #        yaxis=dict(
#            #        title="Latitud",
#            #        titlefont=dict(size=14, family="Arial"),
#            #        tickfont=dict(size=12, family="Arial"),
#            #        range=[18.5, 19.7]  # Ajustar los límites iniciales del eje Y (Latitud)
#            #    ),
#                geo=dict(
##                    center=dict(
##                        lon=-104.0,  # Longitud central
##                        lat=19.3     # Latitud central
##                    ),
##                    projection_scale=1  # Ajustar el zoom inicial
#            #    ),
#            #    margin=dict(l=20, r=20, t=50, b=20) 
#            #)

##            fig.update_layout(
##                xaxis=dict(
##                    title="Longitud",
##                    titlefont=dict(size=14, family="Arial"),
# #                   tickfont=dict(size=12, family="Arial"),
# #                   range=[-104.7, -103.3]
# #               ),
# #               yaxis=dict(
# #                   title="Latitud",
# #                   titlefont=dict(size=14, family="Arial"),
# #                   tickfont=dict(size=12, family="Arial"),
# #                   range=[18.5, 19.7]
# #               ),
# #               margin=dict(l=20, r=20, t=50, b=20)
# #           )


            
##            fig.update_layout(
##                width=1000,  # Ancho del gráfico
##                height=600,  # Altura del gráfico
##                title=f"Mapa de estaciones y contornos interpolados ({columna_grafico.strip()} para el año {ano}, mes {mes})",
##                xaxis_title="Longitud",
##                yaxis_title="Latitud",
##                margin=dict(l=0, r=0, t=50, b=0)  # Márgenes del gráfico
##            )

            # Ajustar el título dinámicamente según la selección de mes
##            if mes == 0:
##                titulo_mes = "Promedio Anual"
##            else:
##                titulo_mes = f"Mes {mes}"

##            # Configuración del título del gráfico
#            fig.update_layout(
##            title=f"Mapa de estaciones y contornos interpolados ({columna_grafico.strip()} para el año {ano}, {titulo_mes})",
##            xaxis_title="Longitud",
##            yaxis_title="Latitud",
##            margin=dict(l=0, r=0, t=50, b=0)
##            )

#            # Ajustar el título dinámicamente según la selección de mes
#            if mes == 0:
#                titulo_mes = "Promedio Anual"
#            else:
#                titulo_mes = f"Mes {mes}"
#
#            # Configuración consolidada del layout del gráfico
#            fig.update_layout(
#                title=dict(
#                    text=f"Mapa de estaciones y contornos interpolados ({columna_grafico.strip()} para el año {ano}, {titulo_mes})",
#                    x=0.5,
#                    xanchor='center',
#                    font=dict(size=18)
#                ),
#                xaxis=dict(
#                    title=dict(
#                        text="Longitud",
#                        font=dict(size=14, family="Arial", color='black')
#                    ),
#                    tickfont=dict(size=12, family="Arial", color='black'),
#                    range=[-104.7, -103.3],
#                    showgrid=False
#                ),
#                yaxis=dict(
#                    title=dict(
#                        text="Latitud",
#                        font=dict(size=14, family="Arial", color='black')
#                    ),
#                    tickfont=dict(size=12, family="Arial", color='black'),
#                    range=[18.5, 19.7],
#                    scaleanchor="x",
#                    showgrid=False
#                ),
#                plot_bgcolor="white",
#                paper_bgcolor="white",
#                width=1000,
#                height=600,
#                margin=dict(l=20, r=20, t=50, b=20),
#                showlegend=True
#            )


            

#            # Mostrar el gráfico
#            st.plotly_chart(fig, use_container_width=True)
#        else:
#            st.warning(f"No hay estaciones con datos válidos en la columna '{columna_grafico}'.")
#    else:
#        st.warning("La columna seleccionada no está disponible en el DataFrame.")
#else:
#    st.write("No hay datos disponibles para mostrar en el mapa.")



                # Crear la figura
                fig = go.Figure()

                # Añadir contornos de valores interpolados
                fig.add_trace(
                    go.Contour(
                        z=interpolados,
                        x=grid_lon[0],
                        y=grid_lat[:, 0],
                        colorscale=coolwarm_colorscale,
                        line=dict(color="black", width=1.0),  # Líneas más gruesas
                        opacity=0.7,
                        contours=dict(
                            coloring="fill",  # Las zonas entre curvas tienen color
                            showlabels=True,  # Mostrar etiquetas en los contornos
                            labelfont=dict(size=10, color="black")
                        ),
                        colorbar=dict(
                            title=f"{columna_grafico.strip()}",
                            len=0.8  # Reducir la longitud de la barra de color
                        ),
                        name=f"Interpolación ({columna_grafico.strip()})"
                    )
                )

                # Añadir puntos de las estaciones
                fig.add_trace(
                    go.Scatter(
                        x=longitudes,
                        y=latitudes,
                        mode="markers",
                        marker=dict(
                            size=10,
                            color="black",
                            opacity=1.0,
                            #colorscale=coolwarm_scale,
                            showscale=False  # Ocultar barra de colores adicional
                        ),
                        text=df_filtrado["Clave"],
                        hoverinfo="text",
                        name="Estaciones"
                    )
                )

                # Añadir contornos de los municipios
                for feature in colima_geojson["features"]:
                    geometry = feature["geometry"]
                    properties = feature["properties"]

                    if "isla" not in properties.get("name", "").lower():
                        if geometry["type"] == "Polygon":
                            for coordinates in geometry["coordinates"]:
                                x_coords, y_coords = zip(*coordinates)
                                fig.add_trace(
                                    go.Scatter(
                                        x=x_coords,
                                        y=y_coords,
                                        mode="lines",
                                        line=dict(color="black", width=2),
                                        showlegend=False
                                    )
                                )
                        elif geometry["type"] == "MultiPolygon":
                            for polygon in geometry["coordinates"]:
                                for coordinates in polygon:
                                    x_coords, y_coords = zip(*coordinates)
                                    fig.add_trace(
                                        go.Scatter(
                                            x=x_coords,
                                            y=y_coords,
                                            mode="lines",
                                            line=dict(color="black", width=2),
                                            showlegend=False
                                        )
                                    )

                # Configuración del diseño
                fig.update_layout(
                    title=f"Mapa de estaciones y contornos interpolados ({columna_grafico.strip()})",
                    xaxis_title="Longitud",
                    yaxis_title="Latitud",
                    margin=dict(l=0, r=0, t=50, b=0)
                )

                fig.update_layout(
                    xaxis=dict(
                        title="Longitud",
                        #titlefont=dict(size=14, family="Arial"),
                        tickfont=dict(size=12, family="Arial"),
                        range=[-104.7, -103.3]  # Ajustar los límites iniciales del eje X (Longitud)
                    ),
                        yaxis=dict(
                        title="Latitud",
                        #titlefont=dict(size=14, family="Arial"),
                        tickfont=dict(size=12, family="Arial"),
                        range=[18.5, 19.7]  # Ajustar los límites iniciales del eje Y (Latitud)
                    ),
                    geo=dict(
                        center=dict(
                            lon=-104.0,  # Longitud central
                            lat=19.3     # Latitud central
                        ),
                        projection_scale=1  # Ajustar el zoom inicial
                    ),
                    margin=dict(l=20, r=20, t=50, b=20) 
                )

                fig.update_layout(
                    width=1000,  # Ancho del gráfico
                    height=600,  # Altura del gráfico
                    title=f"Mapa de estaciones y contornos interpolados ({columna_grafico.strip()} para el año {ano}, mes {mes})",
                    xaxis_title="Longitud",
                    yaxis_title="Latitud",
                    margin=dict(l=0, r=0, t=50, b=0)  # Márgenes del gráfico
                )


                # Mostrar el gráfico
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning(f"No hay estaciones con datos válidos en la columna '{columna_grafico}'.")
        else:
            st.warning("La columna seleccionada no está disponible en el DataFrame.")
    else:
        st.write("No hay datos disponibles para mostrar en el mapa.")



    import streamlit as st

    # Expander con pestañas para explicar los métodos de interpolación
    with st.expander("Métodos de Interpolación", expanded=True):
        tab1, tab2, tab3 = st.tabs(["Linear", "Nearest", "IDW"])
    
        with tab1:
            st.markdown("""
            ### Interpolación Linear
            Este método calcula los valores interpolados mediante un ajuste lineal entre los puntos más cercanos a la ubicación deseada. 
            Es ideal para datos que se distribuyen suavemente en el espacio, ya que evita cambios bruscos entre las zonas interpoladas.

            **Implementación en el código:**
            - En el código, se utiliza la función `griddata` del paquete `scipy.interpolate`.
            - El parámetro `method="linear"` indica que se debe realizar una interpolación lineal.
            - Se calcula una grilla regular de valores interpolados basada en las latitudes, longitudes y valores de las estaciones cercanas.
            """, unsafe_allow_html=True)
    
        with tab2:
            st.markdown("""
            ### Interpolación Nearest (Vecino más cercano)
            Este método asigna el valor del punto más cercano a cada posición interpolada. 
            Es útil para datos discretos o cuando se desea mantener los valores originales sin suavizar la información.

            **Implementación en el código:**
            - En el código, también se utiliza la función `griddata` del paquete `scipy.interpolate`.
            - El parámetro `method="nearest"` asegura que el valor asignado en cada celda de la grilla corresponde al de la estación más cercana.
            - Este método es más rápido pero menos suave en comparación con la interpolación lineal.
            """, unsafe_allow_html=True)
    
        with tab3:
            st.markdown("""
            ### Interpolación Inverse Distance Weighting (IDW)
            Este método utiliza una fórmula basada en la distancia inversa para asignar valores interpolados.
            Los puntos más cercanos tienen mayor influencia en el valor final, mientras que los puntos más lejanos tienen menor impacto.

            **Implementación en el código:**
            - Se define una función `idw_interpolation` personalizada.
            - Para cada punto de la grilla, se calcula la distancia a todas las estaciones y se asigna un peso inversamente proporcional a esta distancia.
            - Los valores interpolados se calculan como la suma ponderada de los valores de las estaciones.
            - Este método es más computacionalmente intensivo, pero permite un control más detallado sobre la influencia de las estaciones cercanas.
            """, unsafe_allow_html=True)

    import numpy as np
    from scipy.interpolate import griddata
    import plotly.graph_objects as go
    import json

    # Parámetros para corrección
    gradiente_temperatura = -6.5  # °C/km
    incremento_radiacion = 0.12   # W/m²/km

## Definir una escala coolwarm personalizada
#coolwarm_scale = [
#    [0.0, 'rgb(59,76,192)'],  # Azul oscuro
#    [0.35, 'rgb(116,173,209)'],  # Azul claro
#    [0.5, 'rgb(221,221,221)'],  # Blanco/neutral
#    [0.65, 'rgb(244,109,67)'],  # Naranja claro
#    [1.0, 'rgb(180,4,38)']  # Rojo oscuro
#]

## Cargar el archivo GeoJSON
#try:
#    with open('Colima.JSON', 'r', encoding='latin-1') as file:
#        colima_geojson = json.load(file)
#except Exception as e:
#    st.error(f"No se pudo cargar el archivo GeoJSON: {e}")
#    st.stop()

## Obtener elevación interpolada para la malla
#def obtener_elevacion_interpolada(grid_lon, grid_lat, elevation_data, tile_size):
#    elevacion = np.zeros_like(grid_lon)
#    for i in range(grid_lon.shape[0]):
#        for j in range(grid_lon.shape[1]):
#            lon, lat = grid_lon[i, j], grid_lat[i, j]
#            lat_idx = int(max(0, min((30 - lat) * tile_size[0] / 15, tile_size[0] - 1)))
#            lon_idx = int(max(0, min((lon + 105) * tile_size[1] / 15, tile_size[1] - 1)))
#            elevacion[i, j] = elevation_data[lat_idx, lon_idx] / 1000  # Convertir a km
#    return elevacion

## Mostrar mapa con corrección de valores interpolados
#if not df_resultado.empty:
#    # Selección del parámetro y método de interpolación
#    columna_grafico = st.selectbox("Seleccione el parámetro para graficar", options=columnas_numericas)
#    #metodo_interpolacion = st.selectbox("Selecciona el método de interpolación", ["Linear", "Nearest", "IDW"])

#    # Filtrar estaciones válidas
#    df_filtrado = df_resultado.dropna(subset=[columna_grafico])

#    if not df_filtrado.empty:
#        latitudes = df_filtrado["Latitud"].values
#        longitudes = df_filtrado["Longitud"].values
#        valores = df_filtrado[columna_grafico].values
        
#        # Crear una malla de puntos para la interpolación con márgenes
#        margen_long = 0.08 * (longitudes.max() - longitudes.min())  # 5% del rango en longitud
#        margen_lat = 0.08 * (latitudes.max() - latitudes.min())    # 5% del rango en latitud

#        grid_lon, grid_lat = np.meshgrid(
#            np.linspace(longitudes.min() - margen_long, longitudes.max() + margen_long, 100),
#            np.linspace(latitudes.min() - margen_lat, latitudes.max() + margen_lat, 100)
#        )

#        # Interpolación inicial
#        if metodo_interpolacion in ["Linear", "Nearest"]:
#            interpolados = griddata(
#                (longitudes, latitudes),
#                valores,
#                (grid_lon, grid_lat),
#                method=metodo_interpolacion.lower()
#            )
#        elif metodo_interpolacion == "IDW":
#            def idw_interpolation(x, y, values, xi, yi):
#                weights = 1 / np.sqrt((x - xi) ** 2 + (y - yi) ** 2 + 1e-10)
#                return np.sum(weights * values) / np.sum(weights)

#            interpolados = np.zeros_like(grid_lon)
#            for i in range(grid_lon.shape[0]):
#                for j in range(grid_lon.shape[1]):
#                    interpolados[i, j] = idw_interpolation(longitudes, latitudes, valores, grid_lon[i, j], grid_lat[i, j])

#        # Obtener elevación interpolada
#        elevacion_interpolada = obtener_elevacion_interpolada(grid_lon, grid_lat, elevation_data, tile_size)

#        # Corregir valores interpolados
#        if "Temperatura" in columna_grafico:
#            valores_corregidos = interpolados + (gradiente_temperatura * elevacion_interpolada)
#        elif "Radiación" in columna_grafico:
#            valores_corregidos = interpolados * (1 + incremento_radiacion * elevacion_interpolada)
#        else:
#            valores_corregidos = interpolados  # Sin corrección para otros parámetros

#        # Crear figura
#        fig = go.Figure()

#        # Añadir contornos corregidos
#        fig.add_trace(
#            go.Contour(
#                z=valores_corregidos,
#                x=grid_lon[0],
#                y=grid_lat[:, 0],
#                colorscale=coolwarm_scale,
#                opacity=0.8,
#                line=dict(color="black", width=1.0),  # Líneas de contorno más gruesas
#                contours=dict(
#                    coloring="fill",  # Las zonas entre curvas tienen color
#                    showlabels=True,  # Mostrar etiquetas en los contornos
#                    labelfont=dict(size=10, color="black")
#                ),
#                colorbar=dict(
#                    title=f"{columna_grafico.strip()}",
#                    len=0.8  # Longitud de la barra de color
#                ),
#                name=f"Interpolación corregida ({columna_grafico.strip()})"
#            )
#        )

#        # Añadir puntos de las estaciones
#        fig.add_trace(
#            go.Scatter(
#                x=longitudes,
#                y=latitudes,
#                mode="markers",
#                marker=dict(
#                    size=10,
#                    color="black"  # Puntos negros
#                ),
#                text=df_filtrado["Clave"],
#                hoverinfo="text",
#                name="Estaciones"
#            )
#        )

#        # Añadir contornos de los municipios
#        for feature in colima_geojson["features"]:
#            geometry = feature["geometry"]
#            properties = feature["properties"]

#            if "isla" not in properties.get("name", "").lower():
#                if geometry["type"] == "Polygon":
#                    for coordinates in geometry["coordinates"]:
#                        x_coords, y_coords = zip(*coordinates)
#                        fig.add_trace(
#                            go.Scatter(
#                                x=x_coords,
#                                y=y_coords,
#                                mode="lines",
#                                line=dict(color="black", width=2),
#                                showlegend=False
#                            )
#                        )
#                elif geometry["type"] == "MultiPolygon":
#                    for polygon in geometry["coordinates"]:
#                        for coordinates in polygon:
#                            x_coords, y_coords = zip(*coordinates)
#                            fig.add_trace(
#                                go.Scatter(
#                                    x=x_coords,
#                                    y=y_coords,
#                                    mode="lines",
#                                    line=dict(color="black", width=2),
#                                    showlegend=False
#                                )
#                            )

#        fig.update_layout(
#            xaxis=dict(
#                title="Longitud",
#                titlefont=dict(size=14, family="Arial"),  # Tamaño y tipo de letra del título del eje X
#                tickfont=dict(size=12, family="Arial"),  # Tamaño y tipo de letra de las etiquetas del eje X
#            ),
#            yaxis=dict(
#                title="Latitud",
#                titlefont=dict(size=14, family="Arial"),  # Tamaño y tipo de letra del título del eje Y
#                tickfont=dict(size=12, family="Arial"),  # Tamaño y tipo de letra de las etiquetas del eje Y
#            )
#        )

#        fig.update_layout(
#            width=1000,  # Ancho del gráfico
#            height=600,  # Altura del gráfico
#            title=f"Mapa de estaciones y contornos interpolados ({columna_grafico.strip()} corregido)",
#            xaxis_title="Longitud",
#            yaxis_title="Latitud",
#            margin=dict(l=0, r=0, t=50, b=0)  # Márgenes del gráfico
#        )

#        fig.update_layout(
#            title=f"Mapa de estaciones y contornos interpolados ({columna_grafico.strip()} corregido)",
#            xaxis=dict(
#                title="Longitud",
#                titlefont=dict(size=14, family="Arial"),
#                tickfont=dict(size=12, family="Arial"),
#                range=[-104.8, -103.5]  # Centrar en Colima
#            ),
#            yaxis=dict(
#                title="Latitud",
#                titlefont=dict(size=14, family="Arial"),
#                tickfont=dict(size=12, family="Arial"),
#                range=[18.5, 19.5]  # Centrar en Colima
#            ),
#            margin=dict(l=20, r=20, t=50, b=20)
#        )


#        fig.update_layout(
#            xaxis=dict(
#                title="Longitud",
#                titlefont=dict(size=14, family="Arial"),
#                tickfont=dict(size=12, family="Arial"),
#                range=[-104.7, -103.3]  # Ajustar los límites iniciales del eje X (Longitud)
#            ),
#            yaxis=dict(
#                title="Latitud",
#                titlefont=dict(size=14, family="Arial"),
#                tickfont=dict(size=12, family="Arial"),
#                range=[18.5, 19.7]  # Ajustar los límites iniciales del eje Y (Latitud)
#            ),
#            geo=dict(
#                center=dict(
#                    lon=-104.0,  # Longitud central
#                    lat=19.3     # Latitud central
#                ),
#                projection_scale=1  # Ajustar el zoom inicial
#            ),
#            margin=dict(l=20, r=20, t=50, b=20) 
#        )




#        # Mostrar gráfico
#        st.plotly_chart(fig, use_container_width=True)
#    else:
#        st.warning("No hay estaciones válidas para la columna seleccionada.")
#else:
#    st.write("No hay datos disponibles.")


    import numpy as np
    from scipy.interpolate import griddata
    import plotly.graph_objects as go
    import json

    st.subheader("Mapa con valores corregidos para la altura")

    st.markdown("""
    <div style="text-align: justify;">
    <p>Los siguientes gráficos muestran los valores interpolados de los parámetros seleccionados, corregidos para considerar los efectos de la altitud sobre el nivel del mar. Estas correcciones incluyen:</p>
    <ul>
    <li>Ajustes en las temperaturas basados en un gradiente ambiental estándar, que reduce la temperatura en función del aumento de la elevación.</li>
    <li>Cálculos de la radiación solar, incluyendo un incremento del 12% por cada kilómetro sobre el nivel del mar, siguiendo el modelo descrito previamente.</li>
    </ul>
    <p>Estas modificaciones aseguran que los valores representados en los mapas reflejen de manera más precisa las condiciones climáticas reales ajustadas por la altitud.</p>
    </div>
    """, unsafe_allow_html=True)


## Parámetros para corrección
#gradiente_temperatura = -6.5  # °C/km
#incremento_radiacion = 0.12   # W/m²/km

## Escala de color personalizada
#coolwarm_scale = [
#    [0.0, 'rgb(59,76,192)'],
#    [0.35, 'rgb(116,173,209)'],
#    [0.5, 'rgb(221,221,221)'],
#    [0.65, 'rgb(244,109,67)'],
#    [1.0, 'rgb(180,4,38)']
#]

## Cargar el archivo GeoJSON
#try:
#    with open('Colima.json', 'r', encoding='latin-1') as file:
#        colima_geojson = json.load(file)
#except Exception as e:
#    st.error(f"No se pudo cargar el archivo GeoJSON: {e}")
#    st.stop()

## Función para obtener elevación interpolada
#def obtener_elevacion_interpolada(grid_lon, grid_lat, elevation_data, tile_size):
#    elevacion = np.zeros_like(grid_lon)
#    for i in range(grid_lon.shape[0]):
#        for j in range(grid_lon.shape[1]):
#            lon, lat = grid_lon[i, j], grid_lat[i, j]
#            lat_idx = int(max(0, min((30 - lat) * tile_size[0] / 15, tile_size[0] - 1)))
#            lon_idx = int(max(0, min((lon + 105) * tile_size[1] / 15, tile_size[1] - 1)))
#            elevacion[i, j] = elevation_data[lat_idx, lon_idx] / 1000  # Convertir a km
#    return elevacion

## Función de interpolación IDW
#def idw_interpolation(x, y, values, xi, yi, power=2):
#    weights = 1 / ((x - xi) ** 2 + (y - yi) ** 2 + 1e-10) ** (power / 2)
#    return np.sum(weights * values) / np.sum(weights)

## Mostrar mapa con corrección de valores interpolados
#if not df_resultado.empty:
#    # Selección del parámetro y método de interpolación
#    columna_grafico = st.selectbox(
#        "Seleccionar el parámetro para graficar",
#        options=columnas_numericas + [
#            "Radiación Solar Promedio (W/m²)",
#            "Radiación Solar Corregida (W/m²)"
#        ]
#    )
#    metodo_interpolacion = st.selectbox(
#        "Seleccionar el método de interpolación",
#        ["Linear", "Nearest", "IDW"]
#    )

#    # Filtrar estaciones válidas
#    df_filtrado = df_resultado.dropna(subset=[columna_grafico])

#    if not df_filtrado.empty:
#        latitudes = df_filtrado["Latitud"].values
#        longitudes = df_filtrado["Longitud"].values
#        valores = df_filtrado[columna_grafico].values

#        # Crear una malla de puntos para la interpolación con márgenes
#        margen_long = 0.08 * (longitudes.max() - longitudes.min())
#        margen_lat = 0.08 * (latitudes.max() - latitudes.min())
#
#        grid_lon, grid_lat = np.meshgrid(
#            np.linspace(longitudes.min() - margen_long, longitudes.max() + margen_long, 100),
#            np.linspace(latitudes.min() - margen_lat, latitudes.max() + margen_lat, 100)
#        )

#        # Realizar la interpolación
#        if metodo_interpolacion in ["Linear", "Nearest"]:
#            interpolados = griddata(
#                (longitudes, latitudes),
#                valores,
#                (grid_lon, grid_lat),
#                method=metodo_interpolacion.lower()
#            )
#        elif metodo_interpolacion == "IDW":
#            interpolados = np.zeros_like(grid_lon)
#            for i in range(grid_lon.shape[0]):
#                for j in range(grid_lon.shape[1]):
#                    interpolados[i, j] = idw_interpolation(longitudes, latitudes, valores, grid_lon[i, j], grid_lat[i, j])

#        # Obtener elevaciones interpoladas
#        elevacion_interpolada = obtener_elevacion_interpolada(grid_lon, grid_lat, elevation_data, tile_size)

#        # Corregir valores interpolados
#        if "Temperatura" in columna_grafico:
#            valores_corregidos = interpolados + (gradiente_temperatura * elevacion_interpolada)
#        elif "Radiación" in columna_grafico:
#            valores_corregidos = interpolados * (1 + 0.0*incremento_radiacion * elevacion_interpolada)
#        else:
#            valores_corregidos = interpolados

#        # Diccionario para las unidades según el parámetro
#        unidades = {
#            "Temperatura Media(ºC)": "ºC",
#            "Temperatura Máxima(ºC)": "ºC",
#            "Temperatura Mínima(ºC)": "ºC",
#            "Precipitación(mm)": "mm",
 #           "Evaporación(mm)": "mm",
 #           "Radiación Solar Promedio (W/m²)": "W/m²",
  #          "Radiación Solar Corregida (W/m²)": "W/m²"
#        }

#        # Crear la figura
#        fig = go.Figure()

#        # Añadir contornos corregidos
#        fig.add_trace(
#            go.Contour(
#                z=valores_corregidos,
#                x=grid_lon[0],
#                y=grid_lat[:, 0],
#                colorscale=coolwarm_colorscale,
#                opacity=0.7,
#                line=dict(color="black", width=1.0),  # Líneas de contorno más gruesas
#                contours=dict(
#                    coloring="fill",
#                    showlabels=True,
#                    labelfont=dict(size=10, color="black")
#                ),
#                colorbar=dict(
#                    title=unidades.get(columna_grafico, ""),  # Solo las unidades
#                    len=0.8,
#                    thickness=20,
#                    x=1.1,
#                    y=0.5
#                ),
#                name=f"Interpolación corregida ({columna_grafico.strip()})"
#            )
#        )


#        # Añadir puntos de las estaciones
#        fig.add_trace(
#            go.Scatter(
#                x=longitudes,
 #               y=latitudes,
#                mode="markers",
#                marker=dict(
#                    size=10,
#                    color="black"
#                ),
#                text=df_filtrado["Clave"],
#                hoverinfo="text",
#                name="Estaciones"
#            )
#        )

#        # Añadir contornos de los municipios
#        for feature in colima_geojson["features"]:
#            geometry = feature["geometry"]
#            properties = feature["properties"]

#            if "isla" not in properties.get("name", "").lower():
#                if geometry["type"] == "Polygon":
#                    for coordinates in geometry["coordinates"]:
#                        x_coords, y_coords = zip(*coordinates)
#                        fig.add_trace(
#                            go.Scatter(
#                                x=x_coords,
#                                y=y_coords,
#                                mode="lines",
#                                line=dict(color="black", width=2),
#                                showlegend=False
#                            )
#                        )
#                elif geometry["type"] == "MultiPolygon":
#                    for polygon in geometry["coordinates"]:
#                        for coordinates in polygon:
#                            x_coords, y_coords = zip(*coordinates)
#                            fig.add_trace(
#                                go.Scatter(
#                                    x=x_coords,
#                                    y=y_coords,
#                                    mode="lines",
#                                    line=dict(color="black", width=2),
#                                    showlegend=False
#                                )
#                            )

#        # Configuración del diseño
#        #fig.update_layout(
#        #    title=f"Mapa de estaciones y contornos interpolados ({columna_grafico.strip()} para el año {ano}, mes {mes})",
#        #    xaxis=dict(
#        #        title="Longitud",
#                #titlefont=dict(size=14, family="Arial"),
#        #        tickfont=dict(size=12, family="Arial"),
#        #        range=[-104.7, -103.3]
#        #    ),
#        #    yaxis=dict(
#        #        title="Latitud",
#                #titlefont=dict(size=14, family="Arial"),
#        #        tickfont=dict(size=12, family="Arial"),
#        #        range=[18.5, 19.7],
#        #        scaleanchor="x"
#        #    ),
#        #    width=1000,
#        #    height=600,
#        #    margin=dict(l=20, r=20, t=50, b=20)
#        #)

#        # Configuración del diseño
                        # Configuración consolidada del layout del gráfico
#        fig.update_layout(
#            title=dict(
#                text=f"Mapa de estaciones y contornos interpolados ({columna_grafico.strip()} para el año {ano}, {titulo_mes})",
#                x=0.5,
#                xanchor='center',
#                font=dict(size=18)
#            ),
#            xaxis=dict(
#                title=dict(
#                    text="Longitud",
#                    font=dict(size=14, family="Arial", color='black')
#                ),
#                tickfont=dict(size=12, family="Arial", color='black'),
#                range=[-104.7, -103.3],
#                showgrid=False
#            ),
#            yaxis=dict(
#                title=dict(
#                    text="Latitud",
#                    font=dict(size=14, family="Arial", color='black')
#                ),
#                tickfont=dict(size=12, family="Arial", color='black'),
#                range=[18.5, 19.7],
#                scaleanchor="x",
#                showgrid=False
#            ),
#            plot_bgcolor="white",
#            paper_bgcolor="white",
#            width=1000,
#            height=600,
#            margin=dict(l=20, r=20, t=50, b=20),
#            showlegend=True
#        )

#        # Mostrar gráfico
#        st.plotly_chart(fig, use_container_width=True)
        
##        # Configuración del diseño
##        fig.update_layout(
##            title=f"Mapa de estaciones y contornos interpolados ({columna_grafico.strip()} para el año {ano}, mes {mes})",
##            xaxis=dict(
##                title="Longitud",
##                titlefont=dict(size=14, family="Arial"),
##                tickfont=dict(size=12, family="Arial"),
##                range=[-104.7, -103.3]
##            ),
##            yaxis=dict(
##                title="Latitud",
##                titlefont=dict(size=14, family="Arial"),
##                tickfont=dict(size=12, family="Arial"),
##                range=[18.5, 19.7]
##            ),
##            width=1000,
##            height=600,
##            margin=dict(l=20, r=20, t=50, b=20)
##        )

#                    # Ajustar el título dinámicamente según la selección de mes
##        if mes == 0:
##            titulo_mes = "Promedio Anual"
##        else:
##            titulo_mes = f"Mes {mes}"

##        # Configuración del título del gráfico
##        fig.update_layout(
##        title=f"Mapa de estaciones y contornos interpolados ({columna_grafico.strip()} para el año {ano}, {titulo_mes})",
##        xaxis_title="Longitud",
##        yaxis_title="Latitud",
##        margin=dict(l=0, r=0, t=50, b=0)
##        )

#        # Mostrar gráfico
#        #st.plotly_chart(fig, use_container_width=True)
#    else:
#        st.warning("No hay estaciones válidas para la columna seleccionada.")
#else:
#    st.write("No hay datos disponibles.")


    # Parámetros para corrección
    gradiente_temperatura = -6.5  # °C/km
    incremento_radiacion = 0.12   # W/m²/km

    # Escala de color personalizada
    coolwarm_scale = [
        [0.0, 'rgb(59,76,192)'],
        [0.35, 'rgb(116,173,209)'],
        [0.5, 'rgb(221,221,221)'],
        [0.65, 'rgb(244,109,67)'],
        [1.0, 'rgb(180,4,38)']
    ]

    # Cargar el archivo GeoJSON
    try:
        with open('Colima.json', 'r', encoding='latin-1') as file:
            colima_geojson = json.load(file)
    except Exception as e:
        st.error(f"No se pudo cargar el archivo GeoJSON: {e}")
        st.stop()

    @st.cache_data
    # Función para obtener elevación interpolada
    def obtener_elevacion_interpolada(grid_lon, grid_lat, elevation_data, tile_size):
        elevacion = np.zeros_like(grid_lon)
        for i in range(grid_lon.shape[0]):
            for j in range(grid_lon.shape[1]):
                lon, lat = grid_lon[i, j], grid_lat[i, j]
                lat_idx = int(max(0, min((30 - lat) * tile_size[0] / 15, tile_size[0] - 1)))
                lon_idx = int(max(0, min((lon + 105) * tile_size[1] / 15, tile_size[1] - 1)))
                elevacion[i, j] = elevation_data[lat_idx, lon_idx] / 1000  # Convertir a km
        return elevacion

    @st.cache_data
    # Función de interpolación IDW
    def idw_interpolation(x, y, values, xi, yi, power=2):
        weights = 1 / ((x - xi) ** 2 + (y - yi) ** 2 + 1e-10) ** (power / 2)
        return np.sum(weights * values) / np.sum(weights)

    # Mostrar mapa con corrección de valores interpolados
    if not df_resultado.empty:
        # Selección del parámetro y método de interpolación
        columna_grafico = st.selectbox(
            "Seleccionar el parámetro para graficar",
            options=columnas_numericas + [
                # Radiación solar desactivada temporalmente en la interfaz
            ]
        )
        metodo_interpolacion = st.selectbox(
            "Seleccionar el método de interpolación",
            ["Linear", "Nearest", "IDW"]
        )

        # Filtrar estaciones válidas
        df_filtrado = df_resultado.dropna(subset=[columna_grafico])

        if not df_filtrado.empty:
            latitudes = df_filtrado["Latitud"].values
            longitudes = df_filtrado["Longitud"].values
            valores = df_filtrado[columna_grafico].values

            # Crear una malla de puntos para la interpolación con márgenes
            margen_long = 0.08 * (longitudes.max() - longitudes.min())
            margen_lat = 0.08 * (latitudes.max() - latitudes.min())

            grid_lon, grid_lat = np.meshgrid(
                np.linspace(longitudes.min() - margen_long, longitudes.max() + margen_long, 100),
                np.linspace(latitudes.min() - margen_lat, latitudes.max() + margen_lat, 100)
            )

            # Realizar la interpolación
            if metodo_interpolacion in ["Linear", "Nearest"]:
                interpolados = griddata(
                    (longitudes, latitudes),
                    valores,
                    (grid_lon, grid_lat),
                    method=metodo_interpolacion.lower()
                )
            elif metodo_interpolacion == "IDW":
                interpolados = np.zeros_like(grid_lon)
                for i in range(grid_lon.shape[0]):
                    for j in range(grid_lon.shape[1]):
                        interpolados[i, j] = idw_interpolation(longitudes, latitudes, valores, grid_lon[i, j], grid_lat[i, j])

            # Obtener elevaciones interpoladas
            elevacion_interpolada = obtener_elevacion_interpolada(grid_lon, grid_lat, elevation_data, tile_size)

            # Corregir valores interpolados
            if "Temperatura" in columna_grafico:
                valores_corregidos = interpolados + (gradiente_temperatura * elevacion_interpolada)
            elif "Radiación" in columna_grafico:
                valores_corregidos = interpolados * (1 + 0.0*incremento_radiacion * elevacion_interpolada)
            else:
                valores_corregidos = interpolados

            # Diccionario para las unidades según el parámetro
            unidades = {
                "Temperatura Media(ºC)": "ºC",
                "Temperatura Máxima(ºC)": "ºC",
                "Temperatura Mínima(ºC)": "ºC",
                "Precipitación(mm)": "mm",
                "Evaporación(mm)": "mm",
                "Radiación Solar Promedio (W/m²)": "W/m²",
                "Radiación Solar Corregida (W/m²)": "W/m²"
            }

            # Crear la figura
            fig = go.Figure()

            # Añadir contornos corregidos
            fig.add_trace(
                go.Contour(
                    z=valores_corregidos,
                    x=grid_lon[0],
                    y=grid_lat[:, 0],
                    colorscale=coolwarm_colorscale,
                    opacity=0.7,
                    line=dict(color="black", width=1.0),  # Líneas de contorno más gruesas
                    contours=dict(
                        coloring="fill",
                        showlabels=True,
                        labelfont=dict(size=10, color="black")
                    ),
                    colorbar=dict(
                        title=unidades.get(columna_grafico, ""),  # Solo las unidades
                        len=0.8,
                        thickness=20,
                        x=1.1,
                        y=0.5
                    ),
                    name=f"Interpolación corregida ({columna_grafico.strip()})"
                )
            )


            # Añadir puntos de las estaciones
            fig.add_trace(
                go.Scatter(
                    x=longitudes,
                    y=latitudes,
                    mode="markers",
                    marker=dict(
                        size=10,
                        color="black"
                    ),
                    text=df_filtrado["Clave"],
                    hoverinfo="text",
                    name="Estaciones"
                )
            )

            # Añadir contornos de los municipios
            for feature in colima_geojson["features"]:
                geometry = feature["geometry"]
                properties = feature["properties"]

                if "isla" not in properties.get("name", "").lower():
                    if geometry["type"] == "Polygon":
                        for coordinates in geometry["coordinates"]:
                            x_coords, y_coords = zip(*coordinates)
                            fig.add_trace(
                                go.Scatter(
                                    x=x_coords,
                                    y=y_coords,
                                    mode="lines",
                                    line=dict(color="black", width=2),
                                    showlegend=False
                                )
                            )
                    elif geometry["type"] == "MultiPolygon":
                        for polygon in geometry["coordinates"]:
                            for coordinates in polygon:
                                x_coords, y_coords = zip(*coordinates)
                                fig.add_trace(
                                    go.Scatter(
                                        x=x_coords,
                                        y=y_coords,
                                        mode="lines",
                                        line=dict(color="black", width=2),
                                        showlegend=False
                                    )
                                )

            # Configuración del diseño
            fig.update_layout(
                title=f"Mapa de estaciones y contornos interpolados ({columna_grafico.strip()} para el año {ano}, mes {mes})",
                xaxis=dict(
                    title="Longitud",
#                    titlefont=dict(size=14, family="Arial"),
                    tickfont=dict(size=12, family="Arial"),
                    range=[-104.7, -103.3]
                ),
                yaxis=dict(
                    title="Latitud",
#                    titlefont=dict(size=14, family="Arial"),
                    tickfont=dict(size=12, family="Arial"),
                    range=[18.5, 19.7]
                ),
                width=1000,
                height=600,
                margin=dict(l=20, r=20, t=50, b=20)
            )

            # Mostrar gráfico
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No hay estaciones válidas para la columna seleccionada.")
    else:
        st.write("No hay datos disponibles.")


    # Nueva sección para cálculo de interpolación en un punto específico
    st.subheader("Interpolación de parámetros en un punto específico")

    st.markdown("""
    <div style="text-align: justify;">
    <p>En esta sección, puede ingresar las coordenadas de un lugar (latitud y longitud) o seleccionar una de las capitales municipales de Colima. El sistema calculará los valores interpolados para el parámetro seleccionado utilizando cada uno de los métodos de interpolación disponibles.</p>
    </div>
    """, unsafe_allow_html=True)

    # Opciones de entrada
    opcion_punto = st.radio(
        "Seleccione la forma de definir el punto:",
        options=["Ingresar coordenadas", "Seleccionar capital municipal"]
    )

    # Diccionario con las capitales municipales y sus coordenadas
    capitales_municipales = {
        "Colima": (19.2433, -103.7247),
        "Villa de Álvarez": (19.2673, -103.7377),
        "Manzanillo": (19.0561, -104.3188),
        "Tecomán": (18.9092, -103.8770),
        "Comala": (19.3278, -103.7578),
        "Coquimatlán": (19.1801, -103.8181),
        "Armería": (18.9398, -103.9632),
        "Minatitlán": (19.3830, -104.0475),
        "Cuauhtémoc": (19.2363, -103.6618),
        "Ixtlahuacán": (18.8955, -103.7260)
    }

    if opcion_punto == "Ingresar coordenadas":
        latitud_punto = st.number_input("Ingrese la latitud", value=19.0, step=0.01)
        longitud_punto = st.number_input("Ingrese la longitud", value=-104.0, step=0.01)
    elif opcion_punto == "Seleccionar capital municipal":
        capital_seleccionada = st.selectbox("Seleccione la capital municipal", options=capitales_municipales.keys())
        latitud_punto, longitud_punto = capitales_municipales[capital_seleccionada]

    # Seleccionar el parámetro y método de interpolación
    parametro_seleccionado = st.selectbox(
        "Seleccione el parámetro climático",
        options=columnas_numericas + [
            # Radiación solar desactivada temporalmente en la interfaz
        ]
    )

    # Cálculo de valores interpolados
    if st.button("Calcular interpolación"):
        if not df_resultado.empty:
            df_filtrado = df_resultado.dropna(subset=[parametro_seleccionado])
            if not df_filtrado.empty:
                latitudes = df_filtrado["Latitud"].values
                longitudes = df_filtrado["Longitud"].values
                valores = df_filtrado[parametro_seleccionado].values

                # Calcular interpolaciones
                resultados_interpolacion = []

                # Interpolación Lineal
                valor_lineal = griddata(
                    (longitudes, latitudes),
                    valores,
                    (longitud_punto, latitud_punto),
                    method="linear"
                )
                resultados_interpolacion.append({"Método": "Lineal", "Valor Interpolado": valor_lineal})

                # Interpolación Nearest
                valor_nearest = griddata(
                    (longitudes, latitudes),
                    valores,
                    (longitud_punto, latitud_punto),
                    method="nearest"
                )
                resultados_interpolacion.append({"Método": "Nearest", "Valor Interpolado": valor_nearest})

                # Interpolación IDW
                valor_idw = idw_interpolation(longitudes, latitudes, valores, longitud_punto, latitud_punto, power=2)
                resultados_interpolacion.append({"Método": "IDW", "Valor Interpolado": valor_idw})

                # Crear DataFrame con los resultados
                df_resultados = pd.DataFrame(resultados_interpolacion)

                # Mostrar resultados
                st.subheader("Resultados de la interpolación")
                st.dataframe(df_resultados)

                # Descarga de los resultados
                csv_resultados = df_resultados.to_csv(index=False)
                st.download_button(
                    label="Descargar resultados como CSV",
                    data=csv_resultados,
                    file_name=f"resultados_interpolacion_{parametro_seleccionado.strip()}.csv",
                    mime="text/csv"
                )
            else:
                st.warning("No hay estaciones válidas para el parámetro seleccionado.")
        else:
            st.error("No hay datos disponibles para realizar la interpolación.")

    #############################################################################

#elif seccion == "Registro de datos históricos":
    claves_colima = st.session_state.claves_colima

    # Parámetro a graficar
    parametro = st.selectbox(
        "Selecciona el parámetro para graficar",
        ['Precipitación(mm)', 'Temperatura Media(ºC)', 'Temperatura Máxima(ºC)', 
         'Temperatura Mínima(ºC)', 'Evaporación(mm)'],
        key="parametro_selectbox"
    )

    # Calcular la cantidad de registros válidos por estación para el parámetro seleccionado
    estaciones_datos = {}
    for estacion in claves_colima:
        archivo_estacion = os.path.join(output_dir_colima, f"{estacion}_df.csv")
        if os.path.exists(archivo_estacion):
            try:
                df_estacion = pd.read_csv(archivo_estacion)
                #df_estacion = pd.read_csv(archivo_estacion)
                df_estacion.columns = df_estacion.columns.str.strip()

                df_estacion['Fecha'] = pd.to_datetime(df_estacion['Fecha'], format='%Y/%m/%d', errors='coerce')
            
                # Asegurar que el parámetro es numérico
                if parametro in df_estacion.columns:
                    df_estacion[parametro] = pd.to_numeric(
                        df_estacion[parametro].astype(str).str.replace('[^0-9.-]', '', regex=True), errors='coerce'
                    )
                    # Contar solo registros válidos (no vacíos y no cero)
                    registros_validos = df_estacion[parametro][(df_estacion[parametro] > 0)].count()
                    estaciones_datos[estacion] = registros_validos
                else:
                    estaciones_datos[estacion] = 0
            except Exception as e:
                st.warning(f"Error al procesar la estación {estacion}: {e}")
        else:
            estaciones_datos[estacion] = 0

    # Identificar la estación con más registros válidos
    estacion_max_datos = max(estaciones_datos, key=estaciones_datos.get)
    max_datos = estaciones_datos[estacion_max_datos]

    # Definir los rangos de grupos
    rango_100_50 = (max_datos * 0.5, max_datos)
    rango_50_25 = (max_datos * 0.25, max_datos * 0.5)
    rango_menos_25 = (0, max_datos * 0.25)

    # Clasificar estaciones en grupos
    grupos_estaciones = {
        "100% - 50% de registros válidos": [est for est, datos in estaciones_datos.items() if rango_100_50[0] <= datos <= rango_100_50[1]],
        "50% - 25% de registros válidos": [est for est, datos in estaciones_datos.items() if rango_50_25[0] <= datos < rango_50_25[1]],
        "Menos del 25% de registros válidos": [est for est, datos in estaciones_datos.items() if rango_menos_25[0] <= datos < rango_menos_25[1]],
    }

    # Mostrar un resumen de los grupos
    st.subheader("Resumen de las estaciones por cantidad de datos válidos")
    st.write(f"Estación con más registros válidos: {estacion_max_datos} ({max_datos} registros válidos)")

    # Menú desplegable para seleccionar el grupo
    grupo_seleccionado = st.selectbox("Selecciona el grupo de estaciones según cantidad de datos válidos", list(grupos_estaciones.keys()), key="grupo_selectbox")

    # Filtrar estaciones según el grupo seleccionado
    estaciones_filtradas = grupos_estaciones[grupo_seleccionado]

    # Nuevo menú desplegable con estaciones filtradas
    estacion = st.selectbox("Selecciona una estación meteorológica", estaciones_filtradas, key="estacion_filtrada_selectbox")

    # Ruta del archivo de la estación seleccionada
    archivo_estacion = os.path.join(output_dir_colima, f"{estacion}_df.csv")

    # Leer el archivo CSV de la estación seleccionada
    try:
        df_estacion = pd.read_csv(archivo_estacion)
        #df_estacion = pd.read_csv(archivo_estacion)
        df_estacion.columns = df_estacion.columns.str.strip()

        df_estacion['Fecha'] = pd.to_datetime(df_estacion['Fecha'], format='%Y/%m/%d', errors='coerce')
        df_estacion['Año'] = df_estacion['Fecha'].dt.year
        df_estacion['Mes'] = df_estacion['Fecha'].dt.month

        # Asegurar que el parámetro es numérico
        if parametro in df_estacion.columns:
            df_estacion[parametro] = pd.to_numeric(
                df_estacion[parametro].astype(str).str.replace('[^0-9.-]', '', regex=True), errors='coerce'
            )

        # Opciones de análisis: anual o mensual
        analisis = st.radio("Selecciona el tipo de análisis", ["Anual", "Mensual"], key="analisis_radio")

        if analisis == "Anual":
            # Calcular promedios anuales y asegurarse de incluir años con 0 registros
            all_years = pd.DataFrame({'Año': range(df_estacion['Año'].min(), df_estacion['Año'].max() + 1)})
            promedios = df_estacion.groupby('Año')[parametro].mean().reset_index()
            promedios.columns = ['Año', f"Promedio de {parametro.strip()}"]

            # Combinar con todos los años para incluir años sin datos
            promedios = all_years.merge(promedios, on='Año', how='left')
            promedios[f"Promedio de {parametro.strip()}"] = promedios[f"Promedio de {parametro.strip()}"].fillna(0)

            #    Gráfico de barras con espacios para años sin datos
            st.subheader(f"Promedios anuales de {parametro.strip()} en la estación {estacion} (Coordenadas: {df_estacion['Latitud'].iloc[0]}, {df_estacion['Longitud'].iloc[0]})")
            fig = go.Figure()

            # Determinar cuartiles para la escala de colores
            valores_validos = promedios[f"Promedio de {parametro.strip()}"][promedios[f"Promedio de {parametro.strip()}"] > 0]
            q1, q2, q3 = valores_validos.quantile([0.25, 0.5, 0.75]).values if not valores_validos.empty else (0, 0, 0)

            # Asignar colores según cuartiles
            for _, row in promedios.iterrows():
                color = "rgb(49,130,189)"  # Azul para Q1
                if row[f"Promedio de {parametro.strip()}"] > q3:
                    color = "rgb(214,39,40)"  # Rojo para Q4
                elif row[f"Promedio de {parametro.strip()}"] > q2:
                    color = "rgb(255,127,14)"  # Naranja para Q3
                elif row[f"Promedio de {parametro.strip()}"] > q1:
                    color = "rgb(255,215,0)"  # Amarillo para Q2

                fig.add_trace(go.Bar(
                    x=[row['Año']],
                    y=[row[f"Promedio de {parametro.strip()}"]],
                    marker_color=color,
                    name=f"Año {int(row['Año'])}"
                ))

            # Configuración del gráfico
            fig.update_layout(
                title=f"Promedios anuales de {parametro.strip()} en la estación {estacion} (Coordenadas: {df_estacion['Latitud'].iloc[0]}, {df_estacion['Longitud'].iloc[0]})",
                xaxis_title="Año",
                yaxis_title=f"Promedio de {parametro.strip()}",
                showlegend=False
            )

            st.plotly_chart(fig)

        else:
            # Seleccionar año para análisis mensual
            ano_seleccionado = st.selectbox(
                "Selecciona el año",
                df_estacion['Año'].unique(),
                key="ano_seleccionado_selectbox"
            )

            # Filtrar por año seleccionado y calcular promedios mensuales
            df_anual = df_estacion[df_estacion['Año'] == ano_seleccionado]
            all_months = pd.Series(range(1, 13))
            promedios = df_anual.groupby('Mes')[parametro].mean().reindex(all_months, fill_value=0).reset_index()
            promedios.columns = ['Mes', f"Promedio de {parametro.strip()}"]

            # Gráfico de barras
            st.subheader(f"Promedios mensuales de {parametro.strip()} en {ano_seleccionado} para la estación {estacion}")
            st.bar_chart(promedios.set_index('Mes'))

    except FileNotFoundError:
        st.error(f"No se encontró el archivo para la estación seleccionada: {estacion}")
    except Exception as e:
        st.error(f"Error al procesar el archivo de la estación {estacion}: {e}")

    columna_grafico = parametro
    import plotly.express as px
    import plotly.graph_objects as go
    import plotly.graph_objects as go

    # Crear el agrupamiento de estaciones según la cantidad de registros por estación
    agrupamiento_estaciones = {
        "50-100%": [],
        "25-50%": [],
        "0-25%": []
    }

    # Calcular el máximo de registros para una estación
    if not df_resultado.empty:
        max_registros = df_resultado['Clave'].value_counts().max()

        # Crear los grupos
        for clave, count in df_resultado['Clave'].value_counts().items():
            if count >= 0.5 * max_registros:
                agrupamiento_estaciones["50-100%"].append(clave)
            elif 0.25 * max_registros <= count < 0.5 * max_registros:
                agrupamiento_estaciones["25-50%"].append(clave)
            else:
                agrupamiento_estaciones["0-25%"].append(clave)

    # Identificar el grupo de la estación seleccionada
    grupo_seleccionado = None
    for grupo, estaciones in agrupamiento_estaciones.items():
        if estacion in estaciones:
            grupo_seleccionado = grupo
            break

    # Verificar si el grupo seleccionado existe y filtrar las estaciones
    if grupo_seleccionado:
        estaciones_del_grupo = agrupamiento_estaciones[grupo_seleccionado]
        df_filtrado = df_resultado[df_resultado['Clave'].isin(estaciones_del_grupo)].dropna(subset=["Latitud", "Longitud"])
    else:
        df_filtrado = pd.DataFrame()  # Si no se encuentra grupo, dejar vacío

    if not df_filtrado.empty:
        # Crear una figura base con fondo blanco
        fig = go.Figure()

        # Añadir las estaciones como puntos
        fig.add_trace(
            go.Scatter(
                x=df_filtrado['Longitud'],
                y=df_filtrado['Latitud'],
                mode='markers',
                marker=dict(size=8, color='blue', symbol='circle'),
                text=df_filtrado['Clave'],
                hoverinfo='text',
                name="Estaciones"
            )
        )

        # Añadir la estación seleccionada con un símbolo destacado
        estacion_seleccionada = df_filtrado[df_filtrado['Clave'] == estacion]
        if not estacion_seleccionada.empty:
            fig.add_trace(
                go.Scatter(
                    x=estacion_seleccionada['Longitud'],
                    y=estacion_seleccionada['Latitud'],
                    mode='markers',
                    marker=dict(size=14, color='gold', symbol='star'),
                    hoverinfo='none',  # Eliminar texto al pasar el cursor
                    name="Estación seleccionada"
                )
            )

        # Añadir los polígonos de los municipios desde GeoJSON
        for feature in colima_geojson["features"]:
            geometry = feature["geometry"]
            properties = feature["properties"]

            # Excluir islas si es necesario
            if "isla" not in properties.get("name", "").lower():
                if geometry["type"] == "Polygon":
                    for coordinates in geometry["coordinates"]:
                        x_coords, y_coords = zip(*coordinates)
                        fig.add_trace(
                            go.Scatter(
                                x=x_coords,
                                y=y_coords,
                                mode="lines",
                                line=dict(color="black", width=1.5),
                                showlegend=False
                            )
                        )
                elif geometry["type"] == "MultiPolygon":
                    for polygon in geometry["coordinates"]:
                        for coordinates in polygon:
                            x_coords, y_coords = zip(*coordinates)
                            fig.add_trace(
                                go.Scatter(
                                    x=x_coords,
                                    y=y_coords,
                                    mode="lines",
                                    line=dict(color="black", width=1.5),
                                    showlegend=False
                                )
                            )

        # Configurar el diseño del gráfico
        fig.update_layout(
            title="Mapa de Estaciones en Colima (Grupo Actual)",
            xaxis_title="Longitud",
            yaxis_title="Latitud",
            xaxis=dict(
                scaleanchor="y",
                scaleratio=1,
                showgrid=False,
                title_font=dict(color='blue'),
                tickfont=dict(color='blue')  # Ticks azules en el eje X
            ),
            yaxis=dict(
                showgrid=False,
                title_font=dict(color='blue'),
                tickfont=dict(color='blue')  # Ticks azules en el eje Y
            ),
            plot_bgcolor="white",  # Fondo blanco
            paper_bgcolor="white",  # Fondo blanco fuera del área de trazado
            legend=dict(
            font=dict(color='blue')),
            showlegend=True,
            width=800,
            height=600
        )

        # Centrar la vista inicial en la capital de Colima
        fig.update_xaxes(range=[-104.5, -103.5])  # Ajustar según las coordenadas de Colima
        fig.update_yaxes(range=[18.5, 19.5])  # Ajustar según las coordenadas de Colima

        # Mostrar el gráfico
        st.plotly_chart(fig)

##########################################

elif seccion == "Predicción con Prophet":
    # ================================================================
    # MÓDULO SIMPLE DE PRONÓSTICO POR FECHA CON PROPHET
    # Los CSV se cargan manualmente para evitar dependencias de rutas,
    # archivos preprocesados o variables guardadas en session_state.
    # ================================================================
    import io
    import os
    import pandas as pd
    import numpy as np
    import streamlit as st
    import plotly.graph_objects as go
    from prophet import Prophet

    st.title("Pronóstico climatológico por fecha")
    st.caption(
        "Carga uno o varios CSV de estaciones meteorológicas, selecciona una estación, "
        "una variable y una fecha futura. Prophet utiliza la serie histórica diaria "
        "para estimar el valor esperado en esa fecha."
    )

    archivos_subidos = st.file_uploader(
        "Carga los archivos CSV de las estaciones",
        type=["csv"],
        accept_multiple_files=True,
        help="Puedes cargar un solo CSV si únicamente necesitas una gráfica."
    )

    def _leer_csv_estacion(archivo):
        """Lee y normaliza un CSV de estación meteorológica."""
        try:
            archivo.seek(0)
            df = pd.read_csv(archivo)
        except UnicodeDecodeError:
            archivo.seek(0)
            df = pd.read_csv(archivo, encoding="latin-1")

        # Los CSV originales traen espacios iniciales en varias columnas.
        df.columns = df.columns.astype(str).str.strip()

        if "Fecha" not in df.columns:
            raise ValueError("El archivo no contiene la columna 'Fecha'.")

        df["Fecha"] = pd.to_datetime(df["Fecha"], errors="coerce", yearfirst=True)
        df = df.dropna(subset=["Fecha"]).copy()

        # Clave de estación: usar la columna si existe; en caso contrario, el nombre del archivo.
        if "Clave" in df.columns and df["Clave"].notna().any():
            clave = str(df["Clave"].dropna().iloc[0]).strip()
        else:
            clave = os.path.basename(getattr(archivo, "name", "Estación")).replace("_df.csv", "").replace(".csv", "")
        df["Clave"] = clave

        # Convertir variables climáticas a numérico y tratar símbolos de dato faltante.
        columnas_no_numericas = {"Fecha", "Clave"}
        for col in df.columns:
            if col not in columnas_no_numericas:
                if df[col].dtype == object:
                    serie = (
                        df[col].astype(str)
                        .str.strip()
                        .replace({"-": np.nan, "": np.nan, "nan": np.nan, "N/A": np.nan, "NA": np.nan})
                        .str.replace(",", "", regex=False)
                    )
                    df[col] = pd.to_numeric(serie, errors="coerce")
                else:
                    df[col] = pd.to_numeric(df[col], errors="coerce")

        return df

    if not archivos_subidos:
        st.info("Carga al menos un CSV para comenzar.")
    else:
        estaciones = {}
        errores = []

        for archivo in archivos_subidos:
            try:
                df_tmp = _leer_csv_estacion(archivo)
                clave_tmp = str(df_tmp["Clave"].iloc[0])
                # Si se cargan dos archivos con la misma clave, se concatenan.
                if clave_tmp in estaciones:
                    estaciones[clave_tmp] = pd.concat([estaciones[clave_tmp], df_tmp], ignore_index=True)
                else:
                    estaciones[clave_tmp] = df_tmp
            except Exception as e:
                errores.append(f"{getattr(archivo, 'name', 'archivo')}: {e}")

        for error in errores:
            st.warning(error)

        if not estaciones:
            st.error("No fue posible leer ningún archivo válido.")
        else:
            estacion_seleccionada = st.selectbox(
                "Estación meteorológica",
                sorted(estaciones.keys())
            )
            df_estacion = estaciones[estacion_seleccionada].copy()
            df_estacion = df_estacion.sort_values("Fecha")

            # Variables climáticas de interés presentes en el CSV.
            preferidas = [
                "Precipitación(mm)",
                "Temperatura Media(ºC)",
                "Temperatura Máxima(ºC)",
                "Temperatura Mínima(ºC)",
                "Evaporación(mm)",
            ]
            variables_disponibles = [
                c for c in preferidas
                if c in df_estacion.columns and pd.to_numeric(df_estacion[c], errors="coerce").notna().sum() >= 20
            ]

            # También permitir otras columnas numéricas, excepto coordenadas.
            excluidas = {"Latitud", "Longitud", "Clave"}
            extras = [
                c for c in df_estacion.columns
                if c not in variables_disponibles
                and c not in excluidas
                and c != "Fecha"
                and pd.api.types.is_numeric_dtype(df_estacion[c])
                and df_estacion[c].notna().sum() >= 20
            ]
            variables_disponibles.extend(extras)

            if not variables_disponibles:
                st.error("El CSV no contiene suficientes datos numéricos para entrenar Prophet.")
            else:
                variable_seleccionada = st.selectbox(
                    "Variable climática",
                    variables_disponibles,
                    index=variables_disponibles.index("Precipitación(mm)") if "Precipitación(mm)" in variables_disponibles else 0
                )

                serie = df_estacion[["Fecha", variable_seleccionada]].copy()
                serie[variable_seleccionada] = pd.to_numeric(serie[variable_seleccionada], errors="coerce")
                serie = serie.dropna(subset=["Fecha", variable_seleccionada])

                # Si existe más de un registro en el mismo día, usar el promedio diario.
                serie = (
                    serie.groupby("Fecha", as_index=False)[variable_seleccionada]
                    .mean()
                    .sort_values("Fecha")
                )

                fecha_min = serie["Fecha"].min()
                fecha_max = serie["Fecha"].max()

                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Primer registro", fecha_min.strftime("%d/%m/%Y"))
                with col2:
                    st.metric("Último registro", fecha_max.strftime("%d/%m/%Y"))
                with col3:
                    st.metric("Días con datos", f"{len(serie):,}")

                fecha_predeterminada = (fecha_max + pd.Timedelta(days=365)).date()
                fecha_objetivo = st.date_input(
                    "Fecha que deseas estimar",
                    value=fecha_predeterminada,
                    min_value=fecha_min.date(),
                    help="Para un pronóstico futuro, selecciona una fecha posterior al último registro histórico."
                )
                fecha_objetivo = pd.Timestamp(fecha_objetivo)

                if fecha_objetivo <= fecha_max:
                    st.info(
                        "La fecha seleccionada está dentro del periodo histórico. "
                        "Se mostrará la estimación del modelo y, cuando exista, el dato observado."
                    )

                # Para evitar cargar Prophet con decenas de miles de ceros o registros duplicados,
                # se mantiene la frecuencia diaria real y se eliminan únicamente los faltantes.
                prophet_df = serie.rename(columns={"Fecha": "ds", variable_seleccionada: "y"})[["ds", "y"]]

                # Prophet requiere por lo menos dos observaciones, pero usamos un umbral mayor por estabilidad.
                if len(prophet_df) < 30:
                    st.warning("Se requieren al menos 30 observaciones válidas para realizar el pronóstico.")
                else:
                    if st.button("Estimar clima en la fecha seleccionada", type="primary"):
                        with st.spinner("Entrenando Prophet y calculando la estimación..."):
                            try:
                                # La estacionalidad anual es especialmente relevante para variables climáticas.
                                modelo = Prophet(
                                    yearly_seasonality=True,
                                    weekly_seasonality=False,
                                    daily_seasonality=False,
                                    interval_width=0.80,
                                )
                                modelo.fit(prophet_df)

                                # Predecir únicamente hasta la fecha requerida.
                                if fecha_objetivo > fecha_max:
                                    dias_futuro = int((fecha_objetivo - fecha_max).days)
                                else:
                                    dias_futuro = 0

                                futuro = modelo.make_future_dataframe(
                                    periods=dias_futuro,
                                    freq="D",
                                    include_history=True
                                )
                                predicciones = modelo.predict(futuro)

                                # Cuando la fecha está dentro del histórico, puede no aparecer si hay huecos;
                                # en ese caso se predice explícitamente ese día.
                                fila_objetivo = predicciones[predicciones["ds"].dt.normalize() == fecha_objetivo.normalize()]
                                if fila_objetivo.empty:
                                    fila_objetivo = modelo.predict(pd.DataFrame({"ds": [fecha_objetivo]}))

                                resultado = fila_objetivo.iloc[0]
                                estimacion = float(resultado["yhat"])
                                inferior = float(resultado["yhat_lower"])
                                superior = float(resultado["yhat_upper"])

                                # Precipitación y evaporación no tienen interpretación física negativa.
                                es_no_negativa = variable_seleccionada in {"Precipitación(mm)", "Evaporación(mm)"}
                                if es_no_negativa:
                                    estimacion = max(0.0, estimacion)
                                    inferior = max(0.0, inferior)
                                    superior = max(0.0, superior)

                                unidades = ""
                                if "(mm)" in variable_seleccionada:
                                    unidades = " mm"
                                elif "ºC" in variable_seleccionada or "°C" in variable_seleccionada:
                                    unidades = " °C"

                                st.success(
                                    f"Estimación para {fecha_objetivo.strftime('%d/%m/%Y')}: "
                                    f"**{estimacion:.2f}{unidades}**"
                                )
                                st.caption(
                                    f"Intervalo predictivo del 80 %: {inferior:.2f} a {superior:.2f}{unidades}. "
                                    "Es una estimación probabilística basada en el comportamiento histórico; no equivale a una medición real."
                                )

                                # Comparación con observación si la fecha pertenece al histórico.
                                observado = serie.loc[
                                    serie["Fecha"].dt.normalize() == fecha_objetivo.normalize(),
                                    variable_seleccionada
                                ]
                                if not observado.empty:
                                    st.write(f"Dato observado en esa fecha: **{observado.iloc[0]:.2f}{unidades}**")

                                # Gráfica enfocada en los últimos 3 años de historia + pronóstico hasta la fecha objetivo.
                                inicio_grafica = max(fecha_min, fecha_max - pd.DateOffset(years=3))
                                pred_plot = predicciones[predicciones["ds"] >= inicio_grafica].copy()
                                hist_plot = prophet_df[prophet_df["ds"] >= inicio_grafica].copy()

                                if es_no_negativa:
                                    for col in ["yhat", "yhat_lower", "yhat_upper"]:
                                        pred_plot[col] = pred_plot[col].clip(lower=0)

                                fig = go.Figure()
                                fig.add_trace(go.Scatter(
                                    x=hist_plot["ds"], y=hist_plot["y"],
                                    mode="markers", name="Dato observado",
                                    marker=dict(size=3, opacity=0.45)
                                ))
                                fig.add_trace(go.Scatter(
                                    x=pred_plot["ds"], y=pred_plot["yhat"],
                                    mode="lines", name="Estimación Prophet"
                                ))
                                fig.add_trace(go.Scatter(
                                    x=pred_plot["ds"], y=pred_plot["yhat_upper"],
                                    mode="lines", line=dict(width=0), showlegend=False
                                ))
                                fig.add_trace(go.Scatter(
                                    x=pred_plot["ds"], y=pred_plot["yhat_lower"],
                                    mode="lines", fill="tonexty", line=dict(width=0),
                                    name="Intervalo predictivo 80 %"
                                ))
                                fig.add_vline(
                                    x=fecha_max.timestamp() * 1000,
                                    line_dash="dash",
                                    annotation_text="Fin de datos históricos"
                                )
                                fig.add_trace(go.Scatter(
                                    x=[fecha_objetivo], y=[estimacion],
                                    mode="markers", name="Fecha seleccionada",
                                    marker=dict(size=11, symbol="diamond")
                                ))
                                fig.update_layout(
                                    title=f"{variable_seleccionada} · Estación {estacion_seleccionada}",
                                    xaxis_title="Fecha",
                                    yaxis_title=f"{variable_seleccionada}",
                                    hovermode="x unified",
                                    legend_title="Serie",
                                )
                                st.plotly_chart(fig, use_container_width=True)

                                # Tabla compacta para usarla como evidencia en la presentación.
                                resumen = pd.DataFrame({
                                    "Estación": [estacion_seleccionada],
                                    "Variable": [variable_seleccionada],
                                    "Fecha objetivo": [fecha_objetivo.strftime("%d/%m/%Y")],
                                    "Estimación": [round(estimacion, 3)],
                                    "Límite inferior (80%)": [round(inferior, 3)],
                                    "Límite superior (80%)": [round(superior, 3)],
                                })
                                st.dataframe(resumen, use_container_width=True, hide_index=True)

                            except Exception as e:
                                st.error(f"No fue posible generar el pronóstico: {e}")


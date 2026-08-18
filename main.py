import io
import math
from datetime import date

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from scipy.interpolate import griddata


st.set_page_config(
    page_title="ClimaPredictor Colima",
    page_icon="🌦️",
    layout="wide",
    initial_sidebar_state="expanded",
)

VARIABLES = [
    "Precipitación(mm)",
    "Temperatura Media(ºC)",
    "Temperatura Máxima(ºC)",
    "Temperatura Mínima(ºC)",
    "Evaporación(mm)",
]

NONNEGATIVE = {"Precipitación(mm)", "Evaporación(mm)"}


# ---------- Utilidades de datos ----------

def normalizar_columnas(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [str(c).strip() for c in df.columns]
    return df


@st.cache_data(show_spinner=False)
def leer_csv_estacion(nombre: str, contenido: bytes) -> pd.DataFrame:
    df = pd.read_csv(io.BytesIO(contenido))
    df = normalizar_columnas(df)

    requeridas = {"Fecha", "Latitud", "Longitud"}
    faltantes = requeridas - set(df.columns)
    if faltantes:
        raise ValueError(f"{nombre}: faltan columnas {', '.join(sorted(faltantes))}")

    df["Fecha"] = pd.to_datetime(df["Fecha"], errors="coerce", yearfirst=True)

    for col in VARIABLES + ["Latitud", "Longitud"]:
        if col in df.columns:
            df[col] = (
                df[col]
                .astype(str)
                .str.strip()
                .replace({"-": np.nan, "": np.nan, "nan": np.nan, "None": np.nan})
            )
            df[col] = pd.to_numeric(df[col], errors="coerce")

    if "Clave" not in df.columns:
        clave = nombre.replace("_df.csv", "").replace(".csv", "")
        df["Clave"] = clave
    else:
        df["Clave"] = df["Clave"].astype(str).str.strip()

    df = df.dropna(subset=["Fecha", "Latitud", "Longitud"])
    return df


def cargar_estaciones(archivos):
    estaciones = {}
    errores = []
    for f in archivos:
        try:
            df = leer_csv_estacion(f.name, f.getvalue())
            if df.empty:
                errores.append(f"{f.name}: sin datos válidos.")
                continue

            clave = str(df["Clave"].dropna().iloc[0]) if df["Clave"].notna().any() else f.name
            estaciones[clave] = df
        except Exception as exc:
            errores.append(str(exc))
    return estaciones, errores


def haversine_km(lat1, lon1, lat2, lon2):
    r = 6371.0088
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


def resumen_estaciones(estaciones, variable, fecha_ini=None, fecha_fin=None):
    filas = []
    for clave, df in estaciones.items():
        if variable not in df.columns:
            continue

        x = df[["Fecha", variable, "Latitud", "Longitud"]].copy()
        if fecha_ini is not None:
            x = x[x["Fecha"] >= pd.Timestamp(fecha_ini)]
        if fecha_fin is not None:
            x = x[x["Fecha"] <= pd.Timestamp(fecha_fin)]
        x = x.dropna(subset=[variable, "Latitud", "Longitud"])
        if x.empty:
            continue

        filas.append(
            {
                "Clave": clave,
                "Latitud": float(x["Latitud"].median()),
                "Longitud": float(x["Longitud"].median()),
                "Valor": float(x[variable].mean()),
                "N": int(x[variable].notna().sum()),
            }
        )
    return pd.DataFrame(filas)


# ---------- Interpolación ----------

def pred_idw(coords, valores, target, power=2.0):
    coords = np.asarray(coords, dtype=float)
    valores = np.asarray(valores, dtype=float)
    target = np.asarray(target, dtype=float)

    d = np.sqrt(((coords - target) ** 2).sum(axis=1))
    if np.any(d < 1e-12):
        return float(valores[np.argmin(d)])

    w = 1.0 / np.power(d, power)
    return float(np.sum(w * valores) / np.sum(w))


def pred_nearest(coords, valores, target):
    coords = np.asarray(coords, dtype=float)
    valores = np.asarray(valores, dtype=float)
    target = np.asarray(target, dtype=float)
    d = np.sqrt(((coords - target) ** 2).sum(axis=1))
    return float(valores[np.argmin(d)])


def pred_linear(coords, valores, target):
    if len(valores) < 3:
        return np.nan
    try:
        pred = griddata(
            np.asarray(coords, dtype=float),
            np.asarray(valores, dtype=float),
            np.asarray([target], dtype=float),
            method="linear",
        )[0]
        return float(pred) if np.isfinite(pred) else np.nan
    except Exception:
        return np.nan


def predecir_metodo(metodo, coords, valores, target):
    if metodo == "IDW":
        return pred_idw(coords, valores, target, power=2.0)
    if metodo == "KNN / vecino más cercano":
        return pred_nearest(coords, valores, target)
    if metodo == "Lineal":
        return pred_linear(coords, valores, target)
    return np.nan


def rmse_leave_one_out(resumen):
    metodos = ["IDW", "KNN / vecino más cercano", "Lineal"]
    resultados = []

    if resumen.empty or len(resumen) < 3:
        return pd.DataFrame(columns=["Método", "RMSE", "Validaciones"])

    coords_all = resumen[["Latitud", "Longitud"]].to_numpy(dtype=float)
    vals_all = resumen["Valor"].to_numpy(dtype=float)

    for metodo in metodos:
        errores = []
        for i in range(len(resumen)):
            mask = np.arange(len(resumen)) != i
            coords = coords_all[mask]
            vals = vals_all[mask]
            target = coords_all[i]
            real = vals_all[i]

            pred = predecir_metodo(metodo, coords, vals, target)
            if np.isfinite(pred):
                errores.append((pred - real) ** 2)

        rmse = math.sqrt(float(np.mean(errores))) if errores else np.inf
        resultados.append(
            {"Método": metodo, "RMSE": rmse, "Validaciones": len(errores)}
        )

    out = pd.DataFrame(resultados)
    out["RMSE"] = pd.to_numeric(out["RMSE"], errors="coerce")
    return out.sort_values("RMSE", na_position="last").reset_index(drop=True)


def serie_interpolada_diaria(estaciones, variable, lat, lon, metodo, fecha_ini, fecha_fin):
    series = []
    coords = {}

    for clave, df in estaciones.items():
        if variable not in df.columns:
            continue

        x = df[["Fecha", variable, "Latitud", "Longitud"]].copy()
        x = x[(x["Fecha"] >= pd.Timestamp(fecha_ini)) & (x["Fecha"] <= pd.Timestamp(fecha_fin))]
        x = x.dropna(subset=[variable, "Latitud", "Longitud"])
        if x.empty:
            continue

        coords[clave] = (
            float(x["Latitud"].median()),
            float(x["Longitud"].median()),
        )
        s = x.groupby("Fecha", as_index=True)[variable].mean().rename(clave)
        series.append(s)

    if not series:
        return pd.DataFrame(columns=["ds", "y"])

    matriz = pd.concat(series, axis=1).sort_index()
    target = (float(lat), float(lon))
    min_est = 3 if metodo == "Lineal" else 2

    fechas = []
    valores = []

    for fecha, row in matriz.iterrows():
        disponibles = row.dropna()
        if len(disponibles) < min_est:
            continue

        claves = [c for c in disponibles.index if c in coords]
        if len(claves) < min_est:
            continue

        cxy = np.array([coords[c] for c in claves], dtype=float)
        vals = np.array([float(disponibles[c]) for c in claves], dtype=float)

        pred = predecir_metodo(metodo, cxy, vals, target)
        if np.isfinite(pred):
            fechas.append(fecha)
            valores.append(pred)

    out = pd.DataFrame({"ds": fechas, "y": valores}).dropna()
    if variable in NONNEGATIVE and not out.empty:
        out["y"] = out["y"].clip(lower=0)
    return out


def serie_estacion_directa(df, variable, fecha_ini, fecha_fin):
    x = df[["Fecha", variable]].copy()
    x = x[(x["Fecha"] >= pd.Timestamp(fecha_ini)) & (x["Fecha"] <= pd.Timestamp(fecha_fin))]
    x = x.dropna(subset=[variable])
    x = x.groupby("Fecha", as_index=False)[variable].mean()
    x.columns = ["ds", "y"]
    if variable in NONNEGATIVE:
        x["y"] = x["y"].clip(lower=0)
    return x


def localizar_estacion(estaciones, lat, lon, tolerancia_km=1.0):
    candidatos = []
    for clave, df in estaciones.items():
        if df.empty:
            continue
        slat = float(df["Latitud"].median())
        slon = float(df["Longitud"].median())
        d = haversine_km(lat, lon, slat, slon)
        candidatos.append((d, clave, slat, slon))

    if not candidatos:
        return None, None

    candidatos.sort(key=lambda x: x[0])
    cercano = candidatos[0]
    return (cercano if cercano[0] <= tolerancia_km else None), cercano


# ---------- Prophet / resumen ----------

def preparar_fechas_prediccion(serie, fecha_inicio, fecha_fin):
    fecha_inicio = pd.Timestamp(fecha_inicio)
    fecha_fin = pd.Timestamp(fecha_fin)

    inicio_graf = max(serie["ds"].max() - pd.DateOffset(years=2), serie["ds"].min())

    fechas_hist = pd.date_range(
        inicio_graf,
        serie["ds"].max(),
        periods=min(120, max(20, len(serie)))
    )

    futuros = pd.date_range(fecha_inicio, fecha_fin, freq="D")

    fechas_pred = pd.DatetimeIndex(
        sorted(set(fechas_hist.tolist() + futuros.tolist()))
    )
    return fechas_pred


def resumen_periodo(pred, variable):
    pred = pred.copy()
    if pred.empty:
        return {}

    if variable in NONNEGATIVE:
        return {
            "Acumulado estimado": float(pred["yhat"].sum()),
            "Promedio diario": float(pred["yhat"].mean()),
            "Máximo diario": float(pred["yhat"].max()),
            "Día de máximo": pred.loc[pred["yhat"].idxmax(), "ds"],
        }

    return {
        "Promedio estimado": float(pred["yhat"].mean()),
        "Mínimo estimado": float(pred["yhat"].min()),
        "Máximo estimado": float(pred["yhat"].max()),
        "Día de máximo": pred.loc[pred["yhat"].idxmax(), "ds"],
    }


def grafica_prophet(hist, forecast, variable, inicio_periodo, fin_periodo):
    fig = go.Figure()

    h = hist.copy()
    if len(h) > 1800:
        paso = int(np.ceil(len(h) / 1800))
        h = h.iloc[::paso]

    fig.add_trace(
        go.Scatter(
            x=h["ds"], y=h["y"],
            mode="lines",
            name="Serie histórica / interpolada",
            line=dict(width=1.4),
        )
    )

    fig.add_trace(
        go.Scatter(
            x=forecast["ds"], y=forecast["yhat_upper"],
            mode="lines",
            line=dict(width=0),
            showlegend=False,
            hoverinfo="skip",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=forecast["ds"], y=forecast["yhat_lower"],
            mode="lines",
            fill="tonexty",
            line=dict(width=0),
            name="Intervalo predictivo",
            hoverinfo="skip",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=forecast["ds"], y=forecast["yhat"],
            mode="lines",
            name="Prophet",
            line=dict(width=2.4),
        )
    )

    fig.add_vrect(
        x0=pd.Timestamp(inicio_periodo),
        x1=pd.Timestamp(fin_periodo),
        opacity=0.12,
        line_width=0,
        annotation_text="Periodo consultado",
        annotation_position="top left",
    )

    fig.update_layout(
        height=470,
        margin=dict(l=20, r=20, t=45, b=20),
        title=f"Predicción temporal · {variable}",
        xaxis_title="Fecha",
        yaxis_title=variable,
        hovermode="x unified",
        legend=dict(orientation="h", y=1.08),
    )
    return fig


# ---------- Navegación ----------

st.sidebar.markdown("## 🌦️ ClimaPredictor")
st.sidebar.caption("Interpolación espacial + predicción temporal")
seccion = st.sidebar.radio(
    "Navegación",
    ["Inicio", "Predicción espacio-temporal"],
)

if seccion == "Inicio":
    st.markdown("""
    <style>
    .hero {
        padding: 2rem 2.2rem;
        border-radius: 22px;
        background: linear-gradient(135deg,#eef7ff 0%,#f7fbf5 58%,#fff8ec 100%);
        border:1px solid #dce8ef;
        margin-bottom:1.15rem;
    }
    .hero h1 {margin:.2rem 0 .55rem 0;color:#12345b;font-size:2.5rem;line-height:1.08;}
    .hero p {font-size:1.08rem;color:#3d5266;max-width:1050px;}
    .pill {display:inline-block;padding:.32rem .7rem;border-radius:999px;background:white;border:1px solid #d7e4ea;margin-right:.3rem;color:#24445f;font-weight:650;}
    .card {padding:1.1rem 1.2rem;border-radius:18px;border:1px solid #e1e8ed;background:#fff;min-height:170px;}
    .card h3 {margin-top:0;color:#173d67;}
    .flow {padding:1.05rem;border-radius:16px;background:#f7f9fb;border:1px solid #e5eaee;text-align:center;font-weight:650;color:#274861;}
    </style>

    <div class="hero">
      <span class="pill">Python + Streamlit</span>
      <span class="pill">Interpolación</span>
      <span class="pill">Prophet</span>
      <h1>ClimaPredictor Colima</h1>
      <p>
      Una propuesta para aprovechar registros históricos de estaciones meteorológicas y convertirlos
      en información útil tanto en el espacio como en el tiempo. La interpolación permite estimar
      condiciones donde no existe medición directa; Prophet permite proyectar la serie obtenida hacia
      una fecha futura o un intervalo completo.
      </p>
    </div>
    """, unsafe_allow_html=True)

    a, b, c = st.columns(3)
    with a:
        st.markdown("""<div class="card"><h3>📍 ¿Dónde?</h3><p>Si la coordenada coincide con una estación, usamos directamente su serie histórica. Si no coincide, estimamos el valor espacial mediante interpolación.</p></div>""", unsafe_allow_html=True)
    with b:
        st.markdown("""<div class="card"><h3>🏆 ¿Qué interpolación?</h3><p>Comparamos IDW, vecino más cercano y lineal mediante validación cruzada. La aplicación selecciona automáticamente el método con menor RMSE.</p></div>""", unsafe_allow_html=True)
    with c:
        st.markdown("""<div class="card"><h3>🔮 ¿Cuándo?</h3><p>La serie histórica —medida o interpolada— alimenta Prophet para estimar una fecha concreta o un periodo como verano, temporada de lluvias o varios meses.</p></div>""", unsafe_allow_html=True)

    st.markdown("### Flujo de la propuesta")
    st.markdown("""
    <div class="flow">
    Coordenadas → ¿existe estación? → serie observada / mejor interpolación → serie temporal → Prophet → fecha o intervalo futuro
    </div>
    """, unsafe_allow_html=True)

    st.info("**Idea central:** la interpolación responde *¿dónde?* y Prophet responde *¿cuándo?*; juntos permiten una estimación espacio-temporal.")
    st.caption("Herramienta exploratoria de apoyo a la toma de decisiones. No sustituye un pronóstico meteorológico oficial.")

else:
    st.title("🔮 Predicción espacio-temporal")
    st.write(
        "Carga los CSV de estaciones meteorológicas, indica una coordenada y define una fecha o intervalo futuro. "
        "La aplicación decide si puede usar una estación directamente o si debe construir primero "
        "una serie histórica interpolada."
    )

    archivos = st.file_uploader(
        "CSV de estaciones meteorológicas",
        type=["csv"],
        accept_multiple_files=True,
        help="Se esperan columnas Fecha, Latitud, Longitud y las variables meteorológicas.",
    )

    if not archivos:
        st.info("Carga al menos un CSV. Para comparar interpolaciones se recomiendan 4 o más estaciones.")
        st.stop()

    estaciones, errores = cargar_estaciones(archivos)
    if errores:
        with st.expander("Archivos con observaciones"):
            for e in errores:
                st.warning(e)

    if not estaciones:
        st.error("No fue posible leer estaciones válidas.")
        st.stop()

    st.success(f"{len(estaciones)} estación(es) válida(s) cargada(s).")

    disponibles = [
        v for v in VARIABLES
        if any(v in df.columns and df[v].notna().any() for df in estaciones.values())
    ]
    if not disponibles:
        st.error("Los CSV no contienen variables meteorológicas reconocidas.")
        st.stop()

    c1, c2, c3 = st.columns(3)
    with c1:
        variable = st.selectbox("Variable", disponibles)
    with c2:
        lat = st.number_input("Latitud", value=19.2433, format="%.6f")
    with c3:
        lon = st.number_input("Longitud", value=-103.7247, format="%.6f")

    fechas_max = [df["Fecha"].max() for df in estaciones.values() if not df.empty]
    max_hist = max(fechas_max)
    min_future = (max_hist + pd.Timedelta(days=1)).date()

    modo = st.radio(
        "Tipo de consulta",
        ["Fecha específica", "Intervalo"],
        horizontal=True,
    )

    if modo == "Fecha específica":
        c4, c5, c6 = st.columns(3)
        with c4:
            fecha_inicio = st.date_input(
                "Fecha futura",
                value=max(min_future, date.today()),
                min_value=min_future,
            )
        fecha_fin = fecha_inicio
        with c5:
            anios_hist = st.slider("Años históricos para entrenar", 3, 20, 10)
        with c6:
            tolerancia = st.slider(
                "Coincidencia con estación (km)",
                min_value=0.1,
                max_value=5.0,
                value=1.0,
                step=0.1,
            )
    else:
        c4, c5, c6, c7 = st.columns(4)
        with c4:
            fecha_inicio = st.date_input(
                "Inicio del periodo",
                value=max(min_future, date.today()),
                min_value=min_future,
            )
        with c5:
            fecha_fin = st.date_input(
                "Fin del periodo",
                value=max(min_future, date.today()) + pd.Timedelta(days=60),
                min_value=min_future,
            )
        with c6:
            anios_hist = st.slider("Años históricos para entrenar", 3, 20, 10)
        with c7:
            tolerancia = st.slider(
                "Coincidencia con estación (km)",
                min_value=0.1,
                max_value=5.0,
                value=1.0,
                step=0.1,
            )

        if pd.Timestamp(fecha_fin) < pd.Timestamp(fecha_inicio):
            st.error("La fecha final debe ser posterior o igual a la fecha inicial.")
            st.stop()

    if st.button("🚀 Estimar clima", type="primary", use_container_width=True):
        fecha_fin_hist = max_hist
        fecha_ini_hist = fecha_fin_hist - pd.DateOffset(years=anios_hist)

        directa, cercana = localizar_estacion(estaciones, lat, lon, tolerancia)

        if directa is not None:
            distancia, clave, slat, slon = directa
            serie = serie_estacion_directa(
                estaciones[clave], variable, fecha_ini_hist, fecha_fin_hist
            )
            origen = f"Estación directa: {clave}"
            st.success(
                f"📍 La coordenada coincide con **{clave}** "
                f"(distancia aproximada: {distancia:.2f} km). "
                "Prophet utilizará la serie observada."
            )
        else:
            if len(estaciones) < 3:
                st.error("Para interpolar se necesitan al menos 3 estaciones válidas.")
                st.stop()

            resumen = resumen_estaciones(
                estaciones, variable, fecha_ini_hist, fecha_fin_hist
            )
            if len(resumen) < 3:
                st.error("No hay suficientes estaciones con datos de la variable y periodo seleccionados.")
                st.stop()

            rmse_tabla = rmse_leave_one_out(resumen)
            validos = rmse_tabla[np.isfinite(rmse_tabla["RMSE"])]
            if validos.empty:
                st.error("No fue posible validar ningún método de interpolación.")
                st.stop()

            mejor_metodo = validos.iloc[0]["Método"]
            mejor_rmse = float(validos.iloc[0]["RMSE"])

            if cercana is not None:
                d0, c0, _, _ = cercana
                st.info(
                    f"La estación más cercana es **{c0}**, a {d0:.2f} km; "
                    f"supera la tolerancia de {tolerancia:.1f} km, por lo que se interpolará."
                )

            st.markdown("#### 🏆 Selección automática de interpolación")
            mostrar = rmse_tabla.copy()
            mostrar["RMSE"] = mostrar["RMSE"].replace([np.inf, -np.inf], np.nan).round(4)
            st.dataframe(mostrar, use_container_width=True, hide_index=True)
            st.success(f"Mejor método: **{mejor_metodo}** · RMSE = **{mejor_rmse:.4f}**")

            with st.spinner("Construyendo serie histórica para la coordenada..."):
                serie = serie_interpolada_diaria(
                    estaciones,
                    variable,
                    lat,
                    lon,
                    mejor_metodo,
                    fecha_ini_hist,
                    fecha_fin_hist,
                )
            origen = f"Serie interpolada con {mejor_metodo}"

        if len(serie) < 60:
            st.error(
                f"La serie resultante contiene solo {len(serie)} observaciones. "
                "Se recomiendan al menos 60 para entrenar Prophet."
            )
            st.stop()

        try:
            from prophet import Prophet
        except Exception as exc:
            st.error(
                "Prophet no está disponible en el entorno. Verifica requirements.txt. "
                f"Detalle: {exc}"
            )
            st.stop()

        serie = serie.sort_values("ds").drop_duplicates(subset=["ds"])
        if variable in NONNEGATIVE:
            serie["y"] = serie["y"].clip(lower=0)

        with st.spinner("Don Profeta está trabajando… 🔮"):
            modelo = Prophet(
                interval_width=0.80,
                daily_seasonality=False,
                weekly_seasonality=True,
                yearly_seasonality=True,
            )
            modelo.fit(serie[["ds", "y"]])

            fechas_pred = preparar_fechas_prediccion(
                serie, fecha_inicio, fecha_fin
            )
            forecast = modelo.predict(pd.DataFrame({"ds": fechas_pred}))

        if variable in NONNEGATIVE:
            for col in ["yhat", "yhat_lower", "yhat_upper"]:
                forecast[col] = forecast[col].clip(lower=0)

        periodo = forecast[
            (forecast["ds"] >= pd.Timestamp(fecha_inicio))
            & (forecast["ds"] <= pd.Timestamp(fecha_fin))
        ].copy()

        st.markdown("---")
        st.markdown("### Resultado")

        if modo == "Fecha específica":
            pred_obj = periodo.iloc[0]
            yhat = float(pred_obj["yhat"])
            low = float(pred_obj["yhat_lower"])
            high = float(pred_obj["yhat_upper"])

            m1, m2, m3 = st.columns(3)
            m1.metric("Estimación", f"{yhat:.2f}")
            m2.metric("Intervalo inferior (80%)", f"{low:.2f}")
            m3.metric("Intervalo superior (80%)", f"{high:.2f}")
        else:
            resumen_pred = resumen_periodo(periodo, variable)

            if variable in NONNEGATIVE:
                m1, m2, m3, m4 = st.columns(4)
                m1.metric("Acumulado estimado", f"{resumen_pred['Acumulado estimado']:.2f}")
                m2.metric("Promedio diario", f"{resumen_pred['Promedio diario']:.2f}")
                m3.metric("Máximo diario", f"{resumen_pred['Máximo diario']:.2f}")
                m4.metric(
                    "Día de máximo",
                    pd.Timestamp(resumen_pred["Día de máximo"]).strftime("%d/%m/%Y")
                )
            else:
                m1, m2, m3, m4 = st.columns(4)
                m1.metric("Promedio estimado", f"{resumen_pred['Promedio estimado']:.2f}")
                m2.metric("Mínimo estimado", f"{resumen_pred['Mínimo estimado']:.2f}")
                m3.metric("Máximo estimado", f"{resumen_pred['Máximo estimado']:.2f}")
                m4.metric(
                    "Día de máximo",
                    pd.Timestamp(resumen_pred["Día de máximo"]).strftime("%d/%m/%Y")
                )

            st.dataframe(
                periodo[["ds", "yhat", "yhat_lower", "yhat_upper"]].rename(
                    columns={
                        "ds": "Fecha",
                        "yhat": "Estimación",
                        "yhat_lower": "Límite inferior 80%",
                        "yhat_upper": "Límite superior 80%",
                    }
                ),
                use_container_width=True,
                hide_index=True,
            )

        st.caption(
            f"{origen} · Coordenada ({lat:.5f}, {lon:.5f}) · "
            f"Periodo: {pd.Timestamp(fecha_inicio).strftime('%d/%m/%Y')} "
            f"→ {pd.Timestamp(fecha_fin).strftime('%d/%m/%Y')} · "
            f"{len(serie):,} observaciones para Prophet."
        )

        st.plotly_chart(
            grafica_prophet(serie, forecast, variable, fecha_inicio, fecha_fin),
            use_container_width=True,
        )

        csv_resultado = periodo[["ds", "yhat", "yhat_lower", "yhat_upper"]].copy()
        csv_resultado.columns = ["Fecha", "Estimacion", "Limite_inferior_80", "Limite_superior_80"]
        st.download_button(
            "⬇️ Descargar predicción del periodo",
            data=csv_resultado.to_csv(index=False).encode("utf-8"),
            file_name="prediccion_espaciotemporal.csv",
            mime="text/csv",
            use_container_width=True,
        )

        with st.expander("¿Qué hizo la aplicación?"):
            if directa is not None:
                st.write(
                    "1. Detectó una estación dentro de la tolerancia establecida. "
                    "2. Construyó la serie diaria observada de esa estación. "
                    "3. Entrenó Prophet. "
                    "4. Estimó la variable para la fecha o intervalo futuro seleccionado."
                )
            else:
                st.write(
                    "1. Confirmó que la coordenada no coincide con una estación. "
                    "2. Comparó IDW, vecino más cercano y lineal mediante validación cruzada leave-one-out. "
                    "3. Seleccionó el método con menor RMSE. "
                    "4. Interpoló cada fecha histórica disponible en la coordenada solicitada para crear una serie temporal sintética. "
                    "5. Entrenó Prophet con esa serie y estimó la variable para la fecha o intervalo futuro."
                )

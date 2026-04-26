import requests
import pandas as pd


def obtener_datos_salarios():
    url = "https://apis.datos.gob.ar/series/api/series/"

    # 1. Definimos los IDs (El histórico y el nuevo/alternativo)
    # Nota: 116.4_TCRPB_0_M_36 es otra variante del RIPTE oficial que suele estar más actualizada
    id_viejo = "158.1_REPTE_0_0_5"
    id_nuevo = "116.4_TCRPB_0_M_36"

    print("⏳ Descargando series de Salarios (RIPTE histórico y actual)...")

    # 2. Función interna para descargar un ID específico
    def descargar_serie(id_serie):
        parametros = {"ids": id_serie, "limit": 5000, "format": "json"}
        respuesta = requests.get(url, params=parametros)
        if respuesta.status_code == 200:
            datos = respuesta.json()['data']
            # Lo convertimos a DataFrame inmediatamente
            return pd.DataFrame(datos, columns=['fecha', 'valor'])
        return pd.DataFrame()  # Devuelve vacío si falla

    # 3. Descargamos ambas tablas
    df_viejo = descargar_serie(id_viejo)
    df_nuevo = descargar_serie(id_nuevo)

    # Si ambas están vacías, abortamos
    if df_viejo.empty and df_nuevo.empty:
        return None

    # ==========================================
    # EL TRUCO SENIOR: EMPALME SEGURO
    # ==========================================
    # Solo procesamos la fecha si el DataFrame NO está vacío
    if not df_viejo.empty:
        df_viejo['fecha'] = pd.to_datetime(df_viejo['fecha'])
        df_viejo.set_index('fecha', inplace=True)

    if not df_nuevo.empty:
        df_nuevo['fecha'] = pd.to_datetime(df_nuevo['fecha'])
        df_nuevo.set_index('fecha', inplace=True)

    # Hacemos el empalme dependiendo de qué datos sobrevivieron
    if not df_nuevo.empty and not df_viejo.empty:
        df_empalmado = df_nuevo.combine_first(df_viejo)
    elif not df_nuevo.empty:
        df_empalmado = df_nuevo
    else:
        df_empalmado = df_viejo

    df_empalmado = df_empalmado.reset_index().dropna()
    df_empalmado['fecha'] = df_empalmado['fecha'].dt.strftime('%Y-%m-%d')

    return df_empalmado.to_dict('records')

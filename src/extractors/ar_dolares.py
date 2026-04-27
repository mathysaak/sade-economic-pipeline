import requests
import pandas as pd
import os


def obtener_datos_dolar_mep():
    url = "https://api.argentinadatos.com/v1/cotizaciones/dolares"
    print("⏳ Descargando base histórica de dólares (Híbrido: API + Parche Local)...")

    # 1. Obtenemos datos de la API
    respuesta = requests.get(url)
    df_api = pd.DataFrame()
    if respuesta.status_code == 200:
        df_api = pd.DataFrame(respuesta.json())
        df_api['fecha'] = pd.to_datetime(df_api['fecha'])

    # 2. Obtenemos el parche histórico local (El que acabamos de crear)
    ruta_parche = "data/parche_blue_2011_2015.csv"
    df_parche = pd.DataFrame()
    if os.path.exists(ruta_parche):
        df_parche = pd.read_csv(ruta_parche)
        df_parche['fecha'] = pd.to_datetime(df_parche['fecha'])

    # 3. Unimos la API con nuestro parche
    if not df_api.empty and not df_parche.empty:
        # ignore_index es clave para que no se pisen los IDs de las filas
        df = pd.concat([df_api, df_parche], ignore_index=True)
    elif not df_api.empty:
        df = df_api
    else:
        return None

    # 4. Agrupamos por Año-Mes y Casa
    df['anio_mes'] = df['fecha'].dt.to_period('M')

    # Promediamos CADA MERCADO por mes ANTES de cruzarlos
    df_mensual = df.groupby(['anio_mes', 'casa'])['venta'].mean().unstack()

    # Nos aseguramos de que las columnas existan por si la API falla
    for mercado in ['bolsa', 'blue', 'oficial']:
        if mercado not in df_mensual.columns:
            df_mensual[mercado] = None

    # 5. LA CASCADA: Si en todo el mes hay MEP, lo usamos. Si no, Blue. Si no, Oficial.
    df_mensual['valor_final'] = df_mensual['bolsa'].fillna(
        df_mensual['blue']).fillna(df_mensual['oficial'])

    # 6. Formateamos para que el motor ETL de SADE lo reciba perfectamente
    df_final = df_mensual[['valor_final']].dropna().reset_index()
    # Le pone día 01 a todos
    df_final['fecha'] = df_final['anio_mes'].dt.to_timestamp()
    df_final['fecha'] = df_final['fecha'].dt.strftime('%Y-%m-%d')
    df_final = df_final.rename(columns={'valor_final': 'valor'})

    return df_final.to_dict('records')

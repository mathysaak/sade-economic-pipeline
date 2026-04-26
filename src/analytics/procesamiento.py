import pandas as pd


def procesar_comparacion_mandatos(datos_api, df_presidentes, lista_presidentes_elegidos):
    # FASE 1: CREAR LA TABLA GIGANTE
    df_infla = pd.DataFrame(datos_api)
    df_infla['fecha'] = pd.to_datetime(df_infla['fecha'])
    df_presidentes['fecha_inicio'] = pd.to_datetime(
        df_presidentes['fecha_inicio'])
    df_presidentes['fecha_fin'] = pd.to_datetime(df_presidentes['fecha_fin'])

    df_infla['presidente'] = None

    for index, fila in df_presidentes.iterrows():
        mascara = (df_infla['fecha'] >= fila['fecha_inicio']) & (
            df_infla['fecha'] <= fila['fecha_fin'])
        df_infla.loc[mascara, 'presidente'] = fila['presidente']

    df_infla = df_infla.dropna(subset=['presidente'])

    # FASE 2: LA LÓGICA DE "LA CARRERA" (Tijera Multi-Presidente)
    # Le pasamos la lista completa. Si son 2, filtra 2. Si son 5, filtra 5.
    df_filtrado = df_infla[df_infla['presidente'].isin(
        lista_presidentes_elegidos)].copy()

    df_filtrado = df_filtrado.sort_values(by='fecha')
    df_filtrado['mes_de_mandato'] = df_filtrado.groupby(
        'presidente').cumcount() + 1

    # Esto sigue funcionando perfecto: busca el máximo de CADA presidente, y luego corta por el menor de todos.
    limite_meses = df_filtrado.groupby(
        'presidente')['mes_de_mandato'].max().min()

    df_final = df_filtrado[df_filtrado['mes_de_mandato'] <= limite_meses]
    df_final = df_final[['mes_de_mandato', 'fecha', 'presidente', 'valor']]

    return df_final

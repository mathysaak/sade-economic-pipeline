import pandas as pd


def procesar_reservas_bcra(datos_api, df_presidentes, lista_presidentes_elegidos):
    df_reservas = pd.DataFrame(datos_api)
    df_reservas['fecha'] = pd.to_datetime(df_reservas['fecha'])

    df_reservas['anio_mes'] = df_reservas['fecha'].dt.to_period('M')
    df_reservas_mensual = df_reservas.groupby('anio_mes').last().reset_index()
    df_reservas_mensual['fecha'] = df_reservas_mensual['anio_mes'].dt.to_timestamp(
    )

    df_presidentes['fecha_inicio'] = pd.to_datetime(
        df_presidentes['fecha_inicio'])
    df_presidentes['fecha_fin'] = pd.to_datetime(df_presidentes['fecha_fin'])
    df_reservas_mensual['presidente'] = None

    for index, fila in df_presidentes.iterrows():
        mascara = (df_reservas_mensual['fecha'] >= fila['fecha_inicio']) & (
            df_reservas_mensual['fecha'] <= fila['fecha_fin'])
        df_reservas_mensual.loc[mascara, 'presidente'] = fila['presidente']

    df_reservas_mensual = df_reservas_mensual.dropna(subset=['presidente'])

    df_filtrado = df_reservas_mensual[df_reservas_mensual['presidente'].isin(
        lista_presidentes_elegidos)].copy()
    df_filtrado = df_filtrado.sort_values(by=['presidente', 'fecha'])

    df_filtrado['mes_de_mandato'] = df_filtrado.groupby(
        'presidente').cumcount() + 1
    df_filtrado['reserva_mes_1'] = df_filtrado.groupby(
        'presidente')['valor'].transform('first')
    df_filtrado['variacion_millones_usd'] = df_filtrado['valor'] - \
        df_filtrado['reserva_mes_1']

    df_final = df_filtrado.rename(columns={'valor': 'reserva_total_bruta'})

    return df_final[['mes_de_mandato', 'fecha', 'presidente', 'reserva_total_bruta', 'variacion_millones_usd']]


def procesar_salario_dolar(datos_salarios, datos_dolar, df_presidentes, lista_presis):
    df_s = pd.DataFrame(datos_salarios).rename(
        columns={'valor': 'sueldo_pesos'})
    df_d = pd.DataFrame(datos_dolar).rename(columns={'valor': 'precio_dolar'})

    df_s['fecha'] = pd.to_datetime(df_s['fecha'])
    df_d['fecha'] = pd.to_datetime(df_d['fecha'])

    df_s['anio_mes'] = df_s['fecha'].dt.to_period('M')
    df_d['anio_mes'] = df_d['fecha'].dt.to_period('M')

    df_d_mensual = df_d.groupby(
        'anio_mes')['precio_dolar'].mean().reset_index()

    df_cruce = pd.merge(df_s, df_d_mensual, on='anio_mes')
    df_cruce['salario_usd'] = (
        df_cruce['sueldo_pesos'] / df_cruce['precio_dolar']).round(2)

    df_cruce['presidente'] = None
    for _, fila in df_presidentes.iterrows():
        mascara = (df_cruce['fecha'] >= fila['fecha_inicio']) & (
            df_cruce['fecha'] <= fila['fecha_fin'])
        df_cruce.loc[mascara, 'presidente'] = fila['presidente']

    df_cruce = df_cruce.dropna(subset=['presidente'])
    df_filtrado = df_cruce[df_cruce['presidente'].isin(lista_presis)].copy()

    df_filtrado = df_filtrado.sort_values(by=['presidente', 'fecha'])
    df_filtrado['mes_de_mandato'] = df_filtrado.groupby(
        'presidente').cumcount() + 1

    return df_filtrado[['mes_de_mandato', 'fecha', 'presidente', 'sueldo_pesos', 'precio_dolar', 'salario_usd']]


def procesar_dolar_constante(datos_inflacion, datos_dolar, df_presidentes, lista_presis):
    df_i = pd.DataFrame(datos_inflacion).rename(
        columns={'valor': 'inflacion_mensual'})
    df_d = pd.DataFrame(datos_dolar).rename(columns={'valor': 'precio_dolar'})

    df_i['fecha'] = pd.to_datetime(df_i['fecha'])
    df_d['fecha'] = pd.to_datetime(df_d['fecha'])

    df_i['anio_mes'] = df_i['fecha'].dt.to_period('M')
    df_d['anio_mes'] = df_d['fecha'].dt.to_period('M')

    df_d_mensual = df_d.groupby(
        'anio_mes')['precio_dolar'].mean().reset_index()
    df_i_mensual = df_i.groupby(
        'anio_mes')['inflacion_mensual'].last().reset_index()

    df_cruce = pd.merge(df_i_mensual, df_d_mensual, on='anio_mes')
    df_cruce['fecha'] = df_cruce['anio_mes'].dt.to_timestamp()
    df_cruce = df_cruce.sort_values('fecha')

    df_cruce['infla_factor'] = 1 + (df_cruce['inflacion_mensual'] / 100)
    df_cruce['indice_inflacion'] = df_cruce['infla_factor'].cumprod()

    indice_hoy = df_cruce['indice_inflacion'].iloc[-1]

    df_cruce['dolar_a_precios_de_hoy'] = df_cruce['precio_dolar'] * \
        (indice_hoy / df_cruce['indice_inflacion'])
    df_cruce['dolar_a_precios_de_hoy'] = df_cruce['dolar_a_precios_de_hoy'].round(
        2)

    df_cruce['presidente'] = None
    for _, fila in df_presidentes.iterrows():
        mascara = (df_cruce['fecha'] >= fila['fecha_inicio']) & (
            df_cruce['fecha'] <= fila['fecha_fin'])
        df_cruce.loc[mascara, 'presidente'] = fila['presidente']

    df_cruce = df_cruce.dropna(subset=['presidente'])
    df_filtrado = df_cruce[df_cruce['presidente'].isin(lista_presis)].copy()

    df_filtrado = df_filtrado.sort_values(by=['presidente', 'fecha'])
    df_filtrado['mes_de_mandato'] = df_filtrado.groupby(
        'presidente').cumcount() + 1

    return df_filtrado[['mes_de_mandato', 'fecha', 'presidente', 'precio_dolar', 'inflacion_mensual', 'dolar_a_precios_de_hoy']]


def procesar_carrera_ahorros(datos_inflacion, datos_dolar, datos_tasas, df_presidentes, lista_presis):
    df_i = pd.DataFrame(datos_inflacion).rename(
        columns={'valor': 'inflacion_mensual'})
    df_d = pd.DataFrame(datos_dolar).rename(columns={'valor': 'precio_dolar'})
    df_t = pd.DataFrame(datos_tasas).rename(columns={'valor': 'tasa_tna'})

    for df in [df_i, df_d, df_t]:
        df['fecha'] = pd.to_datetime(df['fecha'])
        df['anio_mes'] = df['fecha'].dt.to_period('M')

    df_d_m = df_d.groupby('anio_mes')['precio_dolar'].mean().reset_index()
    df_t_m = df_t.groupby('anio_mes')['tasa_tna'].mean().reset_index()
    df_i_m = df_i.groupby('anio_mes')['inflacion_mensual'].last().reset_index()

    df_temp = pd.merge(df_i_m, df_d_m, on='anio_mes')
    df_cruce = pd.merge(df_temp, df_t_m, on='anio_mes')
    df_cruce['fecha'] = df_cruce['anio_mes'].dt.to_timestamp()

    df_cruce['presidente'] = None
    for _, fila in df_presidentes.iterrows():
        mascara = (df_cruce['fecha'] >= fila['fecha_inicio']) & (
            df_cruce['fecha'] <= fila['fecha_fin'])
        df_cruce.loc[mascara, 'presidente'] = fila['presidente']

    df_cruce = df_cruce.dropna(subset=['presidente'])
    df_filtrado = df_cruce[df_cruce['presidente'].isin(lista_presis)].copy()
    df_filtrado = df_filtrado.sort_values(by=['presidente', 'fecha'])
    df_filtrado['mes_de_mandato'] = df_filtrado.groupby(
        'presidente').cumcount() + 1

    CAPITAL_INICIAL = 100000

    df_filtrado['infla_factor'] = 1 + (df_filtrado['inflacion_mensual'] / 100)
    df_filtrado['costo_vida_ars'] = CAPITAL_INICIAL * \
        df_filtrado.groupby('presidente')['infla_factor'].cumprod()

    df_filtrado['tasa_efectiva_mensual'] = df_filtrado['tasa_tna'] / 12 / 100
    df_filtrado['pf_factor'] = 1 + df_filtrado['tasa_efectiva_mensual']
    df_filtrado['ahorro_pf_ars'] = CAPITAL_INICIAL * \
        df_filtrado.groupby('presidente')['pf_factor'].cumprod()

    df_filtrado['dolar_mes_1'] = df_filtrado.groupby(
        'presidente')['precio_dolar'].transform('first')
    df_filtrado['usd_comprados_mes_1'] = CAPITAL_INICIAL / \
        df_filtrado['dolar_mes_1']
    df_filtrado['ahorro_dolar_ars'] = df_filtrado['usd_comprados_mes_1'] * \
        df_filtrado['precio_dolar']

    for col in ['costo_vida_ars', 'ahorro_pf_ars', 'ahorro_dolar_ars']:
        df_filtrado[col] = df_filtrado[col].round(2)

    return df_filtrado[['mes_de_mandato', 'fecha', 'presidente', 'costo_vida_ars', 'ahorro_pf_ars', 'ahorro_dolar_ars']]

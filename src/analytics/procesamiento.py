import pandas as pd


def procesar_comparacion_mandatos(datos_api, df_presidentes, lista_presidentes_elegidos):
    # ==========================================
    # FASE 1: INGESTA Y LIMPIEZA
    # ==========================================
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

    # ==========================================
    # FASE 2: ALINEACIÓN Y CÁLCULO ACUMULADO
    # ==========================================
    df_filtrado = df_infla[df_infla['presidente'].isin(
        lista_presidentes_elegidos)].copy()

    # 1. Ordenamos estrictamente por fecha (CRÍTICO para que la acumulada funcione)
    df_filtrado = df_filtrado.sort_values(by=['presidente', 'fecha'])

    # 2. Creamos el cronómetro (Mes 1, Mes 2...)
    df_filtrado['mes_de_mandato'] = df_filtrado.groupby(
        'presidente').cumcount() + 1

    # ---------------------------------------------------------
    # LA NUEVA MAGIA: CÁLCULO DE INFLACIÓN ACUMULADA
    # ---------------------------------------------------------
    # 3. Convertimos porcentaje a factor multiplicador (ej: 5% -> 1.05)
    df_filtrado['factor_multiplicador'] = 1 + (df_filtrado['valor'] / 100)

    # 4. Aplicamos el Producto Acumulado (cumprod) agrupado por presidente
    df_filtrado['acumulada_decimal'] = df_filtrado.groupby(
        'presidente')['factor_multiplicador'].cumprod()

    # 5. Volvemos a convertir el decimal a porcentaje (ej: 1.15 -> 15%)
    df_filtrado['inflacion_acumulada'] = (
        df_filtrado['acumulada_decimal'] - 1) * 100

    # 6. Redondeamos a 2 decimales para que el CSV quede limpio
    df_filtrado['inflacion_acumulada'] = df_filtrado['inflacion_acumulada'].round(
        2)
    # ---------------------------------------------------------

    # ==========================================
    # FASE 3: LA TIJERA Y EXPORTACIÓN
    # ==========================================
    limite_meses = df_filtrado.groupby(
        'presidente')['mes_de_mandato'].max().min()
    df_final = df_filtrado[df_filtrado['mes_de_mandato'] <= limite_meses]

    # Renombramos 'valor' para que quede claro qué es
    df_final = df_final.rename(columns={'valor': 'inflacion_mensual'})

    # Limpiamos las columnas matemáticas temporales y ordenamos la salida final
    df_final = df_final[['mes_de_mandato', 'fecha',
                         'presidente', 'inflacion_mensual', 'inflacion_acumulada']]

    return df_final

import pandas as pd


def procesar_comparacion_mandatos(datos_api, df_presidentes, presi_1, presi_2):
    """
    Toma los datos crudos de la API y el CSV de presidentes, 
    crea la 'Tabla Gigante', y devuelve un DataFrame recortado y listo.
    """

    # ==========================================
    # FASE 1: CREAR LA TABLA GIGANTE
    # ==========================================

    # 1. Convertimos el JSON de la API en un DataFrame (Tabla) de Pandas
    df_infla = pd.DataFrame(datos_api)

    # 2. Convertimos las columnas de fecha a formato matemático "datetime"
    df_infla['fecha'] = pd.to_datetime(df_infla['fecha'])
    df_presidentes['fecha_inicio'] = pd.to_datetime(
        df_presidentes['fecha_inicio'])
    df_presidentes['fecha_fin'] = pd.to_datetime(df_presidentes['fecha_fin'])

    # 3. Creamos una columna vacía para el presidente
    df_infla['presidente'] = None

    # 4. Llenamos la columna: Le pegamos el presidente a la fecha que corresponde
    # Iteramos sobre el archivo de presidentes (que es cortito)
    for index, fila in df_presidentes.iterrows():
        # Máscara: ¿La fecha de inflación está dentro del mandato de ESTE presidente?
        mascara = (df_infla['fecha'] >= fila['fecha_inicio']) & (
            df_infla['fecha'] <= fila['fecha_fin'])

        # A las filas que dieron Verdadero, le pegamos el nombre
        df_infla.loc[mascara, 'presidente'] = fila['presidente']

    # 5. Borramos los meses viejos (ej. 1940) que no entraron en ningún mandato actual
    df_infla = df_infla.dropna(subset=['presidente'])

    # ==========================================
    # FASE 2: LA LÓGICA DE "LA CARRERA" (Tijera)
    # ==========================================

    # 6. De la tabla gigante, nos quedamos SOLO con los dos presidentes elegidos
    df_filtrado = df_infla[df_infla['presidente'].isin(
        [presi_1, presi_2])].copy()

    # 7. Ordenamos por fecha
    df_filtrado = df_filtrado.sort_values(by='fecha')

    # 8. Creamos el cronómetro individual (Mes 1, Mes 2, Mes 3...)
    df_filtrado['mes_de_mandato'] = df_filtrado.groupby(
        'presidente').cumcount() + 1

    # 9. Buscamos el mandato más corto para saber dónde cortar
    limite_meses = df_filtrado.groupby(
        'presidente')['mes_de_mandato'].max().min()

    # 10. La tijera: Cortamos los meses sobrantes del mandato más largo
    df_final = df_filtrado[df_filtrado['mes_de_mandato'] <= limite_meses]

    # Reordenamos las columnas para que se vea más profesional al exportar
    df_final = df_final[['mes_de_mandato', 'fecha', 'presidente', 'valor']]

    return df_final

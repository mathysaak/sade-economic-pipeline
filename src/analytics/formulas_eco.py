import pandas as pd


def procesar_reservas_bcra(datos_api, df_presidentes, lista_presidentes_elegidos):
    df_reservas = pd.DataFrame(datos_api)
    df_reservas['fecha'] = pd.to_datetime(df_reservas['fecha'])

    # ==========================================
    # EL TRUCO SENIOR: De Diario a Mensual
    # ==========================================
    # La API del BCRA da datos por día. No queremos eso.
    # Agrupamos por Año-Mes y nos quedamos con el 'last()' (el último dato del mes)
    df_reservas['anio_mes'] = df_reservas['fecha'].dt.to_period('M')
    df_reservas_mensual = df_reservas.groupby('anio_mes').last().reset_index()
    # Volvemos a convertir a formato fecha normal
    df_reservas_mensual['fecha'] = df_reservas_mensual['anio_mes'].dt.to_timestamp(
    )

    # Preparamos presidentes
    df_presidentes['fecha_inicio'] = pd.to_datetime(
        df_presidentes['fecha_inicio'])
    df_presidentes['fecha_fin'] = pd.to_datetime(df_presidentes['fecha_fin'])
    df_reservas_mensual['presidente'] = None

    # Asignamos presidente (Igual que con la inflación)
    for index, fila in df_presidentes.iterrows():
        mascara = (df_reservas_mensual['fecha'] >= fila['fecha_inicio']) & (
            df_reservas_mensual['fecha'] <= fila['fecha_fin'])
        df_reservas_mensual.loc[mascara, 'presidente'] = fila['presidente']

    df_reservas_mensual = df_reservas_mensual.dropna(subset=['presidente'])

    # ==========================================
    # LA MATEMÁTICA: Variación Base Cero
    # ==========================================
    df_filtrado = df_reservas_mensual[df_reservas_mensual['presidente'].isin(
        lista_presidentes_elegidos)].copy()
    df_filtrado = df_filtrado.sort_values(by=['presidente', 'fecha'])

    # Cronómetro de meses
    df_filtrado['mes_de_mandato'] = df_filtrado.groupby(
        'presidente').cumcount() + 1

    # 1. Buscamos cuántos dólares había en el Mes 1 de cada presidente
    # Usamos 'transform(first)' para pegarle ese valor a todas las filas de ese presidente
    df_filtrado['reserva_mes_1'] = df_filtrado.groupby(
        'presidente')['valor'].transform('first')

    # 2. Calculamos la variación: ¿Cuántos millones ganó o perdió desde que asumió?
    df_filtrado['variacion_millones_usd'] = df_filtrado['valor'] - \
        df_filtrado['reserva_mes_1']

    # ==========================================
    # LA TIJERA
    # ==========================================
    limite_meses = df_filtrado.groupby(
        'presidente')['mes_de_mandato'].max().min()
    df_final = df_filtrado[df_filtrado['mes_de_mandato'] <= limite_meses]

    # Limpiamos
    df_final = df_final.rename(columns={'valor': 'reserva_total_bruta'})
    df_final = df_final[['mes_de_mandato', 'fecha', 'presidente',
                         'reserva_total_bruta', 'variacion_millones_usd']]

    return df_final

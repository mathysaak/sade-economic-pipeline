import pandas as pd


def comparar_inflacion_mandatos(df_inflacion, presidente_1, presidente_2):
    df_filtrado = df_inflacion[df_inflacion['presidente'].isin(
        [presidente_1, presidente_2])]
    df_filtrado = df_filtrado.sort_values(by='fecha')
    df_filtrado['mes_de_mandato'] = df_filtrado.groupby(
        'presidente').cumcount() + 1
    meses_totales = df_filtrado.groupby('presidente')['mes_de_mandato'].max()
    limite_meses = meses_totales.min()
    df_recortado = df_filtrado[df_filtrado['mes_de_mandato'] <= limite_meses]
    return df_recortado

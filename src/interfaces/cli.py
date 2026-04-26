import questionary
import pandas as pd
import os
from extractors.ar_indec import obtener_datos_inflacion
from analytics.procesamiento import procesar_comparacion_mandatos


def iniciar_sade_cli():
    while True:
        # 1. EL MENÚ PRINCIPAL INTERACTIVO
        opcion = questionary.select(
            "📊 BIENVENIDO A SADE v1.1 - ¿Qué deseas auditar?",
            choices=[
                "1. Extraer última inflación mensual",
                "2. Comparar inflación entre dos presidentes",
                "3. Salir del sistema"
            ]
        ).ask()

        if opcion.startswith("1"):
            print("\n⏳ Obteniendo datos desde la API oficial...")
            datos_inflacion = obtener_datos_inflacion()
            if datos_inflacion:
                ultimo = datos_inflacion[-1]
                print(
                    f"✅ Éxito -> Fecha: {ultimo.get('fecha')} | Inflación: {ultimo.get('valor')}%\n")
            else:
                print("❌ Error de conexión.\n")

        elif opcion.startswith("2"):
            _ejecutar_comparacion_mandatos()

        elif opcion.startswith("3"):
            print("\nCerrando SADE. ¡Hasta pronto! 👋")
            break


def _ejecutar_comparacion_mandatos():
    print("\n--- PREPARANDO MOTOR ETL ---")
    df_presidentes = pd.read_csv(
        "data/presidentesAR.csv", skipinitialspace=True)
    df_presidentes['fecha_fin'] = pd.to_datetime(df_presidentes['fecha_fin'])

    datos_api = obtener_datos_inflacion()
    if not datos_api:
        return

    primera_fecha_inflacion = pd.to_datetime(datos_api[0]['fecha'])
    df_filtrado = df_presidentes[df_presidentes['fecha_fin']
                                 >= primera_fecha_inflacion]
    df_ordenado = df_filtrado.sort_values(by='fecha_inicio', ascending=False)

    # Lista de nombres para el menú
    lista_nombres = df_ordenado['presidente'].unique().tolist()

    # 2. SELECCIÓN INTERACTIVA DEL PRESIDENTE BASE (Con flechas)
    nombre_presi_1 = questionary.select(
        "Seleccione el PRIMER presidente (Mandato Base):",
        choices=lista_nombres
    ).ask()

    # 3. SELECCIÓN INTERACTIVA DEL PRESIDENTE A COMPARAR
    nombre_presi_2 = questionary.select(
        "Seleccione el SEGUNDO presidente (A comparar):",
        choices=lista_nombres
    ).ask()

    print(f"\n⚙️ Procesando: {nombre_presi_1} vs {nombre_presi_2}...")

    # Procesamos
    df_resultado = procesar_comparacion_mandatos(
        datos_api, df_presidentes, nombre_presi_1, nombre_presi_2)

    # Verificamos si la carpeta existe, si no, la creamos
    os.makedirs("data/exports", exist_ok=True)

    ruta_exportacion = "data/exports/comparacion_mandatos.csv"
    df_resultado.to_csv(ruta_exportacion, index=False)
    print(f"✅ ¡Análisis completado! Archivo guardado en: {ruta_exportacion}\n")

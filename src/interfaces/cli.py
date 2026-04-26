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
                "2. Comparar inflación entre mandatos presidenciales",
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
    df_presidentes['fecha_inicio'] = pd.to_datetime(
        df_presidentes['fecha_inicio'])  # Aseguramos formato

    datos_api = obtener_datos_inflacion()
    if not datos_api:
        return

    # FILTRO DEMOCRACIA: Nos quedamos solo con los que asumieron desde el 10/12/1983
    df_democracia = df_presidentes[df_presidentes['fecha_inicio']
                                   >= '1983-12-10']
    df_ordenado = df_democracia.sort_values(by='fecha_inicio', ascending=False)

    # Lista de nombres para el menú
    lista_nombres = df_ordenado['presidente'].unique().tolist()

    # EL NUEVO MENÚ CHECKBOX
    print("\nInstrucciones: Usa ESPACIO para seleccionar, FLECHAS para moverte, ENTER para confirmar.")
    presidentes_seleccionados = questionary.checkbox(
        "Seleccione los presidentes a comparar (Mínimo 2):",
        choices=lista_nombres
    ).ask()

    # Validación de usuario
    if not presidentes_seleccionados or len(presidentes_seleccionados) < 2:
        print("❌ Operación cancelada: Debes seleccionar al menos 2 presidentes para comparar.\n")
        return

    print(
        f"\n⚙️ Procesando análisis múltiple para: {', '.join(presidentes_seleccionados)}...")

    # Procesamos pasándole la lista entera
    df_resultado = procesar_comparacion_mandatos(
        datos_api, df_presidentes, presidentes_seleccionados)

    import os
    os.makedirs("data/exports", exist_ok=True)
    ruta_exportacion = "data/exports/comparacion_multi_mandatos.csv"
    df_resultado.to_csv(ruta_exportacion, index=False)

    print(f"✅ ¡Análisis completado! Archivo guardado en: {ruta_exportacion}\n")

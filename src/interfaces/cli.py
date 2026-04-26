import questionary
import pandas as pd
import os
from extractors.ar_indec import obtener_datos_inflacion
from extractors.ar_reservas import obtener_datos_reservas
from extractors.ar_salarios import obtener_datos_salarios
from extractors.ar_dolares import obtener_datos_dolar_mep
from analytics.procesamiento import procesar_comparacion_mandatos
from analytics.formulas_eco import procesar_reservas_bcra, procesar_salario_dolar, procesar_dolar_constante, procesar_carrera_ahorros
from extractors.ar_riesgo import obtener_datos_riesgo_pais


def iniciar_sade_cli():
    while True:
        # 1. EL MENÚ PRINCIPAL INTERACTIVO
        opcion = questionary.select(
            "📊 BIENVENIDO A SADE v1.1 - ¿Qué deseas auditar?",
            choices=[
                "1. Ver tablero ejecutivo de coyuntura económica",
                "2. Comparar inflación entre mandatos presidenciales",
                "3. Comparar reservas del BCRA entre mandatos presidenciales",
                "4. Comparar poder adquisitivo entre mandatos presidenciales",
                "5. Calcular tipo de cambio real (Dólar Constante)",
                "6. Simular carrera de ahorros",
                "7. Salir del sistema"
            ]
        ).ask()

        if opcion.startswith("1"):
            _mostrar_tablero_ejecutivo()

        elif opcion.startswith("2"):
            _ejecutar_comparacion_mandatos()

        elif opcion.startswith("3"):
            _ejecutar_comparacion_reservas()

        elif opcion.startswith("4"):
            _ejecutar_comparacion_salarios()

        elif opcion.startswith("5"):
            _ejecutar_dolar_constante()

        elif opcion.startswith("6"):
            _ejecutar_carrera_ahorros()

        elif opcion.startswith("7"):
            print("\nCerrando SADE. ¡Hasta pronto! 👋")
            break


def _mostrar_tablero_ejecutivo():
    print("\n" + "═"*70)
    print(" 📈 TABLERO DE COYUNTURA ECONÓMICA ACTUAL")
    print(" (Último dato oficial disponible vs período anterior)")
    print("═"*70)

    # 🛒 INFLACIÓN
    infla = obtener_datos_inflacion()
    if infla:
        actual, previa = infla[-1]['valor'], infla[-2]['valor']
        fecha = infla[-1]['fecha'][:7]  # Recortamos a YYYY-MM
        diff = round(actual - previa, 1)
        icon = "🔻" if diff < 0 else "🔺"
        color = "🟢" if diff < 0 else "🔴"
        print(
            f"🛒 Inflación   [{fecha}]: {actual: >5}%  | {icon} {abs(diff): >4}% vs previo {color}")

    # 🏦 RESERVAS BCRA
    res = obtener_datos_reservas()
    if res:
        actual, previa = res[-1]['valor'], res[-2]['valor']
        fecha = res[-1]['fecha'][:7]
        diff = round((actual - previa) / 1000, 2)
        icon = "🔺" if diff > 0 else "🔻"
        color = "🟢" if diff > 0 else "🔴"
        print(
            f"🏦 Reservas    [{fecha}]: {round(actual/1000, 2): >5}B | {icon} {abs(diff): >4}B USD {color}")

    # 💵 DÓLAR MEP
    mep = obtener_datos_dolar_mep()
    if mep:
        actual, previa = mep[-1]['valor'], mep[-2]['valor']
        # El dólar sí lo mostramos por día completo YYYY-MM-DD
        fecha = mep[-1]['fecha']
        diff = round(actual - previa, 2)
        icon = "🔺" if diff > 0 else "🔻"
        color = "🔴" if diff > 0 else "🟢"
        print(
            f"💵 Dólar MEP   [{fecha}]: ${actual: >4}  | {icon} ${abs(diff): >4} {color}")

    # 💼 SALARIO (RIPTE)
    sals = obtener_datos_salarios()
    if sals:
        actual, previa = sals[-1]['valor'], sals[-2]['valor']
        fecha = sals[-1]['fecha'][:7]
        diff_pct = round(((actual / previa) - 1) * 100, 1)
        icon = "🔺" if diff_pct > 0 else "🔻"
        color = "🟢" if diff_pct > 0 else "🔴"
        print(
            f"💼 Salario ARS [{fecha}]: {icon} {abs(diff_pct)}% nominal mensual {color}")

    # 🌎 RIESGO PAÍS (NUEVO)
    riesgo = obtener_datos_riesgo_pais()
    if riesgo:
        actual, previa = riesgo[-1]['valor'], riesgo[-2]['valor']
        fecha = riesgo[-1]['fecha']
        diff = int(actual - previa)
        icon = "🔻" if diff < 0 else "🔺"
        color = "🟢" if diff < 0 else "🔴"
        print(
            f"🌎 Riesgo País [{fecha}]: {int(actual): >4} pts| {icon} {abs(diff): >4} pts {color}")

    print("═"*70 + "\n")


def _ejecutar_comparacion_reservas():
    print("\n--- PREPARANDO MOTOR ETL ---")
    df_presidentes = pd.read_csv(
        "data/presidentesAR.csv", skipinitialspace=True)
    df_presidentes['fecha_inicio'] = pd.to_datetime(
        df_presidentes['fecha_inicio'])
    df_presidentes['fecha_fin'] = pd.to_datetime(df_presidentes['fecha_fin'])

    from extractors.ar_reservas import obtener_datos_reservas
    from analytics.formulas_eco import procesar_reservas_bcra

    datos_api = obtener_datos_reservas()
    if not datos_api:
        print("❌ No se pudieron obtener datos de las reservas.")
        return

    df_democracia = df_presidentes[df_presidentes['fecha_inicio']
                                   >= '1983-12-10']
    df_ordenado = df_democracia.sort_values(by='fecha_inicio', ascending=False)
    lista_nombres = df_ordenado['presidente'].unique().tolist()

    print("\nInstrucciones: Usa ESPACIO para seleccionar, FLECHAS para moverte, ENTER para confirmar.")
    presidentes_seleccionados = questionary.checkbox(
        "Seleccione los presidentes a comparar (Mínimo 2):",
        choices=lista_nombres
    ).ask()

    if not presidentes_seleccionados or len(presidentes_seleccionados) < 2:
        print("❌ Operación cancelada: Debes seleccionar al menos 2 presidentes.\n")
        return

    print(
        f"\n⚙️ Procesando análisis de reservas para: {', '.join(presidentes_seleccionados)}...")

    df_resultado = procesar_reservas_bcra(
        datos_api, df_presidentes, presidentes_seleccionados)

    os.makedirs("data/exports", exist_ok=True)
    ruta_exportacion = "data/exports/comparacion_reservas_mandatos.csv"
    df_resultado.to_csv(ruta_exportacion, index=False)

    print(f"✅ ¡Análisis completado! Archivo guardado en: {ruta_exportacion}\n")


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


def _ejecutar_comparacion_salarios():
    print("\n--- INICIANDO ANÁLISIS DE PODER ADQUISITIVO ---")
    df_presis = pd.read_csv("data/presidentesAR.csv", skipinitialspace=True)
    df_presis['fecha_inicio'] = pd.to_datetime(df_presis['fecha_inicio'])

# Ingesta Dual
    sals = obtener_datos_salarios()
    mep = obtener_datos_dolar_mep()

    if not sals or not mep:
        # AGREGA ESTA LÍNEA
        print("❌ Error: Las APIs no devolvieron datos. Operación abortada.\n")
        return

    lista_nombres = df_presis[df_presis['fecha_inicio']
                              >= '1983-12-10']['presidente'].unique().tolist()

    sel = questionary.checkbox(
        "Seleccione presidentes para comparar Salario en USD:", choices=lista_nombres).ask()

    if len(sel) < 2:
        return

    df_res = procesar_salario_dolar(sals, mep, df_presis, sel)

    os.makedirs("data/exports", exist_ok=True)
    ruta = "data/exports/comparacion_salarios_usd.csv"
    df_res.to_csv(ruta, index=False)
    print(f"✅ ¡Éxito! El análisis de bolsillo fue exportado a: {ruta}\n")


def _ejecutar_dolar_constante():
    print("\n--- CALCULANDO TIPO DE CAMBIO REAL MULTILATERAL ---")
    df_presis = pd.read_csv("data/presidentesAR.csv", skipinitialspace=True)
    df_presis['fecha_inicio'] = pd.to_datetime(df_presis['fecha_inicio'])

    infla = obtener_datos_inflacion()
    mep = obtener_datos_dolar_mep()

    if not infla or not mep:
        print("❌ Error de APIs. Operación abortada.\n")
        return

    lista_nombres = df_presis[df_presis['fecha_inicio']
                              >= '1983-12-10']['presidente'].unique().tolist()
    sel = questionary.checkbox(
        "Seleccione presidentes (Mínimo 2):", choices=lista_nombres).ask()

    if not sel or len(sel) < 2:
        return

    df_res = procesar_dolar_constante(infla, mep, df_presis, sel)
    ruta = "data/exports/comparacion_dolar_constante.csv"
    df_res.to_csv(ruta, index=False)
    print(f"✅ ¡Éxito! Índice de Dólar Constante exportado a: {ruta}\n")


def _ejecutar_carrera_ahorros():
    print("\n--- INICIANDO SIMULADOR DE LICUADORA DE AHORROS ---")
    from extractors.ar_tasas import obtener_datos_plazo_fijo

    df_presis = pd.read_csv("data/presidentesAR.csv", skipinitialspace=True)
    df_presis['fecha_inicio'] = pd.to_datetime(df_presis['fecha_inicio'])

    infla = obtener_datos_inflacion()
    mep = obtener_datos_dolar_mep()
    tasas = obtener_datos_plazo_fijo()

    if not infla or not mep or not tasas:
        print("❌ Error de APIs. Operación abortada.\n")
        return

    # Filtramos desde el 2000 en adelante porque las tasas confiables digitalizadas arrancan después del 1 a 1
    lista_nombres = df_presis[df_presis['fecha_inicio']
                              >= '2001-01-01']['presidente'].unique().tolist()
    sel = questionary.checkbox(
        "Seleccione presidentes para la Carrera del Ahorro:", choices=lista_nombres).ask()

    if not sel or len(sel) < 2:
        return

    df_res = procesar_carrera_ahorros(infla, mep, tasas, df_presis, sel)
    ruta = "data/exports/comparacion_carrera_ahorros.csv"
    df_res.to_csv(ruta, index=False)
    print(f"✅ ¡Éxito! Simulación exportada a: {ruta}\n")

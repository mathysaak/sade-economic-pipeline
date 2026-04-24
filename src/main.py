import pandas as pd
from extractors.ar_indec import obtener_datos_inflacion
from qa.procesamiento import procesar_comparacion_mandatos


def mostrar_menu():
    print("\n" + "="*35)
    print(" 📊 BIENVENIDO A SADE v1.0 📊")
    print(" Sistema de Auditoría de Datos Económicos")
    print("="*35)
    print("1. Extraer última inflación mensual")
    print("2. Comparar inflación entre dos presidentes")
    print("3. Salir")

    opcion = input("\nSeleccione una opción (1-3): ")
    return opcion


def ejecutar_opcion(opcion):
    if opcion == "1":
        print("\n⏳ Obteniendo última inflación mensual desde la API oficial...")
        datos_inflacion = obtener_datos_inflacion()

        if datos_inflacion:
            ultimo_dato = datos_inflacion[-1]
            print("✅ ¡Datos obtenidos con éxito!")
            print(
                f"👉 Fecha: {ultimo_dato.get('fecha')} | Inflación: {ultimo_dato.get('valor')}%")
        else:
            print("❌ Error: No se pudieron obtener los datos de la API.")

    elif opcion == "2":
        print("\n" + "-"*30)
        print(" COMPAREDOR DE MANDATOS (BASE 0)")
        print("-"*30)

        try:
            # 1. LA SOLUCIÓN AL ERROR: skipinitialspace=True ignora los espacios ocultos
            df_presidentes = pd.read_csv(
                "data/presidentesAR.csv", skipinitialspace=True)

            # 2. Convertimos las fechas a un formato matemático para poder comparar
            df_presidentes['fecha_fin'] = pd.to_datetime(
                df_presidentes['fecha_fin'])

            # 3. FILTRO: Obtenemos los datos de la API para saber cuándo arranca la inflación
            print("⏳ Consultando fechas históricas en la API...")
            datos_api = obtener_datos_inflacion()

            if not datos_api:
                print("❌ Error: No se pudieron obtener los datos base de la API.")
                return  # Vuelve al menú principal

            primera_fecha_inflacion = pd.to_datetime(datos_api[0]['fecha'])

            # 4. LA LIMPIEZA: Nos quedamos solo con presidentes que gobernaron DESPUÉS de la primera medición
            df_filtrado = df_presidentes[df_presidentes['fecha_fin']
                                         >= primera_fecha_inflacion]

            # 5. EL ORDEN: Ordenamos desde el más actual al más antiguo y sacamos los nombres
            df_ordenado = df_filtrado.sort_values(
                by='fecha_inicio', ascending=False)
            lista_presidentes = df_ordenado['presidente'].unique()

            # 6. Dibujamos el menú
            print("\n--- Presidentes con datos disponibles ---")
            for i, presidente in enumerate(lista_presidentes):
                print(f"[{i}] {presidente}")

            # 7. Pedimos los números al usuario
            eleccion_1 = int(
                input("\nIngrese el NÚMERO del PRIMER presidente (Base): "))
            eleccion_2 = int(
                input("Ingrese el NÚMERO del SEGUNDO presidente (A comparar): "))

            nombre_presi_1 = lista_presidentes[eleccion_1]
            nombre_presi_2 = lista_presidentes[eleccion_2]

            print(
                f"\n⚙️ Iniciando motor ETL para: {nombre_presi_1} vs {nombre_presi_2}...")

            # --- AQUÍ LLAMAREMOS A procesamiento.py ---

            df_resultado = procesar_comparacion_mandatos(
                datos_api, df_presidentes, nombre_presi_1, nombre_presi_2)            # Exportamos a CSV
            ruta_exportacion = "data/exports/comparacion_mandatos.csv"
            df_resultado.to_csv(ruta_exportacion, index=False)
            print(
                f"✅ ¡Análisis completado! Archivo guardado en: {ruta_exportacion}")

        except ValueError:
            print("❌ Error: Debes ingresar un número.")
        except IndexError:
            print("❌ Error: El número no existe en la lista.")
        except FileNotFoundError:
            print("❌ Error: Falta el archivo 'presidentesAR.csv'.")
        except KeyError as e:
            print(
                f"❌ Error de columnas en el CSV. Asegúrate de que se llame: {e}")

    elif opcion == "3":
        print("\nCerrando SADE. ¡Hasta pronto! 👋")
        exit()
    else:
        print("\n❌ Opción no válida. Por favor, intente nuevamente.")


if __name__ == "__main__":
    while True:
        opcion = mostrar_menu()
        ejecutar_opcion(opcion)

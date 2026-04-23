from extractors.ar_indec import obtener_datos_inflacion


def mostrar_menu():
    print("\n--- Bienvenido a SADE 1.0 ---")
    print("Sistema de Análisis de Datos Económicos")
    print("1. Extraer última inflación mensual de Argentina")
    print("2. Salir")

    opcion = input("Seleccione una opción: ")
    return opcion


def ejecutar_opcion(opcion):
    if opcion == "1":
        print("\nUltima inflación mensual de Argentina...")
        datos_inflacion = obtener_datos_inflacion()
        if datos_inflacion:
            print("Datos de inflación obtenidos:")
            print(datos_inflacion[-1])  # Mostrar el último dato de inflación
        else:
            print("No se pudieron obtener los datos de inflación.")

    elif opcion == "2":
        print("Saliendo del programa. ¡Hasta luego!")
        exit()
    else:
        print("Opción no válida. Por favor, intente nuevamente.")


if __name__ == "__main__":
    while True:
        opcion = mostrar_menu()
        ejecutar_opcion(opcion)

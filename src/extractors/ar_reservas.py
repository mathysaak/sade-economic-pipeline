import requests


def obtener_datos_reservas():
    # La API oficial de series temporales del gobierno
    url = "https://apis.datos.gob.ar/series/api/series/"

    parametros = {
        "ids": "92.1_RID_0_0_32",  # ID de Reservas del BCRA (Mensual)
        "limit": 5000,             # Traemos toda la historia disponible
        "format": "json"
    }

    print("⏳ Conectando con la API de Datos Argentina (BCRA)...")
    respuesta = requests.get(url, params=parametros)

    if respuesta.status_code == 200:
        datos_crudos = respuesta.json()

        # La API de datos.gob.ar devuelve una lista de listas: ['2024-01-01', 25000.5]
        # Lo transformamos al formato estándar de SADE para no romper la compatibilidad
        lista_formateada = []
        for registro in datos_crudos['data']:
            lista_formateada.append({
                "fecha": registro[0],
                "valor": registro[1]
            })

        return lista_formateada
    else:
        print(f"❌ Error de la API: {respuesta.status_code}")
        return None


# Si quieres probarlo rápido ejecutando solo este archivo:
if __name__ == "__main__":
    datos = obtener_datos_reservas()
    if datos:
        print("Último dato de reservas:")
        print(datos[-1])

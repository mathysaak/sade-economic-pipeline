import requests


def obtener_datos_plazo_fijo():
    # Usamos la API del Estado para obtener la serie temporal histórica
    url = "https://apis.datos.gob.ar/series/api/series/"
    parametros = {
        "ids": "89.1_TIPF35D_0_0_35",  # ID oficial del BCRA para Plazo Fijo a 30 días
        "limit": 5000,
        "format": "json"
    }

    print("⏳ Conectando con la API del BCRA (Histórico Plazo Fijo)...")
    try:
        respuesta = requests.get(url, params=parametros)
        if respuesta.status_code == 200:
            datos_crudos = respuesta.json()

            # Formateamos los datos al estándar de SADE
            lista_formateada = []
            for registro in datos_crudos['data']:
                lista_formateada.append({
                    "fecha": registro[0],
                    "valor": registro[1]  # La TNA en porcentaje
                })
            return lista_formateada
        else:
            print(f"❌ Error en API BCRA: {respuesta.status_code}")
    except Exception as e:
        print(f"❌ Error de conexión: {e}")

    return None

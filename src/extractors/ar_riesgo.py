import requests


def obtener_datos_riesgo_pais():
    url = "https://api.argentinadatos.com/v1/finanzas/rendimientos/riesgo-pais"
    try:
        respuesta = requests.get(url)
        if respuesta.status_code == 200:
            return respuesta.json()
    except:
        pass
    return None

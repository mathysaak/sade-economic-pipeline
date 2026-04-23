import requests


def obtener_datos_inflacion():

    url = "https://api.argentinadatos.com/v1/finanzas/indices/inflacion"

    datos_de_infla = requests.get(url)
    if datos_de_infla.status_code == 200:
        datos = datos_de_infla.json()
        return datos
    else:
        print("Error al obtener los datos de inflación. Código de estado:",
              datos_de_infla.status_code)
        return []

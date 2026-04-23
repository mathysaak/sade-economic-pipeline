import requests

url = "https://api.argentinadatos.com/v1/finanzas/indices/inflacion"

datos_de_infla = requests.get(url)

if datos_de_infla.status_code == 200:
    print("Datos obtenidos")
    datos_de_infla_json = datos_de_infla.json()
    ultimo_mes = datos_de_infla_json[-1].get("valor")
    print(f"Último mes registrado: {ultimo_mes}")

else:
    print(f"Error: {datos_de_infla.status_code}")

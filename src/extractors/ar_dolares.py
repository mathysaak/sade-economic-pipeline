import requests


def obtener_datos_dolar_mep():
    url = "https://api.argentinadatos.com/v1/cotizaciones/dolares"
    print("⏳ Conectando con la API de Cotizaciones (Dólar MEP)...")
    respuesta = requests.get(url)

    if respuesta.status_code == 200:
        datos = respuesta.json()
        # LA API USA LA PALABRA 'bolsa' PARA EL MEP
        return [{"fecha": d['fecha'], "valor": d['venta']} for d in datos if d['casa'] == 'bolsa']
    return None

# GrafoRotas - Integracao opcional com a API do Google Maps (alternativa ao OpenStreetMap).
# Teoria dos Grafos | Bacharelado em Ciencia da Computacao
# Integrantes: Guilherme Haddad Borro - RA 10427699 | Rafael Lima - RA 10425819 | Pedro Augusto Yoshikuni - RA 10410287 | Tiago Silveira Lopes - RA 10417600
# Historico: 2026-09-02

import os

# A chave NAO deve ser versionada no GitHub. Configure-a como variavel de
# ambiente: export GOOGLE_MAPS_API_KEY="sua_chave_aqui"
API_KEY = os.environ.get("GOOGLE_MAPS_API_KEY", "")
URL_BASE = "https://maps.googleapis.com/maps/api/distancematrix/json"


def distancia_rodoviaria(origem_latlon, destino_latlon):
    """Retorna a distancia rodoviaria (km) entre dois pontos via Google Maps.

    origem_latlon / destino_latlon: tuplas (latitude, longitude).
    Retorna None se a chave nao estiver configurada ou em caso de erro,
    permitindo que o chamador use a distancia geografica como fallback.

    Exemplo de uso (quando a chave estiver disponivel):
        km = distancia_rodoviaria((-23.55, -46.63), (-22.91, -47.06))
    """
    if not API_KEY:
        return None
    try:
        import requests  # importado sob demanda para nao exigir a dependencia
        params = {
            "origins": f"{origem_latlon[0]},{origem_latlon[1]}",
            "destinations": f"{destino_latlon[0]},{destino_latlon[1]}",
            "mode": "driving",
            "key": API_KEY,
        }
        resp = requests.get(URL_BASE, params=params, timeout=10)
        dados = resp.json()
        metros = dados["rows"][0]["elements"][0]["distance"]["value"]
        return round(metros / 1000.0, 1)
    except Exception:
        return None

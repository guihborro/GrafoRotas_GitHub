# GrafoRotas - Coleta de dados reais (IBGE + OpenStreetMap) e geracao de grafo.txt e cidades.csv.
# Teoria dos Grafos | Bacharelado em Ciencia da Computacao
# Integrantes: Guilherme Haddad Borro - RA 10427699 | Rafael Lima - RA 10425819 | Pedro Augusto Yoshikuni - RA 10410287 | Tiago Silveira Lopes - RA 10417600
# Historico: 2026-09-02 | [Autor] | versao atual

import csv
import time
from math import radians, sin, cos, asin, sqrt

import requests

# --------------------------------------------------------------------------- #
# CONFIGURACAO
# --------------------------------------------------------------------------- #
# Recorte oficial adotado: Regioes Geograficas Intermediarias do IBGE (2017).
# A intermediaria de Sao Paulo sozinha tem ~50 municipios (abaixo do minimo de
# 80 vertices); por isso combinamos intermediarias oficiais e contiguas ate
# ultrapassar o minimo. Para ajustar o recorte, edite a lista abaixo.
INTERMEDIARIAS_ALVO = ["Sao Paulo", "Sorocaba", "Campinas"]

# (Opcional) Se quiser um recorte menor, liste aqui os nomes das Regioes
# Geograficas IMEDIATAS desejadas; se a lista estiver vazia, usa a
# intermediaria inteira definida acima.
IMEDIATAS_ALVO = []          # ex.: ["Sao Paulo", "Osasco", "Guarulhos"]

K_VIZINHOS = 5               # cada cidade liga-se as K mais proximas
PAUSA_SEG = 1.1             # pausa entre chamadas (respeita limites gratuitos)

UA = {"User-Agent": "GrafoRotas-TeoriaDosGrafos/1.0 (projeto academico)"}


# --------------------------------------------------------------------------- #
# 1) MUNICIPIOS OFICIAIS (IBGE)
# --------------------------------------------------------------------------- #
def normaliza(txt):
    """Remove acentos e caixa para comparar nomes com seguranca."""
    import unicodedata
    txt = unicodedata.normalize("NFKD", txt)
    txt = "".join(c for c in txt if not unicodedata.combining(c))
    return txt.strip().lower()


def obter_municipios_ibge():
    """Busca na API do IBGE os municipios de SP filtrados pelo recorte oficial.

    Retorna lista de dicts: {codigo_ibge, nome, imediata, intermediaria}.
    """
    url = "https://servicodados.ibge.gov.br/api/v1/localidades/estados/35/municipios"
    print("Consultando IBGE:", url)
    resp = requests.get(url, headers=UA, timeout=30)
    resp.raise_for_status()
    dados = resp.json()

    alvos_inter = {normaliza(x) for x in INTERMEDIARIAS_ALVO}
    alvos_imed = {normaliza(x) for x in IMEDIATAS_ALVO}

    selecionados = []
    for m in dados:
        imed = m.get("regiao-imediata", {})
        inter = imed.get("regiao-intermediaria", {}) if imed else {}
        nome_imed = imed.get("nome", "")
        nome_inter = inter.get("nome", "")
        if alvos_imed:
            ok = normaliza(nome_imed) in alvos_imed
        else:
            ok = normaliza(nome_inter) in alvos_inter
        if ok:
            selecionados.append({
                "codigo_ibge": m["id"],
                "nome": m["nome"],
                "imediata": nome_imed,
                "intermediaria": nome_inter,
            })
    selecionados.sort(key=lambda x: x["nome"])
    from collections import Counter
    por_inter = Counter(m["intermediaria"] for m in selecionados)
    print(f"  -> {len(selecionados)} municipios no recorte selecionado.")
    print(f"     por intermediaria: {dict(por_inter)}")
    return selecionados


# --------------------------------------------------------------------------- #
# 2) COORDENADAS (OpenStreetMap / Nominatim)
# --------------------------------------------------------------------------- #
def geocodificar(nome_municipio):
    """Obtem (lat, lon) do municipio via Nominatim (OpenStreetMap)."""
    url = "https://nominatim.openstreetmap.org/search"
    params = {"q": f"{nome_municipio}, Sao Paulo, Brasil",
              "format": "json", "limit": 1}
    resp = requests.get(url, params=params, headers=UA, timeout=30)
    resp.raise_for_status()
    r = resp.json()
    if not r:
        return None
    return float(r[0]["lat"]), float(r[0]["lon"])


# --------------------------------------------------------------------------- #
# 3) DISTANCIA GEOGRAFICA (para escolher vizinhos) e RODOVIARIA (OSRM)
# --------------------------------------------------------------------------- #
def haversine_km(lat1, lon1, lat2, lon2):
    R = 6371.0
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    return round(2 * R * asin(sqrt(a)), 1)


def distancia_rodoviaria_km(lat1, lon1, lat2, lon2):
    """Distancia rodoviaria real (km) via OSRM (OpenStreetMap). None se falhar."""
    url = (f"https://router.project-osrm.org/route/v1/driving/"
           f"{lon1},{lat1};{lon2},{lat2}?overview=false")
    try:
        resp = requests.get(url, headers=UA, timeout=30)
        resp.raise_for_status()
        dados = resp.json()
        if dados.get("code") == "Ok" and dados.get("routes"):
            return round(dados["routes"][0]["distance"] / 1000.0, 1)
    except Exception as e:
        print("   aviso OSRM:", e)
    return None


# --------------------------------------------------------------------------- #
# PIPELINE PRINCIPAL
# --------------------------------------------------------------------------- #
def main():
    # 1) municipios oficiais
    municipios = obter_municipios_ibge()
    if len(municipios) < 80:
        print(f"ATENCAO: recorte tem {len(municipios)} municipios (< 80 exigidos).")
        print("Ajuste INTERMEDIARIA_ALVO/IMEDIATAS_ALVO no topo do arquivo.")

    # 2) coordenadas via OpenStreetMap
    print("\nGeocodificando municipios (OpenStreetMap/Nominatim)...")
    cidades = []
    for i, m in enumerate(municipios):
        coord = geocodificar(m["nome"])
        if coord is None:
            print(f"  [{i}] {m['nome']}: SEM coordenada, ignorado.")
            continue
        cidades.append({**m, "lat": coord[0], "lon": coord[1]})
        print(f"  [{len(cidades)-1}] {m['nome']}: {coord[0]:.4f}, {coord[1]:.4f}")
        time.sleep(PAUSA_SEG)

    # 3) arestas: cada cidade -> K vizinhas mais proximas (por haversine)
    print("\nDefinindo arestas (K vizinhos mais proximos)...")
    candidatas = set()
    for i, a in enumerate(cidades):
        dists = []
        for j, b in enumerate(cidades):
            if i == j:
                continue
            dists.append((haversine_km(a["lat"], a["lon"], b["lat"], b["lon"]), j))
        dists.sort()
        for _, j in dists[:K_VIZINHOS]:
            candidatas.add((min(i, j), max(i, j)))
    print(f"  -> {len(candidatas)} arestas candidatas.")

    # 4) distancia rodoviaria real de cada aresta (OSRM)
    print("\nObtendo distancias rodoviarias reais (OpenStreetMap/OSRM)...")
    arestas = []
    for n, (u, v) in enumerate(sorted(candidatas), 1):
        a, b = cidades[u], cidades[v]
        km = distancia_rodoviaria_km(a["lat"], a["lon"], b["lat"], b["lon"])
        if km is None:  # fallback: distancia geografica, marcada
            km = haversine_km(a["lat"], a["lon"], b["lat"], b["lon"])
        arestas.append((u, v, km))
        if n % 25 == 0:
            print(f"  {n}/{len(candidatas)} arestas processadas...")
        time.sleep(PAUSA_SEG)

    # 5) gravacao dos arquivos
    with open("cidades.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["id", "nome", "codigo_ibge", "lat", "lon"])
        for idc, c in enumerate(cidades):
            w.writerow([idc, c["nome"], c["codigo_ibge"], c["lat"], c["lon"]])

    with open("grafo.txt", "w", encoding="utf-8") as f:
        f.write(f"{len(cidades)}\n")
        for idc, c in enumerate(cidades):
            f.write(f"{idc};{c['nome']}\n")
        f.write(f"{len(arestas)}\n")
        for u, v, km in arestas:
            f.write(f"{u};{v};{km}\n")

    print("\n==================== COLETA CONCLUIDA ====================")
    print(f"Municipios (vertices): {len(cidades)}")
    print(f"Ligacoes (arestas):    {len(arestas)}")
    print("Arquivos gerados: cidades.csv e grafo.txt")
    print("Fontes: IBGE (municipios) e OpenStreetMap (coordenadas e distancias).")


if __name__ == "__main__":
    main()

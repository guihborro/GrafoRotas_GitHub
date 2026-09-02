# GrafoRotas - Geracao das figuras do relatorio (esboco e malha completa).
# Teoria dos Grafos | Bacharelado em Ciencia da Computacao
# Integrantes: Guilherme Haddad Borro - RA 10427699 | Rafael Lima - RA 10425819 | Pedro Augusto Yoshikuni - RA 10410287 | Tiago Silveira Lopes - RA 10417600
# Historico: 2026-09-02 | [Autor] | versao atual

import csv
import os
import sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from grafo import Grafo

AZUL = "#2563EB"
AZUL_ESC = "#1E3A5F"
CINZA = "#94A3B8"
TXT = "#0F172A"


def carregar_coordenadas(caminho="cidades.csv"):
    """Le cidades.csv -> dict {id: (nome, lat, lon)}."""
    coords = {}
    with open(caminho, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            coords[int(row["id"])] = (row["nome"], float(row["lat"]), float(row["lon"]))
    return coords


# --- Esboco conceitual (independente do dataset) --------------------------- #
def gerar_esboco():
    pos = {
        "Sao Paulo": (0.40, 0.45), "Guarulhos": (0.55, 0.62),
        "Santo Andre": (0.55, 0.28), "Sao Bernardo do Campo": (0.42, 0.18),
        "Mogi das Cruzes": (0.80, 0.55), "Jundiai": (0.22, 0.72),
        "Osasco": (0.20, 0.42), "Sao Jose dos Campos": (0.86, 0.78),
    }
    arestas = [
        ("Sao Paulo", "Guarulhos", 15), ("Sao Paulo", "Santo Andre", 16),
        ("Sao Paulo", "Osasco", 16), ("Sao Paulo", "Sao Bernardo do Campo", 17),
        ("Santo Andre", "Sao Bernardo do Campo", 5), ("Guarulhos", "Mogi das Cruzes", 36),
        ("Mogi das Cruzes", "Sao Jose dos Campos", 62), ("Osasco", "Jundiai", 40),
        ("Guarulhos", "Sao Jose dos Campos", 73), ("Jundiai", "Sao Paulo", 49),
    ]
    fig, ax = plt.subplots(figsize=(9, 6.2))
    for a, b, km in arestas:
        xa, ya = pos[a]; xb, yb = pos[b]
        ax.plot([xa, xb], [ya, yb], color=CINZA, lw=1.8, zorder=1)
        ax.text((xa + xb) / 2, (ya + yb) / 2, f"{km} km", fontsize=8.5,
                color=AZUL_ESC, ha="center", va="center",
                bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="none", alpha=0.85),
                zorder=2)
    for nome, (x, y) in pos.items():
        ax.scatter([x], [y], s=1500, color=AZUL, edgecolors="white", linewidths=2, zorder=3)
        ax.text(x, y - 0.075, nome, fontsize=8.5, ha="center", va="top",
                color=TXT, weight="bold", zorder=4)
    ax.set_title("Esboco da modelagem: cidades (vertices) e distancias (arestas ponderadas)",
                 fontsize=12, color=TXT, weight="bold", pad=14)
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")
    plt.tight_layout()
    plt.savefig("esboco_grafo.png", dpi=150, bbox_inches="tight", facecolor="white")
    plt.close()
    print("esboco_grafo.png gerado")


# --- Malha completa (dados reais) ------------------------------------------ #
def gerar_malha():
    coords = carregar_coordenadas("cidades.csv")
    g = Grafo().ler_arquivo("grafo.txt")
    n = g.numero_vertices(); m = g.numero_arestas()
    fig, ax = plt.subplots(figsize=(11, 8.5))
    for u, v, _ in g._lista_arestas():
        _, lat_u, lon_u = coords[u]; _, lat_v, lon_v = coords[v]
        ax.plot([lon_u, lon_v], [lat_u, lat_v], color=CINZA, lw=0.6, alpha=0.55, zorder=1)
    graus = {v: g.grau(v) for v in g.adjacencia}
    lons = [coords[v][2] for v in g.adjacencia]
    lats = [coords[v][1] for v in g.adjacencia]
    tam = [30 + graus[v] * 22 for v in g.adjacencia]
    ax.scatter(lons, lats, s=tam, c=AZUL, edgecolors="white", linewidths=0.7, zorder=2)
    for v in sorted(g.adjacencia, key=lambda v: graus[v], reverse=True)[:14]:
        ax.text(coords[v][2], coords[v][1] + 0.02, coords[v][0], fontsize=7.5,
                ha="center", va="bottom", color=TXT, zorder=3)
    ax.set_title(f"Malha modelada: {n} municipios e {m} ligacoes (tamanho do no = grau)",
                 fontsize=12.5, color=TXT, weight="bold", pad=12)
    ax.set_xlabel("Longitude", fontsize=9, color=TXT)
    ax.set_ylabel("Latitude", fontsize=9, color=TXT)
    ax.grid(True, color="#E2E8F0", lw=0.5)
    ax.set_facecolor("#FBFCFE")
    plt.tight_layout()
    plt.savefig("rede_completa.png", dpi=150, bbox_inches="tight", facecolor="white")
    plt.close()
    print("rede_completa.png gerado")


if __name__ == "__main__":
    gerar_esboco()
    if os.path.exists("cidades.csv") and os.path.exists("grafo.txt"):
        gerar_malha()
    else:
        print("cidades.csv/grafo.txt nao encontrados: rode coletar_dados.py primeiro.")
        sys.exit(0)

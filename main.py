# GrafoRotas - Roteiro de testes das funcionalidades da infraestrutura do grafo.
# Teoria dos Grafos | Bacharelado em Ciencia da Computacao
# Integrantes: Guilherme Haddad Borro - RA 10427699 | Rafael Lima - RA 10425819 | Pedro Augusto Yoshikuni - RA 10410287 | Tiago Silveira Lopes - RA 10417600
# Historico: 2026-09-02

import os
import sys
from grafo import Grafo

LINHA = "=" * 70


def secao(titulo):
    print("\n" + LINHA)
    print(titulo)
    print(LINHA)


def main():
    if not os.path.exists("grafo.txt"):
        print("ERRO: arquivo 'grafo.txt' nao encontrado.")
        print("Rode primeiro:  python3 coletar_dados.py")
        sys.exit(1)

    # 1) Leitura do arquivo -------------------------------------------------
    secao("1) LEITURA DO ARQUIVO grafo.txt")
    g = Grafo().ler_arquivo("grafo.txt")
    print(f"Grafo carregado: {g.numero_vertices()} vertices, "
          f"{g.numero_arestas()} arestas.")

    # 2) Exibicao (amostra) -------------------------------------------------
    secao("2) EXIBICAO DO GRAFO (primeiros 8 vertices)")
    print(g.exibir(limite=8))

    # 3) Conexidade ---------------------------------------------------------
    secao("3) DETERMINACAO DA CONEXIDADE")
    comps = g.componentes_conexas()
    print(f"O grafo e conexo? {'SIM' if g.eh_conexo() else 'NAO'}")
    print(f"Numero de componentes conexas: {len(comps)}")
    print(f"Tamanho das componentes: {sorted((len(c) for c in comps), reverse=True)}")

    # 4) Grafo reduzido -----------------------------------------------------
    secao("4) GRAFO REDUZIDO (componentes contraidas)")
    print(g.grafo_reduzido().exibir())

    # 5) Testes de insercao/remocao de vertice ------------------------------
    secao("5) TESTE: INSERCAO E REMOCAO DE VERTICE")
    novo_id = max(g.adjacencia) + 1
    v_ref = min(g.adjacencia)
    g.inserir_vertice(novo_id, "Cidade Teste")
    g.inserir_aresta(novo_id, v_ref, 123.4)
    print(f"Apos inserir 'Cidade Teste': {g.numero_vertices()} vertices, "
          f"{g.numero_arestas()} arestas, grau do novo = {g.grau(novo_id)}")
    g.remover_vertice(novo_id)
    print(f"Apos remover 'Cidade Teste': {g.numero_vertices()} vertices, "
          f"{g.numero_arestas()} arestas")

    # 6) Testes de insercao/remocao de aresta -------------------------------
    secao("6) TESTE: INSERCAO E REMOCAO DE ARESTA")
    ids = sorted(g.adjacencia)
    u, v = ids[0], ids[-1]
    antes = g.numero_arestas()
    g.inserir_aresta(u, v, 999.0)
    print(f"Arestas apos inserir ({u},{v}): {g.numero_arestas()} (era {antes})")
    g.remover_aresta(u, v)
    print(f"Arestas apos remover ({u},{v}): {g.numero_arestas()}")

    # 7) Gravacao -----------------------------------------------------------
    secao("7) GRAVACAO DO GRAFO EM ARQUIVO")
    g.gravar_arquivo("grafo_salvo.txt")
    print("Grafo gravado em grafo_salvo.txt")

    # 8) Estatisticas -------------------------------------------------------
    secao("8) ESTATISTICAS DA MALHA")
    graus = [g.grau(v) for v in g.adjacencia]
    print(f"Grau minimo: {min(graus)} | Grau maximo: {max(graus)} | "
          f"Grau medio: {sum(graus)/len(graus):.2f}")
    mais = max(g.adjacencia, key=lambda v: g.grau(v))
    print(f"Cidade mais conectada: {g.rotulos[mais]} ({g.grau(mais)} ligacoes)")


if __name__ == "__main__":
    main()

# GrafoRotas

Modelagem e análise de rotas rodoviárias entre municípios do estado de São Paulo
usando **Teoria dos Grafos**, dados oficiais do **IBGE** e do **OpenStreetMap**.

Projeto da disciplina de Teoria dos Grafos — Bacharelado em Ciência da Computação.

## Integrantes

- Guilherme Haddad Borro — RA 10427699
- Rafael Lima — RA 10425819
- Pedro Augusto Yoshikuni — RA 10410287
- Tiago Silveira Lopes — RA 10417600

## Descrição

Cada **vértice** é um município e cada **aresta** é a ligação entre duas cidades,
ponderada pela **distância rodoviária real** entre elas. O grafo é **não orientado
com peso na aresta** (categoria 2). O **problema central** é o caminho de menor
distância entre cidades (algoritmo de **Dijkstra**); a árvore geradora mínima é
análise complementar.

**Recorte adotado:** os municípios das **Regiões Geográficas Intermediárias de São
Paulo, Sorocaba e Campinas** (regionalização oficial do IBGE, 2017) — unidades
oficiais, contíguas e centradas na maior metrópole do país. A combinação das três
regiões resulta em **215 municípios (vértices) e 643 ligações (arestas)**,
ultrapassando o mínimo de 80 vértices exigido pelo trabalho. Para ajustar o recorte,
edite a lista `INTERMEDIARIAS_ALVO` no topo de `coletar_dados.py`.

**Fontes de dados:** IBGE (lista oficial de municípios) e OpenStreetMap
(coordenadas via Nominatim e distâncias rodoviárias reais via OSRM). A coleta é
feita pelo script `coletar_dados.py` e é totalmente reproduzível.

## Estrutura dos arquivos

| Arquivo | Descrição |
|---|---|
| `coletar_dados.py` | **Coleta os dados reais** (IBGE + OpenStreetMap) e gera `grafo.txt` e `cidades.csv` |
| `grafo.py` | Classe `Grafo` (infraestrutura: lista de adjacência, I/O, conexidade, grafo reduzido) |
| `main.py` | Roteiro de testes de todas as funcionalidades da etapa |
| `gerar_imagens.py` | Geração das figuras (esboço e malha completa) |
| `google_maps_api.py` | Integração opcional com o Google Maps (alternativa ao OSM) |
| `grafo.txt` | Arquivo de dados do grafo, gerado pela coleta (vértices + arestas ponderadas) |
| `cidades.csv` | id, nome, código IBGE, latitude e longitude de cada município (gerado pela coleta) |
| `imagens/esboco_grafo.png` | Figura conceitual da modelagem (cidades como vértices e distâncias como arestas) |
| `imagens/rede_completa.png` | Figura da malha completa modelada (todos os municípios e ligações reais) |
| `Relatorio_GrafoRotas_Parte2.docx` / `.pdf` | Relatório escrito da Parte 2 |
| `requirements.txt` | Dependências Python (`requests`, `matplotlib`) |
| `.gitignore` | Arquivos não versionados (`grafo_salvo.txt`, `__pycache__/`, `.env`) |

## Formato do `grafo.txt`

```
N                     # numero de vertices
id;nome_da_cidade     # N linhas
...
M                     # numero de arestas
id_u;id_v;peso_km     # M linhas (peso = distancia rodoviaria real, km)
```

## Como executar

```bash
pip install -r requirements.txt
python3 coletar_dados.py    # coleta IBGE + OpenStreetMap -> grafo.txt e cidades.csv
python3 main.py             # roda todos os testes da infraestrutura
python3 gerar_imagens.py    # gera esboco_grafo.png e rede_completa.png (versionadas em imagens/)
```

> A coleta (`coletar_dados.py`) faz muitas consultas a serviços gratuitos, com
> pausa entre elas, então leva alguns minutos. Rode em um ambiente com internet
> (ex.: GitHub Codespaces).

## Funcionalidades implementadas (Parte 2)

- [x] Coleta de dados reais (IBGE + OpenStreetMap)
- [x] Leitura e gravação do arquivo `grafo.txt`
- [x] Inserção e remoção de vértices
- [x] Inserção e remoção de arestas
- [x] Exibição do grafo
- [x] Determinação da conexidade (busca em profundidade)
- [x] Construção do grafo reduzido
- [x] Código modular e documentado

## Próxima etapa

- [ ] **Algoritmo de caminho mínimo (Dijkstra) — problema central**
- [ ] Árvore geradora mínima (Prim/Kruskal) — análise complementar

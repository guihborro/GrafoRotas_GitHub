# GrafoRotas - Infraestrutura do grafo (classe Grafo): lista de adjacencia, I/O do grafo.txt, conexidade e grafo reduzido.
# Teoria dos Grafos | Bacharelado em Ciencia da Computacao
# Integrantes: Guilherme Haddad Borro - RA 10427699 | Rafael Lima - RA 10425819 | Pedro Augusto Yoshikuni - RA 10410287 | Tiago Silveira Lopes - RA 10417600
# Historico: 2026-09-02 | [Autor] | versao atual

class Grafo:
    """Grafo nao orientado, ponderado nas arestas, representado por lista de
    adjacencia.

    Estruturas de dados:
      - self.rotulos: dict {id_vertice -> nome/rotulo da cidade}
      - self.adjacencia: dict {id_vertice -> {id_vizinho -> peso}}
        A adjacencia usa dicionario aninhado para permitir consulta,
        insercao e remocao de arestas em tempo medio O(1).
    """

    def __init__(self):
        self.rotulos = {}       # id_vertice -> nome da cidade
        self.adjacencia = {}    # id_vertice -> {id_vizinho: peso}

    # ------------------------------------------------------------------ #
    # Manipulacao de vertices
    # ------------------------------------------------------------------ #
    def inserir_vertice(self, id_vertice, rotulo=""):
        """Insere um novo vertice. Retorna True se inserido, False se ja existe."""
        if id_vertice in self.adjacencia:
            return False
        self.adjacencia[id_vertice] = {}
        self.rotulos[id_vertice] = rotulo
        return True

    def remover_vertice(self, id_vertice):
        """Remove um vertice e todas as arestas incidentes a ele."""
        if id_vertice not in self.adjacencia:
            return False
        # remove as referencias a este vertice nas listas dos vizinhos
        for vizinho in list(self.adjacencia[id_vertice].keys()):
            self.adjacencia[vizinho].pop(id_vertice, None)
        del self.adjacencia[id_vertice]
        self.rotulos.pop(id_vertice, None)
        return True

    # ------------------------------------------------------------------ #
    # Manipulacao de arestas
    # ------------------------------------------------------------------ #
    def inserir_aresta(self, u, v, peso):
        """Insere aresta nao orientada {u, v} com peso. Cria vertices ausentes."""
        if u not in self.adjacencia:
            self.inserir_vertice(u)
        if v not in self.adjacencia:
            self.inserir_vertice(v)
        if u == v:
            return False  # nao permite laco (self-loop)
        self.adjacencia[u][v] = peso
        self.adjacencia[v][u] = peso
        return True

    def remover_aresta(self, u, v):
        """Remove a aresta nao orientada {u, v}, se existir."""
        if u in self.adjacencia and v in self.adjacencia[u]:
            del self.adjacencia[u][v]
            del self.adjacencia[v][u]
            return True
        return False

    # ------------------------------------------------------------------ #
    # Consultas
    # ------------------------------------------------------------------ #
    def numero_vertices(self):
        return len(self.adjacencia)

    def numero_arestas(self):
        return sum(len(viz) for viz in self.adjacencia.values()) // 2

    def grau(self, id_vertice):
        """Grau do vertice (numero de arestas incidentes)."""
        return len(self.adjacencia.get(id_vertice, {}))

    # ------------------------------------------------------------------ #
    # Persistencia: leitura e gravacao do arquivo grafo.txt
    # ------------------------------------------------------------------ #
    def ler_arquivo(self, caminho="grafo.txt"):
        """Le o grafo a partir do arquivo texto (formato descrito no relatorio)."""
        self.rotulos.clear()
        self.adjacencia.clear()
        with open(caminho, "r", encoding="utf-8") as f:
            linhas = [ln.strip() for ln in f if ln.strip()]
        idx = 0
        n = int(linhas[idx]); idx += 1
        for _ in range(n):
            partes = linhas[idx].split(";"); idx += 1
            id_v = int(partes[0])
            nome = partes[1] if len(partes) > 1 else ""
            self.inserir_vertice(id_v, nome)
        m = int(linhas[idx]); idx += 1
        for _ in range(m):
            u, v, peso = linhas[idx].split(";"); idx += 1
            self.inserir_aresta(int(u), int(v), float(peso))
        return self

    def gravar_arquivo(self, caminho="grafo.txt"):
        """Grava o estado atual do grafo no arquivo texto."""
        with open(caminho, "w", encoding="utf-8") as f:
            f.write(f"{self.numero_vertices()}\n")
            for id_v in sorted(self.adjacencia):
                f.write(f"{id_v};{self.rotulos.get(id_v, '')}\n")
            arestas = self._lista_arestas()
            f.write(f"{len(arestas)}\n")
            for u, v, peso in arestas:
                f.write(f"{u};{v};{peso}\n")
        return caminho

    def _lista_arestas(self):
        """Lista de arestas unicas (u < v) como (u, v, peso)."""
        vistas = set()
        arestas = []
        for u in sorted(self.adjacencia):
            for v, peso in self.adjacencia[u].items():
                a, b = min(u, v), max(u, v)
                if (a, b) not in vistas:
                    vistas.add((a, b))
                    arestas.append((a, b, peso))
        return sorted(arestas)

    # ------------------------------------------------------------------ #
    # Exibicao
    # ------------------------------------------------------------------ #
    def exibir(self, limite=None):
        """Retorna uma representacao textual do grafo (lista de adjacencia)."""
        linhas = [f"Grafo: {self.numero_vertices()} vertices, "
                  f"{self.numero_arestas()} arestas"]
        for i, id_v in enumerate(sorted(self.adjacencia)):
            if limite is not None and i >= limite:
                linhas.append("  ...")
                break
            nome = self.rotulos.get(id_v, "")
            vizinhos = ", ".join(
                f"{self.rotulos.get(w, w)}({p} km)"
                for w, p in sorted(self.adjacencia[id_v].items())
            )
            linhas.append(f"  [{id_v}] {nome} -> {vizinhos}")
        return "\n".join(linhas)

    # ------------------------------------------------------------------ #
    # Conexidade (busca em profundidade)
    # ------------------------------------------------------------------ #
    def _dfs(self, inicio, visitados):
        """Busca em profundidade iterativa a partir de 'inicio'."""
        pilha = [inicio]
        while pilha:
            atual = pilha.pop()
            if atual in visitados:
                continue
            visitados.add(atual)
            for vizinho in self.adjacencia[atual]:
                if vizinho not in visitados:
                    pilha.append(vizinho)

    def componentes_conexas(self):
        """Retorna a lista de componentes conexas (cada uma como conjunto de ids)."""
        visitados = set()
        componentes = []
        for v in self.adjacencia:
            if v not in visitados:
                atual = set()
                self._dfs(v, atual)
                visitados |= atual
                componentes.append(atual)
        return componentes

    def eh_conexo(self):
        """True se o grafo possui uma unica componente conexa."""
        if self.numero_vertices() == 0:
            return True
        return len(self.componentes_conexas()) == 1

    # ------------------------------------------------------------------ #
    # Grafo reduzido
    # ------------------------------------------------------------------ #
    def grafo_reduzido(self):
        """Constroi o grafo reduzido: cada componente conexa vira um supervertice.

        Como o grafo e nao orientado, o grafo reduzido possui um vertice por
        componente conexa e nenhuma aresta entre supervertices (as componentes
        sao, por definicao, desconexas entre si). E util para diagnosticar se a
        malha modelada esta totalmente conectada.
        """
        reduzido = Grafo()
        for i, comp in enumerate(self.componentes_conexas()):
            exemplo = self.rotulos.get(next(iter(comp)), "")
            rotulo = f"Componente {i} ({len(comp)} cidades, ex.: {exemplo})"
            reduzido.inserir_vertice(i, rotulo)
        return reduzido

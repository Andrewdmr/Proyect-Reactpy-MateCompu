import random
import networkx as nx
import matplotlib.pyplot as plt
import io
import base64

def generar_grafo(n, probAristaNoDirigido=0.2, proAristaDirigido=0.15):
    G = nx.DiGraph()
    letras = [chr(65 + i) for i in range(n)]
    G.add_nodes_from(letras)
    
    # Aristas no dirigidos
    for i in range(n):
        for j in range(i + 1, n):
            if random.random() < probAristaNoDirigido:
                G.add_edge(letras[i], letras[j])
                G.add_edge(letras[j], letras[i])
    
    # Aristas dirigidos
    for i in range(n):
        for j in range(n):
            if i != j and random.random() < proAristaDirigido:
                if not G.has_edge(letras[i], letras[j]):
                    G.add_edge(letras[i], letras[j])
    return G

def dibujo_grafo_base64(G):
    """Convierte el grafo a imagen base64 para mostrarlo en la web"""
    plt.figure(figsize=(8, 6))
    pos = nx.spring_layout(G, k=3, iterations=50, seed=42)
    
    nx.draw(G, pos, with_labels=True, node_color='skyblue',
            node_size=800, edge_color='black', arrows=True,
            arrowsize=20, arrowstyle='->', font_size=12, font_weight='bold')
    plt.title("Grafo Generado", fontsize=16)
    plt.axis('off')
    
    # Convertir a base64
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.getvalue()).decode()
    plt.close()
    
    return f"data:image/png;base64,{image_base64}"

def graficar_componentes_base64(G, componentes):
    """Convierte cada componente a imagen base64"""
    imagenes_componentes = []
    
    for i, comp in enumerate(componentes, 1):
        subG = G.subgraph(comp).copy()
        
        plt.figure(figsize=(6, 3))
        pos = nx.spring_layout(subG, seed=42)
        nx.draw(subG, pos, with_labels=True, node_color='lightgreen',
                node_size=600, edge_color='black', arrows=True,
                arrowsize=20, arrowstyle='->', font_size=10, font_weight='bold')
        plt.title(f"Componente {i}: {comp}", fontsize=12)
        plt.axis('off')
        
        # Convertir a base64
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue()).decode()
        plt.close()
        
        imagenes_componentes.append({
            'numero': i,
            'nodos': comp,
            'imagen': f"data:image/png;base64,{image_base64}"
        })
    
    return imagenes_componentes

def componentes_por_matriz(matriz, nodos):
    n = len(nodos)
    visitados = set()
    componentes = []

    for i in range(n):
        if nodos[i] not in visitados:
            comp = {nodos[i]}
            cambios = True
            while cambios:
                cambios = False
                for j in range(n):
                    if nodos[j] not in comp:
                        #Si hay conexion mutua (1 en ambos sentidos)
                        if any((matriz[a_idx][j] == 1 and matriz[j][a_idx] == 1)
                               for a_idx, a in enumerate(nodos) if a in comp):
                            comp.add(nodos[j])
                            cambios = True
            visitados |= comp
            componentes.append(sorted(list(comp)))

    return componentes

def procesar_pasos_completos(matriz_adyacencia, nodos, G):
    """Ejecuta todos los pasos del algoritmo y retorna los resultados"""
    n = len(nodos)
    matriz = [fila.copy() for fila in matriz_adyacencia]
    resultados = {
        'original': {'matriz': [fila.copy() for fila in matriz], 'nodos': nodos.copy()},
        'paso1': None,
        'paso2': None,
        'paso3': None,
        'paso4': None,
        'componentes': None,
        'grafo_original': G
    }
    
    # PASO 1: Unos diagonales
    print("PASO 1: Poner unos diagonales")
    for i in range(n):
        matriz[i][i] = 1
    resultados['paso1'] = {'matriz': [fila.copy() for fila in matriz], 'nodos': nodos.copy()}
    
    # PASO 2: Matriz de caminos
    print("PASO 2: Hallar matriz de caminos")
    for fila in range(n):
        while 1 in matriz[fila]:
            for columna in range(n):
                if matriz[fila][columna] == 1:
                    count = 0
                    for unos in matriz[columna]:
                        if unos == 1 and matriz[fila][count] != 2:
                            matriz[fila][count] = 1
                        count += 1
                    matriz[fila][columna] = 2
        for columna in range(n):
            if matriz[fila][columna] == 2:
                matriz[fila][columna] = 1
    resultados['paso2'] = {'matriz': [fila.copy() for fila in matriz], 'nodos': nodos.copy()}
    
    # PASO 3: Ordenar filas
    print("PASO 3: Ordenar filas")
    nodos_originales = nodos.copy()
    matriz_original_p3 = [fila.copy() for fila in matriz]
    
    for i in range(n):
        for j in range(i + 1, n):
            count_i = matriz[i].count(1)
            count_j = matriz[j].count(1)
            if count_i < count_j:
                #intercambiar filas y nodos
                matriz[i], matriz[j] = matriz[j], matriz[i]
                nodos[i], nodos[j] = nodos[j], nodos[i]
            elif count_i == count_j and nodos[i] > nodos[j]:  #en caso de empate de 1s se ordena de acuerdo al orden
               #intercambiar filas y nodos
                matriz[i], matriz[j] = matriz[j], matriz[i]
                nodos[i], nodos[j] = nodos[j], nodos[i]
    resultados['paso3'] = {'matriz': [fila.copy() for fila in matriz], 'nodos': nodos.copy(), 'colum_original':nodos_originales.copy() }
    
    # PASO 4: Ordenar columnas
    print("PASO 4: Ordenar columnas")
    matriz_original_p4 = [fila.copy() for fila in matriz]
    
    for i in range(n):
        for j in range(n):
            nodo_actual = nodos[j]
            pos_original = nodos_originales.index(nodo_actual)
            for fila in range(n):
                matriz[fila][j] = matriz_original_p4[fila][pos_original]
    resultados['paso4'] = {'matriz': [fila.copy() for fila in matriz], 'nodos': nodos.copy()}
    
    componentes = componentes_por_matriz(matriz, nodos)
    resultados['componentes'] = componentes
    
    #indetificar bloques del paso 4
    bloques_paso4 = identificar_bloques_matriz(matriz, nodos, componentes)
    resultados['bloques_paso4'] = bloques_paso4
    
    resultados['imagenes_componentes'] = graficar_componentes_base64(G, componentes)
    
    return resultados

#para los bloques de la matriz del paso 4
def identificar_bloques_matriz(matriz, nodos, componentes):
    """Identifica las posiciones de los bloques de componentes en la matriz"""
    bloques = []
    
    for componente in componentes:
        # Encontrar los indices de los nodos de esta componente
        indices = [nodos.index(nodo) for nodo in componente]
        
        if indices:
            # Crear bloque con las coordenadas del rectangulo
            bloque = {
                'fila_inicio': min(indices),
                'fila_fin': max(indices),
                'columna_inicio': min(indices),
                'columna_fin': max(indices),
                'nodos': componente
            }
            bloques.append(bloque)
    
    return bloques
from reactpy import component, html, hooks
import networkx as nx

@component
def MatrizTabla(matriz, nodos, titulo="", bloques=None):
    def crear_celda(fila_idx, col_idx, valor):
        # Verificar si esta celda pertenece a algun bloque
        es_borde_superior = False
        es_borde_inferior = False
        es_borde_izquierdo = False
        es_borde_derecho = False
        
        if bloques:
            for bloque in bloques:
                if (bloque['fila_inicio'] <= fila_idx <= bloque['fila_fin'] and 
                    bloque['columna_inicio'] <= col_idx <= bloque['columna_fin']):
                    
                    # Verificar bordes del bloque
                    if fila_idx == bloque['fila_inicio']:
                        es_borde_superior = True
                    if fila_idx == bloque['fila_fin']:
                        es_borde_inferior = True
                    if col_idx == bloque['columna_inicio']:
                        es_borde_izquierdo = True
                    if col_idx == bloque['columna_fin']:
                        es_borde_derecho = True
                    break
        
        #css para los bordes del bloque
        estilo_bordes = []
        if es_borde_superior:
            estilo_bordes.append("border-top: 3px solid #e74c3c")
        if es_borde_inferior:
            estilo_bordes.append("border-bottom: 3px solid #e74c3c")
        if es_borde_izquierdo:
            estilo_bordes.append("border-left: 3px solid #e74c3c")
        if es_borde_derecho:
            estilo_bordes.append("border-right: 3px solid #e74c3c")
        
        estilo = "; ".join(estilo_bordes)
        
        return html.td({
            "class_name": "celda",
            "style": estilo + ("; background-color: #f8f9fa" if any([es_borde_superior, es_borde_inferior, es_borde_izquierdo, es_borde_derecho]) else "")
        }, str(valor))
    
    #antes hasta aqui
    return html.div({"class_name": "matriz-container"},
        html.h3(titulo) if titulo else None,
        html.table({"class_name": "matriz-table"},
            html.thead(
                html.tr(
                    html.th(""),
                    [html.th(nodo) for nodo in nodos]
                )
            ),
            html.tbody(
                [
                    html.tr(
                        html.th(nodos[i]),
                        [crear_celda(i, j, valor) for j, valor in enumerate(fila)]
                    )
                    for i, fila in enumerate(matriz)
                ]
            )
        )
    )
@component
def ComponentesLista(componentes):
    return html.div({"class_name": "componentes-container"},
        html.h3("Componentes Conexas"),
        html.ul(
            [
                html.li(
                    {"key": i},
                    f"V{i+1}: {comp}"
                )
                for i, comp in enumerate(componentes)
            ]
        ),
        html.p(f"Número total de componentes conexas: {len(componentes)}")
    )

@component
def ComponentesGraficas(imagenes_componentes):
    return html.div({"class_name": "componentes-graficas"},
        html.h3("Gráficas de las Componentes Conexas"),
        html.div(
            [
                html.div(
                    {"key": comp['numero'], "class_name": "componente-item"},
                    html.h4(f"Componente {comp['numero']}: {comp['nodos']}"),
                    html.img({
                        "src": comp['imagen'], 
                        "alt": f"Componente {comp['numero']}",
                        "class_name": "componente-img"
                    })
                )
                for comp in imagenes_componentes
            ]
        )
    )

@component
def GrafoInput():
    n, set_n = hooks.use_state(6)
    opcion, set_opcion = hooks.use_state("2")
    matriz_manual, set_matriz_manual = hooks.use_state([])
    resultados, set_resultados = hooks.use_state(None)
    grafo_image, set_grafo_image = hooks.use_state(None)
    loading, set_loading = hooks.use_state(False)
    
    from grafo_logic import generar_grafo, dibujo_grafo_base64, procesar_pasos_completos
    
    def handle_generar_grafo(event):
        set_loading(True)
        try:
            if opcion == "2":  # Grafo automatico
                G = generar_grafo(n)
                nodos = list(G.nodes())
                matriz_adyacencia = nx.to_numpy_array(G, nodelist=nodos, dtype=int).tolist()
                
                # Generar imagen del grafo
                imagen = dibujo_grafo_base64(G)
                set_grafo_image(imagen)
                
                # Procesar pasos completos
                resultados = procesar_pasos_completos(matriz_adyacencia, nodos, G)
                set_resultados(resultados)
                
            else:  # Grafo manual
                if matriz_manual:
                    nodos = [chr(65 + i) for i in range(len(matriz_manual))]
                    G = nx.DiGraph()
                    G.add_nodes_from(nodos)
                    for i in range(len(matriz_manual)):
                        for j in range(len(matriz_manual)):
                            if matriz_manual[i][j] == 1:
                                G.add_edge(nodos[i], nodos[j])
                    
                    imagen = dibujo_grafo_base64(G)
                    set_grafo_image(imagen)
                    
                    resultados = procesar_pasos_completos(matriz_manual, nodos, G)
                    set_resultados(resultados)
                    
        except Exception as e:
            print(f"Error: {e}")
        finally:
            set_loading(False)
    
    def handle_matriz_manual_change(fila, columna, valor):
        nueva_matriz = [fila.copy() for fila in matriz_manual]
        nueva_matriz[fila][columna] = 1 if valor else 0
        set_matriz_manual(nueva_matriz)
    
    def inicializar_matriz_manual():
        nueva_matriz = [[0 for _ in range(n)] for _ in range(n)]
        set_matriz_manual(nueva_matriz)
    
    # Efecto para inicializar matriz manual cuando cambia n u opcion
    hooks.use_effect(inicializar_matriz_manual, [n, opcion])
    
    return html.div({"class_name": "grafo-app"},
        html.h1("COMPONENTES CONEXAS DE UN GRAFO"),
        
        # Selección de opciones
        html.div({"class_name": "config-panel"},
            html.h2("Configuración del Grafo"),
            
            html.div({"class_name": "form-group"},
                html.label("Tipo de grafo:"),
                html.select({
                    "value": opcion,
                    "on_change": lambda e: set_opcion(e["target"]["value"])
                },
                    html.option({"value": "1"}, "Ingresar matriz manualmente"),
                    html.option({"value": "2"}, "Generar grafo aleatorio")
                )
            ),
            
            html.div({"class_name": "form-group"},
                html.label("Número de nodos (6-12):"),
                html.input({
                    "type": "number",
                    "value": n,
                    "on_change": lambda e: set_n(max(6, min(12, int(e["target"]["value"] or 6)))),
                    "min": "6",
                    "max": "12"
                })
            ),
            
            # Matriz manual input
            html.div(
                {"class_name": "matriz-input-container", "style": {"display": "block" if opcion == "1" else "none"}},
                html.h3("Matriz de Adyacencia Manual"),
                html.p("Selecciona las conexiones:"),
                html.table({"class_name": "matriz-input-table"},
                    html.thead(
                        html.tr(
                            html.th(""),
                            [html.th(chr(65 + j)) for j in range(n)]
                        )
                    ),
                    html.tbody(
                        [
                            html.tr(
                                html.th({"class_name": "fila-label"}, chr(65 + i)),
                                [
                                    html.td(
                                        html.input({
                                            "type": "checkbox",
                                            "checked": bool(matriz_manual[i][j] if matriz_manual and i < len(matriz_manual) and j < len(matriz_manual[i]) else False),
                                            "on_change": lambda e, i=i, j=j: handle_matriz_manual_change(i, j, e["target"]["checked"])
                                        })
                                    ) for j in range(n)
                                ]
                            ) for i in range(n)
                        ]
                    )
                )
            ) if opcion == "1" else None,
            
            html.button({
                "on_click": handle_generar_grafo,
                "disabled": loading,
                "class_name": "generate-btn"
            }, "Generar Grafo" if not loading else "Generando...")
        ),
        
        # Resultados
        html.div({"class_name": "results-panel"},
            grafo_image and html.div({"class_name": "grafo-image"},
                html.img({"src": grafo_image, "alt": "Grafo", "class_name": "main-grafo-img"})
            ),
            
            resultados and html.div({"class_name": "analisis-resultados"},
                
                MatrizTabla(
                    resultados['original']['matriz'],
                    resultados['original']['nodos'],
                    "Matriz de Adyacencia Original"
                ),
                
                MatrizTabla(
                    resultados['paso1']['matriz'],
                    resultados['paso1']['nodos'],
                    "Paso 1: Unos Diagonales"
                ),
                
                MatrizTabla(
                    resultados['paso2']['matriz'],
                    resultados['paso2']['nodos'],
                    "Paso 2: Matriz de Caminos"
                ),
                
                MatrizTabla(
                    resultados['paso3']['matriz'],
                    resultados['paso3']['nodos'],
                    "Paso 3: Ordenar Filas"
                ),
                
                MatrizTabla(
                    resultados['paso4']['matriz'],
                    resultados['paso4']['nodos'],
                    "Paso 4: Ordenar Columnas",
                    bloques=resultados.get('bloques_paso4') 
                ),
                
                ComponentesLista(resultados['componentes']),
                
                resultados['imagenes_componentes'] and ComponentesGraficas(resultados['imagenes_componentes'])
            )
        )
    )
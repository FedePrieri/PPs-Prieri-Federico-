import csv
from tkinter import *
from tkinter import ttk,messagebox
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import time

#SIMULADOR  SIMULADOR  SIMULADOR

class Grafo:
    def __init__(self):
      self.nombre_producto="ProdA"
      self.numero_linea=0
      self.lista_narrados=[]
      self.n_segundos=0
      self.G=nx.Graph()

    def elegir_producto(self,nombre_elegido,ax,canvas):
        self.nombre_producto=nombre_elegido
        self.G.clear()
        print("La lista de nodos es:")
        print(self.lista_nodos())
        self.cargar_grafo()
        self.actualizar(ax,canvas)
    
    def lista_nodos(self):
        return list(self.G.nodes)
    
    def actualizar(self,ax,canvas):
        ax.clear()

        for i, layer in enumerate(nx.topological_generations(self.G)):
            for n in layer:
              self.G.nodes[n]["layer"] = i
        pos = nx.multipartite_layout(self.G, subset_key="layer", align="horizontal")
        for k in pos:
            pos[k][-1] *= -1

        color_map = []
        for node in self.G:
            if self.G.nodes[node]['tipo']=='MP':
                color_map.append('lime')
            else:
                color_map.append("deepskyblue")

        options = {
        "font_size": 10,
        "node_size": 1200,
        #"node_height":80,
        #"node_width":40,
        "node_shape":"o",
        #"node_color": "red",
        "alpha":0.8,
        "font_weight":"bold",
        "edgecolors": "blue",
        "linewidths": 0.5,
        "width": 1,
        }
        #plt.figure()
        nx.draw(self.G, pos=pos,node_color=color_map, with_labels=True,**options)
        canvas.draw()
    
    def tiempo_espera(self,tiempo):
        tiempo=int(tiempo)
        self.n_segundos += tiempo
        m, s = divmod(self.n_segundos, 60)
        min_sec_format = '{:02d}:{:02d}'.format(m, s)
        #print(min_sec_format, end="  ")
        return [tiempo,min_sec_format]
        
    def narrar(self,nodo):
        predecesor=list(self.G.predecessors(nodo))[0]

        if(self.G.nodes[nodo]['tipo'] =='MP'):
            frase="Envio la "+ nodo + " a la estación Nº:"+ str( self.G.nodes[predecesor]['n_estacion'])
            tiempo=self.tiempo_espera(self.G.nodes[nodo]['t_almacen'])
            self.lista_narrados.append([frase,tiempo[0],tiempo[1]])

        if(self.G.nodes[nodo]['tipo'] =='P'):            
            frase="Realizo la "+str( self.G.nodes[nodo]['operacion'])+" y envio el "+ nodo +" a la estación Nº:"+ str(self.G.nodes[predecesor]['n_estacion'])
            tiempo=self.tiempo_espera(self.G.nodes[nodo]['t_procesado'])
            self.lista_narrados.append([frase,tiempo[0],tiempo[1]])

            if(self.G.nodes[predecesor]['n_estacion']==100):
                frase="Producto terminado"
                tiempo=["0","00:00"]
                self.lista_narrados.append([frase,tiempo[0],tiempo[1]])
                self.n_segundos=0
    
    def lista_de_narrados(self):
        return self.lista_narrados
    
    def borrar_lista_narrados(self):
        self.lista_narrados.clear()

    def cargar_grafo(self):
        lista_lineas=Archivo_csv("BD Grafos.csv").armar_lista()
        for row in lista_lineas:
            if row[0]==self.nombre_producto:
                aristas_nodos=[None] * int(0.5*len(row))
                for j in range(0,-1+len(row),2):
                    aristas_nodos[int(j/2)]=(row[j],row[j+1])
        self.G= nx.from_edgelist(aristas_nodos, create_using=nx.DiGraph)
        lista_nodos=list(self.G.nodes)
        for nodo in lista_nodos:
            if nodo==lista_nodos[0]:
                self.G.add_node(nodo, tipo='P', n_estacion=100,operacion='exibir')
            else:
                if nodo[0]+nodo[1]+nodo[2]+nodo[3]=="SubP":
                    lista_lineas=Archivo_csv("BD SubProductos.csv").armar_lista()
                    for row in lista_lineas:
                        if row[0]==nodo:
                            self.G.add_node(nodo, tipo='P',operacion=row[1],n_estacion=row[2],t_procesado=row[3],t_estacion=row[4])
                else:
                    lista_lineas=Archivo_csv("BD Materias Primas.csv").armar_lista()
                    for row in lista_lineas:
                        if row[0]==nodo:
                            self.G.add_node(nodo, tipo='MP',n_almacen=row[1],t_almacen=row[2])
          
    def estrctura_recorrido2(self,n_de_partida):
        list(self.G.predecessors(n_de_partida))
        precedente=list(self.G.predecessors(n_de_partida))[0]
        self.narrar(n_de_partida)
        sucesores=list(self.G.successors(precedente))
        for i in sucesores:
            if (i!=n_de_partida):
                T = nx.dfs_tree(self.G, i)
                camino_mas_largo=nx.dag_longest_path(T)

                if( len(camino_mas_largo)==2):
                    for k in list(self.G.successors(i)):
                        self.narrar(k)

                if( len(camino_mas_largo) > 2):
                    elemento_final2=camino_mas_largo[-1+len(camino_mas_largo)]
                    for j in list(self.G.successors( list(self.G.predecessors(elemento_final2))[0] )) :
                        #print("Envio-- "+ j)
                        self.narrar(j)

                T.clear()
                self.narrar(i)
    
    def estrctura_recorrido(self,n_de_partida):
        list(self.G.predecessors(n_de_partida))
        precedente=list(self.G.predecessors(n_de_partida))[0]
        self.narrar(n_de_partida)
        sucesores=list(self.G.successors(precedente))
        for i in sucesores:
            if (i!=n_de_partida):
                T = nx.dfs_tree(self.G, i)
                camino_mas_largo=nx.dag_longest_path(T)

                if( len(camino_mas_largo)==2):
                    for k in list(self.G.successors(i)):
                        self.narrar(k)

                if( len(camino_mas_largo) > 2):
                    elemento_final=camino_mas_largo[-1+len(camino_mas_largo)]
                    for j in list(self.G.successors( list(self.G.predecessors(elemento_final))[0] )) :
                        self.narrar(j)
                    self.estrctura_recorrido2( list(self.G.predecessors(elemento_final))[0] )

                T.clear()
                self.narrar(i)

    def ejecutar_grafo(self):
        caminito_mas_largo=nx.dag_longest_path(self.G)
        for n in range(len(caminito_mas_largo)-1,0,-1):
            self.estrctura_recorrido(caminito_mas_largo[n])
   

grafo=Grafo()

class VentanaPrincipal(Tk):
    def __init__(self):
        super().__init__()
        self.config(width=400, height=300)
        self.title("Simulador de Grafo")

        grafo.cargar_grafo()
        self.fig,self.ax = plt.subplots()
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)

        self.canvas.get_tk_widget().config(width=800,height=400)
        self.canvas.get_tk_widget().place(x=350, y=250)

        menu=Menu(self)
        self.config(menu=menu)
        self.title("Visualizador de Grafo")
        File= Menu(menu, tearoff=0)

        submenu = Menu(File, tearoff=False)
        productos_elegibles=Archivo_csv("BD Grafos.csv").armar_lista_1er_columna()
        for i in range(len(productos_elegibles)):
           submenu.add_command(label=productos_elegibles[i],command=lambda i=i: grafo.elegir_producto(productos_elegibles[i],self.ax,self.canvas)) 

        File.add_cascade(label='Productos', menu=submenu)

        File.add_separator()
        File.add_command(label="Exit")

        Edit=Menu(menu,tearoff=0)
        Help=Menu(menu,tearoff=0)

        menu.add_cascade(label="File",menu=File)
        menu.add_cascade(label="Edit",menu=Edit)
        menu.add_cascade(label="Help",menu=Help)

        self.caja_texto = Text(self)
        self.scrollbar = Scrollbar(orient=VERTICAL, command=self.caja_texto.yview)
        self.scrollbar.place(x=890, y=10, height=180)

        self.caja_texto.configure(width=100, height=10,yscrollcommand=self.scrollbar.set)
        self.caja_texto.place(x=20, y=40)
        self.boton_agregar_linea = Button(self, text="Correr simulacion", command=self.correr_simulacion)
        self.boton_agregar_linea.place(x=950, y=60)

        grafo.actualizar(self.ax,self.canvas)

    def mostrar_narrados(self):
        j=0
        lista=grafo.lista_de_narrados()
        self.actualizar_caja_texto(j,lista)
    
    def actualizar_caja_texto(self,i,lista):
        self.agregar_linea("----------")
        #print(i)
        if i < len(lista):
            if i==0 :
                self.agregar_linea("00:00" + "  " + lista[i][0])
                i=i+1
                self.after(1000*lista[0][1],self.actualizar_caja_texto,i,lista)
            else :
                self.agregar_linea(lista[i-1][2]+ "  " + lista[i][0])
                i=i+1
                self.after(1000*lista[i-1][1],self.actualizar_caja_texto,i,lista) 
            
    def correr_simulacion(self):
        grafo.borrar_lista_narrados()
        grafo.cargar_grafo()
        grafo.ejecutar_grafo()
        self.mostrar_narrados()
    
    def agregar_linea(self,contenido):
        self.caja_texto.configure(state='normal')
        self.caja_texto.insert(END,contenido)
        self.caja_texto.insert(END,"\n")
        self.caja_texto.configure(state='disabled')
        self.caja_texto.see(index=END)

class Archivo_csv:
    def __init__(self,nombre):
        self.nombre=nombre
    
    def armar_lista(self):
        with open(self.nombre) as File:
            reader = csv.reader(File, delimiter=',', quotechar=',',quoting=csv.QUOTE_MINIMAL)
            filas = list(reader)
            return filas
    
    def armar_lista_1er_columna(self):
        filas = self.armar_lista()
        del filas[0]
        cantidad_filas=sum(1 for fila in filas)
        elementos=[None] * cantidad_filas
        l=0
        for row in filas:
            elementos[l]=row[0]
            l=l+1 
        return elementos
            
ventana_principal=VentanaPrincipal()

ventana_principal.mainloop()
import csv
from tkinter import *
from tkinter import ttk,messagebox
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class Grafo:
    def __init__(self):
      self.nombre_producto="ProdA"
      self.numero_linea=0
      self.existe_el_nombre= False

    def elegir_producto(self,nombre_elegido,ax,canvas):
        self.nombre_producto=nombre_elegido
        self.existe_el_nombre=True
        self.cargar()
        self.actualizar(ax,canvas)
    
    def nuevo_producto(self,nombre):
        self.G.clear()
        self.G.add_node("Prod"+ nombre)
        posicion_nombre=self.ubicacion_producto_nuevo("Prod"+ nombre,Archivo_csv('BD Grafos.csv').armar_lista_1er_columna())
        if self.existe_el_nombre==True:
            print("El nombre ya existe"+str(posicion_nombre))
            messagebox.showerror("Error", "El nombre ya existe. Ingresa uno nuevo")
            self.existe_el_nombre=False
            VentanaSecundariaNuevoProducto()
        else:
            self.numero_linea=posicion_nombre + 1
            self.asignar_tipo_nodo("Prod"+ nombre)
            self.actualizar(ventana_principal.ax,ventana_principal.canvas)

    def ubicacion_producto_nuevo(self,nombre_propuesto,lista_productos):
        i=0
        ubicacion_correspondiente=0
        del lista_productos[0]
        for nombre_producto in lista_productos:
            if nombre_propuesto==nombre_producto:
                self.existe_el_nombre=True
            else:
                if nombre_propuesto > nombre_producto:
                    i=i+1
                    ubicacion_correspondiente=i
                else:
                    ubicacion_correspondiente=i
        print("Ubicacion es"+ str(ubicacion_correspondiente+1))
        return ubicacion_correspondiente+1

    def cargar(self):
        lista_lineas=Archivo_csv("BD Grafos.csv").armar_lista()
        k=0
        for row in lista_lineas:
            if row[0]==self.nombre_producto:
                self.numero_linea=k
                aristas_nodos=[None] * int(0.5*len(row))
                for j in range(0,-1+len(row),2):
                    aristas_nodos[int(j/2)]=(row[j],row[j+1])
            k=k+1
        self.G= nx.from_edgelist(aristas_nodos, create_using=nx.DiGraph)
        lista_nodos=list(self.G.nodes)
        for nodo in lista_nodos:
            self.asignar_tipo_nodo(nodo)

    def asignar_tipo_nodo(self,nodo):
            if nodo[0]+nodo[1]+nodo[2]+nodo[3]=="Prod":
                self.G.add_node(nodo, tipo='P', n_estacion=100,operacion='Exhibir')
            else:
                if nodo[0]+nodo[1]+nodo[2]+nodo[3]=="SubP":
                    lista_lineas=Archivo_csv("BD SubProductos.csv").armar_lista()
                    for row in lista_lineas:
                        if row[0]==nodo:
                            #print(row[0][0:12])
                            self.G.add_node(nodo, tipo='P',operacion=row[1],n_estacion=row[2],t_procesado=row[3],t_estacion=row[4])
                else:
                    lista_lineas=Archivo_csv("BD Materias Primas.csv").armar_lista()
                    for row in lista_lineas:
                        if row[0]==nodo:
                            self.G.add_node(nodo, tipo='MP',n_almacen=row[1],t_almacen=row[2])

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
        
        pos_attrs = {}
        for node, coords in pos.items():
            pos_attrs[node] = (coords[0], coords[1] - 0.12)

        node_attrs = nx.get_node_attributes(self.G, 'operacion')
        custom_node_attrs = {}
        for node, attr in node_attrs.items():
            custom_node_attrs[node] = " (" + attr + ")"  

        nx.draw_networkx_labels(self.G, pos_attrs,font_size=10, labels=custom_node_attrs)
        
        canvas.draw()

    def agregar_nodo(self,nuevo_nodo,nodo_enganche):
        nodo_posterior=nuevo_nodo
        self.asignar_tipo_nodo(nodo_posterior)
        if nodo_posterior:
                self.G.add_node(nodo_posterior)
                self.G.add_edge(nodo_enganche, nodo_posterior)
        self.actualizar(ventana_principal.ax,ventana_principal.canvas)

    def borrar_nodo(self,nodo):
        rama_borrar=self.determinar_rama(nodo)
        print(rama_borrar)
        self.G.remove_node(nodo)
        for elemento in rama_borrar:
            self.G.remove_node(elemento)

        self.actualizar(ventana_principal.ax,ventana_principal.canvas)
        print(list(self.G.nodes))
    
    def determinar_rama(self,nodo_partida):
        posicion_de_partida=0
        sucesores=list(self.G.successors(nodo_partida))
        for k in range(20):
            for i in range(posicion_de_partida,len(sucesores)):
                sucesores=sucesores + list(self.G.successors(sucesores[i]))
                posicion_de_partida=posicion_de_partida + 1
        return sucesores

    def modificar_archivo(self):
        grafo_modificado=[None] *2* self.G.number_of_edges()
        i=0
        for line in nx.generate_edgelist(self.G, data=False) :
            par_de_numeros= line.split()
            grafo_modificado[i]=par_de_numeros[0]
            grafo_modificado[i+1]=par_de_numeros[1]
            i=i+2
        filas=Archivo_csv('BD Grafos.csv').armar_lista()
        if self.existe_el_nombre==True:
            del filas[self.numero_linea]
        filas.insert(self.numero_linea, grafo_modificado)
        print("Numero de linea otra ves "+ str(self.numero_linea))
        print("Grafo modificado")
        print(grafo_modificado)
                
        with open("BD Grafos.csv", 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerows(filas)
                file.close()
   
    def subproductos_utilizados(self,lista_nodos):
        subproductos=[]
        subproductos.append(lista_nodos[0] )
        for elemento in lista_nodos:
            if elemento[:4]=="SubP":
               subproductos.append(elemento)
        return subproductos
    
    def subp_operaciones_utilizadas(self,lista):
        lista_modificada=lista
        for i in range(len(lista)):
            lista_modificada[i]=lista[i]+" / "+self.G.nodes[lista[i]]['operacion']
        return lista_modificada

    def subp_correspondiente(self,subp_operacion):
        lista=Archivo_csv("BD SubProductos.csv").armar_lista_1er_columna()
        subp_buscado="cualquiera"
        if subp_operacion[0:4]=="Prod":
            subp_buscado=subp_operacion[0:5]
        for row in lista:
            if row==subp_operacion[0:5]:
                subp_buscado=row
        return subp_buscado

grafo=Grafo()


class VentanaPrincipal(Tk):
    def __init__(self):
        super().__init__()
        self.config(width=400, height=300)
        self.title("Visualizador de Grafo")

        grafo.cargar()
        self.fig,self.ax = plt.subplots()
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=1)

        menu=Menu(self)
        self.config(menu=menu)
        self.title("Editor de Productos")
        File= Menu(menu, tearoff=0)

        File.add_command(label="Nuevo Producto",command=VentanaSecundariaNuevoProducto)

        File.add_command(label="Guardar",command=grafo.modificar_archivo)

        submenu = Menu(File, tearoff=False)
        productos_elegibles=Archivo_csv("BD Grafos.csv").armar_lista_1er_columna()
        for i in range(len(productos_elegibles)):
           submenu.add_command(label=productos_elegibles[i],command=lambda i=i: grafo.elegir_producto(productos_elegibles[i],self.ax,self.canvas)) 

        File.add_cascade(label='Elegir Producto', menu=submenu)

        Edit=Menu(menu,tearoff=0)

        Edit.add_command(label="Borrar nodo",command=VentanaSecundariaBorrar)
        Edit.add_command(label="Insertar SubProducto",command=lambda:VentanaSecundariaInsertar("Subproducto"))
        Edit.add_command(label="Isertar Materias Primas ",command=lambda:VentanaSecundariaInsertar("Materia Prima"))

        menu.add_cascade(label="Archivo",menu=File)
        menu.add_cascade(label="Edición",menu=Edit)

        grafo.actualizar(self.ax,self.canvas)


class VentanaSecundariaInsertar(Toplevel):

    def __init__(self,materia_prima_o_subproducto):
        super().__init__()
    
        self.materia_prima_o_subproducto=materia_prima_o_subproducto
        lista_nodos=grafo.lista_nodos()

        if self.materia_prima_o_subproducto=="Materia Prima":
           self.title("Insertar Materia Prima")
           archivo1=Archivo_csv("BD Materias Primas.csv")
           lista_combobox_nodo_nuevo=archivo1.armar_lista_1er_columna()
        else:
           self.title("Insertar SubProducto")
           archivo1=Archivo_csv("BD SubProductos.csv")
           lista_combobox_nodo_nuevo=archivo1.armar_lista_subp_operaciones()

        lista_combobox_nodo_existente=grafo.subp_operaciones_utilizadas(grafo.subproductos_utilizados(lista_nodos))

        self.config(width=300,height=150)
    
        self.combo_nodo_existente =ttk.Combobox(self, state="readonly",values=lista_combobox_nodo_existente)   
        self.combo_nodo_existente.place(x=50, y=50)

        self.combo_nodo_nuevo =ttk.Combobox(self, state="readonly",values=lista_combobox_nodo_nuevo)   
        self.combo_nodo_nuevo.place(x=50, y=80)

        if self.materia_prima_o_subproducto=="Materia Prima":
            boton_agregar_nodo = Button(self,text="Agregar nodo", command=lambda: [grafo.agregar_nodo( self.combo_nodo_nuevo.get() ,grafo.subp_correspondiente(self.combo_nodo_existente.get())),self.actualizar_combo()])        
        else:           
            boton_agregar_nodo = Button(self,text="Agregar nodo", command=lambda: [grafo.agregar_nodo( grafo.subp_correspondiente(self.combo_nodo_nuevo.get()) ,grafo.subp_correspondiente(self.combo_nodo_existente.get())),self.actualizar_combo()])
        
        boton_agregar_nodo.place(x=200, y=60)

        self.focus()
        self.grab_set()

    def actualizar_combo(self):
        nueva_lista_combobox=grafo.subproductos_utilizados(grafo.lista_nodos())
        self.combo_nodo_existente['values'] =nueva_lista_combobox

class VentanaSecundariaBorrar(Toplevel):

    def __init__(self):
        super().__init__()
    
        lista_combobox_nodo=grafo.lista_nodos()

        self.title("Ventana secundaria")
        self.config(width=300,height=150)

        self.combo_nodo =ttk.Combobox(self, state="readonly",values=lista_combobox_nodo)   
        self.combo_nodo.place(x=50, y=80)

        boton_agregar_nodo = Button(self,text="Eliminar", command=lambda: [grafo.borrar_nodo(self.combo_nodo.get()),self.actualizar_combo()])
        boton_agregar_nodo.place(x=200, y=80)

        self.focus()
        self.grab_set()
    
    def actualizar_combo(self):
        nueva_lista_combobox_nodo=grafo.lista_nodos()
        self.combo_nodo['values'] =nueva_lista_combobox_nodo


class VentanaSecundariaNuevoProducto(Toplevel):

    def __init__(self):
        super().__init__()
    
        self.title("Ventana secundaria")
        self.config(width=300,height=150)

        self.caja_texto = Entry(self)
        self.caja_texto.place(x=50, y=30)
    
        boton_cancelar=Button(self,text="Cancelar",command=self.destroy)
        boton_cancelar.place(x=200,y=70)

        boton_aceptar = Button(self,text="Aceptar", command=self.aceptar)
        boton_aceptar.place(x=100, y=70)

        self.focus()
        self.grab_set()

    def aceptar(self):
        palabra = self.caja_texto.get()
        print("Palabra ingresada:", palabra)
        grafo.nuevo_producto(palabra)
        self.destroy()
    
    
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
    
    def armar_lista_subp_operaciones(self):
        filas = self.armar_lista()
        del filas[0]
        cantidad_filas=sum(1 for fila in filas)
        elementos=[None] * cantidad_filas
        l=0
        for row in filas:
            elementos[l]=row[0]+" / "+row[1]
            l=l+1 
        return elementos
              
ventana_principal=VentanaPrincipal()

ventana_principal.mainloop()
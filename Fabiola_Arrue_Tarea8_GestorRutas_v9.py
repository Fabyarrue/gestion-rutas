import tkinter as tk
from tkinter import messagebox, filedialog
from tkinter import ttk
import os
import csv
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderUnavailable
from geopy.distance import geodesic
import webbrowser
import tkintermapview
import subprocess

# Asegurar el directorio de trabajo correcto
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

class Nodo:
    """
    Representa un nodo en el árbol binario.  Cada nodo contiene la información
    de una ruta de entrega.
    """
    def __init__(self, id_ruta, nombre, distancia, partida=None, destino=None,
                 lat_partida=None, lon_partida=None, lat_destino=None,
                 lon_destino=None, capacidad=0, carga_actual=0):
        """
        Inicializa un nuevo nodo.

        Args:
            id_ruta (int): Identificador único de la ruta.
            nombre (str): Nombre de la ruta.
            distancia (float): Distancia de la ruta en kilómetros.
            partida (str, optional): Lugar de partida.
            destino (str, optional): Lugar de destino.
            lat_partida (float, optional): Latitud del punto de partida.
            lon_partida (float, optional): Longitud del punto de partida.
            lat_destino (float, optional): Latitud del punto de destino.
            lon_destino (float, optional): Longitud del punto de destino.
            capacidad (float, optional): Capacidad máxima de carga de la ruta.
            carga_actual (float, optional): Carga actual de la ruta.
        """
        self.id_ruta = id_ruta
        self.nombre = nombre
        self.distancia = distancia
        self.partida = partida
        self.destino = destino
        self.latitud_partida = lat_partida
        self.longitud_partida = lon_partida
        self.latitud_destino = lat_destino
        self.longitud_destino = lon_destino
        self.izquierda = None  # Nodo hijo izquierdo
        self.derecha = None    # Nodo hijo derecho
        self.capacidad = capacidad
        self.carga_actual = carga_actual

    def calcular_eficiencia(self):
        """Calcula la eficiencia de la ruta (carga actual / capacidad)."""
        if self.capacidad <= 0:
            return "N/A"  # Evita división por cero y maneja capacidades no definidas
        porcentaje = (self.carga_actual / self.capacidad) * 100
        if porcentaje < 50:
            return "🔴 Baja"
        elif 50 <= porcentaje < 80:
            return "🟡 Media"
        else:
            return "🟢 Alta"


class ArbolBinarioBusqueda:
    """
    Implementa un árbol binario de búsqueda para almacenar y gestionar las rutas.
    """
    def __init__(self):
        """Inicializa un árbol binario de búsqueda vacío."""
        self.raiz = None

    def insertar(self, id_ruta, nombre, distancia, partida=None, destino=None, lat_partida=None, lon_partida=None,
                 lat_destino=None, lon_destino=None, capacidad=0, carga_actual=0):
        """
        Inserta una nueva ruta en el árbol.

        Args:
            id_ruta (int): Identificador único de la ruta.
            nombre (str): Nombre de la ruta.
            distancia (float): Distancia de la ruta.
            partida (str, optional):  Punto de partida.
            destino (str, optional): Punto de destino.
            lat_partida (float, optional): Latitud del punto de partida.
            lon_partida (float, optional): Longitud del punto de partida.
            lat_destino (float, optional): Latitud del punto de destino.
            lon_destino (float, optional): Longitud del punto de destino.
            capacidad (float, optional): Capacidad de la ruta.
            carga_actual (float, optional): Carga actual de la ruta.

        Returns:
            bool: True si la inserción fue exitosa, False si la ruta ya existe (ID duplicado).
        """
        # DEBUG: print(f"DEBUG (Arbol): Intentando insertar ruta con ID: {id_ruta}")
        if self.buscar(id_ruta) or self.buscar_por_nombre(nombre):
            # DEBUG: print(f"DEBUG (Arbol): Ruta con ID {id_ruta} o nombre {nombre} ya existe.")
            return False  # Ya existe una ruta con ese ID o nombre
        self.raiz = self._insertar_nodo(self.raiz, id_ruta, nombre, distancia, partida, destino, lat_partida,
                                        lon_partida, lat_destino, lon_destino, capacidad, carga_actual)
        # DEBUG: print(f"DEBUG (Arbol): Inserción de ruta con ID {id_ruta} exitosa.")
        return True

    def _insertar_nodo(self, nodo, id_ruta, nombre, distancia, partida, destino, lat_partida, lon_partida,
                      lat_destino, lon_destino, capacidad, carga_actual):
        """
        Función auxiliar recursiva para insertar un nodo en el árbol.
        """
        if nodo is None:
            # DEBUG: print(f"DEBUG (Arbol): Creando nuevo nodo para ID: {id_ruta}")
            return Nodo(id_ruta, nombre, distancia, partida, destino, lat_partida, lon_partida, lat_destino,
                        lon_destino, capacidad, carga_actual)
        if id_ruta < nodo.id_ruta:
            nodo.izquierda = self._insertar_nodo(nodo.izquierda, id_ruta, nombre, distancia, partida, destino,
                                                lat_partida, lon_partida, lat_destino, lon_destino, capacidad, carga_actual)
        else:
            nodo.derecha = self._insertar_nodo(nodo.derecha, id_ruta, nombre, distancia, partida, destino,
                                              lat_partida, lon_partida, lat_destino, lon_destino, capacidad, carga_actual)
        return nodo

    def buscar(self, id_ruta):
        """
        Busca una ruta en el árbol por su ID.

        Args:
            id_ruta (int): El ID de la ruta a buscar.

        Returns:
            Nodo: El nodo que contiene la ruta, o None si no se encuentra.
        """
        return self._buscar_nodo(self.raiz, id_ruta)

    def _buscar_nodo(self, nodo, id_ruta):
        """
        Función auxiliar recursiva para buscar un nodo por ID.
        """
        if nodo is None:
            return None
        if nodo.id_ruta == id_ruta:
            return nodo
        if id_ruta < nodo.id_ruta:
            return self._buscar_nodo(nodo.izquierda, id_ruta)
        return self._buscar_nodo(nodo.derecha, id_ruta)

    def buscar_por_nombre(self, nombre):
        """
        Busca una ruta en el árbol por su nombre (no es la búsqueda principal,
        pero puede ser útil).

        Args:
            nombre (str): El nombre de la ruta a buscar.

        Returns:
            Nodo: El nodo que contiene la ruta, o None si no se encuentra.
        """
        return self._buscar_por_nombre(self.raiz, nombre)

    def _buscar_por_nombre(self, nodo, nombre):
        """Función auxiliar recursiva para buscar un nodo por nombre."""
        if nodo is None:
            return None
        if nodo.nombre.lower() == nombre.lower():
            return nodo
        izquierda = self._buscar_por_nombre(nodo.izquierda, nombre)
        return izquierda if izquierda else self._buscar_por_nombre(nodo.derecha, nombre)
    
    def eliminar(self, id_ruta):
        """
        Elimina una ruta del árbol por su ID.

        Args:
            id_ruta (int): El ID de la ruta a eliminar.
        Returns:
            bool: True si se elimino correctamente, False si no se encontro.
        """
        self.raiz, eliminado = self._eliminar_nodo(self.raiz, id_ruta)
        return eliminado

    def _eliminar_nodo(self, nodo, id_ruta):
        """
        Funcion auxiliar recursiva para eliminar un nodo por ID
        """
        if nodo is None:
            return nodo, False #Nodo no encontrado
        
        if id_ruta < nodo.id_ruta:
            nodo.izquierda, eliminado = self._eliminar_nodo(nodo.izquierda, id_ruta)
        elif id_ruta > nodo.id_ruta:
            nodo.derecha, eliminado = self._eliminar_nodo(nodo.derecha, id_ruta)
        else: #Encontramos el nodo a eliminar
            if nodo.izquierda is None:
                return nodo.derecha, True #Caso 1 y 2: 0 o 1 hijo
            elif nodo.derecha is None:
                return nodo.izquierda, True #Caso 2: 1 hijo
            
            #Caso 3: 2 hijos
            sucesor = self._minimo_valor(nodo.derecha) #Encontrar el sucesor inorden
            #Copiar los datos del sucesor al nodo actual
            nodo.id_ruta, nodo.nombre, nodo.distancia, nodo.partida, nodo.destino, nodo.latitud_partida, nodo.longitud_partida, nodo.latitud_destino, nodo.longitud_destino, nodo.capacidad, nodo.carga_actual = sucesor.id_ruta, sucesor.nombre, sucesor.distancia, sucesor.partida, sucesor.destino, sucesor.latitud_partida, sucesor.longitud_partida, sucesor.latitud_destino, sucesor.longitud_destino, sucesor.capacidad, sucesor.carga_actual
            #Eliminar el sucesor
            nodo.derecha, _ = self._eliminar_nodo(nodo.derecha, sucesor.id_ruta)
            return nodo, True
        return nodo, eliminado #Retorna el nodo modificado y si se elimino

    def _minimo_valor(self, nodo):
        """
        Encuentra el nodo con el valor minimo (el mas a la izquierda)
        """
        while nodo.izquierda:
            nodo = nodo.izquierda
        return nodo

    def obtener_rutas(self):
        """
        Obtiene todas las rutas almacenadas en el árbol.

        Returns:
            list: Una lista de tuplas, donde cada tupla contiene la información de una ruta.
        """
        # print("DEBUG (Arbol): Obteniendo todas las rutas...")
        rutas = []
        self._inorden(self.raiz, rutas)
        # print(f"DEBUG (Arbol): Rutas obtenidas: {rutas}")
        return rutas

    def _inorden(self, nodo, rutas):
        """
        Recorrido inorden del árbol (auxiliar para obtener_rutas).
        """
        if nodo:
            self._inorden(nodo.izquierda, rutas)
            rutas.append((nodo.id_ruta, nodo.nombre, nodo.distancia, nodo.partida, nodo.destino, nodo.latitud_partida,
                          nodo.longitud_partida, nodo.latitud_destino, nodo.longitud_destino, nodo.capacidad, nodo.carga_actual))
            self._inorden(nodo.derecha, rutas)


    def modificar(self, id_ruta, nuevo_nombre, nueva_distancia, nueva_partida, nuevo_destino,
                  lat_partida=None, lon_partida=None, lat_destino=None, lon_destino=None,
                  nueva_capacidad=None, nueva_carga_actual=None):
        """
        Modifica la información de una ruta existente.

        Args:
            id_ruta (int): El ID de la ruta a modificar.
            nuevo_nombre (str): El nuevo nombre de la ruta.
            nueva_distancia (float): La nueva distancia de la ruta.
            nueva_partida (str): El nuevo punto de partida.
            nuevo_destino (str): El nuevo punto de destino.
            lat_partida (float, optional): La nueva latitud de partida.
            lon_partida (float, optional): La nueva longitud de partida.
            lat_destino (float, optional): La nueva latitud de destino.
            lon_destino (float, optional): La nueva longitud de destino.
            nueva_capacidad (float, optional): La nueva capacidad de la ruta.
            nueva_carga_actual (float, optional): La nueva carga actual de la ruta.

        Returns:
            bool: True si la modificación fue exitosa, False si la ruta no se encontró
                  o si ya existe una ruta con el nuevo nombre.
        """

        # DEBUG: print(f"DEBUG (Arbol): Intentando modificar ruta con ID: {id_ruta}")
        nodo = self.buscar(id_ruta)

        if nodo:
            if nuevo_nombre != nodo.nombre and self.buscar_por_nombre(nuevo_nombre):
                # DEBUG: print(f"DEBUG (Arbol): Ya existe una ruta con el nombre {nuevo_nombre}")
                return False  # Ya existe una ruta con ese nombre

            nodo.nombre = nuevo_nombre
            nodo.distancia = nueva_distancia
            nodo.partida = nueva_partida
            nodo.destino = nuevo_destino
            nodo.latitud_partida = lat_partida
            nodo.longitud_partida = lon_partida
            nodo.latitud_destino = lat_destino
            nodo.longitud_destino = lon_destino

            # Validar y actualizar Capacidad y Carga Actual
            if nueva_capacidad is not None:
                nodo.capacidad = nueva_capacidad
            if nueva_carga_actual is not None:
                nodo.carga_actual = nueva_carga_actual

            # DEBUG: print(f"DEBUG (Arbol): Modificación de ruta con ID {id_ruta} exitosa.")
            return True

        # DEBUG: print(f"DEBUG (Arbol): No se encontró la ruta con ID {id_ruta} para modificar.")
        return False


class Aplicacion:
    def __init__(self, root):
        self.arbol = ArbolBinarioBusqueda()
        self.root = root
        self.root.title("Gestión de Rutas")
        self.root.configure(bg="#E2FFD1")
        # Variables para almacenar latitud y longitud
        self.latitud_partida = None
        self.longitud_partida = None
        self.latitud_destino = None
        self.longitud_destino = None
        self.mapa_dialog = None  
        self.modo_edicion = False

        # --- Título ---
        self.label_titulo = tk.Label(root, text="Gestión de Rutas de Entrega", bg="#E2FFD1", font=("Arial", 16, "bold"))
        self.label_titulo.grid(row=0, column=0, columnspan=5, pady=10, sticky="ew")

        # --- Interfaz ---
        # Se usa un Frame para agrupar los widgets de entrada
        input_frame = tk.Frame(root, bg="#E2FFD1")
        input_frame.grid(row=1, column=0, columnspan=5, padx=10, pady=5, sticky="nsew")
        # Se configura el frame para que se centre
        input_frame.columnconfigure(0, weight=1)
        input_frame.columnconfigure(1, weight=1)
        input_frame.columnconfigure(2, weight=1)
        input_frame.columnconfigure(3, weight=1)

        # ID
        self.label_id = tk.Label(input_frame, text="ID:", bg="#E3F2FD", font=("Arial", 10, "bold"))
        self.label_id.grid(row=0, column=0, padx=(0, 5), pady=5, sticky="e")
        self.entry_id = tk.Entry(input_frame, width=10)
        self.entry_id.grid(row=0, column=1, padx=(0, 5), pady=5, sticky="w")
        self.entry_id.config(state="normal")
        self.id_info_label = tk.Label(input_frame, text="* (Autogenerado - No utilizar para agregar ruta)", bg="#E3F2FD", font=("Arial", 8, "italic"), fg="red")
        self.id_info_label.grid(row=0, column=2, padx=(0, 10), pady=5, sticky="w")

        # Ruta
        self.label_nombre = tk.Label(input_frame, text="Ruta:", bg="#E3F2FD", font=("Arial", 10, "bold"))
        self.label_nombre.grid(row=1, column=0, padx=(0, 5), pady=5, sticky="e") #Usamos east para alinear a la derecha
        self.entry_nombre = tk.Entry(input_frame, width=20)
        self.entry_nombre.grid(row=1, column=1, padx=(0, 5), pady=5, sticky="w")

        # Punto de Partida
        self.label_partida = tk.Label(input_frame, text="Punto de Partida:", bg="#E3F2FD", font=("Arial", 10, "bold"))
        self.label_partida.grid(row=2, column=0, padx=(0, 5), pady=5, sticky="e") #Usamos east para alinear a la derecha
        self.entry_partida = tk.Entry(input_frame, width=25)
        self.entry_partida.grid(row=2, column=1, padx=(0, 5), pady=5, sticky="w")
        self.btn_seleccionar_partida = tk.Button(input_frame, text="Seleccionar en Mapa", command=lambda: self.mostrar_mapa("partida"), bg="#ADD8E6", fg="black", font=("Arial", 9))
        self.btn_seleccionar_partida.grid(row=2, column=2, padx=(0, 10), pady=5, sticky="w")

        # Punto de Destino
        self.label_destino = tk.Label(input_frame, text="Punto de Destino:", bg="#E3F2FD", font=("Arial", 10, "bold"))
        self.label_destino.grid(row=3, column=0, padx=(0, 5), pady=5, sticky="e") #Usamos east para alinear a la derecha
        self.entry_destino = tk.Entry(input_frame, width=25)
        self.entry_destino.grid(row=3, column=1, padx=(0, 5), pady=5, sticky="w")
        self.btn_seleccionar_destino = tk.Button(input_frame, text="Seleccionar en Mapa", command=lambda: self.mostrar_mapa("destino"), bg="#ADD8E6", fg="black", font=("Arial", 9))
        self.btn_seleccionar_destino.grid(row=3, column=2, padx=(0, 10), pady=5, sticky="w")

        # Distancia
        self.label_distancia = tk.Label(input_frame, text="Distancia (km):", bg="#E3F2FD", font=("Arial", 10, "bold"))
        self.label_distancia.grid(row=4, column=0, padx=(0, 5), pady=5, sticky="e") #Usamos east para alinear a la derecha
        self.entry_distancia = tk.Entry(input_frame, width=10)
        self.entry_distancia.grid(row=4, column=1, padx=(0, 5), pady=5, sticky="w")
        
        # Etiqueta de información para la distancia
        self.distancia_info_label = tk.Label(input_frame, text="* (Se calcula automáticamente si se deja en blanco)", bg="#E3F2FD", font=("Arial", 8, "italic"), fg="blue")
        self.distancia_info_label.grid(row=4, column=2, padx=(0,10), pady=5, sticky="w")

        # Capacidad
        self.label_capacidad = tk.Label(input_frame, text="Capacidad (kg):", bg="#E3F2FD", font=("Arial", 10, "bold"))
        self.label_capacidad.grid(row=5, column=0, padx=(0, 5), pady=5, sticky="e")
        self.entry_capacidad = tk.Entry(input_frame, width=10)
        self.entry_capacidad.grid(row=5, column=1, padx=(0, 5), pady=5, sticky="w")

        # Carga Actual
        self.label_carga_actual = tk.Label(input_frame, text="Carga Actual (kg):", bg="#E3F2FD", font=("Arial", 10, "bold"))
        self.label_carga_actual.grid(row=6, column=0, padx=(0, 5), pady=5, sticky="e")
        self.entry_carga_actual = tk.Entry(input_frame, width=10)
        self.entry_carga_actual.grid(row=6, column=1, padx=(0, 5), pady=5, sticky="w")


        # --- Botones ---
        # Frame para los botones
        button_frame = tk.Frame(root, bg="#E2FFD1")
        button_frame.grid(row=2, column=0, columnspan=5, pady=10, sticky="ew")
        #Se configura el frame para que se centre
        button_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(1, weight=1)
        button_frame.columnconfigure(2, weight=1)
        button_frame.columnconfigure(3, weight=1)
        button_frame.columnconfigure(4, weight=1)
        button_frame.columnconfigure(5, weight=1)


        # Definir botones con estilo y tamaño uniforme
        button_width = 15  # Ancho fijo para los botones
        self.btn_agregar = tk.Button(button_frame, text="Agregar Ruta", command=self.agregar_ruta, bg="#4CAF50", fg="white", font=("Arial", 10), width=button_width)
        self.btn_buscar = tk.Button(button_frame, text="Buscar Ruta", command=self.buscar_ruta, bg="#2196F3", fg="white", font=("Arial", 10), width=button_width)
        self.btn_eliminar = tk.Button(button_frame, text="Eliminar Ruta", command=self.eliminar_ruta, bg="#F44336", fg="white", font=("Arial", 10), width=button_width)
        self.btn_modificar = tk.Button(button_frame, text="Modificar Ruta", command=self.modificar_ruta, bg="#FFA000", fg="white", font=("Arial", 10), width=button_width)
        self.btn_informe = tk.Button(button_frame, text="Generar Informe", command=self.generar_informe, bg="#90EE90", fg="black", font=("Arial", 10), width=button_width)
        self.btn_ver_mapa = tk.Button(button_frame, text="Ver en Mapa", command=self.ver_ruta_en_mapa, bg="#6495ED", fg="white", font=("Arial", 10), width=button_width)

        # Colocar botones en el frame
        self.btn_agregar.pack(side=tk.LEFT, padx=5)
        self.btn_buscar.pack(side=tk.LEFT, padx=5)
        self.btn_eliminar.pack(side=tk.LEFT, padx=5)
        self.btn_modificar.pack(side=tk.LEFT, padx=5)
        self.btn_informe.pack(side=tk.LEFT, padx=5)
        self.btn_ver_mapa.pack(side=tk.LEFT, padx=5)


        # --- Treeview para mostrar los datos ---
        self.tree = ttk.Treeview(root, columns=("ID", "Ruta", "Distancia", "Partida", "Destino", "Capacidad", "Carga Actual", "Eficiencia"), show="headings", height=10)
        # Configurar los encabezados de las columnas
        self.tree.heading("ID", text="ID")
        self.tree.heading("Ruta", text="Ruta")
        self.tree.heading("Distancia", text="Distancia")
        self.tree.heading("Partida", text="Partida")
        self.tree.heading("Destino", text="Destino")
        self.tree.heading("Capacidad", text="Capacidad")
        self.tree.heading("Carga Actual", text="Carga Actual")
        self.tree.heading("Eficiencia", text="Eficiencia")
        self.tree.bind("<<TreeviewSelect>>", self.seleccionar_ruta)
        self.tree.grid(row=8, column=0, columnspan=5, padx=10, pady=10, sticky="nsew")


        self.tree.configure(selectmode="browse")  # Permitir seleccionar una sola fila

        # Definir los encabezados de las columnas
        self.tree.heading("ID", text="ID")
        self.tree.heading("Ruta", text="Ruta")
        self.tree.heading("Distancia", text="Distancia (km)")
        self.tree.heading("Partida", text="Punto de Partida")
        self.tree.heading("Destino", text="Punto de Destino")
        self.tree.heading("Capacidad", text="Capacidad (kg)")
        self.tree.heading("Carga Actual", text="Carga Actual")
        self.tree.heading("Eficiencia", text="Eficiencia")
        self.tree.column("Eficiencia", width=80)

        # Ajustar el ancho de las columnas
        self.tree.column("ID", width=30)
        self.tree.column("Ruta", width=100)
        self.tree.column("Distancia", width=70)
        self.tree.column("Partida", width=130)
        self.tree.column("Destino", width=130)
        self.tree.column("Capacidad", width=70)
        self.tree.column("Carga Actual", width=70)

        # Configuración para expandir la tabla con la ventana.
        self.root.grid_rowconfigure(8, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_columnconfigure(2, weight=1)
        self.root.grid_columnconfigure(3, weight=1)
        self.root.grid_columnconfigure(4, weight=1)


        # Vincular el evento de selección
        self.tree.bind("<<TreeviewSelect>>", self.seleccionar_ruta)

         # Vincular clic izquierdo (fuera de la tabla) 
        self.root.bind("<Button-1>", lambda event: self.limpiar_campos() \
            if event.widget not in (self.tree, self.btn_agregar, self.btn_buscar, self.btn_eliminar, \
                                    self.btn_modificar, self.btn_informe, self.btn_ver_mapa, \
                                    self.btn_seleccionar_partida, self.btn_seleccionar_destino, \
                                    self.entry_id, self.entry_nombre, self.entry_distancia, \
                                    self.entry_partida, self.entry_destino, self.entry_capacidad, self.entry_carga_actual) \
            and not self.modo_edicion else None)

        self.root.bind("<Escape>", lambda event: self.limpiar_campos())  # <-- Limpiar con Escape
        self.cargar_datos_iniciales()

    def obtener_coordenadas(self, lugar):
        """Obtiene las coordenadas (latitud, longitud) de un lugar usando Nominatim.
            Maneja errores y devuelve (None, None) si falla.
        """
        geolocalizador = Nominatim(user_agent="gestor_rutas_app", timeout=10)
        try:
            ubicacion = geolocalizador.geocode(lugar)
            if ubicacion:
                #DEBUG: print(f"DEBUG (obtener_coordenadas): Geocodificación exitosa para '{lugar}'.")
                #DEBUG: print(f"DEBUG (obtener_coordenadas): Latitud: {ubicacion.latitude}, Longitud: {ubicacion.longitude}")  # Imprime las coordenadas
                return (ubicacion.latitude, ubicacion.longitude)  # Devuelve latitud, longitud
            else:
                #DEBUG: print(f"DEBUG (obtener_coordenadas): No se encontró ubicación para '{lugar}'.")
                messagebox.showerror("Error de Geocodificación", f"No se encontró la ubicación: '{lugar}'")
                return (None, None)  # Devuelve None, None en caso de error
        except GeocoderTimedOut:
            #DEBUG: print(f"DEBUG (obtener_coordenadas): Timeout para '{lugar}'.")
            messagebox.showerror("Error de Geocodificación", "El servicio tardó demasiado. Revise su conexión a Internet.")
            return (None, None)
        except GeocoderUnavailable:
            #DEBUG: print(f"DEBUG (obtener_coordenadas): Servicio no disponible para '{lugar}'.")
            messagebox.showerror("Error de Geocodificación", "El servicio no está disponible. Intente más tarde.")
            return (None, None)
        except Exception as e:
            #DEBUG: print(f"DEBUG (obtener_coordenadas): Error inesperado para '{lugar}': {e}")
            messagebox.showerror("Error de Geocodificación", f"Error inesperado: {e}")
            return (None, None)

    def agregar_ruta(self):
        #DEBUG: print("DEBUG: agregar_ruta INICIO")
        try:
            nombre = self.entry_nombre.get().strip()
            partida = self.entry_partida.get().strip()
            destino = self.entry_destino.get().strip()
            distancia_str = self.entry_distancia.get().strip()

            # --- Campos para Capacidad y Carga Actual ---
            capacidad_str = self.entry_capacidad.get().strip()
            carga_actual_str = self.entry_carga_actual.get().strip()


            if not nombre or not partida or not destino:
                messagebox.showerror("Error", "Los campos Ruta, Partida y Destino son obligatorios.")
                #DEBUG: print("DEBUG: agregar_ruta - Campos obligatorios vacíos")
                return

            # --- Obtener coordenadas SIEMPRE ---
            coordenadas_partida = self.obtener_coordenadas(partida)
            coordenadas_destino = self.obtener_coordenadas(destino)

            if not coordenadas_partida or not coordenadas_destino:
                #DEBUG: print("DEBUG: agregar_ruta - Falló la geocodificación")
                return

            self.latitud_partida, self.longitud_partida = coordenadas_partida
            self.latitud_destino, self.longitud_destino = coordenadas_destino

            # --- Cálculo de distancia / Validación de distancia ---
            if distancia_str:
                try:
                    distancia = float(distancia_str)
                    if distancia < 0:
                        messagebox.showerror("Error", "La distancia no puede ser negativa.")
                        return
                    distancia = round(distancia, 2)
                except ValueError:
                    messagebox.showerror("Error", "La distancia debe ser un número válido.")
                    return
            else:
                distancia = self.calcular_distancia(self.latitud_partida, self.longitud_partida,
                                                    self.latitud_destino, self.longitud_destino)
                if distancia is None:
                    #DEBUG: print("DEBUG: agregar_ruta - Falló el cálculo de distancia")
                    return
                distancia = round(distancia, 2)

            # --- Mostrar la distancia ---
            self.entry_distancia.delete(0, tk.END)
            self.entry_distancia.insert(0, str(distancia))


            # --- Validación de Capacidad y Carga Actual ---
            try:
                capacidad = float(capacidad_str)
                if capacidad <= 0:
                    messagebox.showerror("Error", "La capacidad debe ser un número positivo.")
                    return
            except ValueError:
                messagebox.showerror("Error", "La capacidad debe ser un número válido.")
                return

            try:
                carga_actual = float(carga_actual_str)
                if carga_actual < 0:
                    messagebox.showerror("Error", "La carga actual no puede ser negativa.")
                    return
                if carga_actual > capacidad:
                    messagebox.showerror("Error", "La carga actual no puede ser mayor que la capacidad.")
                    return
            except ValueError:
                messagebox.showerror("Error", "La carga actual debe ser un número válido.")
                return

            # --- Generar ID y resto de la lógica ---
            id_ruta = self.obtener_siguiente_id()
            #DEBUG: print(f"DEBUG: agregar_ruta - ID generado: {id_ruta}")

            # --- Pasar capacidad y carga_actual al constructor del Nodo ---
            exito = self.arbol.insertar(id_ruta, nombre, distancia, partida, destino,
                                        self.latitud_partida, self.longitud_partida,
                                        self.latitud_destino, self.longitud_destino,
                                        capacidad, carga_actual)  # <-- Pasar capacidad y carga
            #DEBUG: print(f"DEBUG: agregar_ruta - Resultado de insertar: {exito}")

            if exito:
                self.actualizar_lista()
                messagebox.showinfo("Éxito", "Ruta agregada correctamente.")
                self.limpiar_campos()
                self.guardar_datos()
            else:
                messagebox.showerror("Error", "Error al agregar la ruta.")

        except Exception as e:
            messagebox.showerror("Error", f"Error inesperado: {e}")
            #DEBUG: print(f"DEBUG: agregar_ruta - Error inesperado: {e}")

        finally:
            self.limpiar_campos()  # Asegura que se limpie
            # self.entry_id.config(state="normal") #Ya se habilita en limpiar campos.
            #DEBUG: print("DEBUG: agregar_ruta FIN")

    def obtener_siguiente_id(self):
        """Obtiene el siguiente ID disponible para una nueva ruta."""
        rutas = self.arbol.obtener_rutas()
        if not rutas:
            return 1  # Si no hay rutas, el primer ID es 1
        else:
            # Obtiene el ID máximo actual y suma 1
            max_id = max(ruta[0] for ruta in rutas)
            return max_id + 1

    def buscar_ruta(self):
        # Habilitar el campo ID para permitir la búsqueda
        self.entry_id.config(state="normal")  # <-- HABILITADO al inicio
        id_ruta = self.entry_id.get().strip()  # Obtener el ID y quitar espacios

        if not id_ruta:  # Verificar si el campo ID está vacío
            messagebox.showerror("Error", "Ingrese un ID para buscar.")
            return  # Salir de la función si no hay ID

        if id_ruta.isdigit():
            id_ruta_num = int(id_ruta)  # Convertir a entero *después* de verificar que es dígito
            nodo = self.arbol.buscar(id_ruta_num)
            if nodo:
                # Carga los datos de la ruta encontrada
                self.cargar_ruta_buscada(id_ruta_num)
                # Ya se maneja en _cargar_ruta
                # self.entry_id.config(state="disabled")
            else:
                messagebox.showerror("Error", "Ruta no encontrada.")
                self.limpiar_campos()  # Limpiar si no se encuentra

        else:
            messagebox.showerror("Error", "Ingrese un ID válido.")
            self.limpiar_campos()  # Limpiar si el ID no es válido

    def cargar_ruta_buscada(self, id_ruta):
        """Carga los datos de una ruta en los campos para visualización/edición."""
        #DEBUG: print("DEBUG: cargar_ruta_buscada - INICIO")
        #DEBUG: print(f"DEBUG: cargar_ruta_buscada - Recibí id_ruta: {id_ruta}")

        nodo = self.arbol.buscar(id_ruta)
        #DEBUG: print(f"DEBUG: cargar_ruta_buscada - Resultado de arbol.buscar: {nodo}")

        if nodo:
            #DEBUG: print("DEBUG: cargar_ruta_buscada - Entrando al IF (nodo encontrado)")

            # --- ID (habilitar, limpiar, insertar, deshabilitar) ---
            self.entry_id.config(state="normal")
            self.entry_id.delete(0, tk.END)
            self.entry_id.insert(0, str(nodo.id_ruta))
            self.entry_id.config(state="disabled")

            # --- Nombre ---
            self.entry_nombre.delete(0, tk.END)
            self.entry_nombre.insert(0, nodo.nombre)

            # --- Distancia ---
            self.entry_distancia.delete(0, tk.END)
            self.entry_distancia.insert(0, str(nodo.distancia))

            # --- Partida ---
            self.entry_partida.delete(0, tk.END)
            self.entry_partida.insert(0, nodo.partida)

            # --- Destino ---
            self.entry_destino.delete(0, tk.END)
            self.entry_destino.insert(0, nodo.destino)

            # --- Capacidad ---
            self.entry_capacidad.delete(0, tk.END)
            self.entry_capacidad.insert(0, str(nodo.capacidad))

            # --- Carga Actual ---
            self.entry_carga_actual.delete(0, tk.END)
            self.entry_carga_actual.insert(0, str(nodo.carga_actual))

            # --- Validaciones de coordenadas ---
            self.latitud_partida = nodo.latitud_partida if nodo.latitud_partida is not None else 0.0
            self.longitud_partida = nodo.longitud_partida if nodo.longitud_partida is not None else 0.0
            self.latitud_destino = nodo.latitud_destino if nodo.latitud_destino is not None else 0.0
            self.longitud_destino = nodo.longitud_destino if nodo.longitud_destino is not None else 0.0

            #DEBUG: print(f"DEBUG: cargar_ruta_buscada - Coordenadas guardadas: lat_partida={self.latitud_partida}, "
            #      f"lon_partida={self.longitud_partida}, lat_destino={self.latitud_destino}, "
            #      f"lon_destino={self.longitud_destino}")

            #DEBUG: print("DEBUG: cargar_ruta_buscada - FIN (nodo encontrado)")

        else:
            pass
            #DEBUG: print("DEBUG: cargar_ruta_buscada - FIN (nodo NO encontrado)")

    def eliminar_ruta(self):
        id_ruta = self.entry_id.get()
        if not id_ruta.isdigit():
            messagebox.showerror("Error", "Ingrese un ID válido.")
            return

        if messagebox.askyesno("Confirmar Eliminación", "¿Está seguro de que desea eliminar esta ruta?"):
            if self.arbol.eliminar(int(id_ruta)):
                self.actualizar_lista()
                self.limpiar_campos()
                self.guardar_datos() #Guarda los datos
            else:
                messagebox.showerror("Error", "Ruta no encontrada.")

    def actualizar_lista(self):
        """Actualiza la lista de rutas en la tabla con colores en la eficiencia."""
        seleccion_actual = self.tree.selection()  # Guardar selección actual

        # Limpiar la tabla antes de actualizar
        for item in self.tree.get_children():
            self.tree.delete(item)

        rutas = self.arbol.obtener_rutas()

        for ruta in rutas:
            id_ruta, nombre, distancia, partida, destino, lat_partida, lon_partida, lat_destino, lon_destino, capacidad, carga_actual = ruta

            # Calcular eficiencia
            eficiencia = carga_actual / capacidad
            if eficiencia <= 0.4:
                eficiencia_texto = "Baja"
            elif eficiencia <= 0.7:
                eficiencia_texto = "Media"
            else:
                eficiencia_texto = "Alta"

            # Insertar fila en la tabla
            item_id = self.tree.insert("", "end", values=(id_ruta, nombre, distancia, partida, destino, capacidad, carga_actual, eficiencia_texto))

            # Aplicar color a la columna "Eficiencia"
            self.tree.item(item_id, tags=(eficiencia_texto,))

        # Restaurar la selección si es posible
        if seleccion_actual:
            seleccion_filtrada = [s for s in seleccion_actual if self.tree.exists(s)]  # Filtrar elementos eliminados
            for item in self.tree.get_children():
                valores = self.tree.item(item, 'values')
                if valores and seleccion_filtrada and str(valores[0]) in [self.tree.item(s, 'values')[0] for s in seleccion_filtrada]:
                    self.tree.selection_set(item)

        # Configurar etiquetas de color para la columna "Eficiencia"
        self.tree.tag_configure("Baja", foreground="red")
        self.tree.tag_configure("Media", foreground="orange")
        self.tree.tag_configure("Alta", foreground="green")

        #DEBUG: print("DEBUG: Lista de rutas actualizada con colores en la eficiencia.")

    def seleccionar_ruta(self, event):
        """Maneja la selección de una ruta en la tabla."""
        seleccion = self.tree.selection()
        #DEBUG: print(f"DEBUG: seleccionar_ruta - Selección: {seleccion}")

        if seleccion:
            item = seleccion[0]
            #DEBUG: print(f"DEBUG: seleccionar_ruta - Item seleccionado: {item}")
            self._cargar_ruta(item)  # Llamar a _cargar_ruta para cargar los datos
        #else: #Ya no es necesario
            #DEBUG: print("DEBUG: seleccionar_ruta - No hay selección.")


    def limpiar_campos(self, event=None):
        """Limpia los campos de entrada y habilita el campo ID *siempre*."""
        #DEBUG: print("DEBUG: Limpiando campos...")

        # *Siempre* habilitar el campo ID antes de limpiar
        self.entry_id.config(state="normal")
        #DEBUG: print("DEBUG: limpiar_campos - ID habilitado (antes de limpiar)")

        # Limpiar *todos* los campos (incluido el ID).
        self.entry_id.delete(0, tk.END)
        self.entry_nombre.delete(0, tk.END)
        self.entry_distancia.delete(0, tk.END)
        self.entry_partida.delete(0, tk.END)
        self.entry_destino.delete(0, tk.END)
        self.entry_capacidad.delete(0, tk.END)
        self.entry_carga_actual.delete(0, tk.END)
        self.modo_edicion = False  # Restablecer el modo de edición

        # *Después* de limpiar, si NO hay selección, deshabilitar.  Si la llamada
        # viene de un evento (Escape), deshabilitar.  Si no (ej. desde agregar_ruta),
        # dejar habilitado.
        if event:  # Si se llamó desde un evento (Escape)
            #DEBUG: print("DEBUG: limpiar_campos - Llamada desde evento, deshabilitando ID")
            self.entry_id.config(state="disabled")
        else:
            pass
            #DEBUG: print("DEBUG: limpiar_campos - No hay evento, ID se mantiene habilitado")
        #DEBUG: print("DEBUG: Campos limpiados.")

    def _cargar_ruta(self, item_id):
        """Carga los datos de la ruta seleccionada y DESHABILITA el campo ID."""
        #DEBUG: print(f"DEBUG: _cargar_ruta - INICIO con item_id: {item_id}")
        try:
            item = self.tree.item(item_id)
            valores = item['values']

            if not valores or len(valores) < 8:  # Verificar que haya suficientes valores
                #DEBUG: print("DEBUG: _cargar_ruta - No hay valores suficientes.")
                return

            # Extraer datos.
            id_ruta, nombre, distancia, partida, destino, capacidad, carga_actual, _ = valores
            id_ruta = str(id_ruta)  # Asegurar que sea cadena
            nombre = str(nombre)
            distancia = str(distancia)
            partida = str(partida)
            destino = str(destino)
            capacidad = str(capacidad)
            carga_actual = str(carga_actual)
            #La eficiencia no se carga

            #DEBUG: print(f"DEBUG: Cargando datos de ruta - ID: {id_ruta}, Nombre: {nombre}")

            # Buscar la ruta en el árbol *usando el ID* para obtener lat/lon
            nodo = self.arbol.buscar(int(id_ruta))  # Convertir a entero.  IMPORTANTE
            if nodo:
                self.latitud_partida = nodo.latitud_partida
                self.longitud_partida = nodo.longitud_partida
                self.latitud_destino = nodo.latitud_destino
                self.longitud_destino = nodo.longitud_destino
            # else: #Comentado el else porque si no se encuentra la ruta en la lista
            # no hacemos nada
                #DEBUG: print(f"DEBUG: _cargar_ruta - Nodo no encontrado para ID: {id_ruta}")
                #return

            # Llenar los campos de entrada
            self.entry_id.config(state="normal")  # Habilitar temporalmente para limpiar/insertar
            self.entry_id.delete(0, tk.END)
            self.entry_id.insert(0, id_ruta)
            self.entry_id.config(state="disabled")  # <-- DESHABILITAR después de cargar

            self.entry_nombre.delete(0, tk.END)
            self.entry_nombre.insert(0, nombre)
            self.entry_distancia.delete(0, tk.END)
            self.entry_distancia.insert(0, distancia)
            self.entry_partida.delete(0, tk.END)
            self.entry_partida.insert(0, partida)
            self.entry_destino.delete(0, tk.END)
            self.entry_destino.insert(0, destino)
            self.entry_capacidad.delete(0, tk.END)
            self.entry_capacidad.insert(0, capacidad)
            self.entry_carga_actual.delete(0, tk.END)
            self.entry_carga_actual.insert(0, carga_actual)

            #DEBUG: print("DEBUG: Campos actualizados correctamente.")
        except Exception as e:
            print(f"ERROR: No se pudo cargar la ruta seleccionada. Detalles: {e}")



    def modificar_ruta(self):
        self.modo_edicion = True  # <-- Iniciar modo edición
        try:
            id_ruta_str = self.entry_id.get()
            nuevo_nombre = self.entry_nombre.get().strip()
            nueva_distancia_str = self.entry_distancia.get()
            nueva_partida = self.entry_partida.get().strip()
            nuevo_destino = self.entry_destino.get().strip()
            nueva_capacidad_str = self.entry_capacidad.get().strip()
            nueva_carga_actual_str = self.entry_carga_actual.get().strip()

            if not nuevo_nombre or not nueva_partida or not nuevo_destino or not nueva_capacidad_str or not nueva_carga_actual_str:
                messagebox.showerror("Error", "Ningún campo (excepto ID y Distancia) puede estar vacío.")
                return

            if not id_ruta_str.isdigit():
                messagebox.showerror("Error", "El ID debe ser un número entero.")
                return

            id_ruta = int(id_ruta_str)

            # --- Validación y conversión de distancia ---
            try:
                nueva_distancia = float(nueva_distancia_str)
                if nueva_distancia < 0:
                    messagebox.showerror("Error", "La distancia no puede ser negativa.")
                    return
            except ValueError:
                messagebox.showerror("Error", "La distancia debe ser un número.")
                return

            # --- Validación de capacidad y carga actual ---
            try:
                nueva_capacidad = float(nueva_capacidad_str)
                nueva_carga_actual = float(nueva_carga_actual_str)

                if nueva_capacidad <= 0:
                    messagebox.showerror("Error", "La capacidad debe ser mayor a 0.")
                    return
                if nueva_carga_actual < 0 or nueva_carga_actual > nueva_capacidad:
                    messagebox.showerror("Error", "La carga actual debe estar entre 0 y la capacidad.")
                    return
            except ValueError:
                messagebox.showerror("Error", "La capacidad y la carga actual deben ser valores numéricos.")
                return

            # Verificar si la ruta existe antes de modificarla
            nodo = self.arbol.buscar(id_ruta)
            if not nodo:
                messagebox.showerror("Error", "La ruta con el ID especificado no existe.")
                return

            # --- Geolocalización ---
            coordenadas_partida = self.obtener_coordenadas(nueva_partida)
            coordenadas_destino = self.obtener_coordenadas(nuevo_destino)

            if not coordenadas_partida or not coordenadas_destino:
                return  # Ya se mostró un error dentro de obtener_coordenadas

            lat_partida, lon_partida = coordenadas_partida
            lat_destino, lon_destino = coordenadas_destino

            # --- Recalcular distancia ---
            nueva_distancia = self.calcular_distancia(lat_partida, lon_partida, lat_destino, lon_destino)
            if nueva_distancia is None:
                return

            nueva_distancia = round(nueva_distancia, 2)

            # --- Modificar ruta en el árbol ---
            if self.arbol.modificar(id_ruta, nuevo_nombre, nueva_distancia, nueva_partida, nuevo_destino,
                                    lat_partida, lon_partida, lat_destino, lon_destino, nueva_capacidad, nueva_carga_actual):
                self.actualizar_lista()
                self.limpiar_campos()
                self.guardar_datos()
                messagebox.showinfo("Modificación", "Ruta modificada con éxito.")
            else:
                messagebox.showerror("Error", "No se pudo modificar la ruta.")

        except ValueError:
            messagebox.showerror("Error", "Ingrese valores válidos (ID numérico, distancia numérica).")
        finally:
            # self.entry_id.config(state="disabled")  # <-- Ya no va aquí
            self.modo_edicion = False  # <-- Finalizar modo edición SIEMPRE

    def obtener_direccion(self, latitud, longitud):
        geolocalizador = Nominatim(user_agent="aplicacion_rutas") #Usar un nombre
        try:
            ubicacion = geolocalizador.reverse((latitud, longitud), exactly_one=True, language="es")
            if ubicacion:
                return ubicacion.address
            else:
                return "Dirección no encontrada"
        except Exception as e:
            print(f"Error en geocodificación inversa: {e}")
            return "Error al obtener dirección"

    def calcular_distancia(self, lat1, lon1, lat2, lon2):
        """Calcula la distancia geodésica entre dos puntos."""
        try:
            punto1 = (lat1, lon1)
            punto2 = (lat2, lon2)
            distancia = geodesic(punto1, punto2).km  # Calcula la distancia en kilómetros
            return distancia
        except Exception as e:
            print(f"Error al calcular la distancia: {e}")
            messagebox.showerror("Error", "Error al calcular la distancia.")
            return None

    def mostrar_mapa(self, tipo):
        """Abre la ventana del mapa para seleccionar coordenadas."""
        if self.mapa_dialog is None:
            # Si no existe una instancia, crea una nueva
            self.mapa_dialog = MapaDialog(self, self.root, tipo)
            # Establece una posición y un zoom predeterminados *solo* al crear
            self.mapa_dialog.map_widget.set_position(-23.65, -70.4)  # Antofagasta
            self.mapa_dialog.map_widget.set_zoom(12)
        else:
            # Si ya existe, reutiliza la instancia existente
            self.mapa_dialog.tipo = tipo  # Actualiza el tipo (partida/destino)
            self.mapa_dialog.map_widget.delete_all_marker()  # Elimina marcadores previos
            self.mapa_dialog.deiconify()  # Muestra la ventana (si estaba oculta)

        self.root.wait_window(self.mapa_dialog)


    def generar_informe(self):
        rutas = self.arbol.obtener_rutas()
        if not rutas:
            messagebox.showinfo("Informe", "No hay rutas registradas.")
            return

        # --- Usar filedialog.asksaveasfilename ---
        try:
            ruta_archivo = filedialog.asksaveasfilename(
                initialdir=os.getcwd(),  # Directorio inicial (opcional)
                title="Guardar informe como",
                filetypes=(("Archivos CSV", "*.csv"), ("Todos los archivos", "*.*")),
                defaultextension=".csv"  # Importante: Agregar extensión por defecto
            )

            if not ruta_archivo:  # El usuario canceló el diálogo
                return

            with open(ruta_archivo, "w", newline="", encoding="utf-8") as f:
                escritor_csv = csv.writer(f)
                escritor_csv.writerow(["ID", "Ruta", "Distancia (km)", "Partida", "Destino","Latitud Partida", "Longitud Partida", "Latitud Destino", "Longitud Destino", "Capacidad", "Carga Actual","Eficiencia"])  # Encabezados + Eficiencia
                for id_ruta, nombre, distancia, partida, destino, lat_partida, lon_partida, lat_destino, lon_destino, capacidad, carga_actual in rutas:
                    #Calculamos la eficiencia
                    eficiencia = "N/A"
                    if capacidad > 0:
                        porcentaje = (carga_actual / capacidad) * 100
                        if porcentaje < 50:
                            eficiencia = "Baja"
                        elif 50 <= porcentaje < 80:
                            eficiencia = "Media"
                        else:
                            eficiencia = "Alta"
                    escritor_csv.writerow([id_ruta, nombre, distancia, partida, destino, lat_partida, lon_partida, lat_destino, lon_destino, capacidad, carga_actual, eficiencia])

            messagebox.showinfo("Informe", f"Informe guardado en: {ruta_archivo}")

            # --- Abrir el archivo ---
            if os.name == 'nt':
                os.startfile(ruta_archivo)
            else:
                try:
                    subprocess.run(["xdg-open", ruta_archivo], check=True)
                except FileNotFoundError:
                    try:
                        subprocess.run(["open", ruta_archivo], check=True)
                    except FileNotFoundError:
                        messagebox.showwarning("Advertencia","No se pudo abrir el archivo automáticamente.")

        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar/abrir el informe: {e}")

    def cargar_datos_iniciales(self):
        """Carga datos desde el archivo CSV, o inserta datos de ejemplo si hay errores."""
        ruta_archivo = os.path.join(os.getcwd(), "rutas_informe.csv")

        if os.path.exists(ruta_archivo):
            try:
                with open(ruta_archivo, "r", newline="", encoding="utf-8") as f:
                    lector_csv = csv.reader(f)
                    encabezados = next(lector_csv, None)  # Leer la primera fila (encabezados)

                    # --- Validación de Encabezados ---
                    if encabezados is None or encabezados != ["ID", "Ruta", "Distancia (km)", "Partida", "Destino", "Latitud Partida", "Longitud Partida", "Latitud Destino", "Longitud Destino", "Capacidad", "Carga Actual", "Eficiencia"]:
                        print("DEBUG: cargar_datos_iniciales - Encabezados incorrectos o archivo vacío.")
                        self.insertar_datos_ejemplo()
                        self.guardar_datos()  # <-- IMPORTANTE: Guardar después de insertar ejemplos
                        return

                    # --- Carga de Datos ---
                    self.arbol = ArbolBinarioBusqueda()  # <-- Crear un *NUEVO* árbol
                    for fila in lector_csv:
                        try:
                            # Leer *todos* los campos, incluyendo la eficiencia (aunque no se use directamente)
                            id_ruta, nombre, distancia_str, partida, destino, lat_partida_str, lon_partida_str, lat_destino_str, lon_destino_str, capacidad_str, carga_actual_str, _ = fila
                            
                            # Conversiones (con manejo de errores)
                            id_ruta = int(id_ruta)
                            distancia = round(float(distancia_str), 2)
                            lat_partida = float(lat_partida_str)
                            lon_partida = float(lon_partida_str)
                            lat_destino = float(lat_destino_str)
                            lon_destino = float(lon_destino_str)
                            capacidad = float(capacidad_str)
                            carga_actual = float(carga_actual_str)


                            self.arbol.insertar(id_ruta, nombre, distancia, partida, destino, lat_partida, lon_partida, lat_destino, lon_destino, capacidad, carga_actual)

                        except (ValueError, IndexError) as e:
                            print(f"DEBUG: cargar_datos_iniciales - Error al leer fila: {fila} - {e}")
                            # Si hay error en *una* fila, NO cargamos datos de ejemplo,
                            # simplemente *ignoramos* la fila y continuamos con la siguiente.
                            continue  # Saltar a la siguiente iteración del bucle for


                    self.actualizar_lista()

            except Exception as e:  # Captura cualquier otra excepción
                print(f"DEBUG: cargar_datos_iniciales - Error inesperado al cargar datos: {e}")
                self.insertar_datos_ejemplo()  # Cargar ejemplos
                self.guardar_datos()

        else:  #Si no existe el archivo CSV
            print("DEBUG: cargar_datos_iniciales - El archivo CSV no existe. Cargando datos de ejemplo.")
            self.insertar_datos_ejemplo()
            self.guardar_datos()

    def insertar_datos_ejemplo(self):
        """Inserta datos de prueba en el árbol de rutas y actualiza la interfaz."""
        #DEBUG: print("DEBUG: insertando datos de ejemplo...")

        datos_ejemplo = [
            (1, "Ruta Centro-Norte", 6.5, "Av. Balmaceda 2500, Antofagasta", "Universidad de Antofagasta",
            -23.641716, -70.398352, -23.608692, -70.399209, 100, 20),  # Baja eficiencia
            (2, "Ruta Costera", 12.3, "Terminal Pesquero Antofagasta", "Balneario Municipal Antofagasta",
            -23.632961, -70.408326, -23.677722, -70.403693, 80, 50),  # Media eficiencia
            (3, "Ruta Mall-Hospital", 8.9, "Mall Plaza Antofagasta", "Hospital Regional de Antofagasta",
            -23.674183, -70.404219, -23.635238, -70.388189, 120, 100),  # Alta eficiencia
        ]

        for datos in datos_ejemplo:
            self.arbol.insertar(*datos)
            #DEBUG: print(f"DEBUG: Insertada ruta de ejemplo - ID: {datos[0]}, Nombre: {datos[1]}")

        # Asegurar que las rutas aparezcan en la tabla tras la inserción
        self.actualizar_lista()

    def guardar_datos(self):
        """Guarda los datos en un archivo CSV."""
        try:
            with open("rutas_informe.csv", "w", newline="", encoding="utf-8") as file:
                writer = csv.writer(file)
                writer.writerow(["ID", "Ruta", "Distancia (km)", "Partida", "Destino", "Latitud Partida", "Longitud Partida", "Latitud Destino", "Longitud Destino", "Capacidad", "Carga Actual", "Eficiencia"])

                rutas = self.arbol.obtener_rutas()
                for ruta in rutas:
                    id_ruta, nombre, distancia, partida, destino, lat_partida, lon_partida, lat_destino, lon_destino, capacidad, carga_actual = ruta
                    # Calcular la eficiencia aquí, para que se guarde en el archivo.
                    eficiencia = "N/A"
                    if capacidad > 0:  # Evitar división por cero
                        porcentaje = (carga_actual / capacidad) * 100
                        if porcentaje < 50:
                            eficiencia = "Baja"
                        elif 50 <= porcentaje < 80:
                            eficiencia = "Media"
                        else:
                            eficiencia = "Alta"

                    writer.writerow([id_ruta, nombre, distancia, partida, destino, lat_partida, lon_partida, lat_destino, lon_destino, capacidad, carga_actual, eficiencia])

            # Ya no son necesarias with open cierra el archivo
            #file.flush()
            #file.close()

            #DEBUG: print("DEBUG: Datos guardados correctamente en rutas_informe.csv")
        except Exception as e:
            print(f"ERROR: No se pudo guardar el archivo CSV. Detalles: {e}")


    def ver_ruta_en_mapa(self):
        """Abre la ruta seleccionada en el navegador web (OpenStreetMap)."""
        seleccion = self.tree.selection()
        if not seleccion:
            messagebox.showwarning("Advertencia", "Seleccione una ruta de la lista.")
            return

        item = self.tree.item(seleccion[0])
        id_ruta = item['values'][0]  # Obtener ID de la ruta seleccionada

        # DEBUG: Imprimir la ruta seleccionada
        #DEBUG: print(f"DEBUG: Ruta seleccionada ID = {id_ruta}")
        #DEBUG: print(f"DEBUG: Atributos de self -> {dir(self)}")

        # Buscar la ruta en el árbol para obtener sus coordenadas
        nodo = self.arbol.buscar(int(id_ruta))
        if not nodo:
            messagebox.showerror("Error", "No se encontró la ruta en la base de datos.")
            return

        # Extraer coordenadas desde el nodo del árbol
        lat_partida, lon_partida = nodo.latitud_partida, nodo.longitud_partida
        lat_destino, lon_destino = nodo.latitud_destino, nodo.longitud_destino

        # DEBUG: Imprimir coordenadas obtenidas
        #DEBUG: print(f"DEBUG: Coordenadas obtenidas - Partida: ({lat_partida}, {lon_partida}), Destino: ({lat_destino}, {lon_destino})")

        # Validar que las coordenadas sean correctas antes de abrir el navegador
        if None in (lat_partida, lon_partida, lat_destino, lon_destino):
            messagebox.showerror("Error", "Las coordenadas de la ruta no son válidas o están incompletas.")
            return

        # Abrir la ruta en OpenStreetMap
        url = f"https://www.openstreetmap.org/directions?from={lat_partida},{lon_partida}&to={lat_destino},{lon_destino}"
        webbrowser.open(url)


    def actualizar_campos(self, direccion, lat, lng, tipo):
        """
        Callback: Actualiza los campos de entrada con la dirección,
        guarda las coordenadas, y calcula/actualiza la distancia.
        Se llama desde MapaDialog.
        """

        if tipo == "partida":
            self.entry_partida.delete(0, tk.END)
            self.entry_partida.insert(0, direccion)
            self.latitud_partida = lat
            self.longitud_partida = lng

        elif tipo == "destino":
            self.entry_destino.delete(0, tk.END)
            self.entry_destino.insert(0, direccion)
            self.latitud_destino = lat
            self.longitud_destino = lng

        # --- Calcular la distancia (si tenemos ambas coordenadas) ---
        if (
            self.latitud_partida is not None
            and self.longitud_partida is not None
            and self.latitud_destino is not None
            and self.longitud_destino is not None
        ):
            distancia = self.calcular_distancia(
                self.latitud_partida, self.longitud_partida, self.latitud_destino, self.longitud_destino
            )
            if distancia is not None:
                distancia = round(distancia, 2)  # <--- Redondeo
                self.entry_distancia.delete(0, tk.END)
                self.entry_distancia.insert(0, str(distancia))  # <--- Usar str, no f-string
        #Se movió la función de guardar datos aquí, para que cada vez que se actualicen los campos
        #Desde el mapa, se guarden los cambios.
        self.guardar_datos()



class MapaDialog(tk.Toplevel):
    def __init__(self, aplicacion, parent, tipo):
        super().__init__(parent)
        self.title("Seleccionar Ubicación")
        self.geometry("600x450")
        self.tipo = tipo  # "partida" o "destino"
        self.lat = None
        self.lon = None
        self.aplicacion = aplicacion  # Referencia a la clase Aplicacion

        self.map_widget = tkintermapview.TkinterMapView(self, width=600, height=400)
        self.map_widget.pack()
        # self.map_widget.set_position(-23.65, -70.4)  <- ELIMINAR ESTA LÍNEA
        # self.map_widget.set_zoom(12)                   <- ELIMINAR ESTA LÍNEA
        self.map_widget.add_left_click_map_command(self.obtener_coordenadas)

        btn_confirmar = tk.Button(self, text="Confirmar", command=self.confirmar)
        btn_confirmar.pack(pady=10)

    def obtener_coordenadas(self, coordenadas):
        self.lat, self.lon = coordenadas
        self.map_widget.set_marker(self.lat, self.lon, text="Seleccionado")
        #Elimina todos los marcadores, menos el ultimo
        marcadores = self.map_widget.canvas_marker_list[:]
        if marcadores:
            for marker in marcadores[:-1]:
                marker.delete()


    def confirmar(self):
        #DEBUG: print(f"DEBUG: confirmar en MapaDialog se ejecutó, tipo: {self.tipo}")
        geolocalizador = Nominatim(user_agent="aplicacion_rutas")
        try:
            direccion = geolocalizador.reverse((self.lat, self.lon), exactly_one=True, language="es")
            if direccion:
                direccion_str = direccion.address
            else:
                direccion_str = "Dirección no encontrada"
        except Exception as e:
            print(f"Error al obtener la dirección: {e}")
            direccion_str = "Error al obtener la dirección"

        # Llamar a actualizar_campos de la instancia de Aplicacion:
        self.aplicacion.actualizar_campos(direccion_str, self.lat, self.lon, self.tipo)  # Usar self.aplicacion
        self.withdraw()  # Oculta la ventana en lugar de destruirla

if __name__ == "__main__":
    root = tk.Tk()
    app = Aplicacion(root)
    root.mainloop()
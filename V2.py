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

# --- Asegurar el directorio de trabajo correcto ---
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

class Nodo:
    def __init__(self, id_ruta, nombre, distancia, partida=None, destino=None, lat_partida=None, lon_partida=None,
                 lat_destino=None, lon_destino=None, capacidad=0, carga_actual=0):
        self.id_ruta = id_ruta
        self.nombre = nombre
        self.distancia = distancia
        self.partida = partida
        self.destino = destino
        self.latitud_partida = lat_partida
        self.longitud_partida = lon_partida
        self.latitud_destino = lat_destino
        self.longitud_destino = lon_destino
        self.izquierda = None
        self.derecha = None
        self.capacidad = capacidad
        self.carga_actual = carga_actual

    def calcular_eficiencia(self):
        """Calcula la eficiencia en base a la carga actual y la capacidad."""
        if self.capacidad <= 0:
            return "N/A"
        porcentaje = (self.carga_actual / self.capacidad) * 100
        if porcentaje < 50:
            return "🔴 Baja"
        elif 50 <= porcentaje < 80:
            return "🟡 Media"
        else:
            return "🟢 Alta"


class ArbolBinarioBusqueda:
    def __init__(self):
        self.raiz = None

    def insertar(self, id_ruta, nombre, distancia, partida=None, destino=None, lat_partida=None, lon_partida=None,
                 lat_destino=None, lon_destino=None, capacidad=0, carga_actual=0):
        print(f"DEBUG (Arbol): Intentando insertar ruta con ID: {id_ruta}")
        if self.buscar(id_ruta) or self.buscar_por_nombre(nombre):
            print(f"DEBUG (Arbol): Ruta con ID {id_ruta} o nombre {nombre} ya existe.")
            return False
        self.raiz = self._insertar_nodo(self.raiz, id_ruta, nombre, distancia, partida, destino, lat_partida,
                                        lon_partida, lat_destino, lon_destino, capacidad, carga_actual)
        print(f"DEBUG (Arbol): Inserción de ruta con ID {id_ruta} exitosa.")
        return True

    def _insertar_nodo(self, nodo, id_ruta, nombre, distancia, partida, destino, lat_partida, lon_partida,
                      lat_destino, lon_destino, capacidad, carga_actual):
        if nodo is None:
            print(f"DEBUG (Arbol): Creando nuevo nodo para ID: {id_ruta}")
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
        return self._buscar_nodo(self.raiz, id_ruta)

    def _buscar_nodo(self, nodo, id_ruta):
        if nodo is None:
            return None
        if nodo.id_ruta == id_ruta:
            return nodo
        if id_ruta < nodo.id_ruta:
            return self._buscar_nodo(nodo.izquierda, id_ruta)
        return self._buscar_nodo(nodo.derecha, id_ruta)

    def buscar_por_nombre(self, nombre):
        return self._buscar_por_nombre(self.raiz, nombre)

    def _buscar_por_nombre(self, nodo, nombre):
        if nodo is None:
            return None
        if nodo.nombre.lower() == nombre.lower():
            return nodo
        izquierda = self._buscar_por_nombre(nodo.izquierda, nombre)
        return izquierda if izquierda else self._buscar_por_nombre(nodo.derecha, nombre)

    def eliminar(self, id_ruta):
        self.raiz, eliminado = self._eliminar_nodo(self.raiz, id_ruta)
        return eliminado

    def _eliminar_nodo(self, nodo, id_ruta):
        if nodo is None:
            return nodo, False
        if id_ruta < nodo.id_ruta:
            nodo.izquierda, eliminado = self._eliminar_nodo(nodo.izquierda, id_ruta)
        elif id_ruta > nodo.id_ruta:
            nodo.derecha, eliminado = self._eliminar_nodo(nodo.derecha, id_ruta)
        else:
            if nodo.izquierda is None:
                return nodo.derecha, True
            elif nodo.derecha is None:
                return nodo.izquierda, True
            sucesor = self._minimo_valor(nodo.derecha)
            nodo.id_ruta, nodo.nombre, nodo.distancia, nodo.partida, nodo.destino, nodo.latitud_partida, nodo.longitud_partida, nodo.latitud_destino, nodo.longitud_destino, nodo.capacidad, nodo.carga_actual = sucesor.id_ruta, sucesor.nombre, sucesor.distancia, sucesor.partida, sucesor.destino, sucesor.latitud_partida, sucesor.longitud_partida, sucesor.latitud_destino, sucesor.longitud_destino, sucesor.capacidad, sucesor.carga_actual
            nodo.derecha, _ = self._eliminar_nodo(nodo.derecha, sucesor.id_ruta)
            return nodo, True
        return nodo, eliminado

    def _minimo_valor(self, nodo):
        while nodo.izquierda:
            nodo = nodo.izquierda
        return nodo

    def obtener_rutas(self):
        print("DEBUG (Arbol): Obteniendo todas las rutas...")
        rutas = []
        self._inorden(self.raiz, rutas)
        print(f"DEBUG (Arbol): Rutas obtenidas: {rutas}")
        return rutas

    def _inorden(self, nodo, rutas):
        if nodo:
            self._inorden(nodo.izquierda, rutas)
            rutas.append((nodo.id_ruta, nodo.nombre, nodo.distancia, nodo.partida, nodo.destino, nodo.latitud_partida,
                          nodo.longitud_partida, nodo.latitud_destino, nodo.longitud_destino, nodo.capacidad, nodo.carga_actual))
            self._inorden(nodo.derecha, rutas)


    def modificar(self, id_ruta, nuevo_nombre, nueva_distancia, nueva_partida, nuevo_destino,
                 lat_partida=None, lon_partida=None, lat_destino=None, lon_destino=None,
                 nueva_capacidad=None, nueva_carga_actual=None):
        print(f"DEBUG (Arbol): Intentando modificar ruta con ID: {id_ruta}")
        nodo = self.buscar(id_ruta)

        if nodo:
            if nuevo_nombre != nodo.nombre and self.buscar_por_nombre(nuevo_nombre):
                print(f"DEBUG (Arbol): Ya existe una ruta con el nombre {nuevo_nombre}")
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

            print(f"DEBUG (Arbol): Modificación de ruta con ID {id_ruta} exitosa.")
            return True

        print(f"DEBUG (Arbol): No se encontró la ruta con ID {id_ruta} para modificar.")
        return False


class Aplicacion:
    def __init__(self, root):
        self.arbol = ArbolBinarioBusqueda()
        self.root = root
        self.root.title("Gestión de Rutas")
        self.root.configure(bg="#E2FFD1")
        self.seleccion_activa = False  # No se usa
        # Variables para almacenar latitud y longitud
        self.latitud_partida = None
        self.longitud_partida = None
        self.latitud_destino = None
        self.longitud_destino = None
        self.mapa_dialog = None
        self.modo_edicion = False # <-- Modo edición

        # --- Título ---
        self.label_titulo = tk.Label(root, text="Gestión de Rutas de Entrega", bg="#E2FFD1", font=("Arial", 16, "bold"))
        self.label_titulo.grid(row=0, column=0, columnspan=5, pady=10, sticky="ew")

        # --- Interfaz ---
        # Usamos un Frame para agrupar los widgets de entrada
        input_frame = tk.Frame(root, bg="#E2FFD1")
        input_frame.grid(row=1, column=0, columnspan=5, padx=10, pady=5, sticky="nsew")
        # Configuramos el frame para que se centre
        input_frame.columnconfigure(0, weight=1)
        input_frame.columnconfigure(1, weight=1)
        input_frame.columnconfigure(2, weight=1)
        input_frame.columnconfigure(3, weight=1)

        # ID
        self.label_id = tk.Label(input_frame, text="ID:", bg="#E3F2FD", font=("Arial", 10, "bold"))
        self.label_id.grid(row=0, column=0, padx=(0, 5), pady=5, sticky="e")
        self.entry_id = tk.Entry(input_frame, width=10)
        self.entry_id.grid(row=0, column=1, padx=(0, 5), pady=5, sticky="w")
        self.entry_id.config(state="normal")  # <-- HABILITADO al inicio
        self.id_info_label = tk.Label(input_frame, text="* (Autogenerado - No utilizar para agregar ruta)", bg="#E3F2FD", font=("Arial", 8, "italic"), fg="red")
        self.id_info_label.grid(row=0, column=2, padx=(0, 10), pady=5, sticky="w")

        # ... (resto de los widgets: Ruta, Partida, Destino, Distancia, Capacidad, Carga Actual) ...
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
        #self.entry_distancia.config(state="disabled") # Ya no es necesario deshabilitarlo

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
        #Configuramos el frame para que se centre
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

         # Vincular clic izquierdo (fuera de la tabla) - Lógica corregida
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
                print(f"DEBUG (obtener_coordenadas): Geocodificación exitosa para '{lugar}'.")
                print(f"DEBUG (obtener_coordenadas): Latitud: {ubicacion.latitude}, Longitud: {ubicacion.longitude}")  # Imprime las coordenadas
                return (ubicacion.latitude, ubicacion.longitude)  # Devuelve latitud, longitud
            else:
                print(f"DEBUG (obtener_coordenadas): No se encontró ubicación para '{lugar}'.")
                messagebox.showerror("Error de Geocodificación", f"No se encontró la ubicación: '{lugar}'")
                return (None, None)  # Devuelve None, None en caso de error
        except GeocoderTimedOut:
            print(f"DEBUG (obtener_coordenadas): Timeout para '{lugar}'.")
            messagebox.showerror("Error de Geocodificación", "El servicio tardó demasiado. Revise su conexión a Internet.")
            return (None, None)
        except GeocoderUnavailable:
            print(f"DEBUG (obtener_coordenadas): Servicio no disponible para '{lugar}'.")
            messagebox.showerror("Error de Geocodificación", "El servicio no está disponible. Intente más tarde.")
            return (None, None)
        except Exception as e:
            print(f"DEBUG (obtener_coordenadas): Error inesperado para '{lugar}': {e}")
            messagebox.showerror("Error de Geocodificación", f"Error inesperado: {e}")
            return (None, None)

    def agregar_ruta(self):
        print("DEBUG: agregar_ruta INICIO")
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
                print("DEBUG: agregar_ruta - Campos obligatorios vacíos")
                return

            # --- Obtener coordenadas SIEMPRE ---
            coordenadas_partida = self.obtener_coordenadas(partida)
            coordenadas_destino = self.obtener_coordenadas(destino)

            if not coordenadas_partida or not coordenadas_destino:
                print("DEBUG: agregar_ruta - Falló la geocodificación")
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
                    print("DEBUG: agregar_ruta - Falló el cálculo de distancia")
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
            print(f"DEBUG: agregar_ruta - ID generado: {id_ruta}")

            # --- Pasar capacidad y carga_actual al constructor del Nodo ---
            exito = self.arbol.insertar(id_ruta, nombre, distancia, partida, destino,
                                        self.latitud_partida, self.longitud_partida,
                                        self.latitud_destino, self.longitud_destino,
                                        capacidad, carga_actual)  # <-- Pasar capacidad y carga
            print(f"DEBUG: agregar_ruta - Resultado de insertar: {exito}")

            if exito:
                self.actualizar_lista()
                messagebox.showinfo("Éxito", "Ruta agregada correctamente.")
                self.limpiar_campos()
            else:
                messagebox.showerror("Error", "Error al agregar la ruta.")

        except Exception as e:
            messagebox.showerror("Error", f"Error inesperado: {e}")
            print(f"DEBUG: agregar_ruta - Error inesperado: {e}")

        finally:
            self.limpiar_campos()
            self.entry_id.config(state="normal")
            print("DEBUG: agregar_ruta FIN")
            
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
            # No es necesario volver a habilitar aquí, ya lo está
            return  # Salir de la función si no hay ID

        if id_ruta.isdigit():
            id_ruta_num = int(id_ruta)  # Convertir a entero *después* de verificar que es dígito
            nodo = self.arbol.buscar(id_ruta_num)
            if nodo:
                # Carga los datos de la ruta encontrada
                self.cargar_ruta_buscada(id_ruta_num)
                # Ya se maneja en _cargar_ruta(): self.entry_id.config(state="disabled")
            else:
                messagebox.showerror("Error", "Ruta no encontrada.")
                self.limpiar_campos()  # Limpiar si no se encuentra, ID queda habilitado

        else:
            messagebox.showerror("Error", "Ingrese un ID válido.")
            self.limpiar_campos()  # Limpiar si el ID no es válido, ID queda habilitado

    def cargar_ruta_buscada(self, id_ruta):
        """Carga los datos de una ruta en los campos para visualización/edición."""
        print("DEBUG: cargar_ruta_buscada - INICIO")
        print(f"DEBUG: cargar_ruta_buscada - Recibí id_ruta: {id_ruta}")

        nodo = self.arbol.buscar(id_ruta)
        print(f"DEBUG: cargar_ruta_buscada - Resultado de arbol.buscar: {nodo}")

        if nodo:
            print("DEBUG: cargar_ruta_buscada - Entrando al IF (nodo encontrado)")

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

            print(f"DEBUG: cargar_ruta_buscada - Coordenadas guardadas: lat_partida={self.latitud_partida}, "
                  f"lon_partida={self.longitud_partida}, lat_destino={self.latitud_destino}, "
                  f"lon_destino={self.longitud_destino}")

            print("DEBUG: cargar_ruta_buscada - FIN (nodo encontrado)")

        else:
            print("DEBUG: cargar_ruta_buscada - FIN (nodo NO encontrado)")

    def eliminar_ruta(self):
        id_ruta = self.entry_id.get()
        if not id_ruta.isdigit():
            messagebox.showerror("Error", "Ingrese un ID válido.")
            return

        if messagebox.askyesno("Confirmar Eliminación", "¿Está seguro de que desea eliminar esta ruta?"):
            if self.arbol.eliminar(int(id_ruta)):
                self.actualizar_lista()
                self.limpiar_campos()
                self.guardar_datos()
            else:
                messagebox.showerror("Error", "Ruta no encontrada.")

    def actualizar_lista(self):
        """Actualiza la lista de rutas en la tabla, aplicando color solo a la palabra 'Alta', 'Media' o 'Baja'."""
        seleccion_actual = self.tree.selection()  # Guardar selección actual

        # Limpiar la tabla antes de actualizar
        for item in self.tree.get_children():
            self.tree.delete(item)

        rutas = self.arbol.obtener_rutas()

        for ruta in rutas:
            id_ruta, nombre, distancia, partida, destino, lat_partida, lon_partida, lat_destino, lon_destino, capacidad, carga_actual = ruta

            # Calcular eficiencia y aplicar color solo a la palabra
            eficiencia = carga_actual / capacidad
            if eficiencia <= 0.4:
                eficiencia_texto = "Baja"
                color_eficiencia = "red"
            elif eficiencia <= 0.7:
                eficiencia_texto = "Media"
                color_eficiencia = "orange"
            else:
                eficiencia_texto = "Alta"
                color_eficiencia = "green"

            # Insertar fila en la tabla sin colores
            item_id = self.tree.insert("", "end", values=(
                id_ruta, nombre, distancia, partida, destino, capacidad, carga_actual, eficiencia_texto
            ))

            # Aplicar color solo a la columna "Eficiencia"
            self.tree.item(item_id, tags=(eficiencia_texto,))

        # Restaurar la selección si es posible
        if seleccion_actual:
            for item in self.tree.get_children():
                valores = self.tree.item(item, 'values')
                if valores and str(valores[0]) in [self.tree.item(s, 'values')[0] for s in seleccion_actual]:
                    self.tree.selection_set(item)  # Restaurar selección

        # Configurar etiquetas de color SOLO para la columna "Eficiencia"
        self.tree.tag_configure("Baja", foreground="red")
        self.tree.tag_configure("Media", foreground="orange")
        self.tree.tag_configure("Alta", foreground="green")

        print("DEBUG: Lista de rutas actualizada con colores en la eficiencia.")

    def seleccionar_ruta(self, event):
        """Maneja la selección de una ruta en la tabla."""
        seleccion = self.tree.selection()  # Obtener la selección actual
        print(f"DEBUG: Selección actual: {seleccion}")

        if not seleccion:  # Si no hay nada seleccionado, salir
            print("DEBUG: No hay selección en la tabla.")
            return

        item = seleccion[0]  # Obtener el primer elemento seleccionado
        valores = self.tree.item(item, "values")  # Obtener los valores
        print(f"DEBUG: Valores obtenidos de la fila: {valores}")

        if not valores or len(valores) < 1:  # Verificar que la fila tenga valores
            print("DEBUG: No hay valores en la fila seleccionada.")
            return
        try:
            id_ruta = valores[0]  # Obtener el ID
            print(f"DEBUG: Ruta seleccionada ID = {id_ruta}")

            #  Asegurar que el ID se muestra
            if hasattr(self, "entry_id"):
                self.entry_id.config(state="normal")
                self.entry_id.delete(0, tk.END)
                self.entry_id.insert(0, id_ruta)
                self.entry_id.config(state="disabled")  # Bloquear

            # Llamar a _cargar_ruta para llenar el resto de los campos
            self._cargar_ruta(item)
            
        except IndexError:
            print("ERROR: No se pudo obtener el ID de la ruta.")
        except Exception as e:
            print(f"ERROR: Ocurrió un problema inesperado en seleccionar_ruta: {e}")



    def limpiar_campos(self, event=None):
        """Limpia los campos de entrada si no hay selección en la tabla."""
        seleccion = self.tree.selection()

        if not seleccion:  # Si no hay nada seleccionado, limpiar
            print("DEBUG: No hay selección activa. Limpiando campos...")
            
            # Habilitar ID para limpiarlo, luego deshabilitarlo
            self.entry_id.config(state="normal")
            self.entry_id.delete(0, tk.END)
            self.entry_id.config(state="disabled")

            # Limpiar los demás campos
            self.entry_nombre.delete(0, tk.END)
            self.entry_distancia.delete(0, tk.END)
            self.entry_partida.delete(0, tk.END)
            self.entry_destino.delete(0, tk.END)
            self.entry_capacidad.delete(0, tk.END)
            self.entry_carga_actual.delete(0, tk.END)

            print("DEBUG: Campos limpiados correctamente.")
        else:
            print("DEBUG: Hay una selección activa. No se limpian los campos.")


    def _cargar_ruta(self, item_id):
        """Carga los datos de la ruta seleccionada en los campos de la interfaz."""
        print(f"DEBUG: _cargar_ruta se ejecutó con item_id = {item_id}")
        try:
            item = self.tree.item(item_id)
            valores = item['values']

            if not valores or len(valores) < 8:  # Verificar que haya suficientes valores
                print("DEBUG: No se pudieron obtener los valores de la fila seleccionada.")
                return

            # Extraer datos asegurando que sean cadenas de texto, y manejando correctamente la eficiencia
            id_ruta, nombre, distancia, partida, destino, capacidad, carga_actual, eficiencia = valores
            id_ruta = str(id_ruta)
            nombre = str(nombre)
            distancia = str(distancia)
            partida = str(partida)
            destino = str(destino)
            capacidad = str(capacidad)
            carga_actual = str(carga_actual)
            #La eficiencia no se carga directamente

            print(f"DEBUG: Cargando datos de ruta - ID: {id_ruta}, Nombre: {nombre}")
            # Buscar la ruta en el árbol *usando el ID* para obtener lat/lon
            nodo = self.arbol.buscar(int(id_ruta))
            if nodo:
                self.latitud_partida = nodo.latitud_partida
                self.longitud_partida = nodo.longitud_partida
                self.latitud_destino = nodo.latitud_destino
                self.longitud_destino = nodo.longitud_destino

            # Llenar los campos de entrada
            self.entry_id.config(state="normal")
            self.entry_id.delete(0, tk.END)
            self.entry_id.insert(0, id_ruta)
            self.entry_id.config(state="disabled") #Siempre se deshabilita

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


            print("DEBUG: Campos actualizados correctamente.")
        except Exception as e:
            print(f"ERROR: No se pudo cargar la ruta seleccionada. Detalles: {e}")



    def modificar_ruta(self):
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
            self.entry_id.config(state="disabled")  # Se bloquea el campo

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
        """Carga datos de ejemplo, o desde CSV si no hay errores."""
        ruta_archivo = os.path.join(os.getcwd(), "rutas_informe.csv")

        if os.path.exists(ruta_archivo):
            try:
                with open(ruta_archivo, "r", newline="", encoding="utf-8") as f:
                    lector_csv = csv.reader(f)
                    encabezados = next(lector_csv, None)

                    # --- MODIFICACIÓN: Adaptar los encabezados al nuevo formato ---
                    if encabezados is None or encabezados[:11] != ["ID", "Ruta", "Distancia (km)", "Partida", "Destino", "Latitud Partida", "Longitud Partida", "Latitud Destino", "Longitud Destino", "Capacidad", "Carga Actual"]:
                        # Si el archivo está vacío o los encabezados son incorrectos, cargar ejemplos
                        print("DEBUG: Encabezados incorrectos o archivo vacío, cargando datos de ejemplo.")
                        self.insertar_datos_ejemplo()
                        self.guardar_datos()  # Guardar los datos de ejemplo
                        return

                    # Si no hay errores en los encabezados, se crea una nueva instancia del árbol y se cargan los datos
                    self.arbol = ArbolBinarioBusqueda()
                    for fila in lector_csv:
                        try:
                            # --- MODIFICACIÓN: Leer solo los primeros 11 valores, ignorar extras ---
                            if len(fila) >= 11:  # Ahora son 11 elementos mínimos, ignoramos el resto si hay más
                                id_ruta, nombre, distancia_str, partida, destino, lat_partida_str, lon_partida_str, lat_destino_str, lon_destino_str, capacidad_str, carga_actual_str = fila[:11]  # Tomar solo los primeros 11 valores
                                distancia = round(float(distancia_str), 2)
                                lat_partida = float(lat_partida_str)
                                lon_partida = float(lon_partida_str)
                                lat_destino = float(lat_destino_str)
                                lon_destino = float(lon_destino_str)
                                capacidad = float(capacidad_str)  # Convertir a float
                                carga_actual = float(carga_actual_str)  # Convertir a float

                                self.arbol.insertar(int(id_ruta), nombre, distancia, partida, destino, lat_partida, lon_partida, lat_destino, lon_destino, capacidad, carga_actual)  # Insertar en el árbol
                            else:
                                print(f"DEBUG: Fila incompleta: {fila}")
                                raise ValueError("Fila incompleta")
                        except (ValueError, IndexError) as e:
                            print(f"DEBUG: Error al leer fila: {fila} - {e}. Se cargarán datos de ejemplo")
                            self.insertar_datos_ejemplo()
                            self.guardar_datos()
                            return

                    self.actualizar_lista()
                    self.guardar_datos()  # Se guarda una vez que se cargan las rutas leídas

            except Exception as e:
                print(f"DEBUG: Error inesperado al cargar datos: {e}")
                self.insertar_datos_ejemplo()
                self.guardar_datos()  # Si hay cualquier otro error, se cargan datos de ejemplo y se guardan

        else:
            print("DEBUG: El archivo CSV no existe. Cargando datos de ejemplo.")
            self.insertar_datos_ejemplo()
            self.guardar_datos()  # Si no hay archivo, se cargan datos de ejemplo y se guardan


    def insertar_datos_ejemplo(self):
        """Inserta datos de prueba en el árbol de rutas y actualiza la interfaz."""
        print("DEBUG: insertando datos de ejemplo...")  # Depuración

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
            print(f"DEBUG: Insertada ruta de ejemplo - ID: {datos[0]}, Nombre: {datos[1]}")  # Depuración por cada inserción

        # 🔹 Asegurar que las rutas aparezcan en la tabla tras la inserción
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

                file.flush()  # Forzar escritura en disco
                # file.close()  # No es necesario, el 'with' ya lo cierra

            print("DEBUG: Datos guardados correctamente en rutas_informe.csv")
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
        print(f"DEBUG: Ruta seleccionada ID = {id_ruta}")
        print(f"DEBUG: Atributos de self -> {dir(self)}")

        # Buscar la ruta en el árbol para obtener sus coordenadas
        nodo = self.arbol.buscar(int(id_ruta))
        if not nodo:
            messagebox.showerror("Error", "No se encontró la ruta en la base de datos.")
            return

        # Extraer coordenadas desde el nodo del árbol
        lat_partida, lon_partida = nodo.latitud_partida, nodo.longitud_partida
        lat_destino, lon_destino = nodo.latitud_destino, nodo.longitud_destino

        # DEBUG: Imprimir coordenadas obtenidas
        print(f"DEBUG: Coordenadas obtenidas - Partida: ({lat_partida}, {lon_partida}), Destino: ({lat_destino}, {lon_destino})")

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

        self.guardar_datos() # Importante guardar despues de actualizar



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
        print(f"DEBUG: confirmar en MapaDialog se ejecutó, tipo: {self.tipo}")
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
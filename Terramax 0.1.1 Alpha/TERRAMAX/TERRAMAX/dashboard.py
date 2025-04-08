import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import datetime
import calendar
import random
from tkcalendar import Calendar
import json
import os
import time
from PIL import Image, ImageTk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from database import Database

# Importar el módulo de animales
try:
    import sys
    import os
    # Asegurarse de que el directorio actual esté en el path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    if current_dir not in sys.path:
        sys.path.append(current_dir)
    
    from animals import AnimalsModule
    print("Módulo de animales importado correctamente")
    ANIMALS_MODULE_AVAILABLE = True
except ImportError as e:
    print(f"Error al importar el módulo de animales: {e}")
    print(f"Directorio actual: {os.path.dirname(os.path.abspath(__file__))}")
    print(f"Archivos en el directorio: {os.listdir(os.path.dirname(os.path.abspath(__file__)))}")
    ANIMALS_MODULE_AVAILABLE = False

try:
    from vaccinations import VaccinationsModule
    VACCINATIONS_MODULE_AVAILABLE = True
except ImportError as e:
    print(f"Error al importar el módulo de vacunaciones: {e}")
    VACCINATIONS_MODULE_AVAILABLE = False

try:
    from treatments import TreatmentsModule
    TREATMENTS_MODULE_AVAILABLE = True
except ImportError as e:
    print(f"Error al importar el módulo de tratamientos: {e}")
    TREATMENTS_MODULE_AVAILABLE = False

class Dashboard:
    def __init__(self, root, logout_callback=None):
        self.root = root
        self.logout_callback = logout_callback
        self.root.title("TERRAMAX - Sistema de Gestión Veterinaria")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 700)
        
        # Inicializar la base de datos
        self.db = Database()
        
        # Definir colores principales
        self.colors = {
            "bg_main": "#f5f5f5",
            "primary": "#3498db",
            "secondary": "#2ecc71",
            "accent": "#e74c3c",
            "warning": "#f39c12",
            "text_dark": "#2c3e50",
            "text_light": "#ecf0f1",
            "card_bg": "#ffffff",
            "sidebar": "#2c3e50",
            "danger": "#e74c3c",
            "bg_accent": "#ecf0f1"  # Agregado el color faltante
        }
        
        # Configurar fuentes
        self.fonts = {
            "header": ("Helvetica", 16, "bold"),
            "subheader": ("Helvetica", 14, "bold"),
            "normal": ("Helvetica", 12),
            "small": ("Helvetica", 10),
            "button": ("Helvetica", 12, "bold"),
            "normal_bold": ("Helvetica", 12, "bold")
        }
        
        # Configurar la estructura principal
        self.setup_main_structure()
        
        # Configurar estilo para los widgets ttk
        style = ttk.Style()
        style.configure("Treeview",
                      background=self.colors["card_bg"],
                      foreground=self.colors["text_dark"],
                      fieldbackground=self.colors["card_bg"])
        
        style.configure("TButton",
                      background=self.colors["primary"],
                      foreground=self.colors["text_light"])
        
        # Construir los componentes de la interfaz
        self.build_header()
        self.build_sidebar()
        self.build_kpi_cards()
        self.build_calendar_section()
        self.build_upcoming_vaccinations()
        self.build_treatments_section()
        self.build_recent_animals()
        self.build_quick_access()
        
        # Actualizar la hora cada segundo
        self.update_clock()
        
        self.vaccinations_module = None
        self.treatments_module = None
    
    def create_sample_data(self):
        """Crear datos de ejemplo en la base de datos"""
        # Verificar si ya hay datos
        animals = self.db.get_animals()
        if animals:
            return
            
        # Datos de ejemplo para animales
        sample_animals = [
            {"name": "Pinto", "species": "Bovino", "breed": "Holstein", "status": "Saludable", "added_date": "2023-11-15"},
            {"name": "Luna", "species": "Equino", "breed": "Criollo", "status": "En tratamiento", "added_date": "2023-11-18"},
            {"name": "Max", "species": "Bovino", "breed": "Angus", "status": "Saludable", "added_date": "2023-11-20"},
            {"name": "Bella", "species": "Porcino", "breed": "Yorkshire", "status": "Saludable", "added_date": "2023-11-21"},
            {"name": "Rocky", "species": "Equino", "breed": "Pura Sangre", "status": "En observación", "added_date": "2023-11-23"},
            {"name": "Daisy", "species": "Bovino", "breed": "Jersey", "status": "Saludable", "added_date": "2023-11-25"}
        ]
        
        # Insertar animales
        for animal in sample_animals:
            animal_id = self.db.add_animal(animal)
            
            # Datos de ejemplo para vacunas
            if animal["name"] == "Pinto":
                self.db.add_vaccination({
                    "animal_id": animal_id,
                    "vaccine_type": "Aftosa",
                    "scheduled_date": "2023-12-05",
                    "status": "Pendiente"
                })
            elif animal["name"] == "Luna":
                self.db.add_vaccination({
                    "animal_id": animal_id,
                    "vaccine_type": "Tétanos",
                    "scheduled_date": "2023-12-02",
                    "status": "Pendiente"
                })
            
            # Datos de ejemplo para tratamientos
            if animal["name"] == "Luna":
                self.db.add_treatment({
                    "animal_id": animal_id,
                    "treatment_type": "Antibiótico",
                    "medication": "Penicilina",
                    "start_date": "2023-11-25",
                    "end_date": "2023-12-05",
                    "status": "En curso",
                    "responsible": "Dr. Martínez"
                })
            elif animal["name"] == "Rocky":
                self.db.add_treatment({
                    "animal_id": animal_id,
                    "treatment_type": "Antiinflamatorio",
                    "medication": "Fenilbutazona",
                    "start_date": "2023-11-22",
                    "end_date": "2023-11-30",
                    "status": "En curso",
                    "responsible": "Dra. Rodríguez"
                })
    
    def __del__(self):
        """Destructor para cerrar la conexión a la base de datos"""
        if hasattr(self, 'db'):
            self.db.close()
        
        # Definir colores principales
        self.colors = {
            "bg_main": "#f5f5f5",
            "primary": "#3498db",
            "secondary": "#2ecc71",
            "accent": "#e74c3c",
            "warning": "#f39c12",
            "text_dark": "#2c3e50",
            "text_light": "#ecf0f1",
            "card_bg": "#ffffff",
            "sidebar": "#2c3e50"
        }
        
        # Configurar fuentes
        self.fonts = {
            "header": ("Helvetica", 16, "bold"),
            "subheader": ("Helvetica", 14, "bold"),
            "normal": ("Helvetica", 12),
            "small": ("Helvetica", 10),
            "button": ("Helvetica", 12, "bold")
        }
    
    def setup_main_structure(self):
        """Configurar la estructura principal del dashboard"""
        # Contenedor principal
        self.main_container = tk.Frame(self.root, bg=self.colors["bg_main"])
        self.main_container.pack(fill=tk.BOTH, expand=True)
        
        # Header
        self.header_frame = tk.Frame(self.main_container, bg=self.colors["primary"], height=70)
        self.header_frame.pack(fill=tk.X)
        self.header_frame.pack_propagate(False)  # Mantener altura fija
        
        # Contenedor para sidebar y contenido
        self.body_container = tk.Frame(self.main_container, bg=self.colors["bg_main"])
        self.body_container.pack(fill=tk.BOTH, expand=True)
        
        # Sidebar
        self.sidebar_frame = tk.Frame(self.body_container, bg=self.colors["sidebar"], width=200)
        self.sidebar_frame.pack(side=tk.LEFT, fill=tk.Y)
        self.sidebar_frame.pack_propagate(False)  # Mantener ancho fijo
        
        # Contenido principal
        self.content_frame = tk.Frame(self.body_container, bg=self.colors["bg_main"])
        self.content_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Crear un canvas con scrollbar para el contenido
        self.canvas = tk.Canvas(self.content_frame, bg=self.colors["bg_main"])
        self.scrollbar = ttk.Scrollbar(self.content_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg=self.colors["bg_main"])
        
        # Configurar el scrolling
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        # Crear ventana en el canvas
        self.canvas_frame = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        
        # Configurar el canvas para expandirse
        self.canvas.bind('<Configure>', self.on_canvas_configure)
        
        # Configurar el scrolling con el mouse
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        
        # Empaquetar canvas y scrollbar
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
        # Configurar el scrollbar
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
    
    def on_canvas_configure(self, event):
        """Ajustar el ancho del frame interno cuando el canvas cambia de tamaño"""
        self.canvas.itemconfig(self.canvas_frame, width=event.width)
    
    def _on_mousewheel(self, event):
        """Manejar el scrolling con la rueda del mouse"""
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    
    def build_header(self):
        """Construir el encabezado del dashboard"""
        # Logo y nombre del programa
        logo_frame = tk.Frame(self.header_frame, bg=self.colors["primary"])
        logo_frame.pack(side=tk.LEFT, padx=20)
        
        logo_label = tk.Label(
            logo_frame, 
            text="TERRAMAX", 
            font=("Helvetica", 22, "bold"),
            fg=self.colors["text_light"],
            bg=self.colors["primary"]
        )
        logo_label.pack(side=tk.LEFT)
        
        subtitle_label = tk.Label(
            logo_frame, 
            text="Sistema Veterinario", 
            font=("Helvetica", 12),
            fg=self.colors["text_light"],
            bg=self.colors["primary"]
        )
        subtitle_label.pack(side=tk.LEFT, padx=10)
        
        # Fecha y Hora
        time_frame = tk.Frame(self.header_frame, bg=self.colors["primary"])
        time_frame.pack(side=tk.RIGHT, padx=20)
        
        self.time_label = tk.Label(
            time_frame,
            text="",
            font=("Helvetica", 12),
            fg=self.colors["text_light"],
            bg=self.colors["primary"]
        )
        self.time_label.pack(side=tk.RIGHT)
        
        # Botón de configuración
        settings_button = tk.Button(
            self.header_frame,
            text="⚙️ Configuración",
            font=self.fonts["normal"],
            bg=self.colors["primary"],
            fg=self.colors["text_light"],
            bd=0,
            padx=10,
            activebackground=self.colors["primary"],
            activeforeground=self.colors["text_light"],
            cursor="hand2",
            command=self.open_settings
        )
        settings_button.pack(side=tk.RIGHT, padx=10)
        
        # Botón de cerrar sesión
        logout_button = tk.Button(
            self.header_frame,
            text="🚪 Cerrar Sesión",
            font=self.fonts["normal"],
            bg=self.colors["primary"],
            fg=self.colors["text_light"],
            bd=0,
            padx=10,
            activebackground=self.colors["primary"],
            activeforeground=self.colors["text_light"],
            cursor="hand2",
            command=self.logout
        )
        logout_button.pack(side=tk.RIGHT, padx=10)
    
    def build_sidebar(self):
        """Construir la barra lateral con menú de navegación"""
        # Título del menú
        menu_title = tk.Label(
            self.sidebar_frame,
            text="MENÚ PRINCIPAL",
            font=self.fonts["subheader"],
            bg=self.colors["sidebar"],
            fg=self.colors["text_light"],
            pady=15
        )
        menu_title.pack(fill=tk.X)
        
        # Diccionario para almacenar referencias a los botones
        self.menu_buttons = {}
        
        # Opciones del menú
        menu_options = [
            ("dashboard", "🏠 Dashboard", self.show_dashboard),
            ("animals", "🐄 Animales", self.show_animals),
            ("vaccinations", "💉 Vacunación", self.show_vaccinations),
            ("treatments", "📋 Tratamientos", self.show_treatments),
            ("reports", "📊 Reportes", self.show_reports),
            ("users", "👥 Usuarios", self.show_users),
        ]
        
        for menu_id, text, command in menu_options:
            button = tk.Button(
                self.sidebar_frame,
                text=text,
                font=self.fonts["normal"],
                bg=self.colors["sidebar"],
                fg=self.colors["text_light"],
                bd=0,
                padx=10,
                pady=10,
                activebackground="#1f2c39",  # Un poco más claro que el fondo
                activeforeground=self.colors["text_light"],
                anchor="w",
                width=20,
                cursor="hand2",
                command=command
            )
            button.pack(fill=tk.X)
            # Guardar referencia al botón para poder cambiar su estilo
            self.menu_buttons[menu_id] = button
        
        # Separador
        separator = ttk.Separator(self.sidebar_frame, orient='horizontal')
        separator.pack(fill=tk.X, pady=10)
        
        # Información adicional
        info_label = tk.Label(
            self.sidebar_frame,
            text="TERRAMAX v1.0",
            font=self.fonts["small"],
            bg=self.colors["sidebar"],
            fg=self.colors["text_light"]
        )
        info_label.pack(side=tk.BOTTOM, pady=10)
    
    def build_kpi_cards(self):
        """Construir las tarjetas de KPI"""
        # Obtener datos de la base de datos
        animals = self.db.get_animals()
        vaccinations = self.db.get_vaccinations(status="Pendiente")
        treatments = self.db.get_treatments()
        
        # Calcular métricas
        total_animals = len(animals)
        pending_vaccinations = len(vaccinations)
        active_treatments = len([t for t in treatments if t[6] == "En curso"])  # t[6] es el status
        
        # Crear frame para las tarjetas
        kpi_frame = tk.Frame(self.scrollable_frame, bg=self.colors["bg_main"])
        kpi_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Configurar grid
        kpi_frame.grid_columnconfigure(0, weight=1)
        kpi_frame.grid_columnconfigure(1, weight=1)
        kpi_frame.grid_columnconfigure(2, weight=1)
        
        # Crear tarjetas
        self.create_kpi_card(
            kpi_frame,
            "Animales Totales",
            total_animals,
            "🐾",
            self.colors["primary"]
        )
        
        self.create_kpi_card(
            kpi_frame,
            "Vacunas Pendientes",
            pending_vaccinations,
            "💉",
            self.colors["warning"]
        )
        
        self.create_kpi_card(
            kpi_frame,
            "Tratamientos Activos",
            active_treatments,
            "🏥",
            self.colors["accent"]
        )

    def create_kpi_card(self, parent, title, value, icon, color):
        """Crear una tarjeta individual de KPI"""
        card = tk.Frame(parent, bg=self.colors["card_bg"], padx=15, pady=15, bd=0)
        card.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)
        
        # Añadir sombra a la tarjeta (simulada con borde)
        card.config(highlightbackground="#dddddd", highlightthickness=1)
        
        # Ícono
        icon_label = tk.Label(
            card,
            text=icon,
            font=("Helvetica", 24),
            bg=self.colors["card_bg"],
            fg=color
        )
        icon_label.pack(anchor="w")
        
        # Valor
        value_label = tk.Label(
            card,
            text=str(value),
            font=("Helvetica", 28, "bold"),
            fg=color,
            bg=self.colors["card_bg"]
        )
        value_label.pack(anchor="w")
        
        # Título
        title_label = tk.Label(
            card,
            text=title,
            font=self.fonts["normal"],
            fg=self.colors["text_dark"],
            bg=self.colors["card_bg"]
        )
        title_label.pack(anchor="w")
        
        return card
    
    def build_calendar_section(self):
        """Construir la sección del calendario"""
        # Título de la sección
        self.calendar_section = tk.Frame(self.scrollable_frame, bg=self.colors["bg_main"], pady=15)
        self.calendar_section.pack(fill=tk.X, padx=20, pady=10)
        
        title_label = tk.Label(
            self.calendar_section,
            text="Calendario de Vacunación",
            font=self.fonts["header"],
            bg=self.colors["bg_main"],
            fg=self.colors["text_dark"]
        )
        title_label.pack(anchor="w")
        
        # Contenedor principal para calendario y eventos
        calendar_container = tk.Frame(self.calendar_section, bg=self.colors["bg_main"])
        calendar_container.pack(fill=tk.X, pady=10)
        
        # Panel izquierdo - Calendario
        calendar_frame = tk.Frame(calendar_container, bg=self.colors["card_bg"], padx=15, pady=15)
        calendar_frame.pack(side=tk.LEFT, fill=tk.BOTH, padx=(0,10))
        calendar_frame.config(highlightbackground="#dddddd", highlightthickness=1)
        
        try:
            # Crear calendario
            current_date = datetime.datetime.now()
            self.cal = Calendar(
                calendar_frame, 
                selectmode='day',
                year=current_date.year, 
                month=current_date.month,
                day=current_date.day,
                background=self.colors["card_bg"],
                foreground=self.colors["text_dark"],
                bordercolor=self.colors["card_bg"],
                headersbackground=self.colors["primary"],
                headersforeground=self.colors["text_light"],
                selectbackground=self.colors["secondary"],
                normalbackground=self.colors["card_bg"],
                weekendbackground=self.colors["card_bg"],
                othermonthbackground="#f0f0f0",
                othermonthforeground="#a0a0a0"
            )
            self.cal.pack(padx=10, pady=10)
            
            # Botón para actualizar el calendario manualmente (para depuración)
            refresh_btn = tk.Button(
                calendar_frame,
                text="🔄 Actualizar Calendario",
                font=self.fonts["normal"],
                bg=self.colors["accent"],
                fg=self.colors["text_light"],
                padx=10,
                pady=5,
                relief=tk.FLAT,
                cursor="hand2",
                command=self.refresh_calendar
            )
            refresh_btn.pack(pady=5, fill=tk.X)
            
            # Botón para ver detalles del día seleccionado
            view_button = tk.Button(
                calendar_frame,
                text="Ver Detalles del Día",
                font=self.fonts["normal"],
                bg=self.colors["primary"],
                fg=self.colors["text_light"],
                padx=10,
                pady=5,
                relief=tk.FLAT,
                cursor="hand2",
                command=self.view_day_details
            )
            view_button.pack(pady=10, fill=tk.X)
            
            # Botón para agregar nueva vacuna
            add_button = tk.Button(
                calendar_frame,
                text="+ Agregar Nueva Vacuna",
                font=self.fonts["normal"],
                bg=self.colors["secondary"],
                fg=self.colors["text_light"],
                padx=10,
                pady=5,
                relief=tk.FLAT,
                cursor="hand2",
                command=self.add_new_vaccine
            )
            add_button.pack(pady=5, fill=tk.X)
            
            # Panel derecho - Eventos del día
            self.events_frame = tk.Frame(calendar_container, bg=self.colors["card_bg"], padx=15, pady=15)
            self.events_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            self.events_frame.config(highlightbackground="#dddddd", highlightthickness=1)
            
            # Título de eventos
            today_str = current_date.strftime("%d/%m/%Y")
            self.events_title = tk.Label(
                self.events_frame,
                text=f"Eventos para: {today_str}",
                font=self.fonts["subheader"],
                bg=self.colors["card_bg"],
                fg=self.colors["text_dark"]
            )
            self.events_title.pack(anchor="w", pady=5)
            
            # Lista de eventos
            self.events_list = tk.Frame(self.events_frame, bg=self.colors["card_bg"])
            self.events_list.pack(fill=tk.BOTH, expand=True, pady=10)
            
            # Si hay eventos para hoy, mostrarlos
            today_str_iso = current_date.strftime("%Y-%m-%d")
            self.show_events_for_date(today_str_iso)
            
            # Actualizar el calendario para mostrar los eventos
            self.refresh_calendar()
            
        except Exception as e:
            print(f"Error al construir el calendario: {str(e)}")
            import traceback
            traceback.print_exc()
            messagebox.showerror("Error", "No se pudo cargar el calendario. Por favor verifique que tkcalendar esté instalado correctamente.")
    
    def show_events_for_date(self, date_str):
        """Mostrar eventos para una fecha específica"""
        try:
            print(f"Intentando mostrar eventos para la fecha: {date_str}")
            
            # Convertir la fecha a formato YYYY-MM-DD
            if isinstance(date_str, datetime.datetime):
                selected_date = date_str.strftime("%Y-%m-%d")
            else:
                try:
                    selected_date = datetime.datetime.strptime(date_str, "%d/%m/%Y").strftime("%Y-%m-%d")
                except ValueError:
                    try:
                        selected_date = datetime.datetime.strptime(date_str, "%Y-%m-%d").strftime("%Y-%m-%d")
                    except ValueError:
                        try:
                            # Formato del calendario tkcalendar: MM/DD/YY
                            selected_date = datetime.datetime.strptime(date_str, "%m/%d/%y").strftime("%Y-%m-%d")
                        except ValueError:
                            print(f"Error: Formato de fecha no válido - {date_str}")
                            messagebox.showerror("Error", "Formato de fecha no válido")
                            return

            print(f"Fecha seleccionada (formato ISO): {selected_date}")
            
            # Obtener las vacunaciones programadas para esta fecha
            vaccinations = self.db.get_vaccinations(scheduled_date=selected_date)
            print(f"Vacunaciones encontradas: {len(vaccinations)}")
            for i, v in enumerate(vaccinations):
                print(f"  Vacunación {i+1}: {v}")
            
            # Limpiar el frame de eventos si existe
            if hasattr(self, 'events_frame') and self.events_frame:
                for widget in self.events_frame.winfo_children():
                    widget.destroy()
            else:
                print("ADVERTENCIA: No se encontró el frame de eventos")
                return
            
            # Título de la sección
            events_title = tk.Label(
                self.events_frame,
                text=f"Eventos para: {self.format_date(selected_date)}",
                font=self.fonts["subheader"],
                bg=self.colors["card_bg"],
                fg=self.colors["text_dark"]
            )
            events_title.pack(pady=10)
            
            if not vaccinations:
                no_events_label = tk.Label(
                    self.events_frame,
                    text="No hay eventos programados para esta fecha",
                    font=self.fonts["normal"],
                    bg=self.colors["card_bg"],
                    fg=self.colors["text_dark"]
                )
                no_events_label.pack(pady=5)
                return
            
            # Crear tabla de eventos
            columns = ("animal", "tipo", "estado")
            events_table = ttk.Treeview(
                self.events_frame,
                columns=columns,
                show="headings",
                height=5
            )
            
            # Configurar columnas
            events_table.heading("animal", text="Animal")
            events_table.heading("tipo", text="Tipo de Vacuna")
            events_table.heading("estado", text="Estado")
            
            events_table.column("animal", width=150)
            events_table.column("tipo", width=150)
            events_table.column("estado", width=100)
            
            # Agregar scrollbar
            scrollbar = ttk.Scrollbar(self.events_frame, orient=tk.VERTICAL, command=events_table.yview)
            events_table.configure(yscrollcommand=scrollbar.set)
            
            # Empaquetar tabla y scrollbar
            events_table.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
            # Llenar la tabla con los eventos
            for vaccination in vaccinations:
                try:
                    # Extraer datos con manejo seguro de índices
                    animal_name = vaccination[7] if len(vaccination) > 7 else "Desconocido"
                    vaccine_type = vaccination[2] if len(vaccination) > 2 else "No especificado"
                    status = vaccination[5] if len(vaccination) > 5 else "Pendiente"
                    
                    values = (animal_name, vaccine_type, status)
                    event_id = events_table.insert("", tk.END, values=values)
                    
                    # Dar color según estado
                    if status == "Vencida":
                        events_table.tag_configure("expired", background="#ffdddd")
                        events_table.item(event_id, tags=("expired",))
                    elif status == "Aplicada":
                        events_table.tag_configure("applied", background="#ddffdd")
                        events_table.item(event_id, tags=("applied",))
                    
                except Exception as e:
                    print(f"Error al procesar vacunación individual: {str(e)}")
                    import traceback
                    traceback.print_exc()
                    continue
            
            # Vincular doble clic para ver detalles
            events_table.bind("<Double-1>", lambda e: self.show_vaccination_details(events_table))
            
        except Exception as e:
            print(f"Error al mostrar eventos: {str(e)}")
            import traceback
            traceback.print_exc()
            messagebox.showerror("Error", f"No se pudo procesar la fecha seleccionada: {str(e)}")
    
    def show_vaccination_details(self, table):
        """Mostrar detalles de una vacunación seleccionada"""
        try:
            selection = table.selection()
            if not selection:
                return
                
            item = selection[0]
            values = table.item(item)["values"]
            
            if not values or len(values) < 2:
                print("Valores insuficientes en la selección")
                return
                
            print(f"Valores seleccionados en tabla: {values}")
            
            # Valores de la tabla: (animal_name, vaccine_type, status)
            animal_name = values[0]
            vaccine_type = values[1]
            
            # Obtener vacunaciones para la fecha seleccionada
            selected_date = self.cal.get_date()
            try:
                date_obj = datetime.datetime.strptime(selected_date, "%m/%d/%y")
                iso_date = date_obj.strftime("%Y-%m-%d")
                print(f"Buscando vacunaciones para fecha: {iso_date}")
                
                # Obtener vacunaciones para esta fecha
                vaccinations = self.db.get_vaccinations(scheduled_date=iso_date)
                print(f"Vacunaciones encontradas para la fecha {iso_date}: {len(vaccinations)}")
                
                # Encontrar la vacunación específica basada en el animal y tipo de vacuna
                vaccination = None
                for v in vaccinations:
                    v_animal_name = v[7] if len(v) > 7 else "Desconocido"
                    v_vaccine_type = v[2] if len(v) > 2 else "Desconocido"
                    
                    print(f"Comparando: {v_animal_name} == {animal_name} y {v_vaccine_type} == {vaccine_type}")
                    
                    if v_animal_name == animal_name and v_vaccine_type == vaccine_type:
                        vaccination = v
                        print(f"¡Coincidencia encontrada! Vacunación: {vaccination}")
                        break
                
                if not vaccination:
                    print("No se encontró vacunación coincidente con los valores seleccionados")
                    messagebox.showinfo("Detalles de Vacunación", "No se encontraron detalles adicionales para esta vacunación")
                    return
                
                # Crear una ventana de detalles
                details_window = tk.Toplevel()
                details_window.title("Detalles de Vacunación")
                details_window.transient(self.root)
                details_window.grab_set()
                
                # Frame principal
                main_frame = tk.Frame(details_window, bg=self.colors["bg_main"], padx=20, pady=20)
                main_frame.pack(fill=tk.BOTH, expand=True)
                
                # Título
                title_label = tk.Label(
                    main_frame,
                    text="Detalles de Vacunación",
                    font=self.fonts["header"],
                    bg=self.colors["bg_main"],
                    fg=self.colors["text_dark"]
                )
                title_label.pack(pady=(0, 20))
                
                # Frame para los detalles
                details_frame = tk.Frame(main_frame, bg=self.colors["card_bg"], padx=15, pady=15)
                details_frame.pack(fill=tk.BOTH, expand=True)
                details_frame.config(highlightbackground="#dddddd", highlightthickness=1)
                
                # Información detallada
                details = [
                    ("ID:", vaccination[0]),
                    ("Animal:", animal_name),
                    ("Tipo de Vacuna:", vaccination[2]),
                    ("Fecha Programada:", self.format_date(vaccination[3]) if vaccination[3] else "No especificada"),
                    ("Estado:", vaccination[5] if len(vaccination) > 5 else "Pendiente"),
                    ("Notas:", vaccination[4] if len(vaccination) > 4 else "Sin notas")
                ]
                
                for label, value in details:
                    frame = tk.Frame(details_frame, bg=self.colors["card_bg"])
                    frame.pack(fill=tk.X, pady=5)
                    
                    label_widget = tk.Label(
                        frame,
                        text=label,
                        font=self.fonts["normal_bold"],
                        bg=self.colors["card_bg"],
                        fg=self.colors["text_dark"],
                        width=20,
                        anchor="w"
                    )
                    label_widget.pack(side=tk.LEFT, padx=5)
                    
                    value_widget = tk.Label(
                        frame,
                        text=str(value),
                        font=self.fonts["normal"],
                        bg=self.colors["card_bg"],
                        fg=self.colors["text_dark"],
                        anchor="w"
                    )
                    value_widget.pack(side=tk.LEFT, fill=tk.X, expand=True)
                
                # Botones de acción
                buttons_frame = tk.Frame(main_frame, bg=self.colors["bg_main"], pady=20)
                buttons_frame.pack(fill=tk.X)
                
                current_status = vaccination[5] if len(vaccination) > 5 else "Pendiente"
                if current_status == "Pendiente":
                    mark_button = tk.Button(
                        buttons_frame,
                        text="Marcar como Aplicada",
                        font=self.fonts["normal"],
                        bg=self.colors["primary"],
                        fg=self.colors["text_light"],
                        padx=10,
                        relief=tk.FLAT,
                        cursor="hand2",
                        command=lambda: self.mark_as_applied({"id": vaccination[0], "vaccine_type": vaccination[2], "animal_name": animal_name}, details_window)
                    )
                    mark_button.pack(side=tk.LEFT, padx=5)
                
                close_button = tk.Button(
                    buttons_frame,
                    text="Cerrar",
                    font=self.fonts["normal"],
                    bg=self.colors["accent"],
                    fg=self.colors["text_light"],
                    padx=10,
                    relief=tk.FLAT,
                    cursor="hand2",
                    command=details_window.destroy
                )
                close_button.pack(side=tk.RIGHT, padx=5)
                
                # Centrar la ventana
                details_window.update_idletasks()
                width = details_window.winfo_width()
                height = details_window.winfo_height()
                x = (details_window.winfo_screenwidth() // 2) - (width // 2)
                y = (details_window.winfo_screenheight() // 2) - (height // 2)
                details_window.geometry('{}x{}+{}+{}'.format(width, height, x, y))
            except Exception as e:
                print(f"Error al procesar vacunación: {str(e)}")
                import traceback
                traceback.print_exc()
                messagebox.showinfo("Detalles de Vacunación", "No se pudieron obtener los detalles de la vacunación")
        except Exception as e:
            print(f"Error al mostrar detalles de vacunación: {str(e)}")
            import traceback
            traceback.print_exc()
            messagebox.showerror("Error", "No se pudieron mostrar los detalles de la vacunación")
    
    def mark_as_applied(self, event, window=None):
        """Marcar una vacuna como aplicada"""
        if messagebox.askyesno("Confirmar Aplicación", 
                              f"¿Confirma que la vacuna {event['vaccine_type']} fue aplicada a {event['animal_name']}?"):
            try:
                print(f"Marcando vacunación como aplicada: ID={event['id']}, Tipo={event['vaccine_type']}, Animal={event['animal_name']}")
                
                # Actualizar en la base de datos
                update_data = {
                    "status": "Aplicada",
                    "applied_date": datetime.datetime.now().strftime("%Y-%m-%d")
                }
                success = self.db.update_vaccination(event["id"], update_data)
                
                if not success:
                    print("Error: La actualización del estado de vacunación falló")
                    messagebox.showerror("Error", "No se pudo actualizar el estado de la vacunación")
                    return
                    
                print("Vacunación marcada como aplicada exitosamente")
                
                # Cerrar la ventana de detalles si existe
                if window:
                    window.destroy()
                    
                # Actualizar vista
                selected_date = self.cal.get_date()
                date_obj = datetime.datetime.strptime(selected_date, "%m/%d/%y")
                iso_date = date_obj.strftime("%Y-%m-%d")
                
                # Actualizar el calendario y sus eventos
                self.refresh_calendar()
                
                # Actualizar la vista del calendario
                self.show_events_for_date(iso_date)
                
                # Si estamos en el módulo de vacunaciones, actualizar su vista también
                if hasattr(self, 'vaccinations_module'):
                    self.vaccinations_module.show_list_view()
                
                messagebox.showinfo("Éxito", "La vacunación ha sido marcada como aplicada")
            except Exception as e:
                print(f"Error al marcar vacunación como aplicada: {str(e)}")
                import traceback
                traceback.print_exc()
                messagebox.showerror("Error", "No se pudo actualizar el estado de la vacunación")
    
    def view_day_details(self):
        """Ver detalles del día seleccionado en el calendario"""
        selected_date = self.cal.get_date()
        # Convertir fecha seleccionada (MM/DD/YY) a formato ISO (YYYY-MM-DD)
        try:
            date_obj = datetime.datetime.strptime(selected_date, "%m/%d/%y")
            iso_date = date_obj.strftime("%Y-%m-%d")
            
            # Limpiar el frame de eventos
            for widget in self.events_frame.winfo_children():
                widget.destroy()
            
            # Actualizar título de eventos
            formatted_date = date_obj.strftime("%d/%m/%Y")
            events_title = tk.Label(
                self.events_frame,
                text=f"Eventos para: {formatted_date}",
                font=self.fonts["subheader"],
                bg=self.colors["card_bg"],
                fg=self.colors["text_dark"]
            )
            events_title.pack(pady=10)
            
            # Obtener las vacunaciones programadas para esta fecha
            vaccinations = self.db.get_vaccinations(scheduled_date=iso_date)
            
            if not vaccinations:
                no_events_label = tk.Label(
                    self.events_frame,
                    text="No hay eventos programados para esta fecha",
                    font=self.fonts["normal"],
                    bg=self.colors["card_bg"],
                    fg=self.colors["text_dark"]
                )
                no_events_label.pack(pady=5)
                return
            
            # Crear tabla de eventos
            columns = ("animal", "tipo", "estado")
            events_table = ttk.Treeview(
                self.events_frame,
                columns=columns,
                show="headings",
                height=5
            )
            
            # Configurar columnas
            events_table.heading("animal", text="Animal")
            events_table.heading("tipo", text="Tipo de Vacuna")
            events_table.heading("estado", text="Estado")
            
            events_table.column("animal", width=150)
            events_table.column("tipo", width=150)
            events_table.column("estado", width=100)
            
            # Agregar scrollbar
            scrollbar = ttk.Scrollbar(self.events_frame, orient=tk.VERTICAL, command=events_table.yview)
            events_table.configure(yscrollcommand=scrollbar.set)
            
            # Empaquetar tabla y scrollbar
            events_table.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
            # Llenar la tabla con los eventos
            for vaccination in vaccinations:
                try:
                    # Extraer datos con manejo seguro de índices
                    animal_name = vaccination[7] if len(vaccination) > 7 else "Desconocido"
                    vaccine_type = vaccination[2] if len(vaccination) > 2 else "No especificado"
                    status = vaccination[5] if len(vaccination) > 5 else "Pendiente"
                    
                    values = (animal_name, vaccine_type, status)
                    event_id = events_table.insert("", tk.END, values=values)
                    
                    # Dar color según estado
                    if status == "Vencida":
                        events_table.tag_configure("expired", background="#ffdddd")
                        events_table.item(event_id, tags=("expired",))
                    elif status == "Aplicada":
                        events_table.tag_configure("applied", background="#ddffdd")
                        events_table.item(event_id, tags=("applied",))
                    
                except Exception as e:
                    print(f"Error al procesar vacunación individual: {str(e)}")
                    continue
            
            # Vincular doble clic para ver detalles
            events_table.bind("<Double-1>", lambda e: self.show_vaccination_details(events_table))
            
        except Exception as e:
            print(f"Error al procesar fecha: {str(e)}")
            messagebox.showwarning("Error", "No se pudo procesar la fecha seleccionada")
    
    def add_new_vaccine(self):
        """Agregar una nueva vacuna al calendario"""
        if not VACCINATIONS_MODULE_AVAILABLE:
            messagebox.showinfo("Nueva Vacuna", "Aquí se abriría un formulario para agregar una nueva vacuna al calendario")
            return
            
        # Simplemente llamamos al método show_vaccinations() y luego le indicamos que muestre el formulario de nueva vacunación
        self.show_vaccinations()
    
    def show_vaccinations(self):
        """Mostrar el módulo de vacunaciones"""
        # Limpiar contenido actual
        self.clear_content()
        
        if not VACCINATIONS_MODULE_AVAILABLE:
            messagebox.showerror("Error", "El módulo de vacunaciones no está disponible. Por favor, verifique que el archivo vaccinations.py existe en el directorio correcto.")
            return
            
        try:
            # Crear contenedor para el módulo de vacunaciones
            vaccinations_container = tk.Frame(self.scrollable_frame, bg=self.colors["bg_main"])
            vaccinations_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
            
            # Crear instancia del módulo de vacunaciones
            self.vaccinations_module = VaccinationsModule(
                vaccinations_container,
                colors=self.colors,
                fonts=self.fonts
            )
            
            # Mostrar la vista de lista por defecto
            self.vaccinations_module.show_list_view()
            
            # Actualizar botón activo en el menú
            self.set_active_menu("vaccinations")
            
            # Configurar el canvas para que se ajuste al nuevo contenido
            self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar el módulo de vacunaciones: {str(e)}")
    
    def show_treatments(self):
        """Mostrar el módulo de tratamientos"""
        # Limpiar contenido actual
        self.clear_content()
        
        if not TREATMENTS_MODULE_AVAILABLE:
            messagebox.showerror("Error", "El módulo de tratamientos no está disponible. Por favor, verifique que el archivo treatments.py existe en el directorio correcto.")
            return
            
        try:
            # Crear contenedor para el módulo de tratamientos
            treatments_container = tk.Frame(self.scrollable_frame, bg=self.colors["bg_main"])
            treatments_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
            
            # Crear instancia del módulo de tratamientos
            self.treatments_module = TreatmentsModule(
                treatments_container,
                colors=self.colors,
                fonts=self.fonts
            )
            
            # Mostrar la vista de lista por defecto
            self.treatments_module.show_list_view()
            
            # Actualizar botón activo en el menú
            self.set_active_menu("treatments")
            
            # Configurar el canvas para que se ajuste al nuevo contenido
            self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar el módulo de tratamientos: {str(e)}")
    
    def show_reports(self):
        """Mostrar el módulo de reportes"""
        # Limpiar contenido actual
        self.clear_content()
        
        # Crear contenedor para el módulo de reportes
        reports_container = tk.Frame(self.scrollable_frame, bg=self.colors["bg_main"])
        reports_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Título
        title_label = tk.Label(
            reports_container,
            text="Reportes",
            font=self.fonts["header"],
            bg=self.colors["bg_main"],
            fg=self.colors["text_dark"]
        )
        title_label.pack(pady=20)
        
        # Mensaje temporal
        message_label = tk.Label(
            reports_container,
            text="El módulo de reportes estará disponible próximamente",
            font=self.fonts["normal"],
            bg=self.colors["bg_main"],
            fg=self.colors["text_dark"]
        )
        message_label.pack(pady=10)
        
        # Actualizar botón activo en el menú
        self.set_active_menu("reports")
        
        # Configurar el canvas para que se ajuste al nuevo contenido
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
    
    def show_users(self):
        """Mostrar el módulo de usuarios"""
        # Limpiar contenido actual
        self.clear_content()
        
        # Crear contenedor para el módulo de usuarios
        users_container = tk.Frame(self.scrollable_frame, bg=self.colors["bg_main"])
        users_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Título
        title_label = tk.Label(
            users_container,
            text="Gestión de Usuarios",
            font=self.fonts["header"],
            bg=self.colors["bg_main"],
            fg=self.colors["text_dark"]
        )
        title_label.pack(pady=20)
        
        # Mensaje temporal
        message_label = tk.Label(
            users_container,
            text="El módulo de usuarios estará disponible próximamente",
            font=self.fonts["normal"],
            bg=self.colors["bg_main"],
            fg=self.colors["text_dark"]
        )
        message_label.pack(pady=10)
        
        # Actualizar botón activo en el menú
        self.set_active_menu("users")
        
        # Configurar el canvas para que se ajuste al nuevo contenido
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
    
    def clear_content(self):
        """Limpiar el contenido actual"""
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        
        # Limpiar referencias a módulos
        if hasattr(self, 'animals_module'):
            del self.animals_module
        if hasattr(self, 'vaccinations_module'):
            del self.vaccinations_module
        if hasattr(self, 'treatments_module'):
            del self.treatments_module
    
    def set_active_menu(self, active_item):
        """Establecer la opción activa en el menú lateral"""
        # Restaurar estilo normal para todos los botones
        for key, button in self.menu_buttons.items():
            button.config(
                bg=self.colors["sidebar"],
                fg=self.colors["text_light"]
            )
            
        # Resaltar el botón activo
        if active_item in self.menu_buttons:
            self.menu_buttons[active_item].config(
                bg="#1f2c39",  # Un poco más claro que el fondo del sidebar
                fg=self.colors["text_light"]
            )

    def build_upcoming_vaccinations(self):
        """Construir la sección de próximas vacunas"""
        try:
            print("Iniciando construcción de sección de vacunaciones...")
            # Título de la sección
            vaccinations_section = tk.Frame(self.scrollable_frame, bg=self.colors["bg_main"], pady=15)
            vaccinations_section.pack(fill=tk.X, padx=20, pady=10)
            
            title_frame = tk.Frame(vaccinations_section, bg=self.colors["bg_main"])
            title_frame.pack(fill=tk.X)
            
            title_label = tk.Label(
                title_frame,
                text="Próximas Vacunas",
                font=self.fonts["header"],
                bg=self.colors["bg_main"],
                fg=self.colors["text_dark"]
            )
            title_label.pack(side=tk.LEFT)
            
            view_all_btn = tk.Button(
                title_frame,
                text="Ver Todas",
                font=self.fonts["small"],
                bg=self.colors["primary"],
                fg=self.colors["text_light"],
                padx=10,
                relief=tk.FLAT,
                cursor="hand2",
                command=self.show_vaccinations
            )
            view_all_btn.pack(side=tk.RIGHT)
            
            # Marco para la tabla
            table_frame = tk.Frame(vaccinations_section, bg=self.colors["card_bg"], padx=15, pady=15)
            table_frame.pack(fill=tk.X, pady=10)
            table_frame.config(highlightbackground="#dddddd", highlightthickness=1)
            
            # Crear tabla con Treeview
            columns = ("animal", "vaccine", "date", "status")
            self.vacc_table = ttk.Treeview(table_frame, columns=columns, show="headings", height=6)
            
            # Definir encabezados
            self.vacc_table.heading("animal", text="Animal")
            self.vacc_table.heading("vaccine", text="Tipo de Vacuna")
            self.vacc_table.heading("date", text="Fecha Programada")
            self.vacc_table.heading("status", text="Estado")
            
            # Definir anchos de columna
            self.vacc_table.column("animal", width=150)
            self.vacc_table.column("vaccine", width=150)
            self.vacc_table.column("date", width=150)
            self.vacc_table.column("status", width=100)
            
            # Agregar scrollbar
            scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.vacc_table.yview)
            self.vacc_table.configure(yscrollcommand=scrollbar.set)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            self.vacc_table.pack(fill=tk.BOTH, expand=True)
            
            print("Obteniendo vacunaciones de la base de datos...")
            # Obtener las vacunaciones y ordenarlas por fecha
            try:
                vaccinations = self.db.get_vaccinations()
                print(f"Vacunaciones obtenidas: {vaccinations}")
                
                if not vaccinations:
                    # Si no hay vacunaciones, mostrar mensaje
                    no_data_label = tk.Label(
                        table_frame,
                        text="No hay vacunaciones programadas",
                        font=self.fonts["normal"],
                        bg=self.colors["card_bg"],
                        fg=self.colors["text_dark"]
                    )
                    no_data_label.pack(pady=20)
                    return
                
                # Ordenar vacunaciones por fecha
                sorted_vaccinations = sorted(
                    [v for v in vaccinations if v is not None and len(v) >= 4],
                    key=lambda x: x[3] if x[3] else ""
                )
                
                print("Llenando tabla con datos...")
                # Llenar tabla con datos
                for vaccination in sorted_vaccinations:
                    try:
                        # Asegurarse de que tenemos todos los datos necesarios
                        animal_name = vaccination[8] if len(vaccination) > 8 else "Desconocido"
                        vaccine_type = vaccination[2] if len(vaccination) > 2 else "No especificado"
                        scheduled_date = vaccination[3] if len(vaccination) > 3 else "Sin fecha"
                        status = vaccination[5] if len(vaccination) > 5 else "Pendiente"
                        
                        values = (
                            animal_name,
                            vaccine_type,
                            self.format_date(scheduled_date),
                            status
                        )
                        
                        item_id = self.vacc_table.insert("", tk.END, values=values)
                        
                        # Dar color según estado
                        if status == "Vencida":
                            self.vacc_table.tag_configure("expired", background="#ffdddd")
                            self.vacc_table.item(item_id, tags=("expired",))
                        elif status == "Aplicada":
                            self.vacc_table.tag_configure("applied", background="#ddffdd")
                            self.vacc_table.item(item_id, tags=("applied",))
                            
                    except Exception as e:
                        print(f"Error al procesar vacunación individual: {str(e)}")
                        continue
                
                # Vincular evento de doble clic
                self.vacc_table.bind("<Double-1>", self.on_vaccination_click)
                
            except Exception as db_error:
                print(f"Error al obtener datos de la base de datos: {str(db_error)}")
                messagebox.showerror("Error", "No se pudieron cargar los datos de vacunaciones")
                return
            
            print("Sección de vacunaciones construida exitosamente")
            
        except Exception as e:
            print(f"Error al construir la sección de vacunaciones: {str(e)}")
            messagebox.showerror("Error", "No se pudo cargar la sección de vacunaciones")
    
    def on_vaccination_click(self, vaccination):
        """Manejar clic en una vacunación"""
        try:
            if not isinstance(vaccination, tuple):
                print("Error: vaccination no es una tupla")
                return
                
            vaccination_id = vaccination[0] if len(vaccination) > 0 else None
            if vaccination_id is None:
                print("Error: No se pudo obtener el ID de la vacunación")
                return
                
            # Obtener los detalles de la vacunación
            vaccination_details = self.db.get_vaccinations(vaccination_id=vaccination_id)
            if not vaccination_details:
                messagebox.showerror("Error", "No se encontró la vacunación seleccionada")
                return
                
            # Mostrar detalles en un mensaje
            vaccination_data = vaccination_details[0]  # Tomar el primer resultado
            animal_name = vaccination_data[8] if len(vaccination_data) > 8 else "Desconocido"
            vaccine_type = vaccination_data[2] if len(vaccination_data) > 2 else "No especificado"
            scheduled_date = vaccination_data[3] if len(vaccination_data) > 3 else "Sin fecha"
            status = vaccination_data[5] if len(vaccination_data) > 5 else "Pendiente"
            
            details_message = f"""
            Animal: {animal_name}
            Tipo de Vacuna: {vaccine_type}
            Fecha Programada: {self.format_date(scheduled_date)}
            Estado: {status}
            """
            
            messagebox.showinfo("Detalles de Vacunación", details_message)
            
        except Exception as e:
            print(f"Error al mostrar detalles de vacunación: {str(e)}")
            messagebox.showerror("Error", "No se pudieron cargar los detalles de la vacunación")
    
    def export_vaccinations(self):
        """Exportar listado de vacunaciones"""
        messagebox.showinfo("Exportar", "Aquí se generaría un reporte en Excel o PDF con el listado de vacunaciones")
        
    def format_date(self, date_str):
        """Convertir fecha ISO a formato legible"""
        try:
            year, month, day = map(int, date_str.split('-'))
            return f"{day:02d}/{month:02d}/{year}"
        except:
            return date_str
    
    def update_clock(self):
        """Actualizar el reloj en el encabezado"""
        current_time = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        self.time_label.config(text=current_time)
        self.root.after(1000, self.update_clock)  # Actualizar cada segundo
    
    def open_settings(self):
        """Abrir ventana de configuración"""
        messagebox.showinfo("Configuración", "Ventana de configuración (por implementar)")
    
    def logout(self):
        """Cerrar sesión"""
        if messagebox.askyesno("Cerrar Sesión", "¿Está seguro que desea cerrar sesión?"):
            if self.logout_callback:
                self.logout_callback()
            else:
                self.root.destroy()
    
    # Métodos para cambiar entre vistas (dummy por ahora)
    def show_dashboard(self):
        """Mostrar la pantalla principal del dashboard"""
        # Limpiar contenido actual
        self.clear_content()
        
        # Reconstruir los componentes del dashboard
        self.build_kpi_cards()
        self.build_calendar_section()
        self.build_upcoming_vaccinations()
        self.build_treatments_section()
        self.build_recent_animals()
        self.build_quick_access()
        
        # Actualizar botón activo en el menú
        self.set_active_menu("dashboard")
        
        # Configurar el canvas para que se ajuste al nuevo contenido
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
    
    def show_animals(self):
        """Mostrar el módulo de animales"""
        # Limpiar contenido actual
        self.clear_content()
        
        # Verificar disponibilidad del módulo
        if not ANIMALS_MODULE_AVAILABLE:
            messagebox.showerror("Error", "El módulo de animales no está disponible. Por favor, verifique que el archivo animals.py existe en el directorio correcto.")
            return
            
        try:
            # Crear contenedor para el módulo de animales dentro del scrollable_frame
            animals_container = tk.Frame(self.scrollable_frame, bg=self.colors["bg_main"])
            animals_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
            
            # Crear instancia del módulo de animales
            self.animals_module = AnimalsModule(
                animals_container,
                colors=self.colors,
                fonts=self.fonts
            )
            
            # Mostrar la vista de lista por defecto
            self.animals_module.show_list_view()
            
            # Actualizar botón activo en el menú
            self.set_active_menu("animals")
            
            # Configurar el canvas para que se ajuste al nuevo contenido
            self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar el módulo de animales: {str(e)}")
    
    def build_treatments_section(self):
        """Construir la sección de tratamientos próximos"""
        # Título de la sección
        treatments_section = tk.Frame(self.scrollable_frame, bg=self.colors["bg_main"], pady=15)
        treatments_section.pack(fill=tk.X, padx=20, pady=10)
        
        title_frame = tk.Frame(treatments_section, bg=self.colors["bg_main"])
        title_frame.pack(fill=tk.X)
        
        title_label = tk.Label(
            title_frame,
            text="Tratamientos Activos",
            font=self.fonts["header"],
            bg=self.colors["bg_main"],
            fg=self.colors["text_dark"]
        )
        title_label.pack(side=tk.LEFT)
        
        view_all_btn = tk.Button(
            title_frame,
            text="Ver Todos",
            font=self.fonts["small"],
            bg=self.colors["primary"],
            fg=self.colors["text_light"],
            padx=10,
            relief=tk.FLAT,
            cursor="hand2",
            command=self.show_treatments
        )
        view_all_btn.pack(side=tk.RIGHT)
        
        # Marco para la tabla
        table_frame = tk.Frame(treatments_section, bg=self.colors["card_bg"], padx=15, pady=15)
        table_frame.pack(fill=tk.X, pady=10)
        table_frame.config(highlightbackground="#dddddd", highlightthickness=1)
        
        # Crear tabla con Treeview
        columns = ("animal", "type", "start_date", "end_date", "status", "responsible")
        self.treatments_table = ttk.Treeview(table_frame, columns=columns, show="headings", height=5)
        
        # Definir encabezados
        self.treatments_table.heading("animal", text="Animal")
        self.treatments_table.heading("type", text="Tipo")
        self.treatments_table.heading("start_date", text="Fecha Inicio")
        self.treatments_table.heading("end_date", text="Fecha Fin")
        self.treatments_table.heading("status", text="Estado")
        self.treatments_table.heading("responsible", text="Responsable")
        
        # Definir anchos de columna
        self.treatments_table.column("animal", width=150)
        self.treatments_table.column("type", width=150)
        self.treatments_table.column("start_date", width=100)
        self.treatments_table.column("end_date", width=100)
        self.treatments_table.column("status", width=100)
        self.treatments_table.column("responsible", width=150)
        
        # Agregar scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.treatments_table.yview)
        self.treatments_table.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.treatments_table.pack(fill=tk.BOTH, expand=True)
        
        # Llenar tabla con datos
        treatments = self.db.get_treatments()
        for treatment in treatments:
            if treatment[5] == "En curso":  # treatment[5] es el status
                values = (
                    treatment[1],  # animal_name
                    treatment[2],  # treatment_type
                    self.format_date(treatment[3]),  # start_date
                    self.format_date(treatment[4]),  # end_date
                    treatment[5],  # status
                    treatment[6]   # responsible
                )
                self.treatments_table.insert("", tk.END, values=values)

    def build_recent_animals(self):
        """Construir la sección de animales recientes"""
        try:
            # Título de la sección
            recent_section = tk.Frame(self.scrollable_frame, bg=self.colors["bg_main"], pady=15)
            recent_section.pack(fill=tk.X, padx=20, pady=10)
            
            title_frame = tk.Frame(recent_section, bg=self.colors["bg_main"])
            title_frame.pack(fill=tk.X)
            
            title_label = tk.Label(
                title_frame,
                text="Animales Recientes",
                font=self.fonts["header"],
                bg=self.colors["bg_main"],
                fg=self.colors["text_dark"]
            )
            title_label.pack(side=tk.LEFT)
            
            view_all_btn = tk.Button(
                title_frame,
                text="Ver Todos",
                font=self.fonts["small"],
                bg=self.colors["primary"],
                fg=self.colors["text_light"],
                padx=10,
                relief=tk.FLAT,
                cursor="hand2",
                command=self.show_animals
            )
            view_all_btn.pack(side=tk.RIGHT)
            
            # Marco para la tabla
            table_frame = tk.Frame(recent_section, bg=self.colors["card_bg"], padx=15, pady=15)
            table_frame.pack(fill=tk.X, pady=10)
            table_frame.config(highlightbackground="#dddddd", highlightthickness=1)
            
            # Crear tabla con Treeview
            columns = ("id", "name", "species", "breed", "status")
            self.recent_table = ttk.Treeview(table_frame, columns=columns, show="headings", height=5)
            
            # Definir encabezados
            self.recent_table.heading("id", text="ID")
            self.recent_table.heading("name", text="Nombre")
            self.recent_table.heading("species", text="Especie")
            self.recent_table.heading("breed", text="Raza")
            self.recent_table.heading("status", text="Estado")
            
            # Definir anchos de columna
            self.recent_table.column("id", width=50)
            self.recent_table.column("name", width=150)
            self.recent_table.column("species", width=100)
            self.recent_table.column("breed", width=150)
            self.recent_table.column("status", width=100)
            
            # Agregar scrollbar
            scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.recent_table.yview)
            self.recent_table.configure(yscrollcommand=scrollbar.set)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            self.recent_table.pack(fill=tk.BOTH, expand=True)
            
            # Obtener los últimos 5 animales agregados
            animals = self.db.get_animals()
            sorted_animals = sorted(animals, key=lambda x: x[12] if len(x) > 12 else "", reverse=True)[:5]  # x[12] es added_date
            
            # Llenar tabla con datos
            for animal in sorted_animals:
                values = (
                    animal[0],  # id
                    animal[1],  # name
                    animal[2],  # species
                    animal[3],  # breed
                    animal[6]   # health_status
                )
                self.recent_table.insert("", tk.END, values=values)
            
            # Vincular doble clic para ver detalles
            self.recent_table.bind("<Double-1>", self.on_animal_click)
            
        except Exception as e:
            print(f"Error al construir la sección de animales recientes: {str(e)}")
            
    def on_animal_click(self, event):
        """Manejar clic en la tabla de animales"""
        if not ANIMALS_MODULE_AVAILABLE:
            messagebox.showinfo("Ver Animal", "Aquí se mostrarían los detalles del animal seleccionado")
            return
            
        item = self.recent_table.selection()[0]
        animal_id = self.recent_table.item(item)["values"][0]
        self.show_animals()
        if hasattr(self, 'animals_module'):
            self.animals_module.show_detail_view(animal_id)

    def build_quick_access(self):
        """Construir la sección de acceso rápido"""
        # Título de la sección
        quick_section = tk.Frame(self.scrollable_frame, bg=self.colors["bg_main"], pady=15)
        quick_section.pack(fill=tk.X, padx=20, pady=10)
        
        title_label = tk.Label(
            quick_section,
            text="Acceso Rápido",
            font=self.fonts["header"],
            bg=self.colors["bg_main"],
            fg=self.colors["text_dark"]
        )
        title_label.pack(anchor="w")
        
        # Contenedor para los botones
        buttons_frame = tk.Frame(quick_section, bg=self.colors["card_bg"], padx=15, pady=15)
        buttons_frame.pack(fill=tk.X, pady=10)
        buttons_frame.config(highlightbackground="#dddddd", highlightthickness=1)
        
        # Botones de acceso rápido
        quick_buttons = [
            ("🐄 Nuevo Animal", self.show_new_animal),
            ("💉 Nueva Vacuna", self.add_new_vaccine),
            ("🏥 Nuevo Tratamiento", self.add_new_treatment),
            ("📊 Generar Reporte", self.generate_report)
        ]
        
        for text, command in quick_buttons:
            button = tk.Button(
                buttons_frame,
                text=text,
                font=self.fonts["normal"],
                bg=self.colors["primary"],
                fg=self.colors["text_light"],
                padx=20,
                pady=10,
                relief=tk.FLAT,
                cursor="hand2",
                command=command
            )
            button.pack(side=tk.LEFT, padx=5)
            
    def show_new_animal(self):
        """Mostrar formulario de nuevo animal"""
        self.show_animals()
        if hasattr(self, 'animals_module'):
            self.animals_module.show_new_animal_view()
            
    def add_new_treatment(self):
        """Mostrar formulario de nuevo tratamiento"""
        self.show_treatments()
        
    def generate_report(self):
        """Mostrar opciones de generación de reportes"""
        self.show_reports()

    def refresh_calendar(self):
        """Actualizar el calendario con los eventos más recientes"""
        try:
            print("Actualizando calendario con eventos recientes")
            
            # Limpiar eventos existentes
            self.cal.calevent_remove("all")
            
            # Configurar tags para eventos (importante hacerlo antes de crear los eventos)
            self.cal.tag_config("vaccination", background=self.colors["primary"], foreground="white")
            
            # Obtener eventos actualizados
            calendar_events = self.db.get_calendar_events()
            print(f"Eventos del calendario encontrados: {calendar_events}")
            
            # Crear eventos para cada fecha
            for date_str, count in calendar_events.items():
                try:
                    print(f"Procesando fecha {date_str} con {count} eventos")
                    year, month, day = map(int, date_str.split('-'))
                    event_date = datetime.datetime(year, month, day)
                    print(f"Fecha procesada: {event_date}")
                    
                    # Crear el evento en el calendario
                    event_id = self.cal.calevent_create(
                        event_date, 
                        f"{count} vacunas", 
                        "vaccination"
                    )
                    print(f"Evento creado con ID: {event_id}")
                    
                except Exception as e:
                    print(f"Error al procesar fecha {date_str}: {str(e)}")
                    import traceback
                    traceback.print_exc()
                    continue
            
            # Actualizar la vista de eventos para el día actual o seleccionado
            current_date = self.cal.get_date()
            self.show_events_for_date(current_date)
            
            print("Calendario actualizado exitosamente")
            
        except Exception as e:
            print(f"Error al actualizar el calendario: {str(e)}")
            import traceback
            traceback.print_exc()

# Código para ejecutar el dashboard directamente para pruebas
if __name__ == "__main__":
    root = tk.Tk()
    
    try:
        # Intentar importar la dependencia tkcalendar
        import tkcalendar
    except ImportError:
        # Si no está instalada, mostrar mensaje
        root.withdraw()  # Ocultar ventana principal
        if messagebox.askokcancel("Dependencia Requerida", 
                               "Este programa requiere el paquete 'tkcalendar'. ¿Desea instalarlo ahora?\n\n" +
                               "Se ejecutará: pip install tkcalendar"):
            import subprocess
            try:
                subprocess.check_call(["pip", "install", "tkcalendar"])
                messagebox.showinfo("Instalación Exitosa", 
                                  "La dependencia ha sido instalada. El programa se iniciará ahora.")
                # Reiniciar aplicación después de instalar
                import sys
                import os
                os.execv(sys.executable, [sys.executable] + sys.argv)
            except:
                messagebox.showerror("Error de Instalación", 
                                   "No se pudo instalar la dependencia. Por favor instálela manualmente:\n\n" +
                                   "pip install tkcalendar")
        root.destroy()
        exit()
    
    app = Dashboard(root)
    root.mainloop() 
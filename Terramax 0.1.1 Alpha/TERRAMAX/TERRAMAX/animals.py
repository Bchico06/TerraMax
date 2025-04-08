import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import datetime
import json
import os
import random  # Para datos de ejemplo

# Verificar e importar dependencias
try:
    from PIL import Image, ImageTk
    PILLOW_AVAILABLE = True
except ImportError:
    print("Error: No se pudo importar PIL (Pillow). Por favor instale con: pip install pillow")
    PILLOW_AVAILABLE = False

try:
    from database import Database
    DATABASE_AVAILABLE = True
except ImportError as e:
    print(f"Error al importar el módulo de base de datos: {e}")
    DATABASE_AVAILABLE = False

try:
    from tkcalendar import Calendar
    CALENDAR_AVAILABLE = True
except ImportError:
    print("Error: No se pudo importar Calendar. Por favor instale con: pip install tkcalendar")
    CALENDAR_AVAILABLE = False

class AnimalsModule:
    def __init__(self, container, colors, fonts):
        # Verificar dependencias
        if not DATABASE_AVAILABLE:
            raise ImportError("El módulo de base de datos no está disponible")
        if not PILLOW_AVAILABLE:
            raise ImportError("Pillow no está instalado")
        if not CALENDAR_AVAILABLE:
            raise ImportError("tkcalendar no está instalado")
            
        self.container = container
        self.colors = colors
        if "bg_accent" not in self.colors:
            self.colors["bg_accent"] = "#ecf0f1"  # Agregar el color faltante
        self.fonts = fonts
        self.db = Database()
        self.current_image_path = None
        
        # Variables para seguimiento de UI
        self.current_view = None  # 'list', 'detail', 'new', 'edit'
        self.current_animal = None
        self.search_var = tk.StringVar()
        self.filter_var = tk.StringVar(value="Todos")
        self.sort_var = tk.StringVar(value="Nombre")
        
        # Mostrar la vista de lista por defecto
        self.show_list_view()
    
    def show_list_view(self):
        """Mostrar la vista de lista de animales"""
        # Limpiar el contenedor actual
        for widget in self.container.winfo_children():
            widget.destroy()
            
        # Crear el título
        title_frame = tk.Frame(self.container, bg=self.colors["bg_main"])
        title_frame.pack(fill=tk.X, padx=20, pady=10)
        
        title_label = tk.Label(
            title_frame,
            text="Gestión de Animales",
            font=self.fonts["header"],
            bg=self.colors["bg_main"],
            fg=self.colors["text_dark"]
        )
        title_label.pack(side=tk.LEFT)
        
        # Botón para agregar nuevo animal
        add_button = tk.Button(
            title_frame,
            text="+ Nuevo Animal",
            font=self.fonts["button"],
            bg=self.colors["primary"],
            fg="white",
            padx=15,
            pady=5,
            relief=tk.FLAT,
            command=self.show_new_animal_view
        )
        add_button.pack(side=tk.RIGHT)
        
        # Crear la tabla de animales
        self.create_animals_table()
        
        # Actualizar la tabla con datos
        self.refresh_animals_table()
    
    def create_animals_table(self):
        """Crear la tabla de animales"""
        # Crear el frame para la tabla
        table_frame = tk.Frame(self.container, bg=self.colors["bg_main"])
        table_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Crear tabla con Treeview
        columns = ("id", "name", "species", "breed", "status", "actions")
        self.animals_table = ttk.Treeview(table_frame, columns=columns, show="headings", height=10)
        
        # Configurar las columnas
        self.animals_table.heading("id", text="ID")
        self.animals_table.heading("name", text="Nombre")
        self.animals_table.heading("species", text="Especie")
        self.animals_table.heading("breed", text="Raza")
        self.animals_table.heading("status", text="Estado de Salud")
        
        # Configurar el ancho de las columnas
        self.animals_table.column("id", width=50)
        self.animals_table.column("name", width=150)
        self.animals_table.column("species", width=100)
        self.animals_table.column("breed", width=150)
        self.animals_table.column("status", width=150)
        
        # Agregar scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.animals_table.yview)
        self.animals_table.configure(yscrollcommand=scrollbar.set)
        
        # Posicionar la tabla y el scrollbar
        self.animals_table.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Configurar el estilo de la tabla
        style = ttk.Style()
        style.configure("Custom.Treeview",
                      background=self.colors["card_bg"],
                      foreground=self.colors["text_dark"],
                      fieldbackground=self.colors["card_bg"])
        
        # Vincular doble clic para ver detalles
        self.animals_table.bind("<Double-1>", self.on_animal_double_click)
    
    def refresh_animals_table(self):
        """Actualizar la tabla con los datos de la base de datos"""
        try:
            # Limpiar la tabla
            for item in self.animals_table.get_children():
                self.animals_table.delete(item)
            
            # Obtener animales de la base de datos
            animals = self.db.get_animals()
            print(f"Animales obtenidos de la base de datos: {len(animals) if animals else 0}")  # Debug
            
            if not animals:
                print("No se encontraron animales en la base de datos")
                return
            
            # Agregar cada animal a la tabla
            for animal in animals:
                try:
                    values = (
                        animal[0],  # id
                        animal[1],  # name
                        animal[2],  # species
                        animal[3],  # breed
                        animal[6],  # health_status
                    )
                    print(f"Insertando animal en la tabla: {values}")  # Debug
                    self.animals_table.insert("", tk.END, values=values)
                except Exception as e:
                    print(f"Error al insertar animal en la tabla: {str(e)}")
                    
        except Exception as e:
            print(f"Error al actualizar la tabla: {str(e)}")
            messagebox.showerror("Error", "No se pudo actualizar la lista de animales")
    
    def on_animal_double_click(self, event):
        """Manejar doble clic en un animal de la tabla"""
        try:
            # Obtener el item seleccionado
            selection = self.animals_table.selection()
            print(f"Selección: {selection}")  # Debug
            
            if not selection:  # Si no hay selección
                print("No hay selección")  # Debug
                return
                
            item = selection[0]
            item_data = self.animals_table.item(item)
            print(f"Datos completos del item: {item_data}")  # Debug
            
            values = item_data.get("values")
            print(f"Valores obtenidos: {values}")  # Debug
            
            if not values:  # Si no hay valores
                print("No se encontraron valores para el item seleccionado")
                return
                
            try:
                animal_id = int(values[0])  # Convertir explícitamente a entero
                print(f"ID del animal convertido a entero: {animal_id}")  # Debug
            except (IndexError, ValueError, TypeError) as e:
                print(f"Error al obtener o convertir el ID del animal: {str(e)}")
                messagebox.showerror("Error", "No se pudo obtener el ID del animal")
                return
            
            if animal_id:
                print(f"Intentando mostrar detalles del animal con ID: {animal_id}")  # Debug
                self.show_detail_view(animal_id)
            else:
                print("El ID del animal es 0 o None")
                messagebox.showerror("Error", "ID de animal inválido")
                
        except Exception as e:
            print(f"Error en double click: {str(e)}")
            print(f"Traza completa del error:", e.__traceback__)
            messagebox.showerror("Error", "No se pudo mostrar los detalles del animal")
    
    def show_new_animal_view(self):
        """Mostrar el formulario para agregar un nuevo animal"""
        # Limpiar el contenedor actual
        for widget in self.container.winfo_children():
            widget.destroy()
            
        # Título del formulario
        title_frame = tk.Frame(self.container, bg=self.colors["bg_main"])
        title_frame.pack(fill=tk.X, padx=20, pady=10)
        
        title_label = tk.Label(
            title_frame,
            text="Agregar Nuevo Animal",
            font=self.fonts["header"],
            bg=self.colors["bg_main"],
            fg=self.colors["text_dark"]
        )
        title_label.pack(side=tk.LEFT)
        
        # Botón para volver a la lista
        back_button = tk.Button(
            title_frame,
            text="← Volver",
            font=self.fonts["button"],
            bg=self.colors["primary"],
            fg=self.colors["text_light"],
            padx=15,
            pady=5,
            relief=tk.FLAT,
            command=self.show_list_view
        )
        back_button.pack(side=tk.RIGHT)
        
        # Crear el formulario
        self.create_animal_form()
    
    def create_animal_form(self, is_editing=False, animal_id=None):
        """Crear el formulario para agregar/editar un animal"""
        form_frame = tk.Frame(self.container, bg=self.colors["bg_main"])
        form_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Variables para los campos del formulario
        self.form_vars = {
            "name": tk.StringVar(),
            "species": tk.StringVar(),
            "breed": tk.StringVar(),
            "gender": tk.StringVar(),
            "birth_date": tk.StringVar(),
            "health_status": tk.StringVar(),
            "weight": tk.StringVar(),
            "feeding_type": tk.StringVar(),
            "father_id": tk.StringVar(),
            "mother_id": tk.StringVar(),
            "medical_history": tk.StringVar(),
            "image_path": tk.StringVar()
        }
        
        # Crear los campos del formulario
        fields = [
            ("Nombre", "name", True),
            ("Especie", "species", True),
            ("Raza", "breed", True),
            ("Género", "gender", True),
            ("Fecha de Nacimiento", "birth_date", True),
            ("Estado de Salud", "health_status", True),
            ("Peso (kg)", "weight", True),
            ("Tipo de Alimentación", "feeding_type", True),
            ("ID del Padre", "father_id", False),
            ("ID de la Madre", "mother_id", False),
            ("Historial Médico", "medical_history", False)
        ]
        
        for label, var_name, required in fields:
            frame = tk.Frame(form_frame, bg=self.colors["bg_main"])
            frame.pack(fill=tk.X, pady=5)
            
            label_text = label + (" *" if required else "")
            label_widget = tk.Label(
                frame,
                text=label_text,
                font=self.fonts["normal"],
                bg=self.colors["bg_main"],
                fg=self.colors["text_dark"],
                width=15,
                anchor="w"
            )
            label_widget.pack(side=tk.LEFT, padx=5)
            
            if var_name == "species":
                # Combo box para especie
                species_options = ["Equino", "Ovino", "Bovino", "Porcino", "Caprino"]
                entry = ttk.Combobox(
                    frame,
                    textvariable=self.form_vars[var_name],
                    values=species_options,
                    state="readonly",
                    font=self.fonts["normal"],
                    width=30
                )
                entry.pack(side=tk.LEFT, padx=5)
            elif var_name == "gender":
                # Combo box para género
                gender_options = ["Macho", "Hembra"]
                entry = ttk.Combobox(
                    frame,
                    textvariable=self.form_vars[var_name],
                    values=gender_options,
                    state="readonly",
                    font=self.fonts["normal"],
                    width=30
                )
                entry.pack(side=tk.LEFT, padx=5)
            elif var_name == "health_status":
                # Combo box para estado de salud
                status_options = ["Saludable", "En tratamiento", "En observación", "Enfermo"]
                entry = ttk.Combobox(
                    frame,
                    textvariable=self.form_vars[var_name],
                    values=status_options,
                    state="readonly",
                    font=self.fonts["normal"],
                    width=30
                )
                entry.pack(side=tk.LEFT, padx=5)
            elif var_name == "feeding_type":
                # Combo box para tipo de alimentación
                feeding_options = ["Pastoreo", "Concentrado", "Mixto", "Especial"]
                entry = ttk.Combobox(
                    frame,
                    textvariable=self.form_vars[var_name],
                    values=feeding_options,
                    state="readonly",
                    font=self.fonts["normal"],
                    width=30
                )
                entry.pack(side=tk.LEFT, padx=5)
            elif var_name == "birth_date":
                # Frame para la fecha con botón de calendario
                date_frame = tk.Frame(frame, bg=self.colors["bg_main"])
                date_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
                
                # Entry para la fecha
                date_entry = tk.Entry(
                    date_frame,
                    textvariable=self.form_vars[var_name],
                    font=self.fonts["normal"],
                    width=25,
                    state="readonly"
                )
                date_entry.pack(side=tk.LEFT, padx=5)
                
                # Botón del calendario
                cal_button = tk.Button(
                    date_frame,
                    text="📅",
                    font=self.fonts["normal"],
                    bg=self.colors["primary"],
                    fg=self.colors["text_light"],
                    padx=5,
                    relief=tk.FLAT,
                    command=lambda v=var_name: self.show_calendar(v)
                )
                cal_button.pack(side=tk.LEFT)
            else:
                # Campo de texto normal
                entry = tk.Entry(
                    frame,
                    textvariable=self.form_vars[var_name],
                    font=self.fonts["normal"],
                    width=32
                )
                entry.pack(side=tk.LEFT, padx=5)
        
        # Frame para la imagen
        image_frame = tk.Frame(form_frame, bg=self.colors["bg_main"])
        image_frame.pack(fill=tk.X, pady=5)
        
        image_label = tk.Label(
            image_frame,
            text="Imagen",
            font=self.fonts["normal"],
            bg=self.colors["bg_main"],
            fg=self.colors["text_dark"],
            width=15,
            anchor="w"
        )
        image_label.pack(side=tk.LEFT, padx=5)
        
        image_entry = tk.Entry(
            image_frame,
            textvariable=self.form_vars["image_path"],
            font=self.fonts["normal"],
            width=32,
            state="readonly"
        )
        image_entry.pack(side=tk.LEFT, padx=5)
        
        browse_button = tk.Button(
            image_frame,
            text="Seleccionar",
            font=self.fonts["normal"],
            bg=self.colors["primary"],
            fg=self.colors["text_light"],
            padx=10,
            pady=2,
            relief=tk.FLAT,
            command=self.select_image
        )
        browse_button.pack(side=tk.LEFT, padx=5)
        
        # Botón para guardar
        save_frame = tk.Frame(form_frame, bg=self.colors["bg_main"])
        save_frame.pack(fill=tk.X, pady=20)
        
        save_button = tk.Button(
            save_frame,
            text="Guardar",
            font=self.fonts["button"],
            bg=self.colors["primary"],
            fg=self.colors["text_light"],
            padx=20,
            pady=10,
            relief=tk.FLAT,
            command=lambda: self.update_animal(animal_id) if is_editing else self.save_animal()
        )
        save_button.pack()
    
    def select_image(self):
        """Permitir al usuario seleccionar una imagen"""
        file_path = filedialog.askopenfilename(
            title="Seleccionar imagen",
            filetypes=[("Imágenes", "*.png *.jpg *.jpeg")]
        )
        if file_path:
            self.form_vars["image_path"].set(file_path)
    
    def show_calendar(self, target_var):
        """Mostrar un calendario para seleccionar la fecha"""
        def set_date():
            selected_date = cal.selection_get()
            self.form_vars[target_var].set(selected_date.strftime("%Y-%m-%d"))
            top.destroy()
        
        top = tk.Toplevel(self.container)
        top.title("Seleccionar Fecha")
        top.transient(self.container)
        top.grab_set()
        
        # Configurar el calendario
        cal = Calendar(
            top,
            selectmode='day',
            year=datetime.datetime.now().year,
            month=datetime.datetime.now().month,
            day=datetime.datetime.now().day,
            background=self.colors["bg_main"],
            foreground=self.colors["text_dark"],
            selectbackground=self.colors["primary"]
        )
        cal.pack(padx=10, pady=10)
        
        # Botón para seleccionar la fecha
        select_button = tk.Button(
            top,
            text="Seleccionar",
            font=self.fonts["normal"],
            bg=self.colors["primary"],
            fg=self.colors["text_light"],
            command=set_date
        )
        select_button.pack(pady=10)
        
        # Centrar la ventana
        top.update_idletasks()
        width = top.winfo_width()
        height = top.winfo_height()
        x = (top.winfo_screenwidth() // 2) - (width // 2)
        y = (top.winfo_screenheight() // 2) - (height // 2)
        top.geometry('{}x{}+{}+{}'.format(width, height, x, y))
    
    def save_animal(self):
        """Guardar un nuevo animal en la base de datos"""
        print("Iniciando guardado de animal...")
        # Validar campos requeridos
        required_fields = ["name", "species", "breed", "gender", "birth_date", "health_status", "weight", "feeding_type"]
        missing_fields = []
        
        for field in required_fields:
            if not self.form_vars[field].get().strip():
                missing_fields.append(field)
                print(f"Campo requerido faltante: {field}")
        
        if missing_fields:
            field_names = {
                "name": "Nombre",
                "species": "Especie",
                "breed": "Raza",
                "gender": "Género",
                "birth_date": "Fecha de Nacimiento",
                "health_status": "Estado de Salud",
                "weight": "Peso",
                "feeding_type": "Tipo de Alimentación"
            }
            missing_names = [field_names.get(field, field) for field in missing_fields]
            messagebox.showerror(
                "Error",
                f"Por favor complete los siguientes campos requeridos:\n\n{', '.join(missing_names)}"
            )
            return
            
        try:
            print("Preparando datos del animal...")
            # Verificar que la fecha de nacimiento sea válida
            birth_date = self.form_vars["birth_date"].get().strip()
            if not birth_date:
                messagebox.showerror("Error", "La fecha de nacimiento es requerida")
                return
                
            # Calcular la edad basada en la fecha de nacimiento
            birth_date_obj = datetime.datetime.strptime(birth_date, "%Y-%m-%d")
            today = datetime.datetime.now()
            age = today.year - birth_date_obj.year - ((today.month, today.day) < (birth_date_obj.month, birth_date_obj.day))
            
            # Procesar los IDs de padre y madre
            father_id = None
            mother_id = None
            
            father_id_str = self.form_vars["father_id"].get().strip()
            mother_id_str = self.form_vars["mother_id"].get().strip()
            
            if father_id_str:
                try:
                    father_id = int(father_id_str)
                except ValueError:
                    messagebox.showerror("Error", "El ID del padre debe ser un número válido")
                    return
                    
            if mother_id_str:
                try:
                    mother_id = int(mother_id_str)
                except ValueError:
                    messagebox.showerror("Error", "El ID de la madre debe ser un número válido")
                    return
            
            # Procesar el peso
            weight = None
            weight_str = self.form_vars["weight"].get().strip()
            if weight_str:
                try:
                    weight = float(weight_str)
                except ValueError:
                    messagebox.showerror("Error", "El peso debe ser un número válido")
                    return
            
            # Crear el diccionario con los datos del animal
            animal_data = {
                "name": self.form_vars["name"].get().strip(),
                "species": self.form_vars["species"].get().strip(),
                "breed": self.form_vars["breed"].get().strip(),
                "gender": self.form_vars["gender"].get().strip(),
                "age": age,
                "health_status": self.form_vars["health_status"].get().strip(),
                "weight": weight,
                "feeding_type": self.form_vars["feeding_type"].get().strip(),
                "father_id": father_id,
                "mother_id": mother_id,
                "medical_history": self.form_vars["medical_history"].get().strip() or None,
                "image_path": self.form_vars["image_path"].get().strip() or None,
                "birth_date": birth_date,
                "added_date": datetime.datetime.now().strftime("%Y-%m-%d")
            }
            print(f"Datos del animal preparados: {animal_data}")
            
            # Guardar en la base de datos
            print("Intentando guardar en la base de datos...")
            self.db.add_animal(animal_data)
            print("Animal guardado exitosamente")
            
            # Mostrar mensaje de éxito
            messagebox.showinfo("Éxito", "Animal guardado correctamente")
            
            # Volver a la vista de lista
            self.show_list_view()
            
        except ValueError as ve:
            print(f"Error de valor: {str(ve)}")
            messagebox.showerror("Error", "La fecha de nacimiento no es válida o el peso no es un número válido")
        except Exception as e:
            print(f"Error al guardar el animal: {str(e)}")
            messagebox.showerror("Error", f"Error al guardar el animal: {str(e)}")
    
    def calculate_age(self, birth_date):
        """Calcular la edad en años, meses y días"""
        try:
            birth_date = datetime.datetime.strptime(birth_date, "%Y-%m-%d")
            today = datetime.datetime.now()
            
            # Calcular años
            years = today.year - birth_date.year
            # Calcular meses
            months = today.month - birth_date.month
            if months < 0:
                years -= 1
                months += 12
            # Calcular días
            days = today.day - birth_date.day
            if days < 0:
                months -= 1
                # Obtener el último día del mes anterior
                last_month = today.replace(day=1) - datetime.timedelta(days=1)
                days += last_month.day
            
            return f"{years} años, {months} meses, {days} días"
        except Exception as e:
            print(f"Error al calcular la edad: {str(e)}")
            return "No disponible"
    
    def show_detail_view(self, animal_id):
        """Mostrar los detalles de un animal"""
        try:
            # Limpiar el contenedor actual
            for widget in self.container.winfo_children():
                widget.destroy()
                
            # Obtener los datos del animal
            print(f"Intentando obtener animal con ID: {animal_id}")  # Debug
            animal = self.db.get_animal(animal_id)
            print(f"Resultado de get_animal: {animal}")  # Debug
            
            if not animal:
                print("Animal no encontrado en la base de datos")  # Debug
                messagebox.showerror("Error", "Animal no encontrado")
                self.show_list_view()
                return
            
            print(f"Datos del animal: {animal}")  # Debug
            print(f"Longitud de la tupla: {len(animal)}")  # Debug
            print(f"Índices disponibles: {list(range(len(animal)))}")  # Debug
            
            # Mapeo de índices
            INDICES = {
                'id': 0,
                'name': 1,
                'species': 2,
                'breed': 3,
                'gender': 4,
                'age': 5,
                'health_status': 6,
                'weight': 7,
                'feeding_type': 8,
                'father_id': 9,
                'mother_id': 10,
                'medical_history': 11,
                'image_path': 12,
                'birth_date': 13,
                'added_date': 14
            }
            
            # Calcular la edad actual
            age = self.calculate_age(animal[INDICES['birth_date']])
            
            # Crear el título y los botones
            title_frame = tk.Frame(self.container, bg=self.colors["bg_main"])
            title_frame.pack(fill=tk.X, padx=20, pady=10)
            
            # Título
            title_label = tk.Label(
                title_frame,
                text=f"Detalles de {animal[INDICES['name']]}",
                font=self.fonts["header"],
                bg=self.colors["bg_main"],
                fg=self.colors["text_dark"]
            )
            title_label.pack(side=tk.LEFT)
            
            # Frame para los botones
            buttons_frame = tk.Frame(title_frame, bg=self.colors["bg_main"])
            buttons_frame.pack(side=tk.RIGHT)
            
            # Botón Editar
            edit_button = tk.Button(
                buttons_frame,
                text="✏️ Editar",
                font=self.fonts["button"],
                bg=self.colors["primary"],
                fg="white",
                padx=15,
                pady=5,
                relief=tk.FLAT,
                command=lambda: self.show_edit_view(animal_id)
            )
            edit_button.pack(side=tk.LEFT, padx=5)
            
            # Botón Eliminar
            delete_button = tk.Button(
                buttons_frame,
                text="🗑️ Eliminar",
                font=self.fonts["button"],
                bg=self.colors["danger"],
                fg="white",
                padx=15,
                pady=5,
                relief=tk.FLAT,
                command=lambda: self.delete_animal(animal_id)
            )
            delete_button.pack(side=tk.LEFT, padx=5)
            
            # Botón Volver
            back_button = tk.Button(
                buttons_frame,
                text="← Volver",
                font=self.fonts["button"],
                bg=self.colors["bg_accent"],
                fg=self.colors["text_dark"],
                padx=15,
                pady=5,
                relief=tk.FLAT,
                command=self.show_list_view
            )
            back_button.pack(side=tk.LEFT, padx=5)
            
            # Frame principal para los detalles
            main_frame = tk.Frame(self.container, bg=self.colors["bg_main"])
            main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
            
            # Frame para la información
            info_frame = tk.Frame(main_frame, bg=self.colors["bg_main"])
            info_frame.pack(fill=tk.BOTH, expand=True, pady=10)
            
            # Lista de campos a mostrar
            fields = [
                ("ID", animal[INDICES['id']]),
                ("Nombre", animal[INDICES['name']]),
                ("Especie", animal[INDICES['species']]),
                ("Raza", animal[INDICES['breed']]),
                ("Género", animal[INDICES['gender']]),
                ("Edad", age),
                ("Estado de Salud", animal[INDICES['health_status']]),
                ("Peso", f"{animal[INDICES['weight']]} kg" if animal[INDICES['weight']] else "No especificado"),
                ("Tipo de Alimentación", animal[INDICES['feeding_type']] if animal[INDICES['feeding_type']] else "No especificado"),
                ("ID del Padre", animal[INDICES['father_id']] if animal[INDICES['father_id']] else "No especificado"),
                ("ID de la Madre", animal[INDICES['mother_id']] if animal[INDICES['mother_id']] else "No especificado"),
                ("Historial Médico", animal[INDICES['medical_history']] if animal[INDICES['medical_history']] else "No especificado")
            ]
            
            # Crear las filas de información
            for label, value in fields:
                row_frame = tk.Frame(info_frame, bg=self.colors["bg_main"])
                row_frame.pack(fill=tk.X, pady=2)
                
                label_widget = tk.Label(
                    row_frame,
                    text=f"{label}:",
                    font=self.fonts["normal_bold"],
                    bg=self.colors["bg_main"],
                    fg=self.colors["text_dark"],
                    width=20,
                    anchor="w"
                )
                label_widget.pack(side=tk.LEFT, padx=5)
                
                value_widget = tk.Label(
                    row_frame,
                    text=str(value),
                    font=self.fonts["normal"],
                    bg=self.colors["bg_main"],
                    fg=self.colors["text_dark"],
                    anchor="w"
                )
                value_widget.pack(side=tk.LEFT, fill=tk.X, expand=True)
                
        except Exception as e:
            print(f"Error al mostrar los detalles del animal: {str(e)}")
            print(f"Traza completa:", e.__traceback__)
            messagebox.showerror("Error", f"Error al mostrar los detalles: {str(e)}")
            self.show_list_view()
    
    def show_edit_view(self, animal_id):
        """Mostrar el formulario para editar un animal"""
        # Limpiar el contenedor actual
        for widget in self.container.winfo_children():
            widget.destroy()
            
        # Obtener los datos del animal
        animal = self.db.get_animal(animal_id)
        if not animal:
            messagebox.showerror("Error", "Animal no encontrado")
            self.show_list_view()
            return
            
        print(f"Datos del animal para editar: {animal}")  # Debug
        print(f"Longitud de la tupla: {len(animal)}")  # Debug
        print(f"Índices disponibles: {list(range(len(animal)))}")  # Debug
        
        # Crear el título y el botón de volver
        title_frame = tk.Frame(self.container, bg=self.colors["bg_main"])
        title_frame.pack(fill=tk.X, padx=20, pady=10)
        
        title_label = tk.Label(
            title_frame,
            text=f"Editar {animal[1]}",  # name
            font=self.fonts["header"],
            bg=self.colors["bg_main"],
            fg=self.colors["text_dark"]
        )
        title_label.pack(side=tk.LEFT)
        
        back_button = tk.Button(
            title_frame,
            text="← Volver",
            font=self.fonts["button"],
            bg=self.colors["bg_accent"],
            fg=self.colors["text_dark"],
            padx=15,
            pady=5,
            relief=tk.FLAT,
            command=lambda: self.show_detail_view(animal_id)
        )
        back_button.pack(side=tk.RIGHT)
        
        # Crear el formulario
        self.create_animal_form(is_editing=True, animal_id=animal_id)
        
        try:
            # Campos básicos (índices confirmados)
            self.form_vars["name"].set(animal[1])        # name
            self.form_vars["species"].set(animal[2])     # species
            self.form_vars["breed"].set(animal[3])       # breed
            self.form_vars["gender"].set(animal[4])      # gender
            self.form_vars["birth_date"].set(animal[13]) # birth_date
            self.form_vars["health_status"].set(animal[6]) # health_status
            
            # Peso (índice 7)
            if animal[7] is not None:
                self.form_vars["weight"].set(str(animal[7]))
            
            # Tipo de alimentación (índice 8)
            if animal[8] is not None:
                self.form_vars["feeding_type"].set(str(animal[8]))
            
            # IDs de padre y madre (índices 9 y 10)
            if animal[9] is not None:  # father_id
                self.form_vars["father_id"].set(str(animal[9]))
            
            if animal[10] is not None:  # mother_id
                self.form_vars["mother_id"].set(str(animal[10]))
            
            # Historial médico (índice 11)
            if animal[11] is not None:
                self.form_vars["medical_history"].set(str(animal[11]))
            
            # Ruta de la imagen (índice 12)
            if animal[12] is not None:
                self.form_vars["image_path"].set(str(animal[12]))
            
        except Exception as e:
            print(f"Error al llenar el formulario: {str(e)}")
            print(f"Datos del animal: {animal}")
            print(f"Longitud de la tupla: {len(animal)}")
            print(f"Error completo: {e.__class__.__name__}: {str(e)}")
            messagebox.showerror("Error", f"Error al cargar los datos: {str(e)}")
    
    def update_animal(self, animal_id):
        """Actualizar un animal existente"""
        try:
            # Obtener los valores de los campos
            name = self.form_vars["name"].get().strip()
            species = self.form_vars["species"].get().strip()
            breed = self.form_vars["breed"].get().strip()
            gender = self.form_vars["gender"].get().strip()
            birth_date = self.form_vars["birth_date"].get().strip()
            health_status = self.form_vars["health_status"].get().strip()
            weight = self.form_vars["weight"].get().strip()
            feeding_type = self.form_vars["feeding_type"].get().strip()
            father_id = self.form_vars["father_id"].get().strip()
            mother_id = self.form_vars["mother_id"].get().strip()
            medical_history = self.form_vars["medical_history"].get().strip()
            
            # Validar campos requeridos
            required_fields = {
                "Nombre": name,
                "Especie": species,
                "Raza": breed,
                "Género": gender,
                "Fecha de Nacimiento": birth_date,
                "Estado de Salud": health_status,
                "Peso": weight,
                "Tipo de Alimentación": feeding_type
            }
            
            missing_fields = [field for field, value in required_fields.items() if not value]
            if missing_fields:
                messagebox.showerror("Error", f"Por favor complete los siguientes campos:\n- " + "\n- ".join(missing_fields))
                return
            
            # Validar fecha de nacimiento
            try:
                birth_date_obj = datetime.datetime.strptime(birth_date, "%Y-%m-%d")
                if birth_date_obj > datetime.datetime.now():
                    messagebox.showerror("Error", "La fecha de nacimiento no puede ser en el futuro")
                    return
            except ValueError:
                messagebox.showerror("Error", "Formato de fecha inválido. Use YYYY-MM-DD")
                return
            
            # Calcular edad
            today = datetime.datetime.now()
            age = today.year - birth_date_obj.year - ((today.month, today.day) < (birth_date_obj.month, birth_date_obj.day))
            
            # Procesar IDs de padres
            father_id = int(father_id) if father_id and father_id.isdigit() else None
            mother_id = int(mother_id) if mother_id and mother_id.isdigit() else None
            
            # Procesar peso
            try:
                weight = float(weight) if weight else None
            except ValueError:
                messagebox.showerror("Error", "El peso debe ser un número válido")
                return
            
            # Preparar los datos
            animal_data = {
                "name": name,
                "species": species,
                "breed": breed,
                "gender": gender,
                "age": age,
                "health_status": health_status,
                "weight": weight,
                "feeding_type": feeding_type,
                "father_id": father_id,
                "mother_id": mother_id,
                "medical_history": medical_history,
                "birth_date": birth_date
            }
            
            # Actualizar en la base de datos
            self.db.update_animal(animal_id, animal_data)
            
            messagebox.showinfo("Éxito", "Animal actualizado correctamente")
            self.show_list_view()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al actualizar: {str(e)}")
    
    def delete_animal(self, animal_id):
        """Eliminar un animal de la base de datos"""
        # Pedir confirmación
        if messagebox.askyesno(
            "Confirmar eliminación",
            "¿Está seguro que desea eliminar este animal? Esta acción no se puede deshacer."
        ):
            try:
                # Eliminar de la base de datos
                self.db.delete_animal(animal_id)
                
                # Mostrar mensaje de éxito
                messagebox.showinfo("Éxito", "Animal eliminado correctamente")
                
                # Volver a la vista de lista
                self.show_list_view()
                
            except Exception as e:
                messagebox.showerror("Error", f"Error al eliminar el animal: {str(e)}")

    def __del__(self):
        """Destructor para cerrar la conexión a la base de datos"""
        if hasattr(self, 'db'):
            self.db.close()

    def format_date(self, date_str):
        """Formatear una fecha YYYY-MM-DD a un formato más legible"""
        try:
            date_obj = datetime.datetime.strptime(date_str, "%Y-%m-%d")
            return date_obj.strftime("%d/%m/%Y")
        except:
            return date_str

# La implementación de las vistas continúa en la siguiente parte 
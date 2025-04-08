import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from database import Database
from tkcalendar import Calendar

class VaccinationsModule:
    def __init__(self, parent, colors, fonts):
        self.parent = parent
        self.colors = colors
        self.fonts = fonts
        self.db = Database()
        self.current_view = None
        self.current_vaccination_id = None
        
        # Crear el contenedor principal
        self.container = tk.Frame(parent, bg=self.colors["bg_main"])
        self.container.pack(fill=tk.BOTH, expand=True)
        
        # Mostrar la vista de lista por defecto
        self.show_list_view()
    
    def show_list_view(self):
        """Mostrar la vista de lista de vacunaciones"""
        try:
            print("\nMostrando lista de vacunaciones...")
            # Limpiar el contenido actual
            self.clear_content()
            
            # Título del módulo
            module_title = tk.Label(
                self.container,
                text="Gestión de Vacunaciones",
                font=self.fonts["header"],
                bg=self.colors["bg_main"],
                fg=self.colors["text_dark"],
                pady=10
            )
            module_title.pack(anchor="w", padx=20, pady=10)
            
            # Botones de acción
            actions_frame = tk.Frame(self.container, bg=self.colors["bg_main"])
            actions_frame.pack(fill=tk.X, padx=20, pady=10)
            
            new_btn = tk.Button(
                actions_frame,
                text="+ Nueva Vacunación",
                font=self.fonts["normal"],
                bg=self.colors["secondary"],
                fg=self.colors["text_light"],
                padx=10,
                relief=tk.FLAT,
                cursor="hand2",
                command=self.show_new_vaccination_view
            )
            new_btn.pack(side=tk.LEFT, padx=5)

            refresh_btn = tk.Button(
                actions_frame,
                text="↻ Actualizar",
                font=self.fonts["normal"],
                bg=self.colors["primary"],
                fg=self.colors["text_light"],
                padx=10,
                relief=tk.FLAT,
                cursor="hand2",
                command=self.show_list_view
            )
            refresh_btn.pack(side=tk.LEFT, padx=5)
            
            # Marco para la tabla
            table_frame = tk.Frame(self.container, bg=self.colors["card_bg"], padx=15, pady=15)
            table_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
            table_frame.config(highlightbackground="#dddddd", highlightthickness=1)
            
            # Crear tabla con Treeview
            columns = ("id", "animal", "vaccine", "date", "status", "notes")
            self.vacc_table = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)
            
            # Definir encabezados
            self.vacc_table.heading("id", text="ID")
            self.vacc_table.heading("animal", text="Animal")
            self.vacc_table.heading("vaccine", text="Tipo de Vacuna")
            self.vacc_table.heading("date", text="Fecha Programada")
            self.vacc_table.heading("status", text="Estado")
            self.vacc_table.heading("notes", text="Notas")
            
            # Definir anchos de columna
            self.vacc_table.column("id", width=50)
            self.vacc_table.column("animal", width=150)
            self.vacc_table.column("vaccine", width=150)
            self.vacc_table.column("date", width=150)
            self.vacc_table.column("status", width=100)
            self.vacc_table.column("notes", width=200)
            
            # La columna ID es visible pero pequeña
            self.vacc_table["displaycolumns"] = ("id", "animal", "vaccine", "date", "status", "notes")
            
            # Agregar scrollbar
            scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.vacc_table.yview)
            self.vacc_table.configure(yscrollcommand=scrollbar.set)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            self.vacc_table.pack(fill=tk.BOTH, expand=True)
            
            # Obtener y mostrar las vacunaciones
            print("Obteniendo vacunaciones de la base de datos...")
            vaccinations = self.db.get_vaccinations()
            print(f"Se encontraron {len(vaccinations)} vacunaciones")
            
            # Si no hay vacunaciones, mostrar mensaje
            if not vaccinations:
                no_data_label = tk.Label(
                    table_frame,
                    text="No hay vacunaciones registradas",
                    font=self.fonts["normal"],
                    bg=self.colors["card_bg"],
                    fg=self.colors["text_dark"]
                )
                no_data_label.place(relx=0.5, rely=0.5, anchor="center")
            
            counter = 0
            for vaccination in vaccinations:
                try:
                    print(f"\nProcesando vacunación {counter+1}:")
                    print(f"  - Datos completos: {vaccination}")
                    
                    # La estructura esperada de la vacunación es:
                    # 0: id, 1: animal_id, 2: vaccine_type, 3: scheduled_date, 4: notes, 5: status, 6: applied_date, 7: animal_name
                    
                    # Intentar obtener el nombre del animal directamente del resultado
                    animal_name = "No encontrado"
                    if len(vaccination) > 7 and vaccination[7]:
                        animal_name = vaccination[7]
                        print(f"  - Nombre del animal de la consulta: {animal_name}")
                    
                    # Si no tenemos nombre, intentar obtenerlo por ID
                    if animal_name == "No encontrado" and len(vaccination) > 1 and vaccination[1]:
                        try:
                            animal_id = vaccination[1]
                            print(f"  - Intentando obtener animal con ID: {animal_id}")
                            animal = self.db.get_animal(animal_id)
                            if animal and len(animal) > 1:
                                animal_name = animal[1]
                                print(f"  - Nombre de animal obtenido por ID: {animal_name}")
                        except Exception as e:
                            print(f"  - Error al obtener animal por ID: {str(e)}")
                    
                    values = (
                        vaccination[0],  # ID
                        animal_name,     # Nombre del animal
                        vaccination[2] if len(vaccination) > 2 else "Desconocido",  # tipo de vacuna
                        self.format_date(vaccination[3]) if len(vaccination) > 3 and vaccination[3] else "No especificada",  # fecha
                        vaccination[5] if len(vaccination) > 5 and vaccination[5] else "Pendiente",  # estado
                        vaccination[4] if len(vaccination) > 4 and vaccination[4] else "Sin notas"  # notas
                    )
                    
                    print(f"  - Valores para la tabla: {values}")
                    
                    item_id = self.vacc_table.insert("", tk.END, values=values)
                    print(f"  - Insertado en la tabla con ID: {item_id}")
                    
                    # Dar color según estado
                    status = vaccination[5] if len(vaccination) > 5 else "Pendiente"
                    if status == "Vencida":
                        self.vacc_table.tag_configure("expired", background="#ffdddd")
                        self.vacc_table.item(item_id, tags=("expired",))
                    elif status == "Aplicada":
                        self.vacc_table.tag_configure("applied", background="#ddffdd")
                        self.vacc_table.item(item_id, tags=("applied",))
                    
                    counter += 1
                    
                except Exception as e:
                    print(f"Error al procesar vacunación: {str(e)}")
                    import traceback
                    traceback.print_exc()
                    continue
            
            print(f"Se mostraron {counter} vacunaciones en la tabla")
            
            # Vincular doble clic para ver detalles
            self.vacc_table.bind("<Double-1>", lambda e: self.show_vaccination_details(self.vacc_table))
            
        except Exception as e:
            print(f"Error al mostrar lista de vacunaciones: {str(e)}")
            import traceback
            traceback.print_exc()
            messagebox.showerror("Error", f"No se pudo mostrar la lista de vacunaciones: {str(e)}")
    
    def clear_content(self):
        """Limpiar el contenido actual del contenedor"""
        for widget in self.container.winfo_children():
            widget.destroy()

    def show_vaccination_details(self, table):
        """Mostrar detalles de una vacunación seleccionada"""
        try:
            selection = table.selection()
            if not selection:
                return
                
            item = selection[0]
            values = table.item(item)["values"]
            
            if not values:
                return
                
            print(f"Valores seleccionados: {values}")
            
            # El ID ahora está en la primera posición de values (índice 0)
            vaccination_id = values[0]
            print(f"ID de vacunación seleccionado: {vaccination_id}")
            
            # Obtener la vacunación directamente por ID
            vaccinations = self.db.get_vaccinations(id=vaccination_id)
            
            if not vaccinations:
                print(f"No se encontró ninguna vacunación con ID: {vaccination_id}")
                messagebox.showinfo("Detalles de Vacunación", "No se encontraron detalles adicionales para esta vacunación")
                return
                
            vaccination = vaccinations[0]
            print(f"Datos de vacunación encontrados: {vaccination}")
            
            # El nombre del animal está en la posición 6 de la tupla de vacunación
            animal_name = vaccination[6] if len(vaccination) > 6 and vaccination[6] else "No encontrado"
            
            # También intentemos obtener el animal directamente por su ID como fallback
            if animal_name == "No encontrado" and vaccination[1]:
                try:
                    animal_id = vaccination[1]
                    print(f"Intentando obtener animal con ID: {animal_id}")
                    animal = self.db.get_animal(animal_id)
                    if animal and len(animal) > 1:
                        animal_name = animal[1]
                        print(f"Nombre de animal obtenido por ID: {animal_name}")
                except Exception as e:
                    print(f"Error al obtener animal por ID: {str(e)}")
            
            # Crear una ventana de detalles
            details_window = tk.Toplevel()
            details_window.title("Detalles de Vacunación")
            details_window.transient(self.container)
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
                ("Estado:", vaccination[5] if vaccination[5] else "Pendiente"),
                ("Notas:", vaccination[4] if vaccination[4] else "Sin notas")
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
            
            current_status = vaccination[5] if vaccination[5] else "Pendiente"
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
            print(f"Error al mostrar detalles de vacunación: {str(e)}")
            import traceback
            traceback.print_exc()
            messagebox.showerror("Error", "No se pudieron mostrar los detalles de la vacunación")

    def mark_as_applied(self, event, window=None):
        """Marcar una vacuna como aplicada"""
        if messagebox.askyesno("Confirmar Aplicación", 
                              f"¿Confirma que la vacuna {event['vaccine_type']} fue aplicada a {event['animal_name']}?"):
            try:
                print(f"Intentando marcar como aplicada la vacunación con ID: {event['id']}")
                
                # Actualizar en la base de datos
                update_success = self.db.update_vaccination(event["id"], {"status": "Aplicada"})
                
                if update_success:
                    # Cerrar la ventana de detalles si existe
                    if window:
                        window.destroy()
                        
                    # Actualizar la vista de la lista
                    self.show_list_view()
                    
                    messagebox.showinfo("Éxito", f"La vacunación '{event['vaccine_type']}' ha sido marcada como aplicada")
                else:
                    messagebox.showerror("Error", "No se pudo actualizar el estado de la vacunación en la base de datos")
            except Exception as e:
                print(f"Error detallado al marcar vacunación como aplicada: {str(e)}")
                messagebox.showerror("Error", f"No se pudo actualizar el estado de la vacunación: {str(e)}")
    
    def show_new_vaccination_view(self):
        """Mostrar el formulario para agregar una nueva vacunación"""
        # Limpiar el contenedor actual
        for widget in self.container.winfo_children():
            widget.destroy()
        
        # Título
        title_frame = tk.Frame(self.container, bg=self.colors["bg_main"], pady=10)
        title_frame.pack(fill=tk.X, padx=20)
        
        title_label = tk.Label(
            title_frame,
            text="Nueva Vacunación",
            font=self.fonts["header"],
            bg=self.colors["bg_main"],
            fg=self.colors["text_dark"]
        )
        title_label.pack(side=tk.LEFT)
        
        # Formulario
        form_frame = tk.Frame(self.container, bg=self.colors["card_bg"], padx=20, pady=20)
        form_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        form_frame.config(highlightbackground="#dddddd", highlightthickness=1)
        
        # Obtener lista de animales
        animals = self.db.get_animals()
        
        # Campos del formulario
        fields = [
            ("animal_id", "Animal", "select", animals),
            ("vaccine_type", "Tipo de Vacuna", "text", ""),
            ("scheduled_date", "Fecha Programada", "date", ""),
            ("notes", "Notas", "text", "")
        ]
        
        self.form_vars = {}
        for i, (field, label, field_type, value) in enumerate(fields):
            frame = tk.Frame(form_frame, bg=self.colors["card_bg"], pady=5)
            frame.pack(fill=tk.X)
            
            label_widget = tk.Label(
                frame,
                text=label + ":",
                font=self.fonts["normal"],
                bg=self.colors["card_bg"],
                fg=self.colors["text_dark"],
                width=15,
                anchor="w"
            )
            label_widget.pack(side=tk.LEFT)
            
            if field_type == "text":
                var = tk.StringVar(value=value)
                entry = tk.Entry(
                    frame,
                    textvariable=var,
                    font=self.fonts["normal"],
                    bg="white",
                    fg=self.colors["text_dark"]
                )
                entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
            elif field_type == "select":
                var = tk.StringVar()
                options = [(str(a[0]), a[1]) for a in animals]  # (id, name)
                combo = ttk.Combobox(
                    frame,
                    textvariable=var,
                    values=[name for _, name in options],
                    font=self.fonts["normal"],
                    state="readonly"
                )
                combo.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
                # Guardar referencia a las opciones para obtener el ID
                combo.options = options
            elif field_type == "date":
                var = tk.StringVar(value=value)
                date_frame = tk.Frame(frame, bg=self.colors["card_bg"])
                date_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
                
                # Entry para la fecha
                date_entry = tk.Entry(
                    date_frame,
                    textvariable=var,
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
                    command=lambda v=field: self.show_calendar(v)
                )
                cal_button.pack(side=tk.LEFT)
            
            self.form_vars[field] = var
        
        # Botones
        buttons_frame = tk.Frame(form_frame, bg=self.colors["card_bg"], pady=20)
        buttons_frame.pack(fill=tk.X)
        
        cancel_button = tk.Button(
            buttons_frame,
            text="Cancelar",
            font=self.fonts["normal"],
            bg=self.colors["accent"],
            fg=self.colors["text_light"],
            padx=10,
            relief=tk.FLAT,
            cursor="hand2",
            command=self.show_list_view
        )
        cancel_button.pack(side=tk.LEFT, padx=5)
        
        save_button = tk.Button(
            buttons_frame,
            text="Guardar",
            font=self.fonts["normal"],
            bg=self.colors["primary"],
            fg=self.colors["text_light"],
            padx=10,
            relief=tk.FLAT,
            cursor="hand2",
            command=self.save_vaccination
        )
        save_button.pack(side=tk.RIGHT, padx=5)
    
    def save_vaccination(self):
        """Guardar una nueva vacunación en la base de datos"""
        try:
            # Verificar campos obligatorios
            print("Intentando guardar una nueva vacunación...")
            
            if not self.form_vars["vaccine_type"].get().strip():
                messagebox.showerror("Error", "El tipo de vacuna es obligatorio")
                return
                
            if not self.form_vars["scheduled_date"].get().strip():
                messagebox.showerror("Error", "La fecha programada es obligatoria")
                return
            
            # Obtener el ID del animal seleccionado
            animal_name = self.form_vars["animal_id"].get()
            if not animal_name:
                messagebox.showerror("Error", "Por favor seleccione un animal")
                return
                
            animals = self.db.get_animals()
            animal_id = None
            for animal in animals:
                if animal[1] == animal_name:  # nombre está en la posición 1
                    animal_id = animal[0]     # id está en la posición 0
                    break
            
            if not animal_id:
                messagebox.showerror("Error", f"Animal no encontrado: '{animal_name}'")
                return
            
            print(f"Animal seleccionado: {animal_name} (ID: {animal_id})")
            
            # Obtener valores del formulario
            vaccination_data = {
                "animal_id": animal_id,
                "vaccine_type": self.form_vars["vaccine_type"].get().strip(),
                "scheduled_date": self.form_vars["scheduled_date"].get().strip(),
                "status": "Pendiente",  # Estado inicial
                "notes": self.form_vars["notes"].get().strip()
            }
            
            print(f"Datos de vacunación a guardar: {vaccination_data}")
            
            # Validar fecha
            try:
                scheduled_date = datetime.strptime(vaccination_data["scheduled_date"], "%Y-%m-%d")
                today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
                
                if scheduled_date < today:
                    messagebox.showerror("Error", "No se puede programar una vacunación para una fecha anterior a hoy")
                    return
                
            except ValueError:
                messagebox.showerror("Error", "Formato de fecha inválido. Use YYYY-MM-DD")
                return
            
            # Guardar en la base de datos usando una estructura simplificada
            try:
                print("Intentando insertar en la base de datos...")
                vaccination_id = self.db.add_vaccination(vaccination_data)
                
                if not vaccination_id:
                    messagebox.showerror("Error", "No se pudo guardar la vacunación en la base de datos")
                    return
                    
                print(f"Vacunación guardada con ID: {vaccination_id}")
                
                # Mostrar mensaje de éxito
                messagebox.showinfo("Éxito", f"Vacunación '{vaccination_data['vaccine_type']}' guardada correctamente para {animal_name}")
                
                # Actualizar calendario si existe una instancia del dashboard
                self.update_dashboard_calendar()
                
                # Volver a la vista de lista
                self.show_list_view()
            except Exception as e:
                print(f"Error detallado al guardar en la base de datos: {str(e)}")
                raise
            
        except Exception as e:
            print(f"Error detallado al guardar la vacunación: {str(e)}")
            messagebox.showerror("Error", f"Error al guardar la vacunación: {str(e)}")
            
    def update_dashboard_calendar(self):
        """Actualizar el calendario del dashboard si existe"""
        try:
            # Intentar obtener la instancia del dashboard desde el parent
            dashboard = None
            for widget in self.parent.winfo_children():
                if widget.__class__.__name__ == "Dashboard":
                    dashboard = widget
                    break
            
            # Si encontramos el dashboard, actualizar su calendario
            if dashboard and hasattr(dashboard, 'refresh_calendar'):
                dashboard.refresh_calendar()
                print("Calendario del dashboard actualizado")
            else:
                print("No se pudo encontrar el dashboard o no tiene método refresh_calendar")
                
        except Exception as e:
            print(f"Error al intentar actualizar el calendario: {str(e)}")
    
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
            year=datetime.now().year,
            month=datetime.now().month,
            day=datetime.now().day,
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
    
    def format_date(self, date_str):
        """Formatear fecha para mostrar en formato DD/MM/YYYY"""
        if not date_str:
            return "No especificada"
            
        try:
            # Intentar convertir desde formato ISO (YYYY-MM-DD)
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            return date_obj.strftime("%d/%m/%Y")
        except ValueError:
            try:
                # Intentar otros formatos comunes
                date_obj = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
                return date_obj.strftime("%d/%m/%Y")
            except ValueError:
                # Si no se puede convertir, devolver la cadena original
                return date_str
    
    def __del__(self):
        """Destructor para cerrar la conexión a la base de datos"""
        if hasattr(self, 'db'):
            self.db.close()
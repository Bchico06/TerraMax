import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from database import Database

class TreatmentsModule:
    def __init__(self, parent, colors, fonts):
        self.parent = parent
        self.colors = colors
        self.fonts = fonts
        self.db = Database()
        self.current_view = None
        self.current_treatment_id = None
        
        # Crear el contenedor principal
        self.container = tk.Frame(parent, bg=self.colors["bg_main"])
        self.container.pack(fill=tk.BOTH, expand=True)
        
        # Mostrar la vista de lista por defecto
        self.show_list_view()
    
    def show_list_view(self):
        """Mostrar la vista de lista de tratamientos"""
        # Limpiar el contenedor actual
        for widget in self.container.winfo_children():
            widget.destroy()
        
        # Título
        title_frame = tk.Frame(self.container, bg=self.colors["bg_main"], pady=10)
        title_frame.pack(fill=tk.X, padx=20)
        
        title_label = tk.Label(
            title_frame,
            text="Gestión de Tratamientos",
            font=self.fonts["header"],
            bg=self.colors["bg_main"],
            fg=self.colors["text_dark"]
        )
        title_label.pack(side=tk.LEFT)
        
        # Botón para agregar nuevo tratamiento
        add_button = tk.Button(
            title_frame,
            text="+ Agregar Nuevo Tratamiento",
            font=self.fonts["normal"],
            bg=self.colors["primary"],
            fg=self.colors["text_light"],
            padx=10,
            relief=tk.FLAT,
            cursor="hand2",
            command=self.show_new_treatment_view
        )
        add_button.pack(side=tk.RIGHT)
        
        # Crear tabla
        table_frame = tk.Frame(self.container, bg=self.colors["card_bg"], padx=15, pady=15)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        table_frame.config(highlightbackground="#dddddd", highlightthickness=1)
        
        # Definir columnas
        columns = ("id", "animal_name", "treatment_type", "start_date", "end_date", "status", "actions")
        self.treatments_table = ttk.Treeview(table_frame, columns=columns, show="headings", height=10)
        
        # Configurar columnas
        self.treatments_table.heading("id", text="ID")
        self.treatments_table.heading("animal_name", text="Animal")
        self.treatments_table.heading("treatment_type", text="Tipo de Tratamiento")
        self.treatments_table.heading("start_date", text="Fecha Inicio")
        self.treatments_table.heading("end_date", text="Fecha Fin")
        self.treatments_table.heading("status", text="Estado")
        self.treatments_table.heading("actions", text="Acciones")
        
        # Ajustar anchos de columna
        self.treatments_table.column("id", width=50)
        self.treatments_table.column("animal_name", width=150)
        self.treatments_table.column("treatment_type", width=150)
        self.treatments_table.column("start_date", width=100)
        self.treatments_table.column("end_date", width=100)
        self.treatments_table.column("status", width=100)
        self.treatments_table.column("actions", width=150)
        
        # Agregar scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.treatments_table.yview)
        self.treatments_table.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.treatments_table.pack(fill=tk.BOTH, expand=True)
        
        # Vincular evento de doble clic
        self.treatments_table.bind("<Double-1>", self.on_treatment_click)
        
        # Llenar tabla con datos
        self.refresh_treatments_table()
    
    def refresh_treatments_table(self):
        """Actualizar la tabla de tratamientos con los datos de la base de datos"""
        # Limpiar tabla
        for item in self.treatments_table.get_children():
            self.treatments_table.delete(item)
        
        # Obtener tratamientos de la base de datos
        treatments = self.db.get_treatments()
        
        # Agregar tratamientos a la tabla
        for treatment in treatments:
            values = (
                treatment[0],  # id
                treatment[7],  # animal_name
                treatment[2],  # treatment_type
                treatment[3],  # start_date
                treatment[4],  # end_date
                treatment[5],  # status
                "Ver/Editar"
            )
            self.treatments_table.insert("", tk.END, values=values)
    
    def show_new_treatment_view(self):
        """Mostrar el formulario para agregar un nuevo tratamiento"""
        # Limpiar el contenedor actual
        for widget in self.container.winfo_children():
            widget.destroy()
        
        # Título
        title_frame = tk.Frame(self.container, bg=self.colors["bg_main"], pady=10)
        title_frame.pack(fill=tk.X, padx=20)
        
        title_label = tk.Label(
            title_frame,
            text="Nuevo Tratamiento",
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
            ("treatment_type", "Tipo de Tratamiento", "text", ""),
            ("start_date", "Fecha Inicio", "date", ""),
            ("end_date", "Fecha Fin", "date", ""),
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
                entry = tk.Entry(
                    frame,
                    textvariable=var,
                    font=self.fonts["normal"],
                    bg="white",
                    fg=self.colors["text_dark"]
                )
                entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
            
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
            command=self.save_treatment
        )
        save_button.pack(side=tk.RIGHT, padx=5)
    
    def save_treatment(self):
        """Guardar un nuevo tratamiento en la base de datos"""
        try:
            # Obtener el ID del animal seleccionado
            animal_name = self.form_vars["animal_id"].get()
            animals = self.db.get_animals()
            animal_id = next((a[0] for a in animals if a[1] == animal_name), None)
            
            if not animal_id:
                messagebox.showerror("Error", "Por favor seleccione un animal válido")
                return
            
            # Obtener valores del formulario
            treatment_data = {
                "animal_id": animal_id,
                "treatment_type": self.form_vars["treatment_type"].get(),
                "start_date": self.form_vars["start_date"].get(),
                "end_date": self.form_vars["end_date"].get(),
                "status": "En curso",  # Estado inicial
                "notes": self.form_vars["notes"].get()
            }
            
            # Validar fechas
            try:
                start_date = datetime.strptime(treatment_data["start_date"], "%Y-%m-%d")
                end_date = datetime.strptime(treatment_data["end_date"], "%Y-%m-%d")
                if end_date < start_date:
                    messagebox.showerror("Error", "La fecha de fin no puede ser anterior a la fecha de inicio")
                    return
            except ValueError:
                messagebox.showerror("Error", "Formato de fecha inválido. Use YYYY-MM-DD")
                return
            
            # Guardar en la base de datos
            self.db.add_treatment(treatment_data)
            
            # Mostrar mensaje de éxito
            messagebox.showinfo("Éxito", "Tratamiento guardado correctamente")
            
            # Volver a la vista de lista
            self.show_list_view()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar el tratamiento: {str(e)}")
    
    def show_detail_view(self, treatment_id):
        """Mostrar los detalles de un tratamiento"""
        # Limpiar el contenedor actual
        for widget in self.container.winfo_children():
            widget.destroy()
        
        # Obtener datos del tratamiento
        treatment = self.db.get_treatment(treatment_id)
        if not treatment:
            messagebox.showerror("Error", "Tratamiento no encontrado")
            self.show_list_view()
            return
        
        # Título
        title_frame = tk.Frame(self.container, bg=self.colors["bg_main"], pady=10)
        title_frame.pack(fill=tk.X, padx=20)
        
        title_label = tk.Label(
            title_frame,
            text="Detalles del Tratamiento",
            font=self.fonts["header"],
            bg=self.colors["bg_main"],
            fg=self.colors["text_dark"]
        )
        title_label.pack(side=tk.LEFT)
        
        # Botones de acción
        buttons_frame = tk.Frame(title_frame, bg=self.colors["bg_main"])
        buttons_frame.pack(side=tk.RIGHT)
        
        edit_button = tk.Button(
            buttons_frame,
            text="Editar",
            font=self.fonts["normal"],
            bg=self.colors["primary"],
            fg=self.colors["text_light"],
            padx=10,
            relief=tk.FLAT,
            cursor="hand2",
            command=lambda: self.show_edit_view(treatment_id)
        )
        edit_button.pack(side=tk.LEFT, padx=5)
        
        back_button = tk.Button(
            buttons_frame,
            text="Volver",
            font=self.fonts["normal"],
            bg=self.colors["accent"],
            fg=self.colors["text_light"],
            padx=10,
            relief=tk.FLAT,
            cursor="hand2",
            command=self.show_list_view
        )
        back_button.pack(side=tk.LEFT, padx=5)
        
        # Contenedor de detalles
        details_frame = tk.Frame(self.container, bg=self.colors["card_bg"], padx=20, pady=20)
        details_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        details_frame.config(highlightbackground="#dddddd", highlightthickness=1)
        
        # Mostrar detalles
        details = [
            ("ID", str(treatment[0])),
            ("Animal", treatment[7]),  # animal_name
            ("Tipo de Tratamiento", treatment[2]),
            ("Fecha Inicio", treatment[3]),
            ("Fecha Fin", treatment[4]),
            ("Estado", treatment[5]),
            ("Notas", treatment[8] if treatment[8] else "Sin notas")
        ]
        
        for label, value in details:
            frame = tk.Frame(details_frame, bg=self.colors["card_bg"], pady=5)
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
            
            value_widget = tk.Label(
                frame,
                text=value,
                font=self.fonts["normal"],
                bg=self.colors["card_bg"],
                fg=self.colors["text_dark"]
            )
            value_widget.pack(side=tk.LEFT, padx=5)
    
    def show_edit_view(self, treatment_id):
        """Mostrar el formulario para editar un tratamiento"""
        # Limpiar el contenedor actual
        for widget in self.container.winfo_children():
            widget.destroy()
        
        # Obtener datos del tratamiento
        treatment = self.db.get_treatment(treatment_id)
        if not treatment:
            messagebox.showerror("Error", "Tratamiento no encontrado")
            self.show_list_view()
            return
        
        # Título
        title_frame = tk.Frame(self.container, bg=self.colors["bg_main"], pady=10)
        title_frame.pack(fill=tk.X, padx=20)
        
        title_label = tk.Label(
            title_frame,
            text="Editar Tratamiento",
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
            ("animal_id", "Animal", "select", animals, treatment[7]),  # animal_name
            ("treatment_type", "Tipo de Tratamiento", "text", treatment[2]),
            ("start_date", "Fecha Inicio", "date", treatment[3]),
            ("end_date", "Fecha Fin", "date", treatment[4]),
            ("status", "Estado", "select", ["En curso", "Completado", "Cancelado"], treatment[5]),
            ("notes", "Notas", "text", treatment[8] if treatment[8] else "")
        ]
        
        self.form_vars = {}
        for i, (field, label, field_type, options, value) in enumerate(fields):
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
                var = tk.StringVar(value=value)
                if field == "animal_id":
                    combo = ttk.Combobox(
                        frame,
                        textvariable=var,
                        values=[a[1] for a in options],  # Solo nombres
                        font=self.fonts["normal"],
                        state="readonly"
                    )
                else:
                    combo = ttk.Combobox(
                        frame,
                        textvariable=var,
                        values=options,
                        font=self.fonts["normal"],
                        state="readonly"
                    )
                combo.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
            
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
            command=lambda: self.show_detail_view(treatment_id)
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
            command=lambda: self.update_treatment(treatment_id)
        )
        save_button.pack(side=tk.RIGHT, padx=5)
    
    def update_treatment(self, treatment_id):
        """Actualizar un tratamiento en la base de datos"""
        try:
            # Obtener el ID del animal seleccionado
            animal_name = self.form_vars["animal_id"].get()
            animals = self.db.get_animals()
            animal_id = next((a[0] for a in animals if a[1] == animal_name), None)
            
            if not animal_id:
                messagebox.showerror("Error", "Por favor seleccione un animal válido")
                return
            
            # Obtener valores del formulario
            treatment_data = {
                "animal_id": animal_id,
                "treatment_type": self.form_vars["treatment_type"].get(),
                "start_date": self.form_vars["start_date"].get(),
                "end_date": self.form_vars["end_date"].get(),
                "status": self.form_vars["status"].get(),
                "notes": self.form_vars["notes"].get()
            }
            
            # Validar fechas
            try:
                start_date = datetime.strptime(treatment_data["start_date"], "%Y-%m-%d")
                end_date = datetime.strptime(treatment_data["end_date"], "%Y-%m-%d")
                if end_date < start_date:
                    messagebox.showerror("Error", "La fecha de fin no puede ser anterior a la fecha de inicio")
                    return
            except ValueError:
                messagebox.showerror("Error", "Formato de fecha inválido. Use YYYY-MM-DD")
                return
            
            # Actualizar en la base de datos
            self.db.update_treatment(treatment_id, treatment_data)
            
            # Mostrar mensaje de éxito
            messagebox.showinfo("Éxito", "Tratamiento actualizado correctamente")
            
            # Volver a la vista de detalles
            self.show_detail_view(treatment_id)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al actualizar el tratamiento: {str(e)}")
    
    def on_treatment_click(self, event):
        """Manejar clic en la tabla de tratamientos"""
        item = self.treatments_table.identify("item", event.x, event.y)
        if item:
            values = self.treatments_table.item(item, "values")
            treatment_id = values[0]  # El ID está en la primera columna
            self.show_detail_view(treatment_id)
    
    def __del__(self):
        """Destructor para cerrar la conexión a la base de datos"""
        if hasattr(self, 'db'):
            self.db.close()
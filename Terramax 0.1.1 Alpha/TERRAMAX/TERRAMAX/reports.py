import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import datetime
from database import Database

class ReportsModule:
    def __init__(self, container, colors, fonts):
        self.container = container
        self.colors = colors
        self.fonts = fonts
        self.db = Database()
        
    def show_reports_view(self):
        """Mostrar la vista principal de reportes"""
        # Limpiar el contenedor actual
        for widget in self.container.winfo_children():
            widget.destroy()
            
        # Crear el título
        title_frame = tk.Frame(self.container, bg=self.colors["bg_main"])
        title_frame.pack(fill=tk.X, padx=20, pady=10)
        
        title_label = tk.Label(
            title_frame,
            text="Reportes y Estadísticas",
            font=self.fonts["header"],
            bg=self.colors["bg_main"],
            fg=self.colors["text_dark"]
        )
        title_label.pack(side=tk.LEFT)
        
        # Crear el contenedor para los reportes
        reports_frame = tk.Frame(self.container, bg=self.colors["bg_main"])
        reports_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Crear pestañas para diferentes tipos de reportes
        notebook = ttk.Notebook(reports_frame)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # Pestaña de Resumen General
        summary_frame = tk.Frame(notebook, bg=self.colors["bg_main"])
        notebook.add(summary_frame, text="Resumen General")
        self.create_summary_tab(summary_frame)
        
        # Pestaña de Estadísticas por Tipo
        type_stats_frame = tk.Frame(notebook, bg=self.colors["bg_main"])
        notebook.add(type_stats_frame, text="Estadísticas por Tipo")
        self.create_type_stats_tab(type_stats_frame)
        
        # Pestaña de Alimentación
        feeding_frame = tk.Frame(notebook, bg=self.colors["bg_main"])
        notebook.add(feeding_frame, text="Alimentación")
        self.create_feeding_tab(feeding_frame)
        
        # Pestaña de Mortalidad
        mortality_frame = tk.Frame(notebook, bg=self.colors["bg_main"])
        notebook.add(mortality_frame, text="Mortalidad")
        self.create_mortality_tab(mortality_frame)
        
    def create_summary_tab(self, parent):
        """Crear la pestaña de resumen general"""
        # Obtener datos del resumen
        total_animals = self.db.execute_query("SELECT COUNT(*) FROM animals")[0][0]
        
        # Crear gráfico de estado de salud
        health_data = self.db.execute_query("""
            SELECT health_status, COUNT(*) as count 
            FROM animals 
            GROUP BY health_status
        """)
        
        fig, ax = plt.subplots(figsize=(6, 4))
        labels = [row[0] for row in health_data]
        values = [row[1] for row in health_data]
        colors = ['#4CAF50', '#FFC107', '#2196F3', '#f44336']
        ax.pie(values, labels=labels, colors=colors, autopct='%1.1f%%')
        ax.set_title('Estado de Salud de los Animales')
        
        # Agregar el gráfico al frame
        canvas = FigureCanvasTkAgg(fig, parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Mostrar estadísticas adicionales
        stats_frame = tk.Frame(parent, bg=self.colors["bg_main"])
        stats_frame.pack(fill=tk.X, pady=10)
        
        stats = [
            ("Total de Animales", total_animals)
        ]
        
        for label, value in stats:
            frame = tk.Frame(stats_frame, bg=self.colors["bg_main"])
            frame.pack(fill=tk.X, pady=2)
            
            label_widget = tk.Label(
                frame,
                text=label + ":",
                font=self.fonts["normal_bold"],
                bg=self.colors["bg_main"],
                fg=self.colors["text_dark"]
            )
            label_widget.pack(side=tk.LEFT, padx=5)
            
            value_widget = tk.Label(
                frame,
                text=str(value),
                font=self.fonts["normal"],
                bg=self.colors["bg_main"],
                fg=self.colors["text_dark"]
            )
            value_widget.pack(side=tk.LEFT)
            
    def create_type_stats_tab(self, parent):
        """Crear la pestaña de estadísticas por tipo"""
        # Obtener datos por especie
        species_data = self.db.execute_query("""
            SELECT species, COUNT(*) as count
            FROM animals
            GROUP BY species
        """)
        
        # Crear gráfico de barras
        fig, ax = plt.subplots(figsize=(8, 4))
        species = [row[0] for row in species_data]
        counts = [row[1] for row in species_data]
        
        ax.bar(species, counts)
        ax.set_title('Animales por Especie')
        ax.set_xlabel('Especie')
        ax.set_ylabel('Cantidad')
        plt.xticks(rotation=45)
        
        # Agregar el gráfico al frame
        canvas = FigureCanvasTkAgg(fig, parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, pady=10)
        
    def create_feeding_tab(self, parent):
        """Crear la pestaña de alimentación"""
        # Obtener datos de alimentación
        feeding_data = self.db.execute_query("""
            SELECT feeding_type, COUNT(*) as count
            FROM animals
            WHERE life_status = 'Vivo'
            GROUP BY feeding_type
        """)
        
        # Crear gráfico circular
        fig, ax = plt.subplots(figsize=(6, 4))
        feeding_types = [row[0] for row in feeding_data]
        counts = [row[1] for row in feeding_data]
        
        ax.pie(counts, labels=feeding_types, autopct='%1.1f%%')
        ax.set_title('Distribución por Tipo de Alimentación')
        
        # Agregar el gráfico al frame
        canvas = FigureCanvasTkAgg(fig, parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Mostrar estadísticas de peso promedio
        weight_data = self.db.execute_query("""
            SELECT feeding_type, AVG(weight) as avg_weight
            FROM animals
            WHERE life_status = 'Vivo'
            GROUP BY feeding_type
        """)
        
        stats_frame = tk.Frame(parent, bg=self.colors["bg_main"])
        stats_frame.pack(fill=tk.X, pady=10)
        
        for feeding_type, avg_weight in weight_data:
            frame = tk.Frame(stats_frame, bg=self.colors["bg_main"])
            frame.pack(fill=tk.X, pady=2)
            
            label_widget = tk.Label(
                frame,
                text=f"Peso promedio ({feeding_type}):",
                font=self.fonts["normal_bold"],
                bg=self.colors["bg_main"],
                fg=self.colors["text_dark"]
            )
            label_widget.pack(side=tk.LEFT, padx=5)
            
            value_widget = tk.Label(
                frame,
                text=f"{avg_weight:.2f} kg",
                font=self.fonts["normal"],
                bg=self.colors["bg_main"],
                fg=self.colors["text_dark"]
            )
            value_widget.pack(side=tk.LEFT)
            
    def create_mortality_tab(self, parent):
        """Crear la pestaña de mortalidad"""
        # Obtener datos de mortalidad por razón
        mortality_data = self.db.execute_query("""
            SELECT death_reason, COUNT(*) as count
            FROM animals
            WHERE life_status = 'Muerto'
            GROUP BY death_reason
        """)
        
        if mortality_data:
            # Crear gráfico de barras
            fig, ax = plt.subplots(figsize=(8, 4))
            reasons = [row[0] for row in mortality_data]
            counts = [row[1] for row in mortality_data]
            
            ax.bar(reasons, counts)
            ax.set_title('Mortalidad por Razón')
            ax.set_xlabel('Razón')
            ax.set_ylabel('Cantidad')
            plt.xticks(rotation=45)
            
            # Agregar el gráfico al frame
            canvas = FigureCanvasTkAgg(fig, parent)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, pady=10)
            
            # Mostrar estadísticas adicionales
            stats_frame = tk.Frame(parent, bg=self.colors["bg_main"])
            stats_frame.pack(fill=tk.X, pady=10)
            
            for reason, count in mortality_data:
                frame = tk.Frame(stats_frame, bg=self.colors["bg_main"])
                frame.pack(fill=tk.X, pady=2)
                
                label_widget = tk.Label(
                    frame,
                    text=f"{reason}:",
                    font=self.fonts["normal_bold"],
                    bg=self.colors["bg_main"],
                    fg=self.colors["text_dark"]
                )
                label_widget.pack(side=tk.LEFT, padx=5)
                
                value_widget = tk.Label(
                    frame,
                    text=str(count),
                    font=self.fonts["normal"],
                    bg=self.colors["bg_main"],
                    fg=self.colors["text_dark"]
                )
                value_widget.pack(side=tk.LEFT)
        else:
            # Mostrar mensaje si no hay datos de mortalidad
            message = tk.Label(
                parent,
                text="No hay datos de mortalidad registrados",
                font=self.fonts["normal"],
                bg=self.colors["bg_main"],
                fg=self.colors["text_dark"]
            )
            message.pack(pady=20) 
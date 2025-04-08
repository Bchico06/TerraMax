import tkinter as tk
from tkinter import ttk
from animals import AnimalsModule
from reports import ReportsModule

class TERRAMAX:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("TERRAMAX - Sistema de Gestión Ganadera")
        self.root.geometry("1200x800")
        
        # Definir colores
        self.colors = {
            "bg_main": "#f5f5f5",
            "bg_accent": "#e0e0e0",
            "primary": "#2196F3",
            "secondary": "#4CAF50",
            "danger": "#f44336",
            "text_dark": "#212121",
            "text_light": "#ffffff"
        }
        
        # Definir fuentes
        self.fonts = {
            "header": ("Helvetica", 24, "bold"),
            "subheader": ("Helvetica", 18, "bold"),
            "normal": ("Helvetica", 12),
            "normal_bold": ("Helvetica", 12, "bold"),
            "button": ("Helvetica", 12)
        }
        
        # Configurar el estilo
        self.setup_styles()
        
        # Crear el contenedor principal
        self.main_container = tk.Frame(self.root, bg=self.colors["bg_main"])
        self.main_container.pack(fill=tk.BOTH, expand=True)
        
        # Crear la barra lateral
        self.create_sidebar()
        
        # Crear el contenedor de contenido
        self.content_container = tk.Frame(self.main_container, bg=self.colors["bg_main"])
        self.content_container.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Inicializar módulos
        self.animals_module = AnimalsModule(self.content_container, self.colors, self.fonts)
        self.reports_module = ReportsModule(self.content_container, self.colors, self.fonts)
        
        # Mostrar la vista de animales por defecto
        self.show_animals_view()
        
    def setup_styles(self):
        """Configurar estilos para widgets"""
        style = ttk.Style()
        style.configure("Sidebar.TButton",
                       font=self.fonts["button"],
                       padding=10)
        
    def create_sidebar(self):
        """Crear la barra lateral de navegación"""
        sidebar = tk.Frame(self.main_container, bg=self.colors["bg_accent"], width=200)
        sidebar.pack(side=tk.LEFT, fill=tk.Y)
        sidebar.pack_propagate(False)
        
        # Título de la aplicación
        title_label = tk.Label(
            sidebar,
            text="TERRAMAX",
            font=self.fonts["header"],
            bg=self.colors["bg_accent"],
            fg=self.colors["text_dark"]
        )
        title_label.pack(pady=20)
        
        # Botones de navegación
        nav_buttons = [
            ("🐄 Animales", self.show_animals_view),
            ("📊 Reportes", self.show_reports_view)
        ]
        
        for text, command in nav_buttons:
            button = tk.Button(
                sidebar,
                text=text,
                font=self.fonts["button"],
                bg=self.colors["bg_accent"],
                fg=self.colors["text_dark"],
                bd=0,
                padx=20,
                pady=10,
                command=command
            )
            button.pack(fill=tk.X, padx=10, pady=5)
            
    def show_animals_view(self):
        """Mostrar la vista de animales"""
        self.animals_module.show_list_view()
        
    def show_reports_view(self):
        """Mostrar la vista de reportes"""
        self.reports_module.show_reports_view()
        
    def run(self):
        """Iniciar la aplicación"""
        self.root.mainloop()

if __name__ == "__main__":
    app = TERRAMAX()
    app.run() 
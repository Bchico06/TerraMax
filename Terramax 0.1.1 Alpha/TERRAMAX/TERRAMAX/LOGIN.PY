import tkinter as tk
from tkinter import messagebox, simpledialog
import json
import os
import hashlib
from tkinter import ttk
import base64

# Importar el dashboard (verificar si existe primero)
try:
    from dashboard import Dashboard
    DASHBOARD_AVAILABLE = True
except ImportError:
    DASHBOARD_AVAILABLE = False

class PinLoginApp:
    def __init__(self, root):
        self.root = root
        self.root.title("TERRAMAX - Acceso Seguro")
        self.root.geometry("400x500")
        self.root.resizable(False, False)
        
        # Set theme colors
        self.bg_color = "#f5f5f5"
        self.primary_color = "#3498db"
        self.accent_color = "#2980b9"
        self.text_color = "#2c3e50"
        
        self.root.configure(bg=self.bg_color)
        
        # Load or create config file
        self.config_file = "config.json"
        self.load_config()
        
        # Set up the UI
        self.setup_ui()
        
    def load_config(self):
        """Load configuration or create default if not exists"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, "r") as f:
                    self.config = json.load(f)
            except:
                self.create_default_config()
        else:
            self.create_default_config()
            
    def create_default_config(self):
        """Create default configuration"""
        self.config = {
            "pin_hash": "",
            "remember_me": False,
            "first_time": True
        }
        self.save_config()
        
    def save_config(self):
        """Save configuration to file"""
        with open(self.config_file, "w") as f:
            json.dump(self.config, f)
            
    def hash_pin(self, pin):
        """Create secure hash of PIN"""
        salt = "TERRAMAX_SALT"  # In production, use a random salt stored securely
        return hashlib.sha256((pin + salt).encode()).hexdigest()
    
    def setup_ui(self):
        """Set up the user interface"""
        # Frame for content
        content_frame = tk.Frame(self.root, bg=self.bg_color)
        content_frame.pack(pady=20, fill=tk.BOTH, expand=True)
        
        # Logo
        self.logo_frame = tk.Frame(content_frame, bg=self.bg_color)
        self.logo_frame.pack(pady=10)
        
        logo_label = tk.Label(
            self.logo_frame, 
            text="TERRAMAX", 
            font=("Helvetica", 24, "bold"),
            fg=self.primary_color,
            bg=self.bg_color
        )
        logo_label.pack()
        
        slogan_label = tk.Label(
            self.logo_frame,
            text="Sistema de Gestión Veterinaria",
            font=("Helvetica", 12),
            fg=self.text_color,
            bg=self.bg_color
        )
        slogan_label.pack(pady=5)
        
        # Main container
        self.main_frame = tk.Frame(content_frame, bg=self.bg_color)
        self.main_frame.pack(pady=20, padx=40, fill=tk.X)
        
        # Title
        title_label = tk.Label(
            self.main_frame,
            text="Ingrese su PIN de acceso",
            font=("Helvetica", 14, "bold"),
            fg=self.text_color,
            bg=self.bg_color
        )
        title_label.pack(pady=10)
        
        # PIN entry
        pin_frame = tk.Frame(self.main_frame, bg=self.bg_color)
        pin_frame.pack(pady=10, fill=tk.X)
        
        self.pin_var = tk.StringVar()
        self.show_pin = tk.BooleanVar(value=False)
        
        style = ttk.Style()
        style.configure("TEntry", padding=10, font=("Helvetica", 12))
        
        self.pin_entry = ttk.Entry(
            pin_frame,
            textvariable=self.pin_var,
            show="•",
            width=20,
            font=("Helvetica", 14),
            justify='center'
        )
        self.pin_entry.pack(pady=5, fill=tk.X)
        
        # Show/Hide PIN checkbox
        show_pin_check = ttk.Checkbutton(
            pin_frame,
            text="Mostrar PIN",
            variable=self.show_pin,
            command=self.toggle_pin_visibility,
            style="TCheckbutton"
        )
        show_pin_check.pack(anchor=tk.W, pady=5)
        
        # Remember me checkbox
        self.remember_var = tk.BooleanVar(value=self.config.get("remember_me", False))
        remember_check = ttk.Checkbutton(
            pin_frame,
            text="Recordarme en este dispositivo",
            variable=self.remember_var,
            style="TCheckbutton"
        )
        remember_check.pack(anchor=tk.W, pady=5)
        
        # Login button
        login_button = tk.Button(
            self.main_frame,
            text="Ingresar",
            font=("Helvetica", 12, "bold"),
            bg=self.primary_color,
            fg="white",
            activebackground=self.accent_color,
            activeforeground="white",
            relief=tk.FLAT,
            padx=10,
            pady=8,
            cursor="hand2",
            command=self.verify_pin
        )
        login_button.pack(pady=15, fill=tk.X)
        
        # Reset PIN link
        reset_frame = tk.Frame(self.main_frame, bg=self.bg_color)
        reset_frame.pack(pady=5)
        
        reset_link = tk.Label(
            reset_frame,
            text="Cambiar PIN",
            font=("Helvetica", 10, "underline"),
            fg=self.primary_color,
            bg=self.bg_color,
            cursor="hand2"
        )
        reset_link.pack()
        reset_link.bind("<Button-1>", self.reset_pin)
        
        # Error message
        self.error_var = tk.StringVar()
        self.error_label = tk.Label(
            self.main_frame,
            textvariable=self.error_var,
            font=("Helvetica", 10),
            fg="red",
            bg=self.bg_color,
            wraplength=300
        )
        self.error_label.pack(pady=10)
        
        # Footer
        footer_frame = tk.Frame(content_frame, bg=self.bg_color)
        footer_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=10)
        
        footer_text = tk.Label(
            footer_frame,
            text="© 2023 TERRAMAX. Todos los derechos reservados.",
            font=("Helvetica", 8),
            fg=self.text_color,
            bg=self.bg_color
        )
        footer_text.pack()
        
        # Check if first time
        if self.config["first_time"]:
            self.root.after(100, self.setup_first_time)
        elif self.config["remember_me"]:
            self.root.after(100, self.auto_login)
            
        # Add key bindings
        self.root.bind("<Return>", lambda event: self.verify_pin())
        self.pin_entry.focus()
        
    def auto_login(self):
        """Auto login if remember me is enabled"""
        self.open_main_application()
        
    def setup_first_time(self):
        """Setup process for first time users"""
        messagebox.showinfo(
            "Bienvenido a TERRAMAX",
            "Parece que es la primera vez que inicia el sistema.\nPor favor, configure un PIN de acceso."
        )
        self.reset_pin()
        
    def toggle_pin_visibility(self):
        """Toggle PIN visibility"""
        if self.show_pin.get():
            self.pin_entry.config(show="")
        else:
            self.pin_entry.config(show="•")
            
    def verify_pin(self):
        """Verify the entered PIN"""
        entered_pin = self.pin_var.get()
        
        if not entered_pin:
            self.error_var.set("Por favor ingrese su PIN")
            return
            
        if not entered_pin.isdigit():
            self.error_var.set("El PIN debe contener solo números")
            return
            
        # For first time, save the PIN
        if self.config["first_time"]:
            self.config["pin_hash"] = self.hash_pin(entered_pin)
            self.config["first_time"] = False
            self.config["remember_me"] = self.remember_var.get()
            self.save_config()
            messagebox.showinfo(
                "PIN Configurado",
                "Su PIN ha sido configurado exitosamente."
            )
            self.open_main_application()
            return
            
        # Verify PIN
        if self.hash_pin(entered_pin) == self.config["pin_hash"]:
            self.config["remember_me"] = self.remember_var.get()
            self.save_config()
            self.error_var.set("")
            self.open_main_application()
        else:
            self.error_var.set("El PIN ingresado es incorrecto. Intentá de nuevo.")
            self.pin_var.set("")
            self.pin_entry.focus()
            
    def reset_pin(self, event=None):
        """Reset or change PIN"""
        if not self.config["first_time"]:
            # Verify current PIN first
            current_pin = simpledialog.askstring(
                "Verificación",
                "Ingrese su PIN actual:",
                show="•"
            )
            
            if not current_pin:
                return
                
            if self.hash_pin(current_pin) != self.config["pin_hash"]:
                messagebox.showerror(
                    "Error",
                    "El PIN actual ingresado es incorrecto."
                )
                return
                
        # Ask for new PIN
        new_pin = simpledialog.askstring(
            "Nuevo PIN", 
            "Ingrese un nuevo PIN numérico (4-6 dígitos):",
            show="•"
        )
        
        if not new_pin:
            return
            
        if not new_pin.isdigit() or len(new_pin) < 4 or len(new_pin) > 6:
            messagebox.showerror(
                "Error",
                "El PIN debe ser numérico y tener entre 4 y 6 dígitos."
            )
            return
            
        # Confirm new PIN
        confirm_pin = simpledialog.askstring(
            "Confirmar PIN",
            "Confirme el nuevo PIN:",
            show="•"
        )
        
        if new_pin != confirm_pin:
            messagebox.showerror(
                "Error",
                "Los PINs no coinciden. Intente nuevamente."
            )
            return
            
        # Save new PIN
        self.config["pin_hash"] = self.hash_pin(new_pin)
        self.config["first_time"] = False
        self.save_config()
        
        messagebox.showinfo(
            "PIN Actualizado",
            "Su PIN ha sido actualizado exitosamente."
        )
        
    def open_main_application(self):
        """Open the main application after successful login"""
        self.root.withdraw()  # Hide login window
        
        # Si el Dashboard está disponible, úsalo; si no, muestra una ventana simple
        if DASHBOARD_AVAILABLE:
            # Crear ventana principal con el dashboard
            main_window = tk.Toplevel(self.root)
            # Pasar una función de callback para el cierre de sesión
            dashboard = Dashboard(main_window, logout_callback=lambda: self.logout(main_window))
            # Configurar comportamiento al cerrar la ventana
            main_window.protocol("WM_DELETE_WINDOW", lambda: self.logout(main_window))
        else:
            # Ventana simple de ejemplo (como respaldo)
            self.create_simple_main_window()
    
    def create_simple_main_window(self):
        """Crear una ventana principal simple si el dashboard no está disponible"""
        # Create and show main application window
        main_window = tk.Toplevel(self.root)
        main_window.title("TERRAMAX - Sistema Principal")
        main_window.geometry("800x600")
        
        # Add a simple welcome screen - in a real app, this would be your main interface
        main_frame = tk.Frame(main_window, bg="#f5f5f5")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        welcome_label = tk.Label(
            main_frame,
            text="¡Bienvenido al Sistema TERRAMAX!",
            font=("Helvetica", 20, "bold"),
            fg="#3498db",
            bg="#f5f5f5"
        )
        welcome_label.pack(pady=30)
        
        info_label = tk.Label(
            main_frame,
            text="Ha iniciado sesión correctamente.",
            font=("Helvetica", 14),
            fg="#2c3e50",
            bg="#f5f5f5"
        )
        info_label.pack(pady=10)
        
        error_label = tk.Label(
            main_frame,
            text="ADVERTENCIA: El módulo dashboard.py no está disponible.\nSe muestra esta interfaz simplificada en su lugar.",
            font=("Helvetica", 12),
            fg="#e74c3c",
            bg="#f5f5f5"
        )
        error_label.pack(pady=20)
        
        # Add a logout button
        logout_button = tk.Button(
            main_frame,
            text="Cerrar Sesión",
            font=("Helvetica", 12),
            bg="#e74c3c",
            fg="white",
            padx=10,
            pady=5,
            relief=tk.FLAT,
            cursor="hand2",
            command=lambda: self.logout(main_window)
        )
        logout_button.pack(pady=20)
        
        # Handle close event
        main_window.protocol("WM_DELETE_WINDOW", lambda: self.logout(main_window))
        
    def logout(self, main_window):
        """Logout from the application"""
        main_window.destroy()
        self.pin_var.set("")
        self.root.deiconify()  # Show login window again
        self.pin_entry.focus()

if __name__ == "__main__":
    root = tk.Tk()
    app = PinLoginApp(root)
    root.mainloop()

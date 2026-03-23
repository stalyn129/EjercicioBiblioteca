import customtkinter as ctk
from datetime import datetime
from Modelo.conexion import crear_conexion

# ── TEMA GLOBAL ────────────────────────────────────────────────────────────
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# Paleta de colores centralizada
COLORES = {
    "bg_principal":  "#0f0f17",
    "bg_sidebar":    "#13131f",
    "bg_card":       "#1a1a2e",
    "bg_hover":      "#22223b",
    "acento":        "#7c3aed",
    "acento_claro":  "#a78bfa",
    "acento2":       "#06b6d4",
    "texto":         "#e2e8f0",
    "texto_dim":     "#94a3b8",
    "borde":         "#2d2d44",
    "exito":         "#10b981",
    "alerta":        "#f59e0b",
    "error":         "#ef4444",
}


class App(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.title("Sistema de Biblioteca")
        self.geometry("1200x720")
        self.minsize(1000, 600)
        self.configure(fg_color=COLORES["bg_principal"])

        # ── LAYOUT PRINCIPAL ───────────────────────────────────────────────
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Sidebar
        from VistaTk.sidebar import Sidebar
        self.sidebar = Sidebar(self, self.cambiar_vista, COLORES)
        self.sidebar.grid(row=0, column=0, sticky="nsew")

        # Panel derecho (header + contenido)
        self.panel_derecho = ctk.CTkFrame(self, fg_color=COLORES["bg_principal"], corner_radius=0)
        self.panel_derecho.grid(row=0, column=1, sticky="nsew")
        self.panel_derecho.grid_rowconfigure(1, weight=1)
        self.panel_derecho.grid_columnconfigure(0, weight=1)

        # Header
        self._crear_header()

        # Contenedor de vistas
        self.container = ctk.CTkFrame(
            self.panel_derecho,
            fg_color=COLORES["bg_principal"],
            corner_radius=0
        )
        self.container.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))

        self.vista_actual = None
        self.cambiar_vista("prestamos")

    # ──────────────────────────────────────────────────────────────────────
    def _crear_header(self):
        header = ctk.CTkFrame(
            self.panel_derecho,
            fg_color=COLORES["bg_card"],
            corner_radius=0,
            height=60,
            border_width=0
        )
        header.grid(row=0, column=0, sticky="ew")
        header.grid_propagate(False)
        header.grid_columnconfigure(1, weight=1)

        # Título de la sección activa
        self.lbl_seccion = ctk.CTkLabel(
            header,
            text="📋  Préstamos",
            font=ctk.CTkFont(family="Segoe UI", size=18, weight="bold"),
            text_color=COLORES["texto"]
        )
        self.lbl_seccion.grid(row=0, column=0, padx=25, pady=15, sticky="w")

        # Reloj en vivo
        self.lbl_reloj = ctk.CTkLabel(
            header,
            text="",
            font=ctk.CTkFont(family="Consolas", size=13),
            text_color=COLORES["texto_dim"]
        )
        self.lbl_reloj.grid(row=0, column=2, padx=25, pady=15, sticky="e")
        self._actualizar_reloj()

        # Separador decorativo
        sep = ctk.CTkFrame(
            self.panel_derecho,
            fg_color=COLORES["acento"],
            height=2,
            corner_radius=0
        )
        sep.grid(row=0, column=0, sticky="sew")

    # ──────────────────────────────────────────────────────────────────────
    def _actualizar_reloj(self):
        ahora = datetime.now().strftime("%A %d/%m/%Y  %H:%M:%S")
        self.lbl_reloj.configure(text=ahora)
        self.after(1000, self._actualizar_reloj)

    # ──────────────────────────────────────────────────────────────────────
    def cambiar_vista(self, nombre):
        if self.vista_actual:
            try:
                self.vista_actual.destroy()
            except Exception:
                pass
        self.vista_actual = None

        titulos = {
            "prestamos":  "📋  Préstamos",
            "libros":     "📖  Catálogo de Libros",
            "usuarios":   "👤  Usuarios",
            "reservas":   "📌  Reservas",
            "donaciones": "🎁  Donaciones",
            "ranking":    "🏆  Ranking de Lectura",
        }
        self.lbl_seccion.configure(text=titulos.get(nombre, ""))

        if nombre == "prestamos":
            from VistaTk.prestamos import VistaPrestamos
            self.vista_actual = VistaPrestamos(self.container, COLORES)

        elif nombre == "libros":
            from VistaTk.libros import VistaLibros
            self.vista_actual = VistaLibros(self.container, COLORES)

        elif nombre == "usuarios":
            from VistaTk.usuarios import VistaUsuarios
            self.vista_actual = VistaUsuarios(self.container, COLORES)

        elif nombre == "reservas":
            from VistaTk.reservas import VistaReservas
            self.vista_actual = VistaReservas(self.container, COLORES)

        elif nombre == "donaciones":
            from VistaTk.donaciones import VistaDonaciones
            self.vista_actual = VistaDonaciones(self.container, COLORES)

        elif nombre == "ranking":
            from VistaTk.ranking import VistaRanking
            self.vista_actual = VistaRanking(self.container, COLORES)

        if self.vista_actual:
            self.vista_actual.pack(expand=True, fill="both")

    # ──────────────────────────────────────────────────────────────────────
    def abrir_catalogo_independiente(self):
        from VistaTk.libros import VistaLibros
        ventana = ctk.CTkToplevel(self)
        ventana.title("📖 Catálogo de Libros")
        ventana.geometry("950x580")
        ventana.configure(fg_color=COLORES["bg_principal"])
        vista = VistaLibros(ventana, COLORES)
        vista.pack(expand=True, fill="both")


# ── INICIO ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    crear_conexion()
    app = App()
    app.mainloop()
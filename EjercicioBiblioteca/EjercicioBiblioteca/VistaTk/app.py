import customtkinter as ctk
from VistaTk.sidebar import Sidebar
from VistaTk.prestamos import VistaPrestamos
from Modelo.conexion import crear_conexion


class App(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.title("Sistema de Biblioteca")
        self.geometry("1100x650")

        # ── SIDEBAR ────────────────────────────────────────────────────────
        self.sidebar = Sidebar(self, self.cambiar_vista)
        self.sidebar.pack(side="left", fill="y")

        # ── CONTENEDOR PRINCIPAL ───────────────────────────────────────────
        self.container = ctk.CTkFrame(self)
        self.container.pack(expand=True, fill="both")

        self.vista_actual = None
        self.cambiar_vista("prestamos")

    # ──────────────────────────────────────────────────────────────────────
    def cambiar_vista(self, nombre):
        if self.vista_actual:
            try:
                self.vista_actual.destroy()
            except Exception:
                pass
        self.vista_actual = None

        if nombre == "prestamos":
            from VistaTk.prestamos import VistaPrestamos
            self.vista_actual = VistaPrestamos(self.container)

        elif nombre == "libros":
            from VistaTk.libros import VistaLibros
            self.vista_actual = VistaLibros(self.container)

        elif nombre == "usuarios":
            from VistaTk.usuarios import VistaUsuarios
            self.vista_actual = VistaUsuarios(self.container)

        elif nombre == "reservas":
            from VistaTk.reservas import VistaReservas
            self.vista_actual = VistaReservas(self.container)

        elif nombre == "donaciones":
            from VistaTk.donaciones import VistaDonaciones
            self.vista_actual = VistaDonaciones(self.container)

        elif nombre == "ranking":
            from VistaTk.ranking import VistaRanking
            self.vista_actual = VistaRanking(self.container)

        if self.vista_actual:
            self.vista_actual.pack(expand=True, fill="both")

    # ──────────────────────────────────────────────────────────────────────
    def abrir_catalogo_independiente(self):
        """
        Abre el catálogo de libros en una ventana independiente (multi-ventana).
        Puede llamarse desde un botón o menú.
        """
        from VistaTk.libros import VistaLibros
        ventana = ctk.CTkToplevel(self)
        ventana.title("Catálogo de Libros")
        ventana.geometry("900x550")
        vista = VistaLibros(ventana)
        vista.pack(expand=True, fill="both")


# ── INICIO ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    crear_conexion()
    app = App()
    app.mainloop()
import customtkinter as ctk
from tkinter import ttk, messagebox
from Controlador.controlador import ControladorBiblioteca

GENEROS = ["Ingeniería", "Medicina", "Ciencias", "Literatura",
           "Historia", "Matemáticas", "Arte", "Tecnología", "Otro"]


def _estilo_treeview(colores):
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("Biblioteca.Treeview",
                    background=colores["bg_card"],
                    foreground=colores["texto"],
                    rowheight=36,
                    fieldbackground=colores["bg_card"],
                    borderwidth=0,
                    font=("Segoe UI", 11))
    style.configure("Biblioteca.Treeview.Heading",
                    background=colores["bg_hover"],
                    foreground=colores["acento_claro"],
                    font=("Segoe UI", 11, "bold"),
                    relief="flat")
    style.map("Biblioteca.Treeview",
              background=[("selected", colores["acento"])],
              foreground=[("selected", "white")])


class VistaDonaciones(ctk.CTkFrame):

    def __init__(self, master, colores):
        super().__init__(master, fg_color="transparent")
        self.C = colores
        self.controlador = ControladorBiblioteca()
        _estilo_treeview(colores)
        self._construir()
        self.cargar_datos()

    def _construir(self):
        C = self.C

        ctk.CTkButton(
            self, text="➕  Registrar Donación",
            fg_color=C["acento"], hover_color=C["acento"],
            font=ctk.CTkFont(size=12), height=36, corner_radius=8,
            command=self.abrir_formulario
        ).pack(anchor="w", padx=8, pady=(10, 8))

        frame_tabla = ctk.CTkFrame(self, fg_color=C["bg_card"], corner_radius=12)
        frame_tabla.pack(expand=True, fill="both")

        cols = ("ID", "Título", "Autor", "Donante", "Fecha")
        self.tree = ttk.Treeview(frame_tabla, columns=cols, show="headings",
                                  style="Biblioteca.Treeview", selectmode="browse")
        anchos = {"ID": 45, "Título": 230, "Autor": 160, "Donante": 160, "Fecha": 110}
        for col in cols:
            self.tree.heading(col, text=col.upper())
            self.tree.column(col, width=anchos.get(col, 130), anchor="center")

        scroll = ttk.Scrollbar(frame_tabla, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll.set)
        self.tree.pack(side="left", expand=True, fill="both", padx=(8, 0), pady=8)
        scroll.pack(side="right", fill="y", pady=8, padx=(0, 8))

    def cargar_datos(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for d in self.controlador.obtener_donaciones():
            self.tree.insert("", "end", values=d)

    def abrir_formulario(self):
        C = self.C
        ventana = ctk.CTkToplevel(self)
        ventana.title("Registrar Donación")
        ventana.geometry("420x400")
        ventana.configure(fg_color=C["bg_principal"])
        ventana.grab_set()

        ctk.CTkLabel(ventana, text="Nueva Donación",
                     font=ctk.CTkFont(size=18, weight="bold"),
                     text_color=C["acento_claro"]).pack(pady=(20, 16))

        campos = [("Título *", "titulo"), ("Autor *", "autor"),
                  ("ISBN", "isbn"), ("Donante *", "donante")]
        entries = {}

        for label, key in campos:
            ctk.CTkLabel(ventana, text=label, text_color=C["texto_dim"],
                         font=ctk.CTkFont(size=11)).pack(anchor="w", padx=30)
            e = ctk.CTkEntry(ventana, width=360,
                             fg_color=C["bg_hover"], border_color=C["borde"])
            e.pack(padx=30, pady=(2, 10))
            entries[key] = e

        ctk.CTkLabel(ventana, text="Género", text_color=C["texto_dim"],
                     font=ctk.CTkFont(size=11)).pack(anchor="w", padx=30)
        combo_g = ctk.CTkComboBox(ventana, values=GENEROS, width=360,
                                   fg_color=C["bg_hover"], border_color=C["borde"],
                                   button_color=C["acento"],
                                   dropdown_fg_color=C["bg_card"])
        combo_g.set(GENEROS[0])
        combo_g.pack(padx=30, pady=(2, 16))

        def guardar():
            titulo  = entries["titulo"].get().strip()
            autor   = entries["autor"].get().strip()
            isbn    = entries["isbn"].get().strip()
            donante = entries["donante"].get().strip()
            genero  = combo_g.get()

            if not titulo or not autor or not donante:
                messagebox.showwarning("Atención",
                                       "Título, autor y donante son obligatorios.",
                                       parent=ventana)
                return
            if self.controlador.registrar_donacion(titulo, autor, isbn, genero, donante):
                messagebox.showinfo("✅ Éxito",
                                    "Donación registrada. Libro añadido al catálogo.",
                                    parent=ventana)
                ventana.destroy()
                self.cargar_datos()
            else:
                messagebox.showerror("Error", "No se pudo registrar.", parent=ventana)

        ctk.CTkButton(ventana, text="💾  Guardar Donación",
                      fg_color=C["acento"], hover_color=C["acento"],
                      font=ctk.CTkFont(size=13), height=40, corner_radius=8,
                      command=guardar).pack(padx=30, fill="x")
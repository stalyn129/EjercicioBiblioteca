import customtkinter as ctk
from tkinter import ttk
from Controlador.controlador import ControladorBiblioteca


def _estilo_treeview(colores):
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("Biblioteca.Treeview",
                    background=colores["bg_card"],
                    foreground=colores["texto"],
                    rowheight=38,
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


class VistaRanking(ctk.CTkFrame):

    def __init__(self, master, colores):
        super().__init__(master, fg_color="transparent")
        self.C = colores
        self.controlador = ControladorBiblioteca()
        _estilo_treeview(colores)
        self._construir()
        self.cargar_datos()

    # ──────────────────────────────────────────────────────────────────────
    def _construir(self):
        C = self.C

        # ── PODIO (TOP 3) ──────────────────────────────────────────────────
        self.frame_podio = ctk.CTkFrame(self, fg_color=C["bg_card"], corner_radius=12)
        self.frame_podio.pack(fill="x", pady=(10, 8))

        ctk.CTkLabel(
            self.frame_podio,
            text="🏆  Top 3 Libros Más Leídos",
            font=ctk.CTkFont(family="Segoe UI", size=15, weight="bold"),
            text_color=C["acento_claro"]
        ).pack(pady=(14, 10))

        self.frame_medallas = ctk.CTkFrame(self.frame_podio, fg_color="transparent")
        self.frame_medallas.pack(fill="x", padx=20, pady=(0, 14))

        # ── BOTÓN ACTUALIZAR ───────────────────────────────────────────────
        ctk.CTkButton(
            self, text="🔄  Actualizar Ranking",
            fg_color=C["acento"], hover_color=C["acento"],
            font=ctk.CTkFont(size=12), height=34, corner_radius=8,
            command=self.cargar_datos
        ).pack(anchor="e", padx=8, pady=(0, 6))

        # ── TABLA COMPLETA ─────────────────────────────────────────────────
        frame_tabla = ctk.CTkFrame(self, fg_color=C["bg_card"], corner_radius=12)
        frame_tabla.pack(expand=True, fill="both")

        cols = ("#", "Título", "Autor", "Veces Prestado")
        self.tree = ttk.Treeview(frame_tabla, columns=cols, show="headings",
                                  style="Biblioteca.Treeview", selectmode="none")

        anchos = {"#": 50, "Título": 280, "Autor": 190, "Veces Prestado": 130}
        for col in cols:
            self.tree.heading(col, text=col.upper())
            self.tree.column(col, width=anchos.get(col, 140), anchor="center")

        # Tags de medallas
        self.tree.tag_configure("oro",    background="#2d2208", foreground="#fbbf24")
        self.tree.tag_configure("plata",  background="#1e2030", foreground="#cbd5e1")
        self.tree.tag_configure("bronce", background="#1f1608", foreground="#d97706")
        self.tree.tag_configure("normal", background=self.C["bg_card"], foreground=self.C["texto"])

        scroll = ttk.Scrollbar(frame_tabla, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll.set)
        self.tree.pack(side="left", expand=True, fill="both", padx=(8, 0), pady=8)
        scroll.pack(side="right", fill="y", pady=8, padx=(0, 8))

    # ──────────────────────────────────────────────────────────────────────
    def cargar_datos(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        # Limpiar podio anterior
        for w in self.frame_medallas.winfo_children():
            w.destroy()

        datos = self.controlador.ranking_libros()
        medallas = ["🥇", "🥈", "🥉"]
        colores_med = ["#fbbf24", "#cbd5e1", "#d97706"]

        # Podio visual (top 3)
        for i, d in enumerate(datos[:3]):
            card = ctk.CTkFrame(self.frame_medallas,
                                fg_color=self.C["bg_hover"],
                                corner_radius=10)
            card.pack(side="left", expand=True, fill="x", padx=8)

            ctk.CTkLabel(card, text=medallas[i],
                         font=ctk.CTkFont(size=28)).pack(pady=(10, 2))
            ctk.CTkLabel(card, text=d[0],
                         font=ctk.CTkFont(size=12, weight="bold"),
                         text_color=colores_med[i],
                         wraplength=180).pack(padx=10)
            ctk.CTkLabel(card, text=d[1],
                         font=ctk.CTkFont(size=10),
                         text_color=self.C["texto_dim"]).pack()
            ctk.CTkLabel(card,
                         text=f"{d[2]} préstamo(s)",
                         font=ctk.CTkFont(size=11),
                         text_color=self.C["acento2"]).pack(pady=(2, 12))

        # Tabla completa
        tags_map = ["oro", "plata", "bronce"]
        for i, d in enumerate(datos):
            tag = tags_map[i] if i < 3 else "normal"
            prefijo = medallas[i] + " " if i < 3 else ""
            self.tree.insert("", "end", values=(
                f"{prefijo}{i+1}",
                d[0], d[1], d[2]
            ), tags=(tag,))
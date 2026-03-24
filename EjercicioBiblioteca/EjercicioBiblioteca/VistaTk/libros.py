import customtkinter as ctk
from tkinter import ttk, messagebox, filedialog
from Controlador.controlador import ControladorBiblioteca
from utils.csv_import import importar_csv

GENEROS = ["Ingeniería", "Medicina", "Ciencias", "Literatura",
           "Historia", "Matemáticas", "Arte", "Tecnología", "Otro"]


def _estilo_tv(C):
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("Biblioteca.Treeview",
                    background=C["bg_card"], foreground=C["texto"],
                    rowheight=36, fieldbackground=C["bg_card"],
                    borderwidth=0, font=("Segoe UI", 11))
    style.configure("Biblioteca.Treeview.Heading",
                    background=C["bg_hover"], foreground=C["acento_claro"],
                    font=("Segoe UI", 11, "bold"), relief="flat")
    style.map("Biblioteca.Treeview",
              background=[("selected", C["acento"])],
              foreground=[("selected", "white")])


class VistaLibros(ctk.CTkFrame):

    def __init__(self, master, colores):
        super().__init__(master, fg_color="transparent")
        self.C = colores
        self.ctrl = ControladorBiblioteca()
        self._cache = []
        _estilo_tv(colores)
        self._ui()
        self.cargar_datos()

    def _ui(self):
        C = self.C

        # Barra superior
        bar = ctk.CTkFrame(self, fg_color=C["bg_card"], corner_radius=12)
        bar.pack(fill="x", pady=(10, 8))

        ctk.CTkLabel(bar, text="🔍", font=ctk.CTkFont(size=16)).pack(side="left", padx=(14,2), pady=10)
        self.entry_bus = ctk.CTkEntry(bar, width=230,
                                       placeholder_text="Buscar título, autor o ISBN...",
                                       fg_color=C["bg_hover"], border_color=C["borde"])
        self.entry_bus.pack(side="left", padx=4, pady=10)
        self.entry_bus.bind("<KeyRelease>", self._buscar)

        ctk.CTkLabel(bar, text="Género:", text_color=C["texto_dim"],
                     font=ctk.CTkFont(size=11)).pack(side="left", padx=(12,4))
        self.cbo_gen = ctk.CTkComboBox(bar, values=["Todos"]+GENEROS, width=145,
                                        fg_color=C["bg_hover"], border_color=C["borde"],
                                        button_color=C["acento"],
                                        dropdown_fg_color=C["bg_card"],
                                        command=lambda _: self._buscar())
        self.cbo_gen.set("Todos")
        self.cbo_gen.pack(side="left", padx=4)

        right = ctk.CTkFrame(bar, fg_color="transparent")
        right.pack(side="right", padx=10)

        acciones = [
            ("➕ Agregar",  C["acento"],  self.agregar),
            ("✏️ Editar",   C["acento2"], self.editar),
            ("🗑️ Eliminar", C["error"],   self.eliminar),
            ("📂 CSV",      C["bg_hover"],self.importar_csv),
            ("🔄",          C["bg_hover"],self.cargar_datos),
        ]
        for txt, col, cmd in acciones:
            ctk.CTkButton(right, text=txt, fg_color=col, hover_color=col,
                          font=ctk.CTkFont(size=12), height=34, corner_radius=8,
                          command=cmd).pack(side="left", padx=3, pady=10)

        self.lbl_cnt = ctk.CTkLabel(self, text="", font=ctk.CTkFont(size=11),
                                     text_color=C["texto_dim"])
        self.lbl_cnt.pack(anchor="e", padx=8)

        # Tabla
        ft = ctk.CTkFrame(self, fg_color=C["bg_card"], corner_radius=12)
        ft.pack(expand=True, fill="both")

        cols = ("ID","Título","Autor","ISBN","Género","Disponible")
        self.tree = ttk.Treeview(ft, columns=cols, show="headings",
                                  style="Biblioteca.Treeview", selectmode="browse")
        w = {"ID":45,"Título":230,"Autor":160,"ISBN":120,"Género":110,"Disponible":90}
        for c in cols:
            self.tree.heading(c, text=c.upper())
            self.tree.column(c, width=w.get(c,120), anchor="center")

        self.tree.tag_configure("si", background="#0f2820", foreground="#6ee7b7")
        self.tree.tag_configure("no", background="#1a1a2e", foreground="#94a3b8")

        sb = ttk.Scrollbar(ft, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set)
        self.tree.pack(side="left", expand=True, fill="both", padx=(8,0), pady=8)
        sb.pack(side="right", fill="y", pady=8, padx=(0,8))

    # ── datos ──────────────────────────────────────────────────────────────
    def cargar_datos(self):
        self._cache = self.ctrl.obtener_todos_libros()
        self._llenar(self._cache)

    def _llenar(self, datos):
        for r in self.tree.get_children():
            self.tree.delete(r)
        for d in datos:
            tag = "si" if d[5] else "no"
            self.tree.insert("", "end", values=(
                d[0], d[1], d[2], d[3] or "—", d[4] or "—",
                "✅ Sí" if d[5] else "❌ No"
            ), tags=(tag,))
        self.lbl_cnt.configure(text=f"{len(datos)} libro(s)")

    def _buscar(self, event=None):
        txt = self.entry_bus.get().lower().strip()
        gen = self.cbo_gen.get()
        res = self._cache
        if txt:
            res = [l for l in res if txt in str(l[1]).lower()
                   or txt in str(l[2]).lower()
                   or txt in str(l[3]).lower()]
        if gen != "Todos":
            res = [l for l in res if l[4] == gen]
        self._llenar(res)

    def _sel(self):
        s = self.tree.selection()
        if not s:
            messagebox.showwarning("Atención", "Seleccione un libro.")
            return None
        return self.tree.item(s[0])["values"]

    # ── formulario reutilizable ────────────────────────────────────────────
    def _formulario(self, titulo_ventana, datos=None, libro_id=None):
        C = self.C
        v = ctk.CTkToplevel(self)
        v.title(titulo_ventana)
        v.geometry("420x370")
        v.configure(fg_color=C["bg_principal"])
        v.grab_set()

        ctk.CTkLabel(v, text=titulo_ventana,
                     font=ctk.CTkFont(size=17, weight="bold"),
                     text_color=C["acento_claro"]).pack(pady=(18,14))

        entries = {}
        for lbl, key, idx in [("Título *","titulo",1),
                               ("Autor *", "autor", 2),
                               ("ISBN",    "isbn",  3)]:
            ctk.CTkLabel(v, text=lbl, text_color=C["texto_dim"],
                         font=ctk.CTkFont(size=11)).pack(anchor="w", padx=30)
            e = ctk.CTkEntry(v, width=360, fg_color=C["bg_hover"],
                             border_color=C["borde"])
            if datos:
                val = str(datos[idx]) if datos[idx] and datos[idx] != "—" else ""
                e.insert(0, val)
            e.pack(padx=30, pady=(2,8))
            entries[key] = e

        ctk.CTkLabel(v, text="Género", text_color=C["texto_dim"],
                     font=ctk.CTkFont(size=11)).pack(anchor="w", padx=30)
        cbo = ctk.CTkComboBox(v, values=GENEROS, width=360,
                               fg_color=C["bg_hover"], border_color=C["borde"],
                               button_color=C["acento"],
                               dropdown_fg_color=C["bg_card"])
        gen_val = datos[4] if datos and datos[4] in GENEROS else GENEROS[0]
        cbo.set(gen_val)
        cbo.pack(padx=30, pady=(2,14))

        def guardar():
            t = entries["titulo"].get().strip()
            a = entries["autor"].get().strip()
            i = entries["isbn"].get().strip()
            g = cbo.get()
            if not t or not a:
                messagebox.showwarning("Atención",
                                       "Título y autor son obligatorios.", parent=v)
                return
            if libro_id:
                ok, msg = self.ctrl.editar_libro(libro_id, t, a, i, g)
            else:
                ok, msg = self.ctrl.registrar_libro(t, a, i, g)
            if ok:
                messagebox.showinfo("✅ Éxito", msg, parent=v)
                v.destroy()
                self.cargar_datos()
            else:
                messagebox.showerror("❌ Error", msg, parent=v)

        ctk.CTkButton(v, text="💾 Guardar",
                      fg_color=C["acento"], hover_color=C["acento"],
                      font=ctk.CTkFont(size=13), height=40, corner_radius=8,
                      command=guardar).pack(padx=30, fill="x")

    # ── acciones CRUD ──────────────────────────────────────────────────────
    def agregar(self):
        self._formulario("➕  Nuevo Libro")

    def editar(self):
        v = self._sel()
        if v:
            self._formulario("✏️  Editar Libro", datos=v, libro_id=v[0])

    def eliminar(self):
        v = self._sel()
        if not v:
            return
        if not messagebox.askyesno(
            "⚠️ Confirmar",
            f"¿Eliminar «{v[1]}»?\n\n"
            "No se puede deshacer.\n"
            "Fallará si tiene préstamos activos."
        ):
            return
        ok, msg = self.ctrl.eliminar_libro(v[0])
        (messagebox.showinfo if ok else messagebox.showerror)(
            "✅ Éxito" if ok else "❌ Error", msg
        )
        if ok:
            self.cargar_datos()

    def importar_csv(self):
        try:
            ruta = filedialog.askopenfilename(filetypes=[("CSV","*.csv")])
            if ruta:
                importar_csv(ruta)
                messagebox.showinfo("✅ Éxito", "Libros importados desde CSV.")
                self.cargar_datos()
        except Exception as e:
            messagebox.showerror("Error", str(e))
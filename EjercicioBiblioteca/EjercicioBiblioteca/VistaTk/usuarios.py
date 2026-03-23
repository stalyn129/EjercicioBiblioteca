import customtkinter as ctk
from tkinter import ttk, messagebox
from Controlador.controlador import ControladorBiblioteca
from utils.qr import generar_qr


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


class VistaUsuarios(ctk.CTkFrame):

    def __init__(self, master, colores):
        super().__init__(master, fg_color="transparent")
        self.C = colores
        self.ctrl = ControladorBiblioteca()
        _estilo_tv(colores)
        self._ui()
        self.cargar_datos()

    def _ui(self):
        C = self.C

        bar = ctk.CTkFrame(self, fg_color=C["bg_card"], corner_radius=12)
        bar.pack(fill="x", pady=(10, 8))

        acciones = [
            ("➕ Registrar",  C["acento"],  self.agregar),
            ("✏️ Editar",     C["acento2"], self.editar),
            ("🗑️ Eliminar",   C["error"],   self.eliminar),
            ("📱 Generar QR", C["bg_hover"],self.generar_qr),
        ]
        for txt, col, cmd in acciones:
            ctk.CTkButton(bar, text=txt, fg_color=col, hover_color=col,
                          font=ctk.CTkFont(size=12), height=36, corner_radius=8,
                          command=cmd).pack(side="left", padx=6, pady=10)

        self.lbl_total = ctk.CTkLabel(bar, text="",
                                       font=ctk.CTkFont(size=11),
                                       text_color=C["texto_dim"])
        self.lbl_total.pack(side="right", padx=16)

        ft = ctk.CTkFrame(self, fg_color=C["bg_card"], corner_radius=12)
        ft.pack(expand=True, fill="both", pady=(0,10))

        cols = ("ID","Nombre","Carrera")
        self.tree = ttk.Treeview(ft, columns=cols, show="headings",
                                  style="Biblioteca.Treeview", selectmode="browse")
        for c, w in [("ID",50),("Nombre",260),("Carrera",260)]:
            self.tree.heading(c, text=c.upper())
            self.tree.column(c, width=w, anchor="center")

        sb = ttk.Scrollbar(ft, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set)
        self.tree.pack(side="left", expand=True, fill="both", padx=(8,0), pady=8)
        sb.pack(side="right", fill="y", pady=8, padx=(0,8))

    # ── datos ──────────────────────────────────────────────────────────────
    def cargar_datos(self):
        for r in self.tree.get_children():
            self.tree.delete(r)
        datos = self.ctrl.obtener_usuarios()
        for d in datos:
            self.tree.insert("", "end", values=d)
        self.lbl_total.configure(text=f"{len(datos)} usuario(s)")

    def _sel(self):
        s = self.tree.selection()
        if not s:
            messagebox.showwarning("Atención", "Seleccione un usuario.")
            return None
        return self.tree.item(s[0])["values"]

    # ── formulario reutilizable ────────────────────────────────────────────
    def _formulario(self, titulo_v, datos=None, usuario_id=None):
        C = self.C
        v = ctk.CTkToplevel(self)
        v.title(titulo_v)
        v.geometry("400x280")
        v.configure(fg_color=C["bg_principal"])
        v.grab_set()

        ctk.CTkLabel(v, text=titulo_v,
                     font=ctk.CTkFont(size=17, weight="bold"),
                     text_color=C["acento_claro"]).pack(pady=(18,14))

        entries = {}
        for lbl, key, idx in [("Nombre *","nombre",1), ("Carrera *","carrera",2)]:
            ctk.CTkLabel(v, text=lbl, text_color=C["texto_dim"],
                         font=ctk.CTkFont(size=11)).pack(anchor="w", padx=30)
            e = ctk.CTkEntry(v, width=340, fg_color=C["bg_hover"],
                             border_color=C["borde"])
            if datos:
                e.insert(0, str(datos[idx]))
            e.pack(padx=30, pady=(2,12))
            entries[key] = e

        def guardar():
            nombre  = entries["nombre"].get().strip()
            carrera = entries["carrera"].get().strip()
            if not nombre or not carrera:
                messagebox.showwarning("Atención",
                                       "Todos los campos son obligatorios.", parent=v)
                return
            if usuario_id:
                ok, msg = self.ctrl.editar_usuario(usuario_id, nombre, carrera)
            else:
                ok, msg = self.ctrl.registrar_usuario(nombre, carrera)
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
        self._formulario("➕  Nuevo Usuario")

    def editar(self):
        v = self._sel()
        if v:
            self._formulario("✏️  Editar Usuario", datos=v, usuario_id=v[0])

    def eliminar(self):
        v = self._sel()
        if not v:
            return
        if not messagebox.askyesno(
            "⚠️ Confirmar",
            f"¿Eliminar al usuario «{v[1]}»?\n\n"
            "Fallará si tiene préstamos activos."
        ):
            return
        ok, msg = self.ctrl.eliminar_usuario(v[0])
        (messagebox.showinfo if ok else messagebox.showerror)(
            "✅ Éxito" if ok else "❌ Error", msg
        )
        if ok:
            self.cargar_datos()

    def generar_qr(self):
        try:
            v = self._sel()
            if not v:
                return
            generar_qr(v[0])
            messagebox.showinfo("📱 QR Generado",
                                f"Carnet generado para:\n\n  👤  {v[1]}\n"
                                f"  Archivo: qr_usuario_{v[0]}.png")
        except Exception as e:
            messagebox.showerror("Error", str(e))
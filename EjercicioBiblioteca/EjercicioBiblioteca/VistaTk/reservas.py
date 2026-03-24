import customtkinter as ctk
from tkinter import ttk, messagebox
from Controlador.controlador import ControladorBiblioteca


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


class VistaReservas(ctk.CTkFrame):

    def __init__(self, master, colores):
        super().__init__(master, fg_color="transparent")
        self.C = colores
        self.ctrl = ControladorBiblioteca()
        _estilo_tv(colores)
        self._ui()
        self.cargar_combos()
        self.cargar_datos()

    def _ui(self):
        C = self.C

        form = ctk.CTkFrame(self, fg_color=C["bg_card"], corner_radius=12)
        form.pack(fill="x", pady=(10,8))

        ctk.CTkLabel(form, text="Nueva Reserva",
                     font=ctk.CTkFont(size=13, weight="bold"),
                     text_color=C["texto_dim"]).grid(
            row=0, column=0, columnspan=4, padx=16, pady=(12,4), sticky="w")

        ctk.CTkLabel(form, text="Usuario:", text_color=C["texto_dim"],
                     font=ctk.CTkFont(size=11)).grid(row=1, column=0, padx=(16,4), pady=10, sticky="w")
        self.cbo_usr = ctk.CTkComboBox(form, values=[], width=220,
                                        fg_color=C["bg_hover"], border_color=C["borde"],
                                        button_color=C["acento"],
                                        dropdown_fg_color=C["bg_card"])
        self.cbo_usr.grid(row=1, column=1, padx=4, pady=10)

        ctk.CTkLabel(form, text="Libro no disponible:", text_color=C["texto_dim"],
                     font=ctk.CTkFont(size=11)).grid(row=1, column=2, padx=(12,4), pady=10, sticky="w")
        self.cbo_lib = ctk.CTkComboBox(form, values=[], width=220,
                                        fg_color=C["bg_hover"], border_color=C["borde"],
                                        button_color=C["acento"],
                                        dropdown_fg_color=C["bg_card"])
        self.cbo_lib.grid(row=1, column=3, padx=(4,16), pady=10)

        bframe = ctk.CTkFrame(form, fg_color="transparent")
        bframe.grid(row=2, column=0, columnspan=4, padx=12, pady=(0,12), sticky="w")

        for txt, col, cmd in [
            ("📌 Hacer Reserva",    C["acento"], self.hacer_reserva),
            ("❌ Cancelar Reserva", C["error"],  self.cancelar_reserva),
            ("🔄 Actualizar",       C["bg_hover"],self.cargar_datos),
        ]:
            ctk.CTkButton(bframe, text=txt, fg_color=col, hover_color=col,
                          font=ctk.CTkFont(size=12), height=34, corner_radius=8,
                          command=cmd).pack(side="left", padx=4)

        ft = ctk.CTkFrame(self, fg_color=C["bg_card"], corner_radius=12)
        ft.pack(expand=True, fill="both")

        cols = ("ID","Usuario","Libro","Fecha","Estado")
        self.tree = ttk.Treeview(ft, columns=cols, show="headings",
                                  style="Biblioteca.Treeview", selectmode="browse")
        for c, w in [("ID",45),("Usuario",180),("Libro",220),("Fecha",110),("Estado",110)]:
            self.tree.heading(c, text=c.upper())
            self.tree.column(c, width=w, anchor="center")

        self.tree.tag_configure("pendiente", background="#1a1a30", foreground="#a78bfa")
        self.tree.tag_configure("atendida",  background="#0f2820", foreground="#6ee7b7")

        sb = ttk.Scrollbar(ft, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set)
        self.tree.pack(side="left", expand=True, fill="both", padx=(8,0), pady=8)
        sb.pack(side="right", fill="y", pady=8, padx=(0,8))

    def cargar_combos(self):
        usuarios = self.ctrl.obtener_usuarios()
        self._umap = {f"{u[0]} · {u[1]}": u[0] for u in usuarios}
        self.cbo_usr.configure(values=list(self._umap.keys()))

        todos = self.ctrl.obtener_todos_libros()
        no_disp = [(l[0], l[1]) for l in todos if l[5] == 0]
        self._lmap = {f"{l[0]} · {l[1]}": l[0] for l in no_disp}
        self.cbo_lib.configure(values=list(self._lmap.keys()))

    def cargar_datos(self):
        for r in self.tree.get_children():
            self.tree.delete(r)
        for row in self.ctrl.obtener_reservas():
            tag = "atendida" if row[4] != "Pendiente" else "pendiente"
            self.tree.insert("", "end", values=row, tags=(tag,))

    def _sel(self):
        s = self.tree.selection()
        if not s:
            messagebox.showwarning("Atención", "Seleccione una reserva.")
            return None
        return self.tree.item(s[0])["values"]

    def hacer_reserva(self):
        try:
            uk = self.cbo_usr.get(); lk = self.cbo_lib.get()
            if not uk or not lk:
                messagebox.showwarning("Atención", "Seleccione usuario y libro.")
                return
            ok, msg = self.ctrl.reservar_libro(
                self._umap.get(uk), self._lmap.get(lk)
            )
            (messagebox.showinfo if ok else messagebox.showerror)(
                "✅ Éxito" if ok else "❌ Error", msg)
            if ok:
                self.cargar_datos()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def cancelar_reserva(self):
        """ACID: elimina la reserva completamente en una sola operación."""
        try:
            v = self._sel()
            if not v: return
            if not messagebox.askyesno(
                "⚠️ Confirmar",
                f"¿Cancelar la reserva de «{v[2]}» para {v[1]}?"
            ):
                return
            ok, msg = self.ctrl.cancelar_reserva(v[0])
            (messagebox.showinfo if ok else messagebox.showerror)(
                "✅ Cancelada" if ok else "❌ Error", msg)
            if ok:
                self.cargar_datos()
        except Exception as e:
            messagebox.showerror("Error", str(e))
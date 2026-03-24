import customtkinter as ctk
from tkinter import ttk, messagebox
from datetime import datetime
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


class VistaPrestamos(ctk.CTkFrame):

    def __init__(self, master, colores):
        super().__init__(master, fg_color="transparent")
        self.C = colores
        self.ctrl = ControladorBiblioteca()
        _estilo_tv(colores)
        self._ui()
        self.cargar_combos()
        self.cargar_datos()

    # ──────────────────────────────────────────────────────────────────────
    def _ui(self):
        C = self.C

        # Stats
        frame_stats = ctk.CTkFrame(self, fg_color="transparent")
        frame_stats.pack(fill="x", pady=(10,0))
        self.s_total   = self._card(frame_stats, "Total",       "0",     C["acento"])
        self.s_activos = self._card(frame_stats, "Activos",     "0",     C["acento2"])
        self.s_multa   = self._card(frame_stats, "Con Multa",   "0",     C["alerta"])
        self.s_monto   = self._card(frame_stats, "Multa Total", "$0.00", C["error"])

        # Formulario
        form = ctk.CTkFrame(self, fg_color=C["bg_card"], corner_radius=12)
        form.pack(fill="x", pady=10)

        ctk.CTkLabel(form, text="Registrar nuevo préstamo",
                     font=ctk.CTkFont(size=13, weight="bold"),
                     text_color=C["texto_dim"]).grid(
            row=0, column=0, columnspan=6, padx=16, pady=(12,4), sticky="w")

        for col_idx, (lbl, attr, width) in enumerate([
            ("Usuario",          "cbo_usr",   200),
            ("Libro disponible", "cbo_lib",   200),
            ("Fecha DD/MM/AAAA", "ent_fecha", 120),
        ]):
            ctk.CTkLabel(form, text=lbl, text_color=C["texto_dim"],
                         font=ctk.CTkFont(size=11)).grid(
                row=1, column=col_idx*2, padx=(16 if col_idx==0 else 10, 4),
                pady=10, sticky="w")

            if "fecha" in attr:
                w = ctk.CTkEntry(form, width=width, fg_color=C["bg_hover"],
                                 border_color=C["borde"],
                                 placeholder_text="DD/MM/AAAA")
                w.insert(0, datetime.now().strftime("%d/%m/%Y"))
            else:
                w = ctk.CTkComboBox(form, values=[], width=width,
                                    fg_color=C["bg_hover"], border_color=C["borde"],
                                    button_color=C["acento"],
                                    dropdown_fg_color=C["bg_card"])
            w.grid(row=1, column=col_idx*2+1, padx=4, pady=10)
            setattr(self, attr, w)

        # Botones de acción
        bframe = ctk.CTkFrame(form, fg_color="transparent")
        bframe.grid(row=2, column=0, columnspan=6, padx=12, pady=(0,12), sticky="w")

        for txt, col, cmd in [
            ("➕ Registrar Préstamo", C["acento"],  self.registrar),
            ("✅ Devolver",           C["exito"],   self.devolver),
            ("❌ Cancelar Préstamo",  C["error"],   self.cancelar),
            ("🔔 Alertas",            C["alerta"],  self.ver_alertas),
            ("🔄 Actualizar",         C["bg_hover"],self.cargar_datos),
        ]:
            ctk.CTkButton(bframe, text=txt, fg_color=col, hover_color=col,
                          font=ctk.CTkFont(size=12), height=34, corner_radius=8,
                          command=cmd).pack(side="left", padx=4)

        # Tabla
        ft = ctk.CTkFrame(self, fg_color=C["bg_card"], corner_radius=12)
        ft.pack(expand=True, fill="both")

        cols = ("ID","Usuario","Libro","Fecha","Estado","Días","Multa")
        self.tree = ttk.Treeview(ft, columns=cols, show="headings",
                                  style="Biblioteca.Treeview", selectmode="browse")
        w = {"ID":40,"Usuario":160,"Libro":200,
             "Fecha":100,"Estado":110,"Días":55,"Multa":80}
        for c in cols:
            self.tree.heading(c, text=c.upper())
            self.tree.column(c, width=w.get(c,100), anchor="center")

        self.tree.tag_configure("prestado",  background="#1a2744", foreground=C["texto"])
        self.tree.tag_configure("devuelto",  background="#0f2820", foreground="#6ee7b7")
        self.tree.tag_configure("con_multa", background="#2d1a0a", foreground=C["alerta"])

        sb = ttk.Scrollbar(ft, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set)
        self.tree.pack(side="left", expand=True, fill="both", padx=(8,0), pady=8)
        sb.pack(side="right", fill="y", pady=8, padx=(0,8))

    # ──────────────────────────────────────────────────────────────────────
    def _card(self, parent, titulo, valor, color):
        card = ctk.CTkFrame(parent, fg_color=self.C["bg_card"], corner_radius=12)
        card.pack(side="left", expand=True, fill="x", padx=5, pady=5)
        ctk.CTkLabel(card, text=titulo,
                     font=ctk.CTkFont(size=11),
                     text_color=self.C["texto_dim"]).pack(pady=(12,2))
        lbl = ctk.CTkLabel(card, text=valor,
                            font=ctk.CTkFont(family="Consolas", size=22, weight="bold"),
                            text_color=color)
        lbl.pack(pady=(0,12))
        ctk.CTkFrame(card, fg_color=color, height=3, corner_radius=0).pack(fill="x", side="bottom")
        return lbl

    # ──────────────────────────────────────────────────────────────────────
    def cargar_combos(self):
        usuarios = self.ctrl.obtener_usuarios()
        self._umap = {f"{u[0]} · {u[1]}": u[0] for u in usuarios}
        self.cbo_usr.configure(values=list(self._umap.keys()))

        libros = self.ctrl.obtener_libros()
        self._lmap = {f"{l[0]} · {l[1]}": l[0] for l in libros}
        self.cbo_lib.configure(values=list(self._lmap.keys()))

    def cargar_datos(self):
        for r in self.tree.get_children():
            self.tree.delete(r)

        datos = self.ctrl.obtener_prestamos()
        total = len(datos); activos = 0; c_multa = 0; monto = 0.0

        for p in datos:
            dias, multa = self.ctrl.calcular_multa(p[3])
            dev = p[4]
            if not dev: activos += 1
            if multa > 0: c_multa += 1; monto += multa

            tag = "devuelto" if dev else ("con_multa" if multa > 0 else "prestado")
            self.tree.insert("", "end", values=(
                p[0], p[1], p[2], p[3],
                "✅ Devuelto" if dev else "📖 Prestado",
                dias, f"${multa:.2f}"
            ), tags=(tag,))

        self.s_total.configure(text=str(total))
        self.s_activos.configure(text=str(activos))
        self.s_multa.configure(text=str(c_multa))
        self.s_monto.configure(text=f"${monto:.2f}")

    def _sel(self):
        s = self.tree.selection()
        if not s:
            messagebox.showwarning("Atención", "Seleccione un préstamo.")
            return None
        return self.tree.item(s[0])["values"]

    # ── acciones ───────────────────────────────────────────────────────────
    def registrar(self):
        try:
            uk = self.cbo_usr.get(); lk = self.cbo_lib.get()
            fecha = self.ent_fecha.get().strip()
            if not uk or not lk:
                messagebox.showwarning("Atención", "Seleccione usuario y libro.")
                return
            datetime.strptime(fecha, "%d/%m/%Y")
            ok, msg = self.ctrl.realizar_prestamo(
                self._umap.get(uk), self._lmap.get(lk), fecha
            )
            (messagebox.showinfo if ok else messagebox.showerror)(
                "✅ Éxito" if ok else "❌ Error", msg)
            if ok:
                self.cargar_combos(); self.cargar_datos()
        except ValueError:
            messagebox.showerror("Error", "Formato de fecha inválido. Use DD/MM/AAAA.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def devolver(self):
        try:
            v = self._sel()
            if not v: return
            prestamo_id = v[0]
            datos = self.ctrl.obtener_prestamos()
            libro_id = next((p[5] for p in datos if p[0] == prestamo_id), None)
            if not libro_id:
                messagebox.showerror("Error", "No se encontró el libro.")
                return
            ok, msg = self.ctrl.devolver_libro(prestamo_id, libro_id)
            (messagebox.showinfo if ok else messagebox.showerror)(
                "✅ Devuelto" if ok else "❌ Error", msg)
            if ok:
                self.cargar_combos(); self.cargar_datos()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def cancelar(self):
        """
        ACID: cancela el préstamo, libera el libro y borra la multa
        asociada, todo en una transacción atómica.
        """
        try:
            v = self._sel()
            if not v: return
            prestamo_id = v[0]

            if not messagebox.askyesno(
                "⚠️ Cancelar Préstamo",
                f"¿Cancelar el préstamo del libro «{v[2]}»?\n\n"
                "El libro quedará disponible nuevamente.\n"
                "No se puede cancelar si ya fue devuelto."
            ):
                return

            ok, msg = self.ctrl.cancelar_prestamo(prestamo_id)
            (messagebox.showinfo if ok else messagebox.showerror)(
                "✅ Cancelado" if ok else "❌ Error", msg)
            if ok:
                self.cargar_combos(); self.cargar_datos()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def ver_alertas(self):
        try:
            alertas = self.ctrl.obtener_prestamos_por_vencer()
            if alertas:
                lista = "\n".join(f"  •  {t}" for t in alertas)
                messagebox.showwarning("⚠️ Por vencer",
                                       f"Préstamos próximos a vencer:\n\n{lista}")
            else:
                messagebox.showinfo("✅ Sin alertas", "No hay préstamos próximos a vencer.")
        except Exception as e:
            messagebox.showerror("Error", str(e))
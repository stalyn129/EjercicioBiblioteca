import customtkinter as ctk


class Sidebar(ctk.CTkFrame):

    ANCHO_EXPANDIDO = 220
    ANCHO_COLAPSADO = 62

    def __init__(self, master, cambiar_vista, colores):
        super().__init__(
            master,
            width=self.ANCHO_EXPANDIDO,
            corner_radius=0,
            fg_color=colores["bg_sidebar"]
        )
        self.grid_propagate(False)
        self.colores       = colores
        self.cambiar_vista = cambiar_vista
        self._expandido    = True
        self._botones      = {}
        self._tooltips     = {}

        self._construir()

    # ══════════════════════════════════════════════════════════════════════
    def _construir(self):
        C = self.colores

        # ── HEADER logo + botón toggle ──────────────────────────────────
        self.frame_logo = ctk.CTkFrame(self, fg_color=C["bg_card"],
                                        corner_radius=0, height=100)
        self.frame_logo.pack(fill="x")
        self.frame_logo.pack_propagate(False)

        self.lbl_emoji = ctk.CTkLabel(
            self.frame_logo, text="📚",
            font=ctk.CTkFont(size=32)
        )
        self.lbl_emoji.place(relx=0.35, rely=0.38, anchor="center")

        self.lbl_marca = ctk.CTkLabel(
            self.frame_logo, text="BIBLIOTECA",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            text_color=C["acento_claro"]
        )
        self.lbl_marca.place(relx=0.60, rely=0.68, anchor="center")

        self.btn_toggle = ctk.CTkButton(
            self.frame_logo,
            text="◀",
            width=26, height=26,
            corner_radius=6,
            fg_color=C["bg_hover"],
            hover_color=C["acento"],
            font=ctk.CTkFont(size=11),
            command=self._toggle
        )
        self.btn_toggle.place(relx=0.88, rely=0.22, anchor="center")

        # ── SEPARADOR ──────────────────────────────────────────────────
        ctk.CTkFrame(self, fg_color=C["borde"], height=1,
                     corner_radius=0).pack(fill="x")

        # ── ETIQUETA SECCIÓN ───────────────────────────────────────────
        self.lbl_seccion = ctk.CTkLabel(
            self, text="MENÚ PRINCIPAL",
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color=C["texto_dim"]
        )
        self.lbl_seccion.pack(anchor="w", padx=20, pady=(18, 6))

        # ── BOTONES DE NAVEGACIÓN ─────────────────────────────────────
        modulos = [
            ("📋", "Préstamos",  "prestamos"),
            ("📖", "Libros",     "libros"),
            ("👤", "Usuarios",   "usuarios"),
            ("📌", "Reservas",   "reservas"),
            ("🎁", "Donaciones", "donaciones"),
            ("🏆", "Ranking",    "ranking"),
        ]

        for icono, texto, clave in modulos:
            btn = self._crear_boton(icono, texto, clave)
            self._botones[clave] = btn

        # ── ESPACIADOR + FOOTER ────────────────────────────────────────
        ctk.CTkFrame(self, fg_color="transparent").pack(expand=True, fill="both")
        ctk.CTkFrame(self, fg_color=C["borde"], height=1,
                     corner_radius=0).pack(fill="x")

        self.lbl_version = ctk.CTkLabel(
            self, text="Sistema Biblioteca v2.0",
            font=ctk.CTkFont(size=10),
            text_color=C["texto_dim"]
        )
        self.lbl_version.pack(pady=12)

        # Marcar activo por defecto
        self._marcar_activo("prestamos")

    # ══════════════════════════════════════════════════════════════════════
    def _crear_boton(self, icono, texto, clave):
        C = self.colores

        frame = ctk.CTkFrame(self, fg_color="transparent", corner_radius=8)
        frame.pack(fill="x", padx=10, pady=2)

        indicador = ctk.CTkFrame(frame, width=4, fg_color="transparent",
                                  corner_radius=2)
        indicador.pack(side="left", fill="y", padx=(0, 5))

        btn = ctk.CTkButton(
            frame,
            text=f"  {icono}  {texto}",
            anchor="w",
            font=ctk.CTkFont(family="Segoe UI", size=13),
            fg_color="transparent",
            text_color=C["texto_dim"],
            hover_color=C["bg_hover"],
            corner_radius=8,
            height=42,
            command=lambda c=clave: self._on_click(c)
        )
        btn.pack(fill="x")

        # Metadatos en el botón para usar al colapsar/expandir
        btn._indicador = indicador
        btn._icono     = icono
        btn._texto     = texto
        btn._clave     = clave

        # Tooltip (se activa solo en modo colapsado)
        self._tooltips[clave] = _Tooltip(btn, texto, C)

        return btn

    # ══════════════════════════════════════════════════════════════════════
    def _on_click(self, clave):
        self._marcar_activo(clave)
        self.cambiar_vista(clave)

    # ══════════════════════════════════════════════════════════════════════
    def _marcar_activo(self, clave):
        C = self.colores
        for c, btn in self._botones.items():
            if c == clave:
                btn.configure(
                    fg_color=C["bg_hover"],
                    text_color=C["acento_claro"],
                    font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold")
                )
                btn._indicador.configure(fg_color=C["acento"])
            else:
                btn.configure(
                    fg_color="transparent",
                    text_color=C["texto_dim"],
                    font=ctk.CTkFont(family="Segoe UI", size=13)
                )
                btn._indicador.configure(fg_color="transparent")

    # ══════════════════════════════════════════════════════════════════════
    def marcar_desde_afuera(self, clave):
        """Llamado desde main_tk para sincronizar el activo al cambiar vista."""
        self._marcar_activo(clave)

    # ══════════════════════════════════════════════════════════════════════
    #  COLAPSO / EXPANSIÓN
    # ══════════════════════════════════════════════════════════════════════
    def _toggle(self):
        if self._expandido:
            self._animar(self.ANCHO_EXPANDIDO, self.ANCHO_COLAPSADO)
        else:
            self._animar(self.ANCHO_COLAPSADO, self.ANCHO_EXPANDIDO)
        self._expandido = not self._expandido

    def _animar(self, desde, hasta, paso=10):
        """Resize cuadro a cuadro cada 12 ms para una animación fluida."""
        delta  = paso if hasta > desde else -paso
        nuevo  = desde + delta

        # ¿Ya llegamos al destino?
        rebasado = (delta > 0 and nuevo >= hasta) or (delta < 0 and nuevo <= hasta)
        if rebasado:
            nuevo = hasta
            self.configure(width=nuevo)
            self._actualizar_contenido()
            return

        self.configure(width=nuevo)
        self.after(12, lambda: self._animar(nuevo, hasta, paso))

    def _actualizar_contenido(self):
        """
        Adapta texto, iconos y tooltips al estado actual del sidebar.
        Se llama UNA sola vez al terminar la animación.
        """
        if self._expandido:
            # ── MODO EXPANDIDO ──────────────────────────────────────────
            self.btn_toggle.configure(text="◀")

            # Restaurar posición del logo
            self.lbl_emoji.place(relx=0.35, rely=0.38, anchor="center")
            self.lbl_marca.place(relx=0.60, rely=0.68, anchor="center")

            # Etiquetas
            self.lbl_seccion.configure(text="MENÚ PRINCIPAL")
            self.lbl_version.configure(text="Sistema Biblioteca v2.0")

            # Botones con texto completo
            for btn in self._botones.values():
                btn.configure(
                    text=f"  {btn._icono}  {btn._texto}",
                    anchor="w",
                    width=0
                )
                self._tooltips[btn._clave].desactivar()

        else:
            # ── MODO COLAPSADO ──────────────────────────────────────────
            self.btn_toggle.configure(text="▶")

            # Centrar solo el emoji
            self.lbl_emoji.place(relx=0.5, rely=0.48, anchor="center")
            self.lbl_marca.place_forget()

            # Etiquetas reducidas
            self.lbl_seccion.configure(text="·")
            self.lbl_version.configure(text="v2")

            # Botones solo con icono, centrados
            for btn in self._botones.values():
                btn.configure(
                    text=btn._icono,
                    anchor="center",
                    width=40
                )
                self._tooltips[btn._clave].activar()


# ══════════════════════════════════════════════════════════════════════════
class _Tooltip:
    """
    Tooltip flotante que aparece a la derecha del sidebar cuando está
    colapsado. Se usa ctk.CTkToplevel sin decoraciones.
    """

    def __init__(self, widget, texto, colores):
        self.widget   = widget
        self.texto    = texto
        self.colores  = colores
        self._activo  = False
        self._win     = None

    def activar(self):
        self._activo = True
        self.widget.bind("<Enter>", self._mostrar)
        self.widget.bind("<Leave>", self._ocultar)

    def desactivar(self):
        self._activo = False
        try:
            self.widget.unbind("<Enter>")
            self.widget.unbind("<Leave>")
        except Exception:
            pass
        self._ocultar()

    def _mostrar(self, event=None):
        if not self._activo:
            return
        self._ocultar()

        C = self.colores
        # Posición: pegado a la derecha del widget
        x = self.widget.winfo_rootx() + self.widget.winfo_width() + 8
        y = self.widget.winfo_rooty() + (self.widget.winfo_height() // 2) - 14

        self._win = ctk.CTkToplevel(self.widget)
        self._win.wm_overrideredirect(True)
        self._win.wm_geometry(f"+{x}+{y}")
        self._win.configure(fg_color=C["bg_hover"])
        self._win.attributes("-topmost", True)

        ctk.CTkLabel(
            self._win,
            text=f"  {self.texto}  ",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            text_color=C["acento_claro"],
            fg_color=C["bg_hover"],
            corner_radius=6
        ).pack(padx=4, pady=6)

    def _ocultar(self, event=None):
        if self._win:
            try:
                self._win.destroy()
            except Exception:
                pass
            self._win = None
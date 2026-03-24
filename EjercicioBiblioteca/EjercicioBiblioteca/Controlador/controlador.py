import sqlite3
from datetime import datetime


class ControladorBiblioteca:

    def conectar(self):
        conn = sqlite3.connect("biblioteca.db")
        conn.execute("PRAGMA foreign_keys = ON")   # Integridad referencial activada
        return conn

    # ════════════════════════════════════════════════════════════════════════
    # LIBROS
    # ════════════════════════════════════════════════════════════════════════

    def registrar_libro(self, titulo, autor, isbn="", genero=""):
        """ACID: Inserción atómica. Si falla el ISBN duplicado, revierte solo."""
        try:
            conn = self.conectar()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO libro (titulo, autor, isbn, genero, disponible)
                VALUES (?, ?, ?, ?, 1)
            """, (titulo, autor, isbn or None, genero))
            conn.commit()
            conn.close()
            return True, "Libro registrado correctamente."
        except sqlite3.IntegrityError:
            return False, "Ya existe un libro con ese ISBN."
        except Exception as e:
            return False, f"Error: {e}"

    def editar_libro(self, libro_id, titulo, autor, isbn, genero):
        """
        ACID – Atomicidad: se actualizan todos los campos o ninguno.
        ACID – Consistencia: valida ISBN único antes de confirmar.
        """
        try:
            conn = self.conectar()
            cursor = conn.cursor()

            # Verificar que el ISBN no lo use OTRO libro
            if isbn:
                cursor.execute(
                    "SELECT id FROM libro WHERE isbn = ? AND id != ?",
                    (isbn, libro_id)
                )
                if cursor.fetchone():
                    conn.close()
                    return False, "Ese ISBN ya está asignado a otro libro."

            cursor.execute("""
                UPDATE libro
                SET titulo = ?, autor = ?, isbn = ?, genero = ?
                WHERE id = ?
            """, (titulo, autor, isbn or None, genero, libro_id))

            conn.commit()
            conn.close()
            return True, "Libro actualizado correctamente."
        except Exception as e:
            return False, f"Error: {e}"

    def eliminar_libro(self, libro_id):
        """
        ACID – Consistencia: no permite eliminar si tiene préstamos activos.
        ACID – Atomicidad: elimina reservas relacionadas en la misma transacción.
        """
        try:
            conn = self.conectar()
            cursor = conn.cursor()

            # Verificar préstamos activos (no devueltos)
            cursor.execute("""
                SELECT COUNT(*) FROM prestamo
                WHERE libro_id = ? AND devuelto = 0
            """, (libro_id,))
            activos = cursor.fetchone()[0]

            if activos > 0:
                conn.close()
                return False, "No se puede eliminar: el libro tiene préstamos activos."

            # Transacción: eliminar reservas y luego el libro
            cursor.execute("DELETE FROM reserva WHERE libro_id = ?", (libro_id,))
            cursor.execute("DELETE FROM libro WHERE id = ?", (libro_id,))

            conn.commit()
            conn.close()
            return True, "Libro eliminado correctamente."
        except Exception as e:
            conn.rollback()
            conn.close()
            return False, f"Error: {e}"

    def obtener_libro_por_id(self, libro_id):
        conn = self.conectar()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, titulo, autor, isbn, genero FROM libro WHERE id = ?",
            (libro_id,)
        )
        dato = cursor.fetchone()
        conn.close()
        return dato

    def obtener_libros(self):
        conn = self.conectar()
        cursor = conn.cursor()
        cursor.execute("SELECT id, titulo, autor, isbn, genero FROM libro WHERE disponible = 1")
        datos = cursor.fetchall()
        conn.close()
        return datos

    def obtener_todos_libros(self):
        conn = self.conectar()
        cursor = conn.cursor()
        cursor.execute("SELECT id, titulo, autor, isbn, genero, disponible FROM libro")
        datos = cursor.fetchall()
        conn.close()
        return datos

    def buscar_por_isbn(self, isbn):
        conn = self.conectar()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, titulo, autor, isbn, genero, disponible
            FROM libro WHERE isbn = ?
        """, (isbn,))
        datos = cursor.fetchall()
        conn.close()
        return datos

    # ════════════════════════════════════════════════════════════════════════
    # USUARIOS
    # ════════════════════════════════════════════════════════════════════════

    def registrar_usuario(self, nombre, carrera):
        try:
            conn = self.conectar()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO usuario (nombre, carrera) VALUES (?, ?)",
                (nombre, carrera)
            )
            conn.commit()
            conn.close()
            return True, "Usuario registrado correctamente."
        except Exception as e:
            return False, f"Error: {e}"

    def editar_usuario(self, usuario_id, nombre, carrera):
        """ACID – Atomicidad: actualiza nombre y carrera juntos o falla."""
        try:
            conn = self.conectar()
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE usuario SET nombre = ?, carrera = ? WHERE id = ?
            """, (nombre, carrera, usuario_id))
            conn.commit()
            conn.close()
            return True, "Usuario actualizado correctamente."
        except Exception as e:
            return False, f"Error: {e}"

    def eliminar_usuario(self, usuario_id):
        """
        ACID – Consistencia: bloquea eliminación si tiene préstamos activos.
        Esto protege la integridad referencial más allá de lo que SQLite haría.
        """
        try:
            conn = self.conectar()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT COUNT(*) FROM prestamo
                WHERE usuario_id = ? AND devuelto = 0
            """, (usuario_id,))
            activos = cursor.fetchone()[0]

            if activos > 0:
                conn.close()
                return False, "No se puede eliminar: el usuario tiene préstamos activos."

            # Transacción: eliminar reservas y luego el usuario
            cursor.execute("DELETE FROM reserva WHERE usuario_id = ?", (usuario_id,))
            cursor.execute("DELETE FROM usuario WHERE id = ?", (usuario_id,))

            conn.commit()
            conn.close()
            return True, "Usuario eliminado correctamente."
        except Exception as e:
            conn.rollback()
            conn.close()
            return False, f"Error: {e}"

    def obtener_usuarios(self):
        conn = self.conectar()
        cursor = conn.cursor()
        cursor.execute("SELECT id, nombre, carrera FROM usuario")
        datos = cursor.fetchall()
        conn.close()
        return datos

    def obtener_usuario_por_id(self, usuario_id):
        conn = self.conectar()
        cursor = conn.cursor()
        cursor.execute("SELECT id, nombre, carrera FROM usuario WHERE id = ?", (usuario_id,))
        dato = cursor.fetchone()
        conn.close()
        return dato

    # ════════════════════════════════════════════════════════════════════════
    # PRÉSTAMOS
    # ════════════════════════════════════════════════════════════════════════

    def realizar_prestamo(self, usuario_id, libro_id, fecha):
        """
        ACID – Atomicidad: inserta el préstamo Y actualiza disponibilidad
        en una sola transacción. Si una falla, ambas revierten.
        """
        try:
            conn = self.conectar()
            cursor = conn.cursor()

            # Verificar disponibilidad (Consistencia)
            cursor.execute("SELECT disponible FROM libro WHERE id = ?", (libro_id,))
            row = cursor.fetchone()
            if not row or row[0] == 0:
                conn.close()
                return False, "El libro no está disponible."

            cursor.execute("""
                INSERT INTO prestamo (usuario_id, libro_id, fecha, devuelto)
                VALUES (?, ?, ?, 0)
            """, (usuario_id, libro_id, fecha))

            cursor.execute(
                "UPDATE libro SET disponible = 0 WHERE id = ?", (libro_id,)
            )

            conn.commit()
            conn.close()
            return True, "Préstamo registrado correctamente."
        except Exception as e:
            conn.rollback()
            conn.close()
            return False, f"Error: {e}"

    def cancelar_prestamo(self, prestamo_id):
        """
        ACID – Atomicidad: al cancelar, revierte disponibilidad del libro
        y elimina multa asociada si existe, todo en una transacción.
        Solo se puede cancelar un préstamo NO devuelto.
        """
        try:
            conn = self.conectar()
            cursor = conn.cursor()

            cursor.execute(
                "SELECT libro_id, devuelto FROM prestamo WHERE id = ?",
                (prestamo_id,)
            )
            row = cursor.fetchone()

            if not row:
                conn.close()
                return False, "Préstamo no encontrado."
            if row[1] == 1:
                conn.close()
                return False, "No se puede cancelar un préstamo ya devuelto."

            libro_id = row[0]

            # Transacción completa
            cursor.execute("DELETE FROM multa WHERE prestamo_id = ?", (prestamo_id,))
            cursor.execute("DELETE FROM prestamo WHERE id = ?", (prestamo_id,))
            cursor.execute("UPDATE libro SET disponible = 1 WHERE id = ?", (libro_id,))

            conn.commit()
            conn.close()
            return True, "Préstamo cancelado y libro liberado."
        except Exception as e:
            conn.rollback()
            conn.close()
            return False, f"Error: {e}"

    def obtener_prestamos(self):
        conn = self.conectar()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT p.id, u.nombre, l.titulo, p.fecha, p.devuelto, l.id
            FROM prestamo p
            JOIN usuario u ON p.usuario_id = u.id
            JOIN libro l ON p.libro_id = l.id
        """)
        datos = cursor.fetchall()
        conn.close()
        return datos

    # ════════════════════════════════════════════════════════════════════════
    # DEVOLUCIÓN Y MULTAS
    # ════════════════════════════════════════════════════════════════════════

    def calcular_multa(self, fecha):
        try:
            fecha_actual  = datetime.now()
            fecha_prestamo = datetime.strptime(fecha, "%d/%m/%Y")
            dias = (fecha_actual - fecha_prestamo).days
            if dias > 7:
                return dias, round((dias - 7) * 1.0, 2)
            return dias, 0
        except Exception:
            return 0, 0

    def devolver_libro(self, prestamo_id, libro_id):
        """
        ACID – Atomicidad: marca devuelto, libera libro e inserta multa
        en una sola transacción. Ningún paso parcial queda persistido.
        """
        try:
            conn = self.conectar()
            cursor = conn.cursor()

            cursor.execute("SELECT fecha, devuelto FROM prestamo WHERE id = ?", (prestamo_id,))
            resultado = cursor.fetchone()

            if not resultado:
                conn.close()
                return False, "Préstamo no encontrado."
            if resultado[1] == 1:
                conn.close()
                return False, "Este préstamo ya fue devuelto."

            fecha = resultado[0]
            dias, multa = self.calcular_multa(fecha)

            if multa > 0:
                cursor.execute("""
                    INSERT INTO multa (prestamo_id, dias_retraso, monto)
                    VALUES (?, ?, ?)
                """, (prestamo_id, dias, multa))

            cursor.execute(
                "UPDATE prestamo SET devuelto = 1 WHERE id = ?", (prestamo_id,)
            )
            cursor.execute(
                "UPDATE libro SET disponible = 1 WHERE id = ?", (libro_id,)
            )

            conn.commit()
            conn.close()
            return True, f"Libro devuelto. {'Multa: $' + str(multa) if multa > 0 else 'Sin multa.'}"
        except Exception as e:
            conn.rollback()
            conn.close()
            return False, f"Error: {e}"

    # ════════════════════════════════════════════════════════════════════════
    # RESERVAS
    # ════════════════════════════════════════════════════════════════════════

    def reservar_libro(self, usuario_id, libro_id):
        try:
            conn = self.conectar()
            cursor = conn.cursor()

            # Evitar reservas duplicadas (Consistencia)
            cursor.execute("""
                SELECT COUNT(*) FROM reserva
                WHERE usuario_id = ? AND libro_id = ? AND estado = 'Pendiente'
            """, (usuario_id, libro_id))
            if cursor.fetchone()[0] > 0:
                conn.close()
                return False, "Este usuario ya tiene una reserva pendiente para ese libro."

            cursor.execute("""
                INSERT INTO reserva (usuario_id, libro_id, fecha, estado)
                VALUES (?, ?, DATE('now'), 'Pendiente')
            """, (usuario_id, libro_id))

            conn.commit()
            conn.close()
            return True, "Reserva registrada correctamente."
        except Exception as e:
            return False, f"Error: {e}"

    def cancelar_reserva(self, reserva_id):
        """ACID – Atomicidad: elimina la reserva completamente."""
        try:
            conn = self.conectar()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM reserva WHERE id = ?", (reserva_id,))
            conn.commit()
            conn.close()
            return True, "Reserva cancelada."
        except Exception as e:
            return False, f"Error: {e}"

    def obtener_reservas(self):
        conn = self.conectar()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT r.id, u.nombre, l.titulo, r.fecha, r.estado
            FROM reserva r
            JOIN usuario u ON r.usuario_id = u.id
            JOIN libro l ON r.libro_id = l.id
        """)
        datos = cursor.fetchall()
        conn.close()
        return datos

    # ════════════════════════════════════════════════════════════════════════
    # DONACIONES
    # ════════════════════════════════════════════════════════════════════════

    def registrar_donacion(self, titulo, autor, isbn, genero, donante):
        """
        ACID – Atomicidad: crea el libro Y registra la donación juntos.
        Si una falla, ninguna persiste.
        """
        try:
            conn = self.conectar()
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO libro (titulo, autor, isbn, genero, disponible)
                VALUES (?, ?, ?, ?, 1)
            """, (titulo, autor, isbn or None, genero))

            libro_id = cursor.lastrowid

            cursor.execute("""
                INSERT INTO donacion (libro_id, donante, fecha)
                VALUES (?, ?, DATE('now'))
            """, (libro_id, donante))

            conn.commit()
            conn.close()
            return True, "Donación registrada correctamente."
        except sqlite3.IntegrityError:
            conn.rollback()
            conn.close()
            return False, "Ya existe un libro con ese ISBN."
        except Exception as e:
            conn.rollback()
            conn.close()
            return False, f"Error: {e}"

    def obtener_donaciones(self):
        conn = self.conectar()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT d.id, l.titulo, l.autor, d.donante, d.fecha
            FROM donacion d
            JOIN libro l ON d.libro_id = l.id
        """)
        datos = cursor.fetchall()
        conn.close()
        return datos

    # ════════════════════════════════════════════════════════════════════════
    # RANKING Y ALERTAS
    # ════════════════════════════════════════════════════════════════════════

    def ranking_libros(self):
        conn = self.conectar()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT l.titulo, l.autor, COUNT(*) as total
            FROM prestamo p
            JOIN libro l ON p.libro_id = l.id
            GROUP BY l.id
            ORDER BY total DESC
        """)
        datos = cursor.fetchall()
        conn.close()
        return datos

    def obtener_prestamos_por_vencer(self):
        prestamos = self.obtener_prestamos()
        alertas = []
        for p in prestamos:
            if not p[4]:
                dias, _ = self.calcular_multa(p[3])
                if dias >= 6:
                    alertas.append(p[2])
        return alertas
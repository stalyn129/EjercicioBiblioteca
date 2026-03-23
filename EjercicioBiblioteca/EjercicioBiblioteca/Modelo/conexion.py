import sqlite3


def crear_conexion():
    try:
        conn = sqlite3.connect("biblioteca.db")

        # 🔥 IMPORTANTE: activar llaves foráneas
        conn.execute("PRAGMA foreign_keys = ON")

        print("✅ Conectado a SQLite")

        crear_tablas(conn)

        return conn

    except Exception as e:
        print("❌ Error al conectar:", e)
        return None


def crear_tablas(conn):

    cursor = conn.cursor()

    # ------------------------
    # TABLA USUARIO
    # ------------------------
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuario (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            carrera TEXT NOT NULL
        )
    """)

    # ------------------------
    # TABLA LIBRO (MEJORADA)
    # ------------------------
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS libro (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT NOT NULL,
            autor TEXT NOT NULL,
            isbn TEXT UNIQUE,
            genero TEXT,
            disponible INTEGER DEFAULT 1
        )
    """)

    # ------------------------
    # TABLA PRESTAMO
    # ------------------------
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS prestamo (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER,
            libro_id INTEGER,
            fecha TEXT,
            devuelto INTEGER DEFAULT 0,
            FOREIGN KEY(usuario_id) REFERENCES usuario(id),
            FOREIGN KEY(libro_id) REFERENCES libro(id)
        )
    """)

    # ------------------------
    # TABLA MULTA
    # ------------------------
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS multa (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            prestamo_id INTEGER,
            dias_retraso INTEGER,
            monto REAL,
            FOREIGN KEY(prestamo_id) REFERENCES prestamo(id)
        )
    """)

    # ------------------------
    # TABLA RESERVA
    # ------------------------
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reserva (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER,
            libro_id INTEGER,
            fecha TEXT,
            estado TEXT
        )
    """)

    # ------------------------
    # TABLA DONACION
    # ------------------------
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS donacion (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            libro_id INTEGER,
            donante TEXT,
            fecha TEXT
        )
    """)

    conn.commit()
    print("✅ Tablas verificadas/creadas correctamente")
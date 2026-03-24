import csv
import sqlite3


def importar_csv(ruta):

    try:
        conn = sqlite3.connect("biblioteca.db")
        cursor = conn.cursor()

        with open(ruta, newline='', encoding='utf-8') as f:
            reader = csv.reader(f)

            for row in reader:
                # validar que tenga datos
                if len(row) < 2:
                    continue

                titulo, autor = row

                cursor.execute(
                    "INSERT INTO libro (titulo, autor, disponible) VALUES (?, ?, 1)",
                    (titulo, autor)
                )

        conn.commit()
        conn.close()

        print("✅ Libros importados correctamente")

    except Exception as e:
        print("❌ Error al importar CSV:", e)
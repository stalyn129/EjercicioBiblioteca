class Prestamo:

    def __init__(self, usuario, libro, fecha):
        self.usuario = usuario
        self.libro = libro
        self.fecha = fecha
        self.devuelto = False

    def mostrar_prestamo(self):

        estado = "Devuelto" if self.devuelto else "Prestado"

        print("Usuario:", self.usuario.nombre)
        print("Libro:", self.libro.titulo)
        print("Fecha:", self.fecha)
        print("Estado:", estado)
        print("-----------------------")
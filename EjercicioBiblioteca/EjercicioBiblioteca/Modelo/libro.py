class Libro:

    contador = 1

    def __init__(self, titulo, autor):
        self.codigo = Libro.contador
        Libro.contador += 1

        self.titulo = titulo
        self.autor = autor
        self.disponible = True
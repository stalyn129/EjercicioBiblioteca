class Usuario:

    contador = 1

    def __init__(self, nombre, carrera):
        self.id = Usuario.contador
        Usuario.contador += 1

        self.nombre = nombre
        self.carrera = carrera
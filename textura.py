#Codigo ayuda: https://github.com/churly92/Engine3D/blob/main/gl.py
#Repositorio perteneciente a Prof. Carlos Alonso

#Mirka Monzon 18139
#Lab2: Shaders

import struct
from gl import color

class Texture(object):
    #Lee el archivo BMP, lo usa como textura para el modelo 3D
    def __init__(self, path):
        self.path = path
        self.readTexture()
    
    def readTexture(self):
        #Lea el archivo BMP, extrae el header y los valores de los pixeles
        
        img = open(self.path, 'rb')
        img.seek(2 + 4 + 4)
        header_size = struct.unpack('=l', img.read(4))[0]
        img.seek(2 + 4 + 4 + 4 + 4)

        self.width = struct.unpack('=l', img.read(4))[0]
        self.height = struct.unpack('=l', img.read(4))[0]
        self.pixels = []
        
        img.seek(header_size)

        for y in range(self.height):
            self.pixels.append([])
            for x in range(self.width):
                b = ord(img.read(1))
                g = ord(img.read(1))
                r = ord(img.read(1))
                self.pixels[y].append(color(r, g, b))
        
        img.close()
    
    def get_color(self, tx, ty, intensity = 1):
        #Obtiene el color de cada píxel del archivo BMP
        x = int(tx * self.width)
        y = int(ty * self.height)

        try:
            #Obtiene el color de cada píxel del archivo BMP
            return bytes(
                map(
                    lambda b: round(b * intensity) if b * intensity > 0 else 0,
                    self.pixels[y][x]
                )
            )
        except IndexError:
            return bytes(
                map(
                    lambda t: int(round(t*intensity)) if (t * intensity) > 0 else 0,
                    self.pixelesBuffer[y-1][x-1]
                )
            )
    
    def getDimensions(self):
        #Obtiene height y width del BMP
        return self.height, self.width
#Codigo ayuda: https://github.com/churly92/Engine3D/blob/main/gl.py
#Repositorio perteneciente a Prof. Carlos Alonso

#Mirka Monzon 18139
#Lab2: Shaders

#Lector de archivos .obj
class ObjReader(object):
    
    def __init__(self, filename, mtl = None):
        self.verifier = False
        #Abre y lee archivos .obj
        with open(filename) as obj_file:
            self.lines = obj_file.read().splitlines()
        
        if mtl:
            self.verifier = True
            with open(mtl) as x:
                self.lines2 = x.read().splitlines()
        
        self.vertices = []
        self.normals = []
        self.tex_coords = []
        self.faces = []

        self.matType = []
        self.kD = []

        self.material = {}

        #Reads individual lines from .obj file
        self.readLines()
    

    def removeSpaces(self, face):
        #Remueve espacios en blanco si los hay
        store_data = face.split('/')

        if ("") in store_data:
            store_data[1] = 0
        
        return map(int, store_data)

    def readLines(self):
        #Lee lineas individuales del archivo .obj

        if self.verifier:
            for line2 in self.lines2:
                if line2:
                    prefix2, value2 = line2.split(' ', 1)
                    if prefix2 == 'newmtl':
                        self.matType.append(value2)
                    if prefix2 == 'Kd':
                        self.kD.append(list(map(float,value2.split(' '))))
            for index in range(len(self.matType)-1):
                self.material[self.matType[index]] = self.Kd[index]
        
        self.mater = ""

        for line in self.lines:        
            if line:
                prefix, value = line.split(' ', 1)
                if prefix == 'v':
                    self.vertices.append(list(map(float,value.split(' '))))
                if prefix == 'vn':
                    self.normals.append(list(map(float,value.split(' '))))
                if prefix == 'vt':
                    self.tex_coords.append(list(map(float,value.split(' '))))
                if prefix == 'f':
                    if self.verifier:
                        listita = [list(self.removeSpaces(face)) for face in value.split(' ')]
                        listita.append(self.mater)
                        self.faces.append(listita)
                    else:
                        self.faces.append([list(self.removeSpaces(face)) for face in value.split(' ')])
                if prefix == 'usemtl':
                    self.mater = value
#Codigo ayuda: https://github.com/churly92/Engine3D/blob/main/gl.py
#Repositorio perteneciente a Prof. Carlos Alonso

#Mirka Monzon 18139
#Lab2: Shaders

import struct
import collections
import math
import time
from random import randint as random
from random import uniform as randomDec
from obj import ObjReader

#Definicion
def char(c):
    return struct.pack('=c', c.encode('ascii'))

def word(w):
    return struct.pack('=h', w)

def dword(d):
    return struct.pack('=l', d)

def color(r,g,b):
    return bytes([b, g, r])

#Metodo creating noise de Perlon Noise
#En base del codigo perlin.c https://gist.github.com/nowl/828013
#Creacion de random para noise
SEED = 0;
hasho = [208,34,231,213,32,248,233,56,161,78,24,140,71,48,140,254,245,255,247,247,40,
                     185,248,251,245,28,124,204,204,76,36,1,107,28,234,163,202,224,245,128,167,204,
                     9,92,217,54,239,174,173,102,193,189,190,121,100,108,167,44,43,77,180,204,8,81,
                     70,223,11,38,24,254,210,210,177,32,81,195,243,125,8,169,112,32,97,53,195,13,
                     203,9,47,104,125,117,114,124,165,203,181,235,193,206,70,180,174,0,167,181,41,
                     164,30,116,127,198,245,146,87,224,149,206,57,4,192,210,65,210,129,240,178,105,
                     228,108,245,148,140,40,35,195,38,58,65,207,215,253,65,85,208,76,62,3,237,55,89,
                     232,50,217,64,244,157,199,121,252,90,17,212,203,149,152,140,187,234,177,73,174,
                     193,100,192,143,97,53,145,135,19,103,13,90,135,151,199,91,239,247,33,39,145,
                     101,120,99,3,186,86,99,41,237,203,111,79,220,135,158,42,30,154,120,67,87,167,
                     135,176,183,191,253,115,184,21,233,58,129,233,142,39,128,211,118,137,139,255,
                     114,20,218,113,154,27,127,246,250,1,8,198,250,209,92,222,173,21,88,102,219]

#Mapa dentro de la matriz por módulo 256 y devolvemos el valor
def noise2(x, y):
    tmp = hasho[(y + SEED) % 256]
    return hasho[(tmp + x) % 256]

#Función X a los parámetros enviados
def lin_inter(x, y, s):
    return float(x + s * (y-x))

#Función X a los parámetros enviados
def smooth_inter(x, y, s):
    return lin_inter(float(x), float(y), float(s * s * (3-2*s)))

#Creaciond de noise de noise2 and smooth_inter
def noise2d(x, y):
    x_int = int(x)
    y_int = int(y)
    x_frac = float(x - x_int)
    y_frac = float(y - y_int)
    s = int(noise2(x_int, y_int))
    t = int(noise2(x_int+1, y_int))
    u = int(noise2(x_int, y_int+1))
    v = int(noise2(x_int+1, y_int+1))
    low = float(smooth_inter(s, t, x_frac))
    high = float(smooth_inter(u, v, x_frac))
    return float(smooth_inter(low, high, y_frac))

#Valor entre 0 y 1
def perlin2d(x, y, freq, depth):
    xa = float(x*freq)
    ya = float(y*freq)
    amp = float(1.0)
    fin = float(0)
    div = float(0.0)

    for i in range(depth):
        div += 256 * amp
        fin += noise2d(xa, ya) * amp
        amp /= 2
        xa *= 2
        ya *= 2

    return float(fin/div)

#Constantes
V2 = collections.namedtuple('Vertex2', ['x', 'y'])
V3 = collections.namedtuple('Vertex3', ['x', 'y', 'z'])

#Calculos 
#Vector suma
def sum(v0, v1):
    return V3(v0.x + v1.x, v0.y + v1.y, v0.z + v1.z)

#Vector de substraccion 
def sub(v0, v1):
    return V3(v0.x - v1.x, v0.y - v1.y, v0.z - v1.z)

#Vector multiplicacion
def mul(v0, k):
    return V3(v0.x * k, v0.y * k, v0.z * k)

#Producto punto
def dot(v0, v1):
    return v0.x * v1.x + v0.y * v1.y + v0.z * v1.z

#Producto cruz
def cross(v0, v1):
    x = v0.y * v1.z - v0.z * v1.y
    y = v0.z * v1.x - v0.x * v1.z
    z = v0.x * v1.y - v0.y * v1.x

    return V3(x, y, z)

#Vector magnitud
def magnitud(v0):
    return (v0.x**2 + v0.y**2 + v0.z**2)**0.5

#Vector normal
def norm(v0):
    l = magnitud(v0)
    if l == 0:
        return V3(0, 0, 0)
    else:
        return V3(v0.x/l, v0.y/l, v0.z/l)

#Multiplicacion de matrices 
def multMatrices(m1,m2):
    if len(m1[0]) == len(m2):
        resultMatrix = [[0] * len(m2[0]) for i in range(len(m1))]
        for x in range(len(m1)):
            for y in range(len(m2[0])):
                for z in range(len(m1[0])):
                    try:
                        resultMatrix[x][y] += m1[x][z] * m2[z][y]
                    except IndexError:
                        pass
        return resultMatrix
    else:
        print("\nERROR: No se pudo realizar la multiplicación de matrices porque el número de columnas de la primera matriz no es igual al número de filas de la segunda matriz")
        return 0

def bbox(A, B, C):
    xs = sorted([int(A.x), int(B.x), int(C.x)])
    ys = sorted([int(A.y), int(B.y), int(C.y)])
    a = V2(int(xs[0]), int(ys[0]))
    b = V2(int(xs[2]), int(ys[2]))    
    
    return a, b

#Convertidor de vértices en coordenadas baricéntricas
def barycentric(A, B, C, P):
    cx, cy, cz = cross(V3(B.x - A.x, C.x - A.x, A.x - P.x), V3(B.y - A.y, C.y - A.y, A.y - P.y))

    #CZ no puede ser menos de 1
    if cz == 0:
        return -1, -1, -1

    #Calcula las coordenadas baricéntricas
    u = cx/cz
    v = cy/cz
    w = 1 - (u + v)

    return  w, v, u

#Constructor
class Bitmap(object):
    def __init__(self, height, width):

        self.height = height
        self.width = width
        self.framebuffer = []
        self.zbuffer = []
        self.clear_color = color(0, 0, 0)
        self.vertex_color = color(255, 255, 0)
        self.glClear()

    #Inicializacion de software render 
    def glInit(self):
        pass

#Funciones de render 
    #Inicializacion de framebuffer
    def glCreateWindow(self, height, width):
        self.height = height
        self.width = width
        self.glClear()
    
    #Creacion de espacio para dibujar
    def glViewPort(self, x, y, width, height):
        self.x = x
        self.y = y
        self.vpx = width
        self.vpy = height

    #Mapa de bits de un solo color
    def glClear(self):
        self.framebuffer = [
            [
                self.clear_color for x in range(self.width)
                ]
            for y in range(self.height)
        ]

        self.zbuffer = [
            [
                -1*float('inf') for x in range(self.width)
                ]
            for y in range(self.height)
        ]
    
    #Cambio de color de glClear
    def glClearColor(self, r, g, b):
        try:
            self.rc = round(255*r)
            self.gc = round(255*g)
            self.bc = round(255*b)
            self.clear_color = color(self.rc, self.rg, self.rb)
        except ValueError:
            print('\nERROR: Ingrese un número entre 1 y 0\n')
    
    #Cambio de color de punto en pantalla
    def glVertex(self, x, y):
        if x <= 1 and x>= -1 and y >= -1 and y <= 1:
                
                if x > 0:
                        self.vx = self.x + round(round(self.vpx/2)*x) - 1
                if y > 0:
                        self.vy = self.y + round(round(self.vpy/2)*y) - 1
                if x <= 0:
                        self.vx = self.x + round(round(self.vpx/2)*x)
                if y <= 0:
                        self.vy = self.y + round(round(self.vpy/2)*y)
                
                self.glPoint(self.vx,self.vy, self.vertex_color)
        else:
                pass
    
    #Cambio de color con el que funciona glVertex
    def glColor(self, r, g, b):
        try:
            self.rv = round(255*r)
            self.gv = round(255*g)
            self.bv = round(255*b)
            self.vertex_color = color(self.rv,self.gv,self.bv)
        except ValueError:
                print('\nERROR: Ingrese un número entre 1 y 0\n')

    #Da el color al punto en pantalla
    def glPoint(self, x, y, color):
        x = int(round((x+1) * self.width / 2))
        y = int(round((y+1) * self.height / 2))
        try:
                self.framebuffer[y][x] = color
        except IndexError:
                #print("\nEl pixel está fuera de los límites de la imagen.\n")
                pass
    
    #Funcion para linea
    def glLine(self, x0, y0, x1, y1):
        #Convierte los valores entre -1 a 1 a cordenadas DMC
        x0 = int(round((x0 + 1) * self.width / 2))
        y0 = int(round((y0 + 1) * self.height / 2))
        x1 = int(round((x1 + 1) * self.width / 2))
        y1 = int(round((y1 + 1) * self.height / 2))

        dy = abs(y1 - y0)
        dx = abs(x1 - x0)

        steep = dy > dx
        
        #Si dy es mayor que dx entonces intercambiamos cada una de las coordenadas
        if steep:
            x0, y0 = y0, x0
            x1, y1 = y1, x1
        
        #Si el punto de inicio en x es mayor que el punto final, intercambia los puntos
        if x0 > x1:
            x0, x1 = x1, x0
            y0, y1 = y1, y0
        
        dy = abs(y1 - y0)
        dx = abs(x1 - x0)

         #Determina los puntos que formarán la línea
        offset = 0 * 2 * dx
        threshold = 0.5 * 2 * dx
        y = y0

        #Rellena la línea con puntos sin dejar espacios
        for x in range(x0, x1 + 1):
            if steep:
                self.glPoint((float(y)/(float(self.width)/2))-1,(float(x)/(float(self.height)/2))-1,self.vertex_color)
            else:
                self.glPoint((float(x)/(float(self.width)/2))-1,(float(y)/(float(self.height)/2))-1,self.vertex_color)
            offset += dy

            if offset >= threshold:
                y += 1 if y0 < y1 else -1
                threshold += 1 * dx

    #Transforma el vértice en tupla
    def glTransform(self, vertex, translate=(0, 0, 0), scale=(1, 1, 1)):
        try:
            return V3(
                (int(round((vertex[0]+1) * self.width / 2)) + translate[0]) * scale[0],
                (int(round((vertex[1]+1) * self.height / 2)) + translate[1]) * scale[1],
                (int(round((vertex[2]+1) * self.width / 2)) + translate[2]) * scale[2]
            )
        except IndexError:
            return V3(
                (int(round((vertex[0]+1) * self.width / 2)) + translate[0]) * scale[0],
                (int(round((vertex[1]+1) * self.height / 2)) + translate[1]) * scale[1],
                (int(round((0.0+1) * self.width / 2)) + translate[2]) * scale[2]
            )

    #Algoritmo para rellenar triangulos
    def glFillTriangle(self, a, b, c):

        if a.y > b.y:
            a, b = b, a
        if a.y > c.y:
            a, c = c, a
        if b.y > c.y:
            b, c = c, b
        
        ac_x_slope = c.x - a.x
        ac_y_slope = c.y - a.y

        if ac_y_slope == 0:
            inverse_ac_slope = 0
        else:
            inverse_ac_slope = ac_x_slope / ac_y_slope

        ab_x_slope = b.x - a.x
        ab_y_slope = b.y - a.y

        if ab_y_slope == 0:
            inverse_ab_slope = 0
        else:
            inverse_ab_slope = ab_x_slope / ab_y_slope

        for y in range(a.y, b.y + 1):
            x0 = round(a.x - inverse_ac_slope * (a.y - y))
            xf = round(a.x - inverse_ab_slope * (a.y - y))

            if x0 > xf:
                x0, xf = xf, x0
            
            for x in range(x0, xf + 1):
                self.glPoint((float(x)/(float(self.width)/2))-1,(float(y)/(float(self.height)/2))-1,self.vertex_color)
        
        bc_x_slope = c.x - b.x
        bc_y_slope = c.y - b.y

        if bc_y_slope == 0:
            inverse_bc_slope = 0
        else:
            inverse_bc_slope = bc_x_slope / bc_y_slope
            
        for y in range (b.y, c.y + 1):
            x0 = int(round(a.x - inverse_ac_slope * (a.y - y)))
            xf = int(round(b.x - inverse_bc_slope * (b.y - y)))

            if x0 > xf:
                x0, xf = xf, x0
            
            for x in range(x0, xf + 1):
                self.glPoint((float(x)/(float(self.width)/2))-1,(float(y)/(float(self.height)/2))-1,self.vertex_color)
    
    #Algoritmo para rellenar triangulos con Coordenadas baricéntricas
    def triangle(self, A, B, C, light, color=None, texture=None, tex_coords=(), intensity = 1, normals_coords = ()):

        bbox_min, bbox_max = bbox(A, B, C)

        for x in range(bbox_min.x, bbox_max.x + 1):
            for y in range(bbox_min.y, bbox_max.y +1):

                w, v, u = barycentric(A, B, C, V2(x, y))

                if w < 0 or v < 0 or u < 0:
                    continue

                if color:
                    self.vertex_color = color

                col = self.gourad2(
                    xy = (x,y),
                    bar = (w,v,u),
                    varing_normals = normals_coords,
                    light = light
                )

                self.vertex_color = col

                if texture:
                    ta, tb, tc = tex_coords
                    tx = ta.x * w + tb.x * v + tc.x * u
                    ty = ta.y * w + tb.y * v + tc.y * u
                    
                    colo = texture.get_color(tx, ty, intensity)
                    self.vertex_color = colo

                    col = self.gourad(
                        bar = (w,v,u),
                        texture_coord=(tx,ty),
                        textu = texture,
                        varing_normals = normals_coords,
                        light = light
                    )
                    self.vertex_color = col

                z = A.z * w + B.z * v + C.z * u

                try:
                    if z > self.zbuffer[y][x]:
                        self.glPoint((float(x)/(float(self.width)/2))-1, (float(y)/(float(self.height)/2))-1,self.vertex_color)
                        self.zbuffer[y][x] = z
                except IndexError:
                    pass
    
    #Shader para modo texturizado
    def gourad(self, **kwargs):
        w, v, u = kwargs['bar']
        
        nA, nB, nC = kwargs['varing_normals']
        
        tx, ty = kwargs['texture_coord']
        
        light = kwargs['light']
        
        tex = kwargs['textu']
        
        tcolor = tex.get_color(tx,ty)
        
        nx = nA.x * w + nB.x * v + nC.x * u
        ny = nA.y * w + nB.y * v + nC.y * u
        nz = nA.z * w + nB.z * v + nC.z * u
        
        vn = V3(nx,ny,nz)
        
        intensity = dot(vn, light)
        
        return bytes([
            int(tcolor[2] * intensity) if tcolor[2] * intensity > 0 else 0,
            int(tcolor[1] * intensity) if tcolor[1] * intensity > 0 else 0,
            int(tcolor[0] * intensity) if tcolor[0] * intensity > 0 else 0
        ])

    #Shader para modo no texturizado
    def gourad2(self, **kwargs):
        w, v, u = kwargs['bar']

        x, y = kwargs['xy']

        nA, nB, nC = kwargs['varing_normals']

        light = kwargs['light']

        nx = nA.x * w + nB.x * v + nC.x * u
        ny = nA.y * w + nB.y * v + nC.y * u
        nz = nA.z * w + nB.z * v + nC.z * u

        vn = V3(nx,ny,nz)

        xi = float(float(x)/float(self.width))
        yi = float(float(y)/float(self.height))

        ruido = perlin2d(xi,yi,10,20)

        y = y + int(perlin2d(xi,yi,15,10)* random(0,40))

        intensity = dot(vn, light)

        if y > 765:
            #Mostaza
            return bytes([
                    int(120 * intensity * ruido) if 120 * intensity > 0 else 0,
                    int(176 * intensity * ruido) if 176 * intensity > 0 else 0,
                    int(194 * intensity * ruido) if 194 * intensity > 0 else 0])
        if y > 755:
            #Piel
            return bytes([
                    int(160 * intensity * ruido) if 160 * intensity > 0 else 0,
                    int(200 * intensity * ruido) if 200 * intensity > 0 else 0,
                    int(220 * intensity * ruido) if 220 * intensity > 0 else 0])
        if y > 745:
            #Cafe claro
            return bytes([
                    int(107 * intensity * ruido) if 107 * intensity > 0 else 0,
                    int(135 * intensity * ruido) if 135 * intensity > 0 else 0,
                    int(193 * intensity * ruido) if 193 * intensity > 0 else 0])
        if y > 715:
            return bytes([
                    int(160 * intensity * ruido) if 160 * intensity > 0 else 0,
                    int(210 * intensity * ruido) if 210 * intensity > 0 else 0,
                    int(240 * intensity * ruido) if 240 * intensity > 0 else 0])
        if y > 700:
            return bytes([
                    int(160 * intensity * ruido) if 160 * intensity > 0 else 0,
                    int(200 * intensity * ruido) if 200 * intensity > 0 else 0,
                    int(220 * intensity * ruido) if 220 * intensity > 0 else 0])
        if y > 690:
            #PielPalido
            return bytes([
                    int(160 * intensity * ruido) if 160 * intensity > 0 else 0,
                    int(200 * intensity * ruido) if 200 * intensity > 0 else 0,
                    int(230 * intensity * ruido) if 230 * intensity > 0 else 0])
        if y > 670:
            #Blanco Gris
            return bytes([
                    int(218 * intensity * ruido) if 218 * intensity > 0 else 0,
                    int(235 * intensity * ruido) if 235 * intensity > 0 else 0,
                    int(231 * intensity * ruido) if 231 * intensity > 0 else 0])
        if y > 650:
            #Mostaza
            return bytes([
                    int(120 * intensity * ruido) if 120 * intensity > 0 else 0,
                    int(176 * intensity * ruido) if 176 * intensity > 0 else 0,
                    int(194 * intensity * ruido) if 194 * intensity > 0 else 0])
        if y > 640:
            #Piel
            return bytes([
                    int(160 * intensity * ruido) if 160 * intensity > 0 else 0,
                    int(210 * intensity * ruido) if 210 * intensity > 0 else 0,
                    int(250 * intensity * ruido) if 240 * intensity > 0 else 0])
        if y > 560:
            #Cafe claro
            return bytes([
                    int(107 * intensity * ruido) if 107 * intensity > 0 else 0,
                    int(135 * intensity * ruido) if 135 * intensity > 0 else 0,
                    int(193 * intensity * ruido) if 193 * intensity > 0 else 0])
        if y > 510:
            #Piel
            return bytes([
                    int(160 * intensity * ruido) if 160 * intensity > 0 else 0,
                    int(210 * intensity * ruido) if 210 * intensity > 0 else 0,
                    int(250 * intensity * ruido) if 240 * intensity > 0 else 0])
        if y > 470:
            #Blanco Gris
            return bytes([
                    int(218 * intensity * ruido) if 218 * intensity > 0 else 0,
                    int(235 * intensity * ruido) if 235 * intensity > 0 else 0,
                    int(231 * intensity * ruido) if 231 * intensity > 0 else 0])
        if y > 430:
            #Mostaza
            return bytes([
                    int(120 * intensity * ruido) if 120 * intensity > 0 else 0,
                    int(176 * intensity * ruido) if 176 * intensity > 0 else 0,
                    int(194 * intensity * ruido) if 194 * intensity > 0 else 0])
        if y > 410:
            #Mostaza
            return bytes([
                    int(100 * intensity * ruido) if 100 * intensity > 0 else 0,
                    int(166 * intensity * ruido) if 166 * intensity > 0 else 0,
                    int(198 * intensity * ruido) if 198 * intensity > 0 else 0])
        if y > 400:
            #Piel
            return bytes([
                    int(160 * intensity * ruido) if 160 * intensity > 0 else 0,
                    int(210 * intensity * ruido) if 210 * intensity > 0 else 0,
                    int(250 * intensity * ruido) if 240 * intensity > 0 else 0])
        if y > 380:
            #Cafe claro
            return bytes([
                    int(107 * intensity * ruido) if 107 * intensity > 0 else 0,
                    int(135 * intensity * ruido) if 135 * intensity > 0 else 0,
                    int(193 * intensity * ruido) if 193 * intensity > 0 else 0])
        if y > 360:
            #Piel
            return bytes([
                    int(160 * intensity * ruido) if 160 * intensity > 0 else 0,
                    int(210 * intensity * ruido) if 210 * intensity > 0 else 0,
                    int(250 * intensity * ruido) if 240 * intensity > 0 else 0])
        if y > 340:
            #Blanco Gris
            return bytes([
                int(218 * intensity * ruido) if 218 * intensity > 0 else 0,
                int(235 * intensity * ruido) if 235 * intensity > 0 else 0,
                int(231 * intensity * ruido) if 231 * intensity > 0 else 0])
        if y > 320:
            #Mostaza
            return bytes([
                int(120 * intensity * ruido) if 120 * intensity > 0 else 0,
                int(176 * intensity * ruido) if 176 * intensity > 0 else 0,
                int(194 * intensity * ruido) if 194 * intensity > 0 else 0])
        if y > 300:
            #Mostaza
            return bytes([
                int(120 * intensity * ruido) if 120 * intensity > 0 else 0,
                int(176 * intensity * ruido) if 176 * intensity > 0 else 0,
                int(194 * intensity * ruido) if 194 * intensity > 0 else 0])        
        if y > 280:
            #Blanco Gris
            return bytes([
                int(218 * intensity * ruido) if 218 * intensity > 0 else 0,
                int(235 * intensity * ruido) if 235 * intensity > 0 else 0,
                int(231 * intensity * ruido) if 231 * intensity > 0 else 0])
        if y > 260:
            #Mostaza
            return bytes([
                int(120 * intensity * ruido) if 120 * intensity > 0 else 0,
                int(176 * intensity * ruido) if 176 * intensity > 0 else 0,
                int(194 * intensity * ruido) if 194 * intensity > 0 else 0])
        if y > 0:
            #Blanco Gris
            return bytes([
                int(218 * intensity * ruido) if 218 * intensity > 0 else 0,
                int(235 * intensity * ruido) if 235 * intensity > 0 else 0,
                int(231 * intensity * ruido) if 231 * intensity > 0 else 0])

    #toon shader 
    def toon(self, **kwargs):
        u, v, w = kwargs['bar']
        na, nb, nc = kwargs['varing_normals']
        ta, tb, tc = kwargs['texture_coord']
        light = kwargs['light']
        tex = kwargs['textu']
        b, g, r = kwargs['color']

        b /= 255
        g /= 255
        r /= 255

        if tex:
            tx = ta.x * u + tb.x * v + tc.x * w
            ty = ta.y * u + tb.y * v + tc.y * w
            tcolor = tex.get_color(tx,ty)
            b *= tcolor[0] / 255
            g *= tcolor[1] / 255
            r *= tcolor[2] / 255

        nx = na[0] * u + nb[0] * v + nc[0] * w
        ny = na[1] * u + nb[1] * v + nc[1] * w
        nz = na[2] * u + nb[2] * v + nc[2] * w
        normal = V3(nx,ny,nz)
        intensity = dot(normal, light)

        if (intensity>0.85):
            intensity = 1
        elif (intensity>0.60):
            intensity = 0.80
        elif (intensity>0.45):
            intensity = 0.60
        elif (intensity>0.30):
            intensity = 0.45
        elif (intensity>0.15):
            intensity = 0.30
        else:
            intensity = 0

        b *= intensity
        g *= intensity
        r *= intensity

        return r, g, b

    def phong(render, **kwargs):
        u, v, w = kwargs['bar']
        ta, tb, tc = kwargs['texture_coord']
        na, nb, nc = kwargs['varing_normals']
        b, g, r = kwargs['color']

        b /= 255
        g /= 255
        r /= 255

        if render.active_texture:
            tx = ta.x * u + tb.x * v + tc.x * w
            ty = ta.y * u + tb.y * v + tc.y * w
            texColor = render.active_texture.getColor(tx, ty)
            b *= texColor[0] / 255
            g *= texColor[1] / 255
            r *= texColor[2] / 255

        nx = na[0] * u + nb[0] * v + nc[0] * w
        ny = na[1] * u + nb[1] * v + nc[1] * w
        nz = na[2] * u + nb[2] * v + nc[2] * w

        normal = V3(nx, ny, nz)

        intensity = np.dot(normal, render.light)

        b *= intensity
        g *= intensity
        r *= intensity

        if intensity > 0 and intensity < 0.25:
            return 1, 0, 0
        if intensity >= 0.25 and intensity < 0.50:
            return 1, 0.25, 0
        if intensity >= 0.50 and intensity < 0.75:
            return 1, 0.50, 0
        if intensity >= 0.75 and intensity < 1:
            return 1, 1, 0
        else:
            return 0,0,0

    #Transformacion de vector
    def glTransformMatrix(self, vector):
        vector_nuevo = [[vector.x],[vector.y],[vector.z],[1]]
        nuevo_vector = multMatrices(self.laMatriz, vector_nuevo)
        return V3(nuevo_vector[0][0]/nuevo_vector[3][0],nuevo_vector[1][0]/nuevo_vector[3][0],nuevo_vector[2][0]/nuevo_vector[3][0])

    #Matriz pipeline
    def glPipelineMatrix(self):
        a = multMatrices(self.Model, self.View)
        b = multMatrices(self.Proyection, a)
        c = multMatrices(self.Viewport, b)
        self.laMatriz = c
    
    def glFillPolygon(self, polygon):
        #Point-in-Polygon (PIP) Algorithm
        for y in range(self.height):
            for x in range(self.width):
                i = 0
                j = len(polygon) - 1
                draw_point = False
                #Verifica si el punto está entre los límites
                for i in range(len(polygon)):
                    if (polygon[i][1] < y and polygon[j][1] >= y) or (polygon[j][1] < y and polygon[i][1] >= y):
                        if polygon[i][0] + (y - polygon[i][1]) / (polygon[j][1] - polygon[i][1]) * (polygon[j][0] - polygon[i][0]) < x:
                            draw_point = not draw_point
                    j = i
                if draw_point:
                    self.glPoint((float(x)/(float(self.width)/2))-1,(float(y)/(float(self.height)/2))-1,self.vertex_color)

    #Lee y renderiza archivos .obj 
    def glLoadObjModel(self, file_name, mtl=None, texture=None, translate=(0,0, 0), scale=(1,1, 1), rotate =(0,0,0)):
        '''Load and Render .obj file'''
        #Lector .obj
        self.loadModelMatrix(translate, scale, rotate)
        self.glPipelineMatrix()
        
        if not mtl:
            model = ObjReader(file_name)
            model.readLines()
        else:
            model = ObjReader(file_name, mtl)
            model.readLines()

        light = V3(0, 0.5, 1)
        
        for face in model.faces:
            if mtl:
                vertices_ctr = len(face) - 1
            else:
                vertices_ctr = len(face)
            
            if vertices_ctr == 3:
                f1 = face[0][0] - 1
                f2 = face[1][0] - 1
                f3 = face[2][0] - 1
                
                a = self.glTransform(model.vertices[f1], translate, scale)
                b = self.glTransform(model.vertices[f2], translate, scale)
                c = self.glTransform(model.vertices[f3], translate, scale)
                
                a = self.glTransformMatrix(a)
                b = self.glTransformMatrix(b)
                c = self.glTransformMatrix(c)
                
                n1 = face[0][2] - 1
                n2 = face[1][2] - 1
                n3 = face[2][2] - 1

                normal = V3(*model.normals[n1])

                light = norm(light)

                intensity = dot(normal, light)
                
                nA = V3(*model.normals[n1])
                nB = V3(*model.normals[n2])
                nC = V3(*model.normals[n3])

                if intensity < 0:
                    continue
                
                if texture:
                    tv1 = face[0][1] - 1
                    tv2 = face[1][1] - 1
                    tv3 = face[2][1] - 1
                    
                    tvA = V2(*model.tex_coords[tv1])
                    tvB = V2(*model.tex_coords[tv2])
                    tvC = V2(*model.tex_coords[tv3])

                    self.triangle(a,b,c, texture = texture, tex_coords = (tvA, tvB, tvC), intensity = intensity)
                
                elif mtl:
                    material2 = face[3]
                    valorcito = model.material[material2]
                    self.triangle(a,b,c,light,color = self.glColor(valorcito[0]*intensity,valorcito[1]*intensity, valorcito[2]*intensity))

                else:
                    self.glColor(intensity, intensity, intensity)
                    self.triangle(a,b,c,light,color = self.glColor(intensity, intensity, intensity), normals_coords = (nA, nC, nB))
    
    def loadModelMatrix(self, translate=(0,0,0),scale=(1,1,1),rotate=(0,0,0)):
        translate_matrix = [
            [1,0,0,translate[0]],
            [0,1,0,translate[1]],
            [0,0,1,translate[2]],
            [0,0,0,1]
        ]
        
        scale_matrix = [
            [scale[0],0,0,0],
            [0,scale[1],0,0],
            [0,0,scale[2],0],
            [0,0,0,1]
        ]
        
        a = rotate[0]
        rotation_matrix_x = [
            [1,0,0,0],
            [0,math.cos(a),-1*(math.sin(a)),0],
            [0,math.sin(a),math.cos(a),0],
            [0,0,0,1]
        ]
        
        a = rotate[1]
        rotation_matrix_y = [
            [math.cos(a),0,math.sin(a),0],
            [0,1,0,0],
            [-1*(math.sin(a)),0,math.cos(a),0],
            [0,0,0,1]
        ]

        a = rotate[2]
        rotation_matrix_z = [
            [math.cos(a),-1*(math.sin(a)),0,0],
            [math.sin(a),math.cos(a),0,0],
            [0,0,1,0],
            [0,0,0,1]
        ]

        primera = multMatrices(rotation_matrix_z,rotation_matrix_y)
        rotation_matrix = multMatrices(primera,rotation_matrix_x)
        
        segunda = multMatrices(rotation_matrix,scale_matrix)
        self.Model = multMatrices(translate_matrix,segunda)

    def lookAt(self, eye, center, up):
        z = norm(sub(eye, center))
        x = norm(cross(up,z))
        y = norm(cross(z,x))
        self.loadViewMatrix(x, y, z, center)
        self.loadProyectionMatrix(1/magnitud(sub(eye,center)))

    def loadViewMatrix(self, x, y, z, center):
        M = [
            [x.x,x.y,x.z,0],
            [y.x,y.y,y.z,0],
            [z.x,z.y,z.z,0],
            [0,0,0,1]
        ]
        O = [
            [1,0,0,-1*center.x],
            [0,1,0,-1*center.y],
            [0,0,1,-1*center.z],
            [0,0,0,1]
        ]
        self.View = multMatrices(M,O)
    
    def loadProyectionMatrix(self, coeff):
        self.Proyection = [
            [1,0,0,0],
            [0,1,0,0],
            [0,0,1,0],
            [0,0,coeff,1]
        ]
    
    def loadViewportMatrix(self, x, y):
        self.Viewport = [
            [self.width/2,0,0,x+self.width/2],
            [0,self.height/2,0,y+self.height/2],
            [0,0,128,128],
            [0,0,0,1]
        ]
    
    #Lee y renderiza archivos de textura
    def glLoadTexture(self, file_name, translate=(0, 0), scale=(1, 1)):
        model = ObjReader(file_name)
        model.readLines()

        for face in model.faces:
            vertices_ctr = len(face)
            if vertices_ctr == 3:

                tv1 = face[0][1] - 1
                tv2 = face[1][1] - 1
                tv3 = face[2][1] - 1

                tvA = V2(*model.tex_coords[tv1])
                tvB = V2(*model.tex_coords[tv2])
                tvC = V2(*model.tex_coords[tv3])
                
                tvAx, tvAy = tvA.x,tvA.y
                tvBx, tvBy = tvB.x,tvB.y
                tvCx, tvCy = tvC.x,tvC.y
                
                tvAx = (tvAx * 2) - 1
                tvAy = (tvAy * 2) - 1
                tvBx = (tvBx * 2) - 1
                tvBy = (tvBy * 2) - 1
                tvCx = (tvCx * 2) - 1
                tvCy = (tvCy * 2) - 1
                
                self.glLine(tvAx, tvAy,tvBx, tvBy)
                self.glLine(tvBx, tvBy,tvCx, tvCy)
                self.glLine(tvCx, tvCy,tvAx, tvAy)


    def glWrite(self, file_name):
        bmp_file = open(file_name, 'wb')

        ##Header
        bmp_file.write(char('B'))
        bmp_file.write(char('M'))
        bmp_file.write(dword(14 + 40 + self.width * self.height))
        bmp_file.write(dword(0))
        bmp_file.write(dword(14 + 40))
        
        #image header 
        bmp_file.write(dword(40))
        bmp_file.write(dword(self.width))
        bmp_file.write(dword(self.height))
        bmp_file.write(word(1))
        bmp_file.write(word(24))
        bmp_file.write(dword(0))
        bmp_file.write(dword(self.width * self.height * 3))
        bmp_file.write(dword(0))
        bmp_file.write(dword(0))
        bmp_file.write(dword(0))
        bmp_file.write(dword(0))

        for x in range(self.height):
            for y in range(self.width):
                self.framebuffer[x][y]
                bmp_file.write(self.framebuffer[x][y])
            
        bmp_file.close()
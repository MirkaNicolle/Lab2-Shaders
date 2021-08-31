#Codigo ayuda: https://github.com/churly92/Engine3D/blob/main/gl.py
#Repositorio perteneciente a Prof. Carlos Alonso

#Mirka Monzon 18139
#Lab2: Shaders

from gl import *
from textura import Texture

bmp = Bitmap(1000, 1000)

def glInit():
    return bmp


if __name__ == '__main__':
    '''Main Program'''

    #Inicializa obj
    bmp = glInit()

    bmp.glCreateWindow(1000, 1000)

    #Cambia todos los pixeles de un color
    bmp.glClear()

    #Set pixel Colors
    bmp.glColor(1, 1, 1)

    bmp.lookAt(V3(-0.2,0,5),V3(0,0,0),norm(V3(0,1,0)))
    bmp.loadViewportMatrix(0, 0)
    bmp.glLoadObjModel("model.obj", translate=(-1.0,-0.9,0), scale=(0.04,0.04,0.04), rotate=(0,0.2,0))
    
    #Output BMP
    bmp.glWrite("phong.bmp")
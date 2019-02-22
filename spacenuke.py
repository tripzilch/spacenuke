import pygame, sys, math, os
import numpy as np
import moderngl
#import ctypes
#from pygame.locals import *

def to_value(ar):
    if ar.ndim == 2:
        return [tuple(x) for x in ar]
    else:
        return tuple(ar)

SIZE = np.array([960.0, 480.0])
ASPECT = SIZE / SIZE[1]
HSIZE = SIZE / 2.0
QUAD = np.array([(1.0, -1.0), (1.0, 1.0), (-1.0, -1.0), (-1.0, 1.0)]) * ASPECT

class Control2DQuad:
    def __init__(self, prog_var, mid=np.array([0.0, 0.0]), zoom=1.0):
        self.var = prog_var
        self.mid = mid
        self.zoom = zoom
        self.update()

    def extent(self):
        return QUAD * self.zoom + self.mid   

    def coord(self, pos):
        return (pos / HSIZE[1] - ASPECT) * self.zoom + self.mid

    def update(self):        
        self.var.value = to_value(self.extent())        
        
    def on_drag(self, dmouse, amount):
        self.mid += dmouse  * (amount * self.zoom / HSIZE[1])
        self.update()

    def on_zoom(self, pos, zoom_dir, amount, exp=0.85):
        pos = self.coord(pos)
        factor = exp ** (zoom_dir * amount)
        self.zoom *= factor
        self.mid -= (self.mid - pos) * (factor - 1)
        self.update()
        #print(factor, Zzoom, Zmid)

class Control2DPoint(Control2DQuad):
    def update(self):
        self.var.value = to_value(self.mid)

    def on_zoom(self, pos, zoom_dir, amount, exp=0.85):
        factor = exp ** (zoom_dir * amount)
        self.zoom *= factor
        self.update()

class Control2DMidZoom(Control2DPoint):
    def update(self):
        self.var[0].value = to_value(self.mid)
        self.var[1].value = self.zoom

if __name__ == '__main__':
    os.environ['SDL_VIDEO_WINDOW_POS'] = "700,100"
    fps = 30
    
    pygame.init()
    window = pygame.display.set_mode(to_value(SIZE.astype(int)), 
        pygame.OPENGL | pygame.DOUBLEBUF)
    ctx = moderngl.create_context()

    prog = ctx.program(
        vertex_shader=open('julia.vert.glsl').read(),
        fragment_shader=open('julia.frag.glsl').read()
    )

    Zpos = Control2DQuad(prog['Zextent'], mid=np.array([0.0, 0.0]), zoom=2.0)
    C = Control2DPoint(prog['C'], 
        mid=np.array([-0.512511498387847167, 0.521295573094847167]), zoom=2.0)
    Trap = Control2DMidZoom((prog['trap_origin'], prog['trap_zoom']), 
        mid=np.array([-1.0, 0.0]), zoom=6.0)

    pmin_iter = prog['min_iter']    
    min_iter = 1.0
    pmin_iter.value = min_iter
    
    vertices = np.array([-1.0, -1.0, -1.0, 1.0, 1.0, -1.0, 1.0, 1.0])
    
    vert_buf = ctx.buffer(vertices.astype('f4').tobytes())
    vert_ar = ctx.simple_vertex_array(prog, vert_buf, 'in_vert')
    
    frame_num = 0
    clock = pygame.time.Clock()
    drag = False
    drag_start = np.array([0, 0])
    cur_ctl = Zpos
    while True:
        zoom_dir = 0
        for event in pygame.event.get():
            # print(event)
            if event.type == pygame.QUIT:
                sys.exit(0)
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                sys.exit(0)
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_z:
                cur_ctl = Zpos
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_x:
                cur_ctl = Trap
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_c:
                cur_ctl = C
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_s:
                pass # save
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                pass # reload
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                drag = True
                drag_start = np.array(event.pos, dtype=float)
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                drag = False
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 4:
                zoom_dir = 1
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 5:                
                zoom_dir = -1

        keys = pygame.key.get_pressed()
        mouse = np.array(pygame.mouse.get_pos(), dtype=float)
        dmouse = np.array(pygame.mouse.get_rel(), dtype=float)

        amount = 1.0
        if keys[pygame.K_RSHIFT]: amount *= 0.1
        if keys[pygame.K_RCTRL]: amount *= 0.01

        if drag:
            cur_ctl.on_drag(dmouse, amount)
        
        if zoom_dir != 0:
            cur_ctl.on_zoom(mouse, zoom_dir, amount)

        vert_ar.render(moderngl.TRIANGLE_STRIP)
        pygame.display.flip()
        clock.tick(fps)
        frame_num += 1

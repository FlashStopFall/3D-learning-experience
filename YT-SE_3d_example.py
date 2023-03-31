import pygame, sys, math, random, os

def rotate2d(pos, rad): x,y=pos; s,c = math.sin(rad),math.cos(rad); return x*c-y*s,y*c+x*s

class Cam:
    def __init__(self, pos=(0,0,0),rot=(0,0)):
        self.pos = list(pos)
        self.rot = list(rot)

    def events(self, event):
        if event.type == pygame.MOUSEMOTION:
            x, y = event.rel; x/=200; y/=200
            if (self.rot[0] <= 1.571 and y > 0) or (self.rot[0] >= -1.571 and y < 0):
                self.rot[0]+=y
            self.rot[1]+=x

    def update(self, dt, key):
        s = 0.25#dt*10

        if key[pygame.K_LSHIFT]: self.pos[1]+=s
        if key[pygame.K_SPACE]: self.pos[1]-=s

        x,y = s*math.sin(self.rot[1]),s*math.cos(self.rot[1])
        x,y = x/2,y/2
        if key[pygame.K_w]: self.pos[0]+=x; self.pos[2]+=y
        if key[pygame.K_s]: self.pos[0]-=x; self.pos[2]-=y
        if key[pygame.K_a]: self.pos[0]-=y; self.pos[2]+=x
        if key[pygame.K_d]: self.pos[0]+=y; self.pos[2]-=x
        if key[pygame.K_r]: self.pos[0]=0; self.pos[1]=0;\
                                         self.pos[2]=-5; self.rot[0]=0; self.rot[1]=0


class Cube:
    faces = (0,1,2,3),(4,5,6,7),(0,1,5,4),(2,3,7,6),(0,3,7,4),(1,2,6,5)
    colors = (255,0,0),(255,128,0),(255,255,0),(255,255,255),(0,0,255),(0,255,0)
    def __init__(self,pos=(0,0,0),color=None,v0=(-1,-1,-1),v1=(1,-1,-1),v2=(1,1,-1),v3=(-1,1,-1),v4=(-1,-1,1),v5=(1,-1,1),v6=(1,1,1),v7=(-1,1,1)):
        if color != None:
            if len(color) == 3 or len(color) == 4:
                self.colors = tuple((color for i in range(6)))
            if len(color) == 6:
                self.colors = color
        self.vertices = (v0,v1,v2,v3,v4,v5,v6,v7)
        x,y,z = pos
        self.verts = [(x+X/2,y+Y/2,z+Z/2) for X,Y,Z in self.vertices]

def update_fps():
    frames = str(int(clock.get_fps()))
    fps_text = font.render(frames, 1, pygame.Color("green"))
    return fps_text

pygame.init()
font = pygame.font.SysFont("Arial", 18)
fps = 0 # = 0 is unlimited
w,h = 640,480; cx,cy = w//2, h//2
#w,h = 1920,1080; cx,cy = w//2, h//2
screen = pygame.display.set_mode((w,h), pygame.RESIZABLE)
#screen = pygame.display.set_mode((0,0), pygame.FULLSCREEN)
clock = pygame.time.Clock()
cam = Cam((0,0,-5))
pygame.event.get(); pygame.mouse.get_rel()
pygame.mouse.set_visible(0); pygame.event.set_grab(1)
occupied = []

cube1 = Cube((0,0,0))
cube2 = Cube((0,0,2))
objects = [cube1, cube2]
focus = 0; opposite = 1; freeze = False

while True:
    dt = clock.tick(fps)/1000
    cx,cy = pygame.display.get_window_size(); cx,cy = cx//2,cy//2

    for event in pygame.event.get():
        if event.type == pygame.QUIT: pygame.quit(); sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE: pygame.quit(); sys.exit()
            if event.key == pygame.K_TAB:
                pygame.mouse.set_visible(opposite); pygame.event.set_grab(focus)
                if freeze == False:
                    focus = 1; opposite = 0; freeze = True
                else:
                    focus = 0; opposite = 1; freeze = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            pygame.mouse.set_visible(opposite); pygame.event.set_grab(focus)
            focus = 0; opposite = 1; freeze = False
                    
        if freeze == False:
            cam.events(event)

    screen.fill((130, 130, 130))

    face_list = []; face_color = []; depth = []

    for obj in objects:

        vert_list = []; screen_coords = []
        for x,y,z in obj.verts:
            x-= cam.pos[0]; y-=cam.pos[1];z-=cam.pos[2]
            x,z = rotate2d((x,z),cam.rot[1])
            y,z = rotate2d((y,z),cam.rot[0])
            vert_list += [(x,y,z)]

            f = 200/z
            x,y = x*f,y*f
            screen_coords+=[(cx+int(x),cy+int(y))]

        for f in range(len(obj.faces)):
            face = obj.faces[f]

            on_screen = False
            for i in face:
                x,y = screen_coords[i]
                if vert_list[i][2]>0 and x>0 and x<w and y>0 and y<h: on_screen = True; break

            # clip geometry at near plane
            if on_screen:
                near = 0.01
                for i in face:
                    if vert_list[i][2]<0:
                        x, y, z = vert_list[i]
                        nearscale = 200/near
                        x,y = x*nearscale,y*nearscale
                        screen_coords[i] = (cx+int(x),cy+int(y))
            
            if on_screen:
                coords = [screen_coords[i] for i in face]
                face_list += [coords]
                face_color += [obj.colors[f]]
                depth += [sum(sum(vert_list[j][i]**2 for i in range(3)) for j in face) / len(face)]

    order = sorted(range(len(face_list)),key=lambda i:depth[i],reverse=1)

    for i in order:
        try: pygame.draw.polygon(screen,face_color[i],face_list[i])
        except: pass

    screen.blit(update_fps(), (10,0))
    pygame.draw.line(screen, (200, 200, 200), (cx-10, cy), (cx+10, cy), width=3)
    pygame.draw.line(screen, (200, 200, 200), (cx, cy-10), (cx, cy+10), width=3)

    if freeze == False:
        key = pygame.key.get_pressed()
        pygame.display.flip()
        cam.update(dt,key)

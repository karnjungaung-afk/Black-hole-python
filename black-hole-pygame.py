import pygame, sys, math, random
import numpy as np

# ---------------- CONFIG ----------------
WIDTH, HEIGHT = 1600, 1000
FPS = 60
BLACK = (0,0,0)
WHITE = (255,255,255)

N_DISK = 6000
N_STARS = 2000
N_PARTICLES = 3000
R_S = 1.5  # Schwarzschild radius

# ---------------- FUNCTIONS ----------------
def rotate_x(y,z,angle):
    c,s = math.cos(angle), math.sin(angle)
    return y*c - z*s, y*s + z*c

def rotate_y(x,z,angle):
    c,s = math.cos(angle), math.sin(angle)
    return x*c + z*s, -x*s + z*c

def project_point(x,y,z,fov,viewer_distance):
    factor = fov / (viewer_distance + z)
    x_proj = x*factor + WIDTH//2
    y_proj = -y*factor + HEIGHT//2
    return int(x_proj), int(y_proj)

def lens_distortion(x,y,strength=1.5):
    cx,cy = WIDTH//2, HEIGHT//2
    dx,dy = x-cx, y-cy
    r = math.sqrt(dx*dx + dy*dy)
    if r==0: return x,y
    factor = 1 + strength*R_S/(r*0.03 + 0.01)
    return int(cx + dx*factor), int(cy + dy*factor)

# ---------------- CREATE OBJECTS ----------------
def create_disk(inner_r=2, outer_r=7, n=N_DISK):
    pts=[]
    for _ in range(n):
        r = math.sqrt(random.uniform(inner_r**2, outer_r**2))
        theta = random.uniform(0,2*math.pi)
        x,y,z = r*math.cos(theta), r*math.sin(theta), random.uniform(-0.15,0.15)
        brightness = max(0.2,1-(r/outer_r))
        color = (int(255*brightness), int(140*brightness), int(70*brightness))
        pts.append([x,y,z,color])
    return pts

def create_stars(n=N_STARS,R=150):
    pts=[]
    for _ in range(n):
        theta = random.uniform(0,2*math.pi)
        phi = math.acos(1-2*random.random())
        x = R*math.sin(phi)*math.cos(theta)
        y = R*math.sin(phi)*math.sin(theta)
        z = R*math.cos(phi)
        pts.append([x,y,z])
    return pts

def create_particles(n=N_PARTICLES,radius=6):
    pts=[]
    for _ in range(n):
        r = random.uniform(radius,radius+5)
        theta = random.uniform(0,2*math.pi)
        x,y = r*math.cos(theta), r*math.sin(theta)
        z = random.uniform(-0.6,0.6)
        pts.append([x,y,z])
    return pts

# ---------------- MAIN ----------------
def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Black Hole 3D Ultra Realistic Simulation")
    clock = pygame.time.Clock()

    disk = create_disk()
    stars = create_stars()
    particles = create_particles()

    angle_x,angle_y = 0,0
    fov = 800
    viewer_distance = 14
    t0 = pygame.time.get_ticks()/1000

    running = True
    while running:
        dt = clock.tick(FPS)/1000
        t = pygame.time.get_ticks()/1000 - t0
        screen.fill(BLACK)

        for event in pygame.event.get():
            if event.type==pygame.QUIT:
                running=False

        # -------- Camera Controls --------
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a]: angle_y -= 0.03
        if keys[pygame.K_d]: angle_y += 0.03
        if keys[pygame.K_w]: angle_x -= 0.03
        if keys[pygame.K_s]: angle_x += 0.03
        if keys[pygame.K_e]: break
        if pygame.mouse.get_pressed()[0]:
            mx,my = pygame.mouse.get_rel()
            angle_y += mx*0.005
            angle_x += my*0.005
        else:
            pygame.mouse.get_rel()

        # -------- Stars --------
        for sx,sy,sz in stars:
            x,y = sx,sy
            y,z = rotate_x(y,sz,angle_x)
            x,z = rotate_y(x,z,angle_y)
            if z>-viewer_distance+1:
                px,py = project_point(x,y,z,fov,viewer_distance)
                px,py = lens_distortion(px,py,1.5)
                pygame.draw.circle(screen,WHITE,(px,py),1)

        # -------- Disk Spiral + Particles --------
        disk_rotation = t*2*math.pi/10
        for dx,dy,dz,color in disk:
            x,y,z = dx,dy,dz
            angle_spiral = math.atan2(y,x)+disk_rotation
            radius = math.sqrt(x*x+y*y)
            x,y = radius*math.cos(angle_spiral), radius*math.sin(angle_spiral)
            y,z = rotate_x(y,z,angle_x)
            x,z = rotate_y(x,z,angle_y)
            if z>-viewer_distance+1:
                px,py = project_point(x,y,z,fov,viewer_distance)
                px,py = lens_distortion(px,py,1.5)
                pygame.draw.circle(screen,color,(px,py),2)

        for p in particles:
            x,y,z = p
            angle_spiral = math.atan2(y,x)+disk_rotation
            radius = math.sqrt(x*x+y*y)
            x,y = radius*math.cos(angle_spiral), radius*math.sin(angle_spiral)
            y,z = rotate_x(y,z,angle_x)
            x,z = rotate_y(x,z,angle_y)
            if z>-viewer_distance+1:
                px,py = project_point(x,y,z,fov,viewer_distance)
                px,py = lens_distortion(px,py,1.5)
                pygame.draw.circle(screen,(255,220,150),(px,py),1)

        # -------- Photon Ring --------
        for i in range(1200):
            theta = 2*math.pi*i/1200
            r = 1.5
            x,y,z = r*math.cos(theta), r*math.sin(theta),0
            y,z = rotate_x(y,z,angle_x)
            x,z = rotate_y(x,z,angle_y)
            if z>-viewer_distance+1:
                px,py = project_point(x,y,z,fov,viewer_distance)
                px,py = lens_distortion(px,py,1.5)
                brightness = 200+55*math.sin(t*5+i)
                pygame.draw.circle(screen,(brightness,brightness,255),(px,py),1)

        # -------- Event Horizon Glow + Bloom --------
        glow_radius = 25 + 10*abs(math.sin(t*3))
        for r in range(15,int(glow_radius)+15):
            val = max(0,180-(r-15)*10)
            pygame.draw.circle(screen,(val,val,val),(WIDTH//2,HEIGHT//2),int(r))

        # -------- Black Hole Center --------
        pygame.draw.circle(screen,BLACK,(WIDTH//2,HEIGHT//2),25)

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__=="__main__":
    main()

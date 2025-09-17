import numpy as np
import matplotlib.pyplot as plt

# ---------- พารามิเตอร์หลัก ----------
rs = 1.0                 # รัศมี (สเกล) ของขอบฟ้าเหตุการณ์ (event horizon)
disk_r_in = 1.5 * rs     # รัศมีในสุดของดิสก์ (ใกล้ ๆ ขอบฟ้า)
disk_r_out = 6.0 * rs    # รัศมีนอกสุดของดิสก์
disk_tilt_deg = 25       # มุมเอียงดิสก์ (องศา)
n_sphere = 200           # ความละเอียดทรงกลม
n_disk = 800             # จำนวนจุดในดิสก์
ring_r = 1.5 * rs        # รัศมีวงโฟตอนคร่าว ๆ (photon sphere ~ 1.5 r_s)
ring_thickness = 0.03    # ความหนาวงโฟตอน

# ---------- ฟังก์ชันช่วย ----------
def rot_x(points, deg):
    rad = np.deg2rad(deg)
    Rx = np.array([[1, 0, 0],
                   [0, np.cos(rad), -np.sin(rad)],
                   [0, np.sin(rad),  np.cos(rad)]])
    return points @ Rx.T

def set_equal_aspect_3d(ax, lim=6):
    ax.set_xlim(-lim, lim)
    ax.set_ylim(-lim, lim)
    ax.set_zlim(-lim, lim)
    ax.set_box_aspect([1,1,1])

# ---------- สร้างรูป ----------
fig = plt.figure(figsize=(8, 8))
ax = fig.add_subplot(projection='3d')
ax.set_axis_off()

# ---------- 1) ขอบฟ้าเหตุการณ์ (ทรงกลมสีดำด้าน) ----------
u = np.linspace(0, 2*np.pi, n_sphere)
v = np.linspace(0, np.pi, n_sphere)
x = rs * np.outer(np.cos(u), np.sin(v))
y = rs * np.outer(np.sin(u), np.sin(v))
z = rs * np.outer(np.ones_like(u), np.cos(v))
# ใช้สีดำทึบสำหรับ "ความว่างเปล่า" ของหลุมดำ
ax.plot_surface(x, y, z, linewidth=0, antialiased=False, color='black', shade=False)

# ---------- 2) ดิสก์สะสมมวล (annulus) ----------
r = np.sqrt(np.random.uniform(disk_r_in**2, disk_r_out**2, n_disk))
theta = np.random.uniform(0, 2*np.pi, n_disk)
xd = r * np.cos(theta)
yd = r * np.sin(theta)
zd = np.zeros_like(xd)

# เอียงดิสก์
pts = np.vstack([xd, yd, zd]).T
pts = rot_x(pts, disk_tilt_deg)
xd, yd, zd = pts[:,0], pts[:,1], pts[:,2]

# ความสว่างแบบง่าย: สว่างใกล้ในและมีเอฟเฟกต์ Doppler beaming คร่าว ๆ
# (ค่าประมาณสวยๆ ไม่ใช่ฟิสิกส์เป๊ะ)
# ความสว่าง ~ 1 / r^1.2
r_planar = np.sqrt(xd**2 + yd**2)
brightness = 1 / (r_planar**1.2)
brightness = (brightness - brightness.min()) / (brightness.max() - brightness.min() + 1e-9)

# เพิ่ม beaming โดยดูทิศทางการหมุน (ให้ดิสก์หมุน แกน z' ขึ้น):
phi = np.arctan2(yd, xd)
beaming = 0.5 + 0.5*np.cos(phi)  # คร่าวๆ: ด้านเข้าหาผู้สังเกตสว่างกว่า
color_vals = np.clip(0.35*brightness + 0.65*beaming, 0, 1)

# แมปสีโทนอุ่น: ใช้กราเดียนท์เอง (แดง->ส้ม->เหลือง->ขาว)
def warm_map(t):
    # t in [0,1]
    r = np.clip(0.3 + 0.9*t, 0, 1)
    g = np.clip(0.15 + 0.8*t, 0, 1)
    b = np.clip(0.05 + 0.2*t, 0, 1)
    return np.vstack([r, g, b]).T

colors = warm_map(color_vals)

# วาดดิสก์เป็นจุดหนาแน่น
ax.scatter(xd, yd, zd, s=1.2, c=colors, alpha=0.95, depthshade=False, linewidths=0)

# ---------- 3) วงโฟตอน (ring) ----------
phi_ring = np.linspace(0, 2*np.pi, 1000)
xr = ring_r * np.cos(phi_ring)
yr = ring_r * np.sin(phi_ring)
zr = np.zeros_like(xr)
ring_pts = np.vstack([xr, yr, zr]).T
ring_pts = rot_x(ring_pts, disk_tilt_deg)
xr, yr, zr = ring_pts[:,0], ring_pts[:,1], ring_pts[:,2]
ax.plot(xr, yr, zr, linewidth=3.5, color='white', alpha=0.85)

# เพิ่มความหนาวงด้วยการซ้อนหลายเส้น
for k in np.linspace(-ring_thickness, ring_thickness, 5):
    rr = ring_r + k
    xr = rr * np.cos(phi_ring)
    yr = rr * np.sin(phi_ring)
    zr = np.zeros_like(xr)
    ring_pts = np.vstack([xr, yr, zr]).T
    ring_pts = rot_x(ring_pts, disk_tilt_deg)
    xr, yr, zr = ring_pts[:,0], ring_pts[:,1], ring_pts[:,2]
    ax.plot(xr, yr, zr, linewidth=1.0, color='white', alpha=0.25)

# ---------- 4) ฉากดวงดาว ----------
n_stars = 800
R_bg = 20
theta_s = np.random.uniform(0, 2*np.pi, n_stars)
phi_s = np.arccos(1 - 2*np.random.rand(n_stars))  # กระจายทั่วทรงกลม
xs = R_bg * np.sin(phi_s) * np.cos(theta_s)
ys = R_bg * np.sin(phi_s) * np.sin(theta_s)
zs = R_bg * np.cos(phi_s)
ax.scatter(xs, ys, zs, s=np.random.uniform(1, 4, n_stars), c='white', alpha=0.6)

# ---------- มุมมองกล้อง ----------
ax.view_init(elev=22, azim=40)
set_equal_aspect_3d(ax, lim=7)

# ---------- ใส่คำอธิบาย ----------
txt = (r"Black Hole (not to scale)" "\n"
       r"Event horizon $r_s$ in black, "
       r"photon ring $\sim1.5\,r_s$, "
       r"accretion disk with simple beaming.")
ax.text2D(0.02, 0.98, txt, transform=ax.transAxes, fontsize=9, va='top', color='white',
          bbox=dict(facecolor='black', alpha=0.35, boxstyle='round,pad=0.3'))

fig.tight_layout()
plt.show()

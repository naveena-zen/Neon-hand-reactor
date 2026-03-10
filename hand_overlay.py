import cv2
import numpy as np
from mediapipe.tasks.python.vision import hand_landmarker
from mediapipe.tasks.python.vision.core import image as mp_image
from mediapipe.tasks.python.core.base_options import BaseOptions
import mediapipe as mp
import math
import time
import random

MODEL_PATH = "hand_landmarker.task"


# ─────────────────────────────────────────────
#  🔴 LASER BEAM between two points
# ─────────────────────────────────────────────
def draw_laser_beam(image, p1, p2):
    laser_outer = (0, 0, 255)
    laser_mid   = (0, 100, 255)
    laser_core  = (255, 255, 255)

    overlay = image.copy()
    cv2.line(overlay, p1, p2, laser_outer, 14, cv2.LINE_AA)
    cv2.addWeighted(overlay, 0.2, image, 0.8, 0, image)

    overlay2 = image.copy()
    cv2.line(overlay2, p1, p2, laser_mid, 8, cv2.LINE_AA)
    cv2.addWeighted(overlay2, 0.3, image, 0.7, 0, image)

    cv2.line(image, p1, p2, laser_core, 2, cv2.LINE_AA)


# ─────────────────────────────────────────────
#  🌟 LASER STRINGS (no distance limit)
# ─────────────────────────────────────────────
def draw_finger_laser_strings(image, hand1, hand2):
    h, w, _ = image.shape

    neon_glow = (255, 255, 100)
    neon_mid  = (255, 255, 180)
    neon_core = (255, 255, 255)

    tip_indices = [4, 8, 12, 16, 20]
    pts1 = [(int(hand1[i].x * w), int(hand1[i].y * h)) for i in tip_indices]
    pts2 = [(int(hand2[i].x * w), int(hand2[i].y * h)) for i in tip_indices]

    for p1, p2 in zip(pts1, pts2):
        draw_laser_beam(image, p1, p2)

        mx = int((p1[0] + p2[0]) / 2)
        my = int((p1[1] + p2[1]) / 2)
        dist   = int(math.hypot(p2[0] - p1[0], p2[1] - p1[1]))
        radius = max(6, int(dist * 0.06))

        overlay3 = image.copy()
        cv2.circle(overlay3, (mx, my), radius + 8, neon_glow, -1)
        cv2.addWeighted(overlay3, 0.18, image, 0.82, 0, image)

        overlay4 = image.copy()
        cv2.circle(overlay4, (mx, my), radius, neon_mid, -1)
        cv2.addWeighted(overlay4, 0.25, image, 0.75, 0, image)

        cv2.circle(image, (mx, my), max(5, radius // 2), neon_core, 2, cv2.LINE_AA)
        cv2.circle(image, (mx, my), radius,              neon_core, 1, cv2.LINE_AA)


# ─────────────────────────────────────────────
#  🌀 VORTEX PORTAL between both palms
# ─────────────────────────────────────────────
def draw_vortex_portal(image, hand1, hand2, angle):
    h, w, _ = image.shape

    p1 = hand1[9]
    p2 = hand2[9]
    cx = int((p1.x + p2.x) / 2 * w)
    cy = int((p1.y + p2.y) / 2 * h)

    dist   = math.hypot((p2.x - p1.x) * w, (p2.y - p1.y) * h)
    base_r = int(dist * 0.25)
    base_r = max(30, min(base_r, 180))

    colors = [
        (255,   0, 180),
        (200,   0, 255),
        (100,  50, 255),
        ( 50, 200, 255),
        (255, 255, 255),
    ]

    for i, color in enumerate(colors):
        r = base_r - i * (base_r // (len(colors) + 1))
        if r < 4:
            continue
        spin = angle + i * 36
        axes  = (r, max(4, int(r * 0.35)))
        overlay = image.copy()
        cv2.ellipse(overlay, (cx, cy), axes, spin, 0, 300,
                    color, 2, cv2.LINE_AA)
        cv2.addWeighted(overlay, 0.6, image, 0.4, 0, image)

    for r in range(base_r // 3, 4, -6):
        ov = image.copy()
        cv2.circle(ov, (cx, cy), r, (180, 80, 255), -1)
        cv2.addWeighted(ov, 0.04, image, 0.96, 0, image)

    cv2.circle(image, (cx, cy), 8,  (255, 255, 255), -1, cv2.LINE_AA)
    cv2.circle(image, (cx, cy), 14, (200,  80, 255),  1, cv2.LINE_AA)


# ─────────────────────────────────────────────
#  💥 EXPLOSION PARTICLES
# ─────────────────────────────────────────────
class Particle:
    def __init__(self, x, y):
        angle  = random.uniform(0, 2 * math.pi)
        speed  = random.uniform(4, 18)
        self.x = float(x)
        self.y = float(y)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.life   = 1.0
        self.decay  = random.uniform(0.03, 0.07)
        self.radius = random.randint(3, 9)
        self.color  = random.choice([
            (255, 255, 255),
            (255, 255,   0),
            (255, 180,   0),
            (255,  80,   0),
            (200,   0, 255),
        ])

    def update(self):
        self.x  += self.vx
        self.y  += self.vy
        self.vy += 0.4
        self.vx *= 0.96
        self.life -= self.decay

    def draw(self, image):
        if self.life <= 0:
            return
        alpha  = self.life
        radius = max(1, int(self.radius * self.life))
        cx, cy = int(self.x), int(self.y)
        overlay = image.copy()
        cv2.circle(overlay, (cx, cy), radius + 3, self.color, -1)
        cv2.addWeighted(overlay, alpha * 0.25, image, 1 - alpha * 0.25, 0, image)
        cv2.circle(image, (cx, cy), radius, self.color, -1, cv2.LINE_AA)


def spawn_explosion(particles, cx, cy, count=150):
    for _ in range(count):
        particles.append(Particle(cx, cy))


def update_and_draw_particles(image, particles):
    alive = []
    for p in particles:
        p.update()
        p.draw(image)
        if p.life > 0:
            alive.append(p)
    particles[:] = alive


# ─────────────────────────────────────────────
#  🖐  Hand Landmarker setup
# ─────────────────────────────────────────────
options = hand_landmarker.HandLandmarkerOptions(
    base_options=BaseOptions(model_asset_path=MODEL_PATH),
    num_hands=2,
    min_hand_detection_confidence=0.5,   # lowered for better detection at distance
    min_hand_presence_confidence=0.5,
    min_tracking_confidence=0.5,
)
landmarker = hand_landmarker.HandLandmarker.create_from_options(options)

tip_history        = []
particles          = []
vortex_angle       = 0.0
collision_cooldown = 0.0

COLLISION_DIST_PX  = 90

cap = cv2.VideoCapture(0)

# ── WIDER RESOLUTION for more detection range ──
cap.set(cv2.CAP_PROP_FRAME_WIDTH,  1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
cap.set(cv2.CAP_PROP_FPS, 30)

actual_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
actual_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
print(f"Camera resolution: {actual_w}x{actual_h}")
print("Press ESC to quit.")

prev_time = time.time()

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    now  = time.time()
    dt   = now - prev_time
    prev_time = now

    frame  = cv2.flip(frame, 1)
    rgb    = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    mp_img = mp_image.Image(image_format=mp_image.ImageFormat.SRGB, data=rgb)
    result = landmarker.detect(mp_img)

    h, w, _ = frame.shape
    vortex_angle = (vortex_angle + 3.5) % 360

    if result.hand_landmarks:

        # ── TWO HANDS only — no single-hand effects ──
        if len(result.hand_landmarks) == 2:
            hand0 = result.hand_landmarks[0]
            hand1 = result.hand_landmarks[1]

            if hand0[0].x * w < hand1[0].x * w:
                left_hand, right_hand = hand0, hand1
            else:
                left_hand, right_hand = hand1, hand0

            lw = (int(left_hand[0].x * w),  int(left_hand[0].y * h))
            rw = (int(right_hand[0].x * w), int(right_hand[0].y * h))
            wrist_dist = math.hypot(rw[0] - lw[0], rw[1] - lw[1])

            collision = wrist_dist < COLLISION_DIST_PX

            if collision:
                if collision_cooldown <= 0:
                    mx = (lw[0] + rw[0]) // 2
                    my = (lw[1] + rw[1]) // 2
                    spawn_explosion(particles, mx, my, count=150)
                    collision_cooldown = 0.6
                cv2.rectangle(frame, (0, 0), (w - 1, h - 1), (255, 255, 255), 6)

            else:
                # Temporal smoothing
                tip_indices = [4, 8, 12, 16, 20]
                left_tips   = [(left_hand[i].x,  left_hand[i].y)  for i in tip_indices]
                right_tips  = [(right_hand[i].x, right_hand[i].y) for i in tip_indices]
                tip_history.append((left_tips, right_tips))
                if len(tip_history) > 3:
                    tip_history.pop(0)

                n = len(tip_history)
                avg_left  = [(sum(t[0][i][0] for t in tip_history) / n,
                              sum(t[0][i][1] for t in tip_history) / n) for i in range(5)]
                avg_right = [(sum(t[1][i][0] for t in tip_history) / n,
                              sum(t[1][i][1] for t in tip_history) / n) for i in range(5)]

                class LM:
                    pass

                left_smoothed  = list(left_hand)
                right_smoothed = list(right_hand)
                for idx, (lx, ly) in zip(tip_indices, avg_left):
                    lm = LM(); lm.x = lx; lm.y = ly; lm.z = 0
                    left_smoothed[idx] = lm
                for idx, (rx, ry) in zip(tip_indices, avg_right):
                    lm = LM(); lm.x = rx; lm.y = ry; lm.z = 0
                    right_smoothed[idx] = lm

                draw_finger_laser_strings(frame, left_smoothed, right_smoothed)
                draw_vortex_portal(frame, left_hand, right_hand, vortex_angle)

    collision_cooldown = max(0.0, collision_cooldown - dt)
    update_and_draw_particles(frame, particles)

    cv2.imshow('⚡ Marvel Hand Powers', frame)
    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()
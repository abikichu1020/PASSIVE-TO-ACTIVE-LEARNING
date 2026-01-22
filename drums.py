import cv2 as cv
import mediapipe as mp
import pygame
import time
import numpy as np
from collections import deque
import os

# Initialize Pygame
pygame.init()
pygame.mixer.init()

# Load drum sounds
DRUM_SOUNDS = {
    "TOM": r"D:\\college\\abi kamu(don of kce) project\\Musics\\tom-0104-107508.mp3",
    "KICK": r"D:\\college\\abi kamu(don of kce) project\\Musics\\kick-drum-263837.mp3",
    "SNARE": r"D:\\college\\abi kamu(don of kce) project\\Musics\\tr808-snare-drum-241403.mp3",
    "HIHAT": r"D:\\college\\abi kamu(don of kce) project\\Musics\\hi-hat-6-231041.mp3",
    "JOKE": r"D:\college\abi kamu(don of kce) project\Musics\joke-drums.mp3"
}

# Cooldown trackers
hand_zone_cooldowns = {}
cooldown_duration = 0.1  # Faster repeated hits

# Webcam setup
cap = cv.VideoCapture(0)
cap.set(cv.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv.CAP_PROP_FRAME_HEIGHT, 720)
frame_width = int(cap.get(cv.CAP_PROP_FRAME_WIDTH))
frame_height = int(cap.get(cv.CAP_PROP_FRAME_HEIGHT))

# Drum layout
drum_zones = [
    {"name": "HIHAT", "x1": frame_width // 6 - 75, "y1": 150, "x2": frame_width // 6 + 75, "y2": 250, "hit_time": 0},
    {"name": "SNARE", "x1": frame_width * 4 // 6 - 75, "y1": 150, "x2": frame_width * 4 // 6 + 75, "y2": 250, "hit_time": 0},
    {"name": "TOM", "x1": frame_width // 4 - 75, "y1": 300, "x2": frame_width // 4 + 75, "y2": 400, "hit_time": 0},
    {"name": "JOKE", "x1": frame_width * 3 // 4 - 75, "y1": 300, "x2": frame_width * 3 // 4 + 75, "y2": 400, "hit_time": 0},
    {"name": "KICK", "x1": frame_width // 2 - 100, "y1": 450, "x2": frame_width // 2 + 100, "y2": 550, "hit_time": 0},
]

# Load PNG images
def load_png(path, size):
    img = cv.imread(path, cv.IMREAD_UNCHANGED)  # Load with alpha channel
    if img is None:
        print(f"Failed to load image at {path}")
        return None
    return cv.resize(img, size)

DRUM_IMAGES = {
    "HIHAT": load_png(r"D:\\college\\abi kamu(don of kce) project\\drum images\\hithat.png", (150, 100)),
    "SNARE": load_png(r"D:\\college\\abi kamu(don of kce) project\\drum images\\snare.png", (150, 100)),
    "TOM": load_png(r"D:\\college\\abi kamu(don of kce) project\\drum images\\tom.png", (150, 100)),
    "JOKE": load_png(r"D:\\college\\abi kamu(don of kce) project\\drum images\\joke.png", (150, 100)),
    "KICK": load_png(r"D:\\college\\abi kamu(don of kce) project\\drum images\\kick.png", (200, 100))
}

# Function to overlay transparent PNG
def overlay_png(bg, fg, x, y):
    h, w = fg.shape[:2]
    if y + h > bg.shape[0] or x + w > bg.shape[1]:
        return  # Avoid out-of-bound
    if fg.shape[2] == 4:
        alpha_fg = fg[:, :, 3] / 255.0
        alpha_bg = 1.0 - alpha_fg
        for c in range(3):
            bg[y:y+h, x:x+w, c] = (alpha_fg * fg[:, :, c] + alpha_bg * bg[y:y+h, x:x+w, c])

# Play sound
def play_sound(name):
    try:
        sound = pygame.mixer.Sound(DRUM_SOUNDS[name])
        sound.play()
    except Exception as e:
        print(f"Error playing {name}: {e}")

# MediaPipe setup
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)
mp_draw = mp.solutions.drawing_utils

# Track fingertip velocity
prev_coords = {}
velocity_window = 5

# Main loop
while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv.flip(frame, 1)
    rgb = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
    result = hands.process(rgb)

    # Draw drum zones with PNGs
    for zone in drum_zones:
        x1, y1 = zone["x1"], zone["y1"]
        w = zone["x2"] - zone["x1"]
        h = zone["y2"] - zone["y1"]
        img = DRUM_IMAGES.get(zone["name"])
        if img is not None:
            overlay_png(frame, img, x1, y1)

        # Flash border on hit
        if time.time() - zone["hit_time"] < 0.15:
            cv.rectangle(frame, (x1, y1), (zone["x2"], zone["y2"]), (255, 255, 255), 2)

        # Optional: label
        cv.putText(frame, zone["name"], (x1 + 10, y1 - 10),
                   cv.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

    # Hand detection
    if result.multi_hand_landmarks:
        for hand_landmarks, hand_info in zip(result.multi_hand_landmarks, result.multi_handedness):
            label = hand_info.classification[0].label  # "Left" or "Right"
            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            h, w, _ = frame.shape
            x = int(hand_landmarks.landmark[8].x * w)
            y = int(hand_landmarks.landmark[8].y * h)

            # Draw fingertip
            color = (0, 0, 255) if label == "Left" else (255, 0, 0)
            cv.circle(frame, (x, y), 10, color, -1)
            cv.putText(frame, f"{label}", (x + 20, y + 20), cv.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

            # Velocity
            if label not in prev_coords:
                prev_coords[label] = deque(maxlen=velocity_window)
            prev_coords[label].append(y)

            velocity = 0
            if len(prev_coords[label]) == velocity_window:
                velocity = prev_coords[label][-1] - prev_coords[label][0]
            cv.putText(frame, f"Vel: {velocity}", (x + 20, y), cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

            # Check for drum hit
            if velocity > 8:
                for zone in drum_zones:
                    margin = 10
                    if (zone["x1"] + margin <= x <= zone["x2"] - margin and
                        zone["y1"] + margin <= y <= zone["y2"] - margin):

                        last_hit = hand_zone_cooldowns.get(label, {}).get(zone["name"], 0)
                        if time.time() - last_hit > cooldown_duration:
                            play_sound(zone["name"])
                            zone['hit_time'] = time.time()

                            if label not in hand_zone_cooldowns:
                                hand_zone_cooldowns[label] = {}
                            hand_zone_cooldowns[label][zone["name"]] = time.time()
    # Show frame
    cv.imshow("AR Drum Kit - PNG Zone Mode", frame)
    if cv.waitKey(1) & 0xFF == ord('q'):
        break

# Cleanup
cap.release()
cv.destroyAllWindows()
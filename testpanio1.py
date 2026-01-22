import cv2 as cv
import mediapipe as mp
import pygame
import time
from collections import deque
import os

# Initialize Pygame
pygame.init()
pygame.mixer.init()

# Piano sound paths
PIANO_SOUNDS = {
    "C4": "D:\\college\\abi kamu(don of kce) project\\panio keys\\key01.mp3",
    "C#4": "D:\\college\\abi kamu(don of kce) project\\panio keys\\key02.mp3",
    "D4": "D:\\college\\abi kamu(don of kce) project\\panio keys\\key03.mp3",
    "D#4": "D:\\college\\abi kamu(don of kce) project\\panio keys\\key04.mp3",
    "E4": "D:\\college\\abi kamu(don of kce) project\\panio keys\\key05.mp3",
    "F4": "D:\\college\\abi kamu(don of kce) project\\panio keys\\key06.mp3",
    "F#4": "D:\\college\\abi kamu(don of kce) project\\panio keys\\key07.mp3",
    "G4": "D:\\college\\abi kamu(don of kce) project\\panio keys\\key08.mp3",
    "G#4": "D:\\college\\abi kamu(don of kce) project\\panio keys\\key09.mp3",
    "A4": "D:\\college\\abi kamu(don of kce) project\\panio keys\\key10.mp3",
    "A#4": "D:\\college\\abi kamu(don of kce) project\\panio keys\\key11.mp3",
    "B4": "D:\\college\\abi kamu(don of kce) project\\panio keys\\key12.mp3",
    "C5": "D:\\college\\abi kamu(don of kce) project\\panio keys\\key13.mp3",
    "C#5": "D:\\college\\abi kamu(don of kce) project\\panio keys\\key14.mp3",
    "D5": "D:\\college\\abi kamu(don of kce) project\\panio keys\\key15.mp3",
    "D#5": "D:\\college\\abi kamu(don of kce) project\\panio keys\\key16.mp3",
    "E5": "D:\\college\\abi kamu(don of kce) project\\panio keys\\key17.mp3",
    "F5": "D:\\college\\abi kamu(don of kce) project\\panio keys\\key18.mp3",
    "F#5": "D:\\college\\abi kamu(don of kce) project\\panio keys\\key19.mp3",
    "G5": "D:\\college\\abi kamu(don of kce) project\\panio keys\\key20.mp3",
    "G#5": "D:\\college\\abi kamu(don of kce) project\\panio keys\\key21.mp3",
    "A5": "D:\\college\\abi kamu(don of kce) project\\panio keys\\key22.mp3",
    "A#5": "D:\\college\\abi kamu(don of kce) project\\panio keys\\key23.mp3",
    "B5": "D:\\college\\abi kamu(don of kce) project\\panio keys\\key24.mp3",
}

# Cooldown trackers to prevent rapid, repeated hits
hand_zone_cooldowns = {}
cooldown_duration = 0.1

# Webcam setup
cap = cv.VideoCapture(0)
cap.set(cv.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv.CAP_PROP_FRAME_HEIGHT, 720)
frame_width = int(cap.get(cv.CAP_PROP_FRAME_WIDTH))
frame_height = int(cap.get(cv.CAP_PROP_FRAME_HEIGHT))

# Piano keys layout
white_key_width = 80
black_key_width = 40
black_key_height = 100
key_height = 180

# Center piano horizontally and vertically
start_x = (frame_width - 14 * white_key_width) // 2
base_y = (frame_height - key_height) // 2

# White keys (14 total: C4 → B5)
white_notes = ["C4","D4","E4","F4","G4","A4","B4","C5","D5","E5","F5","G5","A5","B5"]

piano_keys = []
for i, note in enumerate(white_notes):
    piano_keys.append({
        "name": note,
        "x1": start_x + i * white_key_width,
        "y1": base_y,
        "x2": start_x + (i+1) * white_key_width,
        "y2": base_y + key_height,
        "hit_time": 0,
        "color": (255,255,255)
    })

# Black keys with alignment relative to white keys
black_positions = {
    "C#4": 0.75, "D#4": 1.75,
    "F#4": 3.75, "G#4": 4.75, "A#4": 5.75,
    "C#5": 7.75, "D#5": 8.75,
    "F#5": 10.75, "G#5": 11.75, "A#5": 12.75
}

for note, pos in black_positions.items():
    x_center = start_x + int(pos * white_key_width)
    piano_keys.append({
        "name": note,
        "x1": x_center - black_key_width//2,
        "y1": base_y,
        "x2": x_center + black_key_width//2,
        "y2": base_y + black_key_height,
        "hit_time": 0,
        "color": (0,0,0)
    })

# Play sound
def play_sound(name):
    try:
        sound = pygame.mixer.Sound(PIANO_SOUNDS[name])
        sound.play()
    except Exception as e:
        print(f"Error playing {name}: {e}. Check file path.")

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

    # Draw piano keys
    for zone in piano_keys:
        color = zone.get("color", (255,255,255))
        if time.time() - zone["hit_time"] < 0.15:
            color = (200,200,200) if color==(255,255,255) else (50,50,50)

        cv.rectangle(frame, (zone["x1"], zone["y1"]), (zone["x2"], zone["y2"]), color, -1)
        cv.rectangle(frame, (zone["x1"], zone["y1"]), (zone["x2"], zone["y2"]), (100,100,100), 2)

        # Labels
        text_color = (0,0,0) if color==(255,255,255) or color==(200,200,200) else (255,255,255)
        text_y_offset = -10 if zone.get("color")==(0,0,0) else 40
        cv.putText(frame, zone["name"], (zone["x1"]+10, zone["y2"]-text_y_offset),
                   cv.FONT_HERSHEY_SIMPLEX, 0.6, text_color, 2)

    # Hand detection
    if result.multi_hand_landmarks:
        for hand_landmarks, hand_info in zip(result.multi_hand_landmarks, result.multi_handedness):
            label = hand_info.classification[0].label
            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            h, w, _ = frame.shape
            x = int(hand_landmarks.landmark[8].x * w)
            y = int(hand_landmarks.landmark[8].y * h)

            # Fingertip marker
            color = (0,0,255) if label=="Left" else (255,0,0)
            cv.circle(frame, (x,y), 10, color, -1)
            cv.putText(frame, f"{label}", (x+20,y+20), cv.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

            # Velocity check
            if label not in prev_coords:
                prev_coords[label] = deque(maxlen=velocity_window)
            prev_coords[label].append(y)

            velocity = 0
            if len(prev_coords[label]) == velocity_window:
                velocity = prev_coords[label][-1] - prev_coords[label][0]

            # Check for key hit
            if velocity > 8:
                for zone in piano_keys:
                    margin = 5
                    if (zone["x1"]+margin <= x <= zone["x2"]-margin and
                        zone["y1"]+margin <= y <= zone["y2"]-margin):

                        last_hit = hand_zone_cooldowns.get(label, {}).get(zone["name"], 0)
                        if time.time() - last_hit > cooldown_duration:
                            play_sound(zone["name"])
                            zone["hit_time"] = time.time()

                            if label not in hand_zone_cooldowns:
                                hand_zone_cooldowns[label] = {}
                            hand_zone_cooldowns[label][zone["name"]] = time.time()

    # Show frame
    cv.imshow("AR Piano", frame)
    if cv.waitKey(1) & 0xFF == ord('q'):
        break

# Cleanup
cap.release()
cv.destroyAllWindows()

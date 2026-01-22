import cv2
import numpy as np
import mediapipe as mp
import math
import time
from enum import Enum

# Import physics lessons (make sure lessons/ has __init__.py)
from lessons.newtons_laws import NewtonsLaws
from lessons.gravity_projectile import GravityProjectile
from lessons.waves_sound import WavesSound
from lessons.electromagnetic import Electromagnetic
from lessons.energy_conservation import EnergyConservation
from lessons.momentum_collisions import MomentumCollisions
from lessons.simple_harmonic_motion import SimpleHarmonicMotion
from lessons.optics_light import OpticsLight


class PhysicsConceptType(Enum):
    NEWTONS_LAWS = 1
    GRAVITY_PROJECTILE = 2
    WAVES_SOUND = 3
    ELECTROMAGNETIC = 4
    ENERGY_CONSERVATION = 5
    MOMENTUM_COLLISIONS = 6
    SIMPLE_HARMONIC_MOTION = 7
    OPTICS_LIGHT = 8


class PhysicsEducationSystem:
    def __init__(self):
        # Initialize MediaPipe Hands
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.5,
        )
        self.mp_draw = mp.solutions.drawing_utils

        # Display parameters
        self.width = 1200
        self.height = 800
        self.menu_width = 300

        # Default lesson
        self.current_concept = PhysicsConceptType.NEWTONS_LAWS

        # Initialize physics lessons
        self.lessons = {
            PhysicsConceptType.NEWTONS_LAWS: NewtonsLaws(self.width, self.height, self.menu_width),
            PhysicsConceptType.GRAVITY_PROJECTILE: GravityProjectile(self.width, self.height, self.menu_width),
            PhysicsConceptType.WAVES_SOUND: WavesSound(self.width, self.height, self.menu_width),
            PhysicsConceptType.ELECTROMAGNETIC: Electromagnetic(self.width, self.height, self.menu_width),
            PhysicsConceptType.ENERGY_CONSERVATION: EnergyConservation(self.width, self.height, self.menu_width),
            PhysicsConceptType.MOMENTUM_COLLISIONS: MomentumCollisions(self.width, self.height, self.menu_width),
            PhysicsConceptType.SIMPLE_HARMONIC_MOTION: SimpleHarmonicMotion(self.width, self.height, self.menu_width),
            PhysicsConceptType.OPTICS_LIGHT: OpticsLight(self.width, self.height, self.menu_width),
        }

    def detect_gestures(self, hand_landmarks):
        """Detect simple hand gestures"""
        lm = hand_landmarks.landmark

        # Count fingers up
        fingers_up = []
        # Thumb
        fingers_up.append(1 if lm[4].x > lm[3].x else 0)
        # Other fingers
        for tip, pip in zip([8, 12, 16, 20], [6, 10, 14, 18]):
            fingers_up.append(1 if lm[tip].y < lm[pip].y else 0)

        total_fingers = sum(fingers_up)

        # Thumb-index distance
        thumb_index_dist = math.dist(
            (lm[4].x, lm[4].y), (lm[8].x, lm[8].y)
        )

        return {
            "position": (lm[9].x, lm[9].y),
            "gestures": {
                "open_palm": total_fingers >= 4,
                "fist": total_fingers <= 1,
                "point": fingers_up[1] == 1 and sum(fingers_up[2:]) <= 1,
                "pinch": thumb_index_dist < 0.05,
            },
            "finger_count": total_fingers,
            "landmarks": lm,
        }

    def draw_menu(self, frame):
        """Draw side menu with lessons & instructions"""
        cv2.rectangle(frame, (0, 0), (self.menu_width, self.height), (30, 30, 30), -1)

        # Title
        cv2.putText(frame, "Physics Concepts", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

        concepts = [
            ("1. Newton's Laws", PhysicsConceptType.NEWTONS_LAWS),
            ("2. Gravity & Motion", PhysicsConceptType.GRAVITY_PROJECTILE),
            ("3. Waves & Sound", PhysicsConceptType.WAVES_SOUND),
            ("4. Electric & Magnetic", PhysicsConceptType.ELECTROMAGNETIC),
            ("5. Energy Conservation", PhysicsConceptType.ENERGY_CONSERVATION),
            ("6. Momentum & Collisions", PhysicsConceptType.MOMENTUM_COLLISIONS),
            ("7. Oscillations", PhysicsConceptType.SIMPLE_HARMONIC_MOTION),
            ("8. Light & Optics", PhysicsConceptType.OPTICS_LIGHT),
        ]

        y = 70
        for text, concept in concepts:
            color = (100, 255, 100) if concept == self.current_concept else (200, 200, 200)
            cv2.putText(frame, text, (10, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
            y += 40

        return frame

    def run(self):
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("❌ Error: Cannot open camera")
            return

        print("🎓 Interactive Physics Education System")
        print("Press keys 1–8 to switch lessons | Q to quit | R to reset")

        fps_counter, fps_time = 0, time.time()
        fps = 0

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            frame = cv2.resize(frame, (self.width, self.height))
            frame = cv2.flip(frame, 1)

            # Detect hands
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.hands.process(rgb)
            hands_data = {}

            if results.multi_hand_landmarks:
                for i, hand_lm in enumerate(results.multi_hand_landmarks):
                    self.mp_draw.draw_landmarks(frame, hand_lm, self.mp_hands.HAND_CONNECTIONS)
                    hands_data[i] = self.detect_gestures(hand_lm)

            # Update + render lesson
            lesson = self.lessons[self.current_concept]
            lesson.update(hands_data)
            frame = lesson.render(frame)

            # Draw side menu
            frame = self.draw_menu(frame)

            # FPS
            fps_counter += 1
            if time.time() - fps_time >= 1.0:
                fps = fps_counter / (time.time() - fps_time)
                fps_counter, fps_time = 0, time.time()

            cv2.putText(frame, f"FPS: {fps:.1f}", (self.width - 100, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

            cv2.imshow("Interactive Physics Education System", frame)

            # Key handling
            key = cv2.waitKey(1) & 0xFF
            if key == ord("q"):
                break
            elif key == ord("r"):
                lesson.reset()
            elif ord("1") <= key <= ord("8"):
                mapping = {
                    ord("1"): PhysicsConceptType.NEWTONS_LAWS,
                    ord("2"): PhysicsConceptType.GRAVITY_PROJECTILE,
                    ord("3"): PhysicsConceptType.WAVES_SOUND,
                    ord("4"): PhysicsConceptType.ELECTROMAGNETIC,
                    ord("5"): PhysicsConceptType.ENERGY_CONSERVATION,
                    ord("6"): PhysicsConceptType.MOMENTUM_COLLISIONS,
                    ord("7"): PhysicsConceptType.SIMPLE_HARMONIC_MOTION,
                    ord("8"): PhysicsConceptType.OPTICS_LIGHT,
                }
                self.current_concept = mapping[key]
                self.lessons[self.current_concept].reset()

        cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    app = PhysicsEducationSystem()
    app.run()

from flask import Flask, render_template_string, request, jsonify, Response
import json
import math
import random
from datetime import datetime, timedelta
import os
import cv2
import mediapipe as mp
import numpy as np
import threading
import time
from queue import Queue
import base64

app = Flask(__name__)

# Enhanced Space Education System with Voice Teaching Capabilities
class VoiceSpaceEducationSystem:
    def __init__(self):
        self.planets = {
            'sun': {
                'name': 'Sun',
                'type': 'Star',
                'radius_km': 696340,
                'mass_kg': 1.989e30,
                'temperature_k': 5778,
                'composition': ['Hydrogen (73%)', 'Helium (25%)', 'Other elements (2%)'],
                'moons': 0,
                'voice_lesson': {
                    'introduction': "Welcome to our journey to the Sun, the magnificent star at the center of our solar system. Listen carefully as I guide you through the wonders of our nearest star.",
                    'key_concepts': [
                        "The Sun is not just any star - it's a G-type main-sequence star, perfectly sized to sustain life on Earth",
                        "Deep in its core, hydrogen atoms fuse together to form helium, releasing tremendous energy in a process called nuclear fusion",
                        "The Sun's surface temperature is about 5,778 Kelvin, but its core burns at 15 million degrees Celsius",
                        "Every second, the Sun converts 600 million tons of hydrogen into helium, powering our entire solar system"
                    ],
                    'interactive_questions': [
                        "Can you imagine waiting 8 minutes and 20 seconds for sunlight to reach us?",
                        "What do you think would happen to Earth if the Sun suddenly stopped producing energy?",
                        "Did you know the Sun contains 99.86% of all the mass in our solar system?"
                    ],
                    'conclusion': "The Sun is truly remarkable - a cosmic furnace that has been burning for 4.6 billion years and will continue for another 5 billion years."
                }
            },
            'mercury': {
                'name': 'Mercury',
                'type': 'Terrestrial Planet',
                'radius_km': 2439.7,
                'mass_kg': 3.301e23,
                'temperature_range': [-173, 427],
                'moons': 0,
                'voice_lesson': {
                    'introduction': "Let's explore Mercury, the swift messenger of the gods and the planet closest to our Sun.",
                    'key_concepts': [
                        "Mercury is the smallest planet in our solar system, only slightly larger than Earth's Moon",
                        "Despite being closest to the Sun, it actually has ice at its poles!",
                        "The temperature swings are incredible - from 427°C in sunlight to -173°C in shadow"
                    ],
                    'interactive_questions': [
                        "Why does Mercury have such extreme temperature variations?",
                        "Can you imagine a day that lasts 59 Earth days?"
                    ],
                    'conclusion': "Mercury teaches us that proximity to the Sun doesn't guarantee warmth everywhere."
                }
            },
            'venus': {
                'name': 'Venus',
                'type': 'Terrestrial Planet',
                'radius_km': 6051.8,
                'mass_kg': 4.867e24,
                'temperature_range': [462, 462],
                'moons': 0,
                'voice_lesson': {
                    'introduction': "Welcome to Venus, Earth's twin sister that took a very different path.",
                    'key_concepts': [
                        "Venus is often called Earth's twin because of similar size and mass",
                        "The surface temperature is a scorching 462°C - hot enough to melt lead!",
                        "Venus rotates backwards, meaning the Sun rises in the west"
                    ],
                    'interactive_questions': [
                        "Why did Venus become so different from Earth?",
                        "Can you imagine a world where the Sun rises in the west?"
                    ],
                    'conclusion': "Venus shows us what happens when a greenhouse effect goes too far."
                }
            },
            'earth': {
                'name': 'Earth',
                'type': 'Terrestrial Planet',
                'radius_km': 6371,
                'mass_kg': 5.972e24,
                'temperature_range': [-89, 58],
                'moons': 1,
                'voice_lesson': {
                    'introduction': "Here we are, on our home planet Earth - the only known world that harbors life.",
                    'key_concepts': [
                        "Earth sits in the perfect location called the habitable zone",
                        "Our atmosphere is a protective blanket with just the right mix of gases",
                        "Water covers 71% of Earth's surface, making it unique"
                    ],
                    'interactive_questions': [
                        "What makes Earth perfect for life?",
                        "Why is water so crucial for life as we know it?"
                    ],
                    'conclusion': "Earth is truly a cosmic oasis in the vast universe."
                }
            },
            'mars': {
                'name': 'Mars',
                'type': 'Terrestrial Planet',
                'radius_km': 3389.5,
                'mass_kg': 6.39e23,
                'temperature_range': [-143, 35],
                'moons': 2,
                'voice_lesson': {
                    'introduction': "Journey with me to Mars, the Red Planet that captures our imagination.",
                    'key_concepts': [
                        "Mars gets its red color from iron oxide covering its surface",
                        "Evidence suggests Mars once had flowing rivers and lakes",
                        "Olympus Mons towers 21 kilometers high - three times taller than Mount Everest"
                    ],
                    'interactive_questions': [
                        "What happened to Mars's ancient water?",
                        "Could humans live on Mars someday?"
                    ],
                    'conclusion': "Mars represents both our past and future among the stars."
                }
            },
            'jupiter': {
                'name': 'Jupiter',
                'type': 'Gas Giant',
                'radius_km': 69911,
                'mass_kg': 1.898e27,
                'moons': 95,
                'voice_lesson': {
                    'introduction': "Behold Jupiter, the king of planets and guardian of our solar system.",
                    'key_concepts': [
                        "Jupiter is more massive than all other planets combined",
                        "The Great Red Spot is a storm larger than Earth",
                        "Jupiter's gravity protects us from asteroids and comets"
                    ],
                    'interactive_questions': [
                        "How does Jupiter protect Earth?",
                        "Which of Jupiter's moons would you visit?"
                    ],
                    'conclusion': "Jupiter stands as our solar system's mighty protector."
                }
            },
            'saturn': {
                'name': 'Saturn',
                'type': 'Gas Giant',
                'radius_km': 58232,
                'mass_kg': 5.683e26,
                'moons': 146,
                'voice_lesson': {
                    'introduction': "Welcome to Saturn, the jewel of the solar system with its spectacular rings.",
                    'key_concepts': [
                        "Saturn is famous for its stunning ring system",
                        "Despite its size, Saturn would float in water!",
                        "Titan has lakes and rivers of liquid methane"
                    ],
                    'interactive_questions': [
                        "How did Saturn's rings form?",
                        "What would it be like on Titan?"
                    ],
                    'conclusion': "Saturn reminds us that beauty and science go hand in hand."
                }
            },
            'uranus': {
                'name': 'Uranus',
                'type': 'Ice Giant',
                'radius_km': 25362,
                'mass_kg': 8.681e25,
                'moons': 27,
                'voice_lesson': {
                    'introduction': "Next, we travel to mysterious Uranus, a planet that dances to its own beat.",
                    'key_concepts': [
                        "Uranus is the only planet that rotates on its side",
                        "Its blue-green color comes from methane gas",
                        "It's the coldest planet in the solar system"
                    ],
                    'interactive_questions': [
                        "What caused Uranus to tip over?",
                        "How cold is -224 degrees Celsius?"
                    ],
                    'conclusion': "Uranus proves the universe is full of surprises."
                }
            },
            'neptune': {
                'name': 'Neptune',
                'type': 'Ice Giant',
                'radius_km': 24622,
                'mass_kg': 1.024e26,
                'moons': 14,
                'voice_lesson': {
                    'introduction': "Our final stop is Neptune, the farthest and windiest planet.",
                    'key_concepts': [
                        "Neptune has the fastest winds in the solar system",
                        "Its deep blue color comes from methane",
                        "Triton orbits backwards around Neptune"
                    ],
                    'interactive_questions': [
                        "What creates Neptune's incredible winds?",
                        "Could life exist on Triton?"
                    ],
                    'conclusion': "Neptune reminds us that even distant worlds are full of wonders."
                }
            }
        }
    
    def get_planet_data(self, planet_name):
        return self.planets.get(planet_name.lower(), {})
    
    def get_voice_lesson(self, planet_name):
        planet_data = self.get_planet_data(planet_name)
        if not planet_data or 'voice_lesson' not in planet_data:
            return None
        
        lesson = planet_data['voice_lesson']
        lesson['planet_name'] = planet_data['name']
        lesson['planet_type'] = planet_data.get('type', 'Celestial Body')
        
        return lesson

# Hand tracking system
class HandTrackingSystem:
    def __init__(self):
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.mp_drawing = mp.solutions.drawing_utils
        self.cap = None
        self.hand_landmarks = []
        self.gesture_state = {
            'pointing': False,
            'thumbs_up': False,
            'peace_sign': False,
            'open_palm': False,
            'finger_position': (0, 0)
        }
        self.is_camera_active = False
        
    def start_camera(self):
        try:
            if not self.is_camera_active:
                self.cap = cv2.VideoCapture(0)
                self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                self.is_camera_active = True
            return True
        except Exception as e:
            print(f"Error starting camera: {e}")
            return False
    
    def stop_camera(self):
        if self.cap:
            self.cap.release()
            self.cap = None
            self.is_camera_active = False
    
    def get_frame(self):
        if not self.cap or not self.is_camera_active:
            # Return a blank frame if camera is not available
            blank_frame = np.zeros((480, 640, 3), dtype=np.uint8)
            cv2.putText(blank_frame, 'Camera not available', (150, 240), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            return blank_frame, None
            
        ret, frame = self.cap.read()
        if not ret:
            # Return a blank frame if read failed
            blank_frame = np.zeros((480, 640, 3), dtype=np.uint8)
            cv2.putText(blank_frame, 'Camera read failed', (150, 240), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            return blank_frame, None
            
        # Flip frame horizontally for mirror effect
        frame = cv2.flip(frame, 1)
        
        # Convert BGR to RGB for MediaPipe
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb_frame)
        
        # Convert back to BGR for display
        annotated_frame = cv2.cvtColor(rgb_frame, cv2.COLOR_RGB2BGR)
        
        self.hand_landmarks = []
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                self.hand_landmarks.append(hand_landmarks)
                self.mp_drawing.draw_landmarks(
                    annotated_frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)
        
        # Analyze gestures
        self.analyze_gestures()
        
        return annotated_frame, results
    
    def analyze_gestures(self):
        if not self.hand_landmarks:
            self.gesture_state = {
                'pointing': False,
                'thumbs_up': False,
                'peace_sign': False,
                'open_palm': False,
                'finger_position': (0, 0)
            }
            return
        
        # Get first hand landmarks
        landmarks = self.hand_landmarks[0].landmark
        
        # Get finger tip and base positions
        thumb_tip = landmarks[4]
        thumb_ip = landmarks[3]
        index_tip = landmarks[8]
        index_pip = landmarks[6]
        middle_tip = landmarks[12]
        middle_pip = landmarks[10]
        ring_tip = landmarks[16]
        ring_pip = landmarks[14]
        pinky_tip = landmarks[20]
        pinky_pip = landmarks[18]
        
        # Calculate finger states (extended or folded)
        thumb_extended = thumb_tip.y < thumb_ip.y
        index_extended = index_tip.y < index_pip.y
        middle_extended = middle_tip.y < middle_pip.y
        ring_extended = ring_tip.y < ring_pip.y
        pinky_extended = pinky_tip.y < pinky_pip.y
        
        # Detect gestures
        # Pointing gesture (only index finger extended)
        self.gesture_state['pointing'] = (
            index_extended and 
            not middle_extended and 
            not ring_extended and 
            not pinky_extended
        )
        
        # Thumbs up (only thumb extended)
        self.gesture_state['thumbs_up'] = (
            thumb_extended and
            not index_extended and
            not middle_extended and
            not ring_extended and
            not pinky_extended
        )
        
        # Peace sign (index and middle extended)
        self.gesture_state['peace_sign'] = (
            index_extended and
            middle_extended and
            not ring_extended and
            not pinky_extended
        )
        
        # Open palm (all fingers extended)
        self.gesture_state['open_palm'] = (
            thumb_extended and
            index_extended and
            middle_extended and
            ring_extended and
            pinky_extended
        )
        
        # Store finger position (index finger tip for pointing)
        if self.gesture_state['pointing']:
            self.gesture_state['finger_position'] = (index_tip.x, index_tip.y)
        else:
            self.gesture_state['finger_position'] = (0, 0)

# Initialize systems
space_edu = VoiceSpaceEducationSystem()
hand_tracker = HandTrackingSystem()

def generate_frames():
    hand_tracker.start_camera()
    
    while True:
        try:
            frame, results = hand_tracker.get_frame()
            if frame is not None:
                # Encode frame as JPEG
                _, buffer = cv2.imencode('.jpg', frame)
                frame_bytes = buffer.tobytes()
                
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
            
            time.sleep(0.033)  # ~30 FPS
        except Exception as e:
            print(f"Error in generate_frames: {e}")
            # Create error frame
            error_frame = np.zeros((480, 640, 3), dtype=np.uint8)
            cv2.putText(error_frame, 'Camera Error', (200, 240), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            _, buffer = cv2.imencode('.jpg', error_frame)
            frame_bytes = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
            time.sleep(1)  # Wait longer on error

# HTML Template
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Voice AI Space Tutor - Hand Gesture Control</title>
    <style>
        :root {
            --space-dark: #0a0a0f;
            --space-blue: #1e3a8a;
            --cosmic-cyan: #06b6d4;
            --voice-active: #ff6b35;
            --spaceship-color: #00ff88;
            --text-primary: #f8fafc;
            --text-secondary: #cbd5e1;
            --panel-bg: rgba(15, 23, 42, 0.85);
            --panel-border: rgba(59, 130, 246, 0.3);
        }

        * { margin: 0; padding: 0; box-sizing: border-box; }

        body {
            font-family: 'Inter', sans-serif;
            background: linear-gradient(135deg, #050508 0%, #0a0a0f 50%, #1e1b4b 100%);
            color: var(--text-primary);
            height: 100vh;
            overflow: hidden;
        }

        .main-container {
            display: flex;
            height: 100vh;
        }

        .space-view {
            flex: 2.5;
            position: relative;
            background: radial-gradient(ellipse at center, rgba(30, 58, 138, 0.1) 0%, transparent 70%);
        }

        .camera-container {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            z-index: 1;
        }

        #video-feed {
            width: 100%;
            height: 100%;
            object-fit: cover;
            opacity: 0.4;
            filter: blur(1px);
        }

        .solar-system-overlay {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            z-index: 3;
        }

        #solarCanvas {
            width: 100%;
            height: 100%;
        }

        .hand-status {
            position: absolute;
            top: 20px;
            left: 20px;
            background: var(--panel-bg);
            border: 2px solid var(--spaceship-color);
            border-radius: 12px;
            padding: 1rem;
            backdrop-filter: blur(15px);
            z-index: 10;
            max-width: 280px;
        }

        .hand-status.tracking {
            border-color: var(--voice-active);
            box-shadow: 0 0 20px rgba(255, 107, 53, 0.3);
        }

        .hand-status h4 {
            color: var(--spaceship-color);
            font-weight: 700;
            margin-bottom: 0.5rem;
            text-align: center;
        }

        .status-item {
            display: flex;
            justify-content: space-between;
            margin: 0.25rem 0;
            font-size: 0.85rem;
        }

        .status-value {
            color: #fbbf24;
            font-weight: 600;
        }

        .hand-indicator {
            width: 12px;
            height: 12px;
            border-radius: 50%;
            display: inline-block;
            margin-left: 0.5rem;
            background: #ef4444;
            animation: pulse 2s ease-in-out infinite;
        }

        .hand-indicator.active {
            background: var(--spaceship-color);
        }

        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }

        .voice-assistant {
            position: absolute;
            bottom: 20px;
            left: 20px;
            background: var(--panel-bg);
            border: 2px solid var(--voice-active);
            border-radius: 20px;
            padding: 1rem;
            backdrop-filter: blur(15px);
            min-width: 280px;
            z-index: 15;
        }

        .voice-assistant.speaking {
            border-color: var(--spaceship-color);
            box-shadow: 0 0 20px rgba(0, 255, 136, 0.3);
            animation: assistantPulse 2s ease-in-out infinite alternate;
        }

        @keyframes assistantPulse {
            0% { transform: scale(1); }
            100% { transform: scale(1.02); }
        }

        .voice-title {
            color: var(--voice-active);
            font-weight: 700;
            margin-bottom: 0.5rem;
            text-align: center;
        }

        .voice-status {
            text-align: center;
            font-size: 0.85rem;
            color: var(--text-secondary);
            margin-top: 0.5rem;
        }

        .control-panel {
            flex: 1.2;
            background: var(--panel-bg);
            border-left: 3px solid var(--panel-border);
            display: flex;
            flex-direction: column;
            backdrop-filter: blur(15px);
            min-width: 400px;
        }

        .panel-header {
            padding: 1.5rem;
            text-align: center;
            background: linear-gradient(135deg, var(--space-blue), #581c87);
            color: white;
            font-weight: 700;
            font-size: 1.25rem;
        }

        .tabs {
            display: flex;
            background: rgba(30, 41, 59, 0.8);
            border-bottom: 1px solid var(--panel-border);
        }

        .tab {
            flex: 1;
            padding: 0.75rem;
            text-align: center;
            cursor: pointer;
            transition: all 0.3s ease;
            border-bottom: 3px solid transparent;
            font-weight: 500;
        }

        .tab.active {
            background: linear-gradient(135deg, var(--cosmic-cyan), var(--space-blue));
            border-bottom-color: var(--cosmic-cyan);
            color: white;
        }

        .tab:hover:not(.active) {
            background: rgba(59, 130, 246, 0.1);
            color: var(--cosmic-cyan);
        }

        .tab-content {
            flex: 1;
            padding: 1.5rem;
            overflow-y: auto;
            display: none;
        }

        .tab-content.active {
            display: block;
        }

        .voice-lesson-panel {
            background: linear-gradient(135deg, rgba(255, 107, 53, 0.1), rgba(236, 72, 153, 0.1));
            border: 2px solid rgba(255, 107, 53, 0.3);
            border-radius: 12px;
            padding: 1.5rem;
            margin-bottom: 1rem;
        }

        .lesson-title {
            font-size: 1.3rem;
            font-weight: 700;
            color: var(--voice-active);
            margin-bottom: 0.5rem;
        }

        .lesson-progress {
            width: 100%;
            height: 8px;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 4px;
            margin: 1rem 0;
        }

        .progress-bar {
            height: 100%;
            background: linear-gradient(90deg, var(--voice-active), var(--spaceship-color));
            border-radius: 4px;
            transition: width 0.5s ease;
            width: 0%;
        }

        .lesson-controls {
            display: flex;
            gap: 1rem;
            justify-content: center;
            margin: 1rem 0;
        }

        .lesson-btn {
            padding: 0.75rem 1.5rem;
            border: 2px solid var(--voice-active);
            background: transparent;
            color: var(--voice-active);
            border-radius: 25px;
            cursor: pointer;
            font-weight: 600;
            transition: all 0.3s ease;
        }

        .lesson-btn:hover {
            background: var(--voice-active);
            color: var(--space-dark);
        }

        .planet-info {
            background: linear-gradient(135deg, rgba(30, 58, 138, 0.1), rgba(88, 28, 135, 0.1));
            border: 2px solid var(--panel-border);
            border-radius: 12px;
            padding: 1.5rem;
            margin-bottom: 1rem;
        }

        .planet-name {
            font-size: 1.5rem;
            font-weight: 700;
            color: var(--cosmic-cyan);
            margin-bottom: 0.5rem;
        }

        .planet-type {
            color: var(--text-secondary);
            font-size: 0.9rem;
            margin-bottom: 1rem;
            padding: 0.25rem 0.75rem;
            background: rgba(59, 130, 246, 0.2);
            border-radius: 15px;
            display: inline-block;
        }

        .gesture-instructions {
            background: var(--panel-bg);
            border: 2px solid var(--cosmic-cyan);
            border-radius: 12px;
            padding: 1.5rem;
            margin-bottom: 1rem;
        }

        .instruction-item {
            display: flex;
            align-items: center;
            gap: 1rem;
            margin: 1rem 0;
            padding: 0.75rem;
            background: rgba(6, 182, 212, 0.1);
            border-radius: 8px;
        }

        .instruction-icon {
            font-size: 1.5rem;
            width: 40px;
            text-align: center;
        }
    </style>
</head>
<body>
    <div class="main-container">
        <!-- Space View with Camera and Solar System -->
        <div class="space-view">
            <!-- Camera Container -->
            <div class="camera-container">
                <img id="video-feed" src="/video_feed" alt="Camera Feed">
            </div>
            
            <!-- Solar System Overlay -->
            <div class="solar-system-overlay">
                <canvas id="solarCanvas"></canvas>
            </div>

            <!-- Hand Tracking Status -->
            <div class="hand-status" id="handStatus">
                <h4>Hand Tracking Status</h4>
                <div class="status-item">
                    <span>Camera:</span>
                    <span class="status-value" id="cameraStatus">Active</span>
                </div>
                <div class="status-item">
                    <span>Hand Detected:</span>
                    <span class="status-value" id="handDetected">
                        <span id="handDetectedText">No</span>
                        <div class="hand-indicator" id="handIndicator"></div>
                    </span>
                </div>
                <div class="status-item">
                    <span>Gesture:</span>
                    <span class="status-value" id="gestureType">None</span>
                </div>
                <div class="status-item">
                    <span>Planet Hover:</span>
                    <span class="status-value" id="planetHover">None</span>
                </div>
            </div>

            <!-- Voice Assistant Interface -->
            <div class="voice-assistant" id="voiceAssistant">
                <div class="voice-title">Professor Cosmos</div>
                <div class="voice-status" id="voiceStatus">
                    Point at a planet to start learning!
                </div>
            </div>
        </div>

        <!-- Control Panel -->
        <div class="control-panel">
            <div class="panel-header">
                Voice AI Space Tutor - Hand Gesture Control
            </div>
            
            <!-- Tabs -->
            <div class="tabs">
                <div class="tab active" data-tab="lesson">Voice Lesson</div>
                <div class="tab" data-tab="gestures">Hand Gestures</div>
                <div class="tab" data-tab="info">Planet Info</div>
            </div>

            <!-- Voice Lesson Tab -->
            <div class="tab-content active" id="lesson">
                <div class="voice-lesson-panel">
                    <div class="lesson-title" id="lessonTitle">Point at a Planet to Begin</div>
                    <div class="lesson-progress">
                        <div class="progress-bar" id="progressBar"></div>
                    </div>
                    
                    <div class="lesson-controls">
                        <button class="lesson-btn" id="playLesson">Play Lesson</button>
                        <button class="lesson-btn" id="pauseLesson">Pause</button>
                        <button class="lesson-btn" id="nextSegment">Next</button>
                    </div>
                    
                    <div id="lessonContent" style="margin-top: 1rem; padding: 1rem; background: rgba(15, 23, 42, 0.6); border-radius: 8px; min-height: 100px;">
                        <p style="text-align: center; color: var(--text-secondary);">
                            Use hand gestures to point at planets in the solar system to start voice lessons!
                        </p>
                    </div>
                </div>
            </div>

            <!-- Hand Gestures Tab -->
            <div class="tab-content" id="gestures">
                <div class="gesture-instructions">
                    <h3 style="color: var(--cosmic-cyan); margin-bottom: 1rem; text-align: center;">How to Use Hand Gestures</h3>
                    
                    <div class="instruction-item">
                        <div class="instruction-icon">👉</div>
                        <div style="flex: 1; color: var(--text-primary);">
                            <strong>Point at Planets:</strong> Extend your index finger and point directly at any planet to hover and select it.
                        </div>
                    </div>
                    
                    <div class="instruction-item">
                        <div class="instruction-icon">✋</div>
                        <div style="flex: 1; color: var(--text-primary);">
                            <strong>Hold for Selection:</strong> Keep your finger pointed at a planet for 2 seconds to start the voice lesson.
                        </div>
                    </div>
                    
                    <div class="instruction-item">
                        <div class="instruction-icon">👍</div>
                        <div style="flex: 1; color: var(--text-primary);">
                            <strong>Thumbs Up:</strong> Give a thumbs up gesture to play/pause the current lesson.
                        </div>
                    </div>
                    
                    <div class="instruction-item">
                        <div class="instruction-icon">✌️</div>
                        <div style="flex: 1; color: var(--text-primary);">
                            <strong>Peace Sign:</strong> Show two fingers to skip to the next lesson segment.
                        </div>
                    </div>
                    
                    <div class="instruction-item">
                        <div class="instruction-icon">🤚</div>
                        <div style="flex: 1; color: var(--text-primary);">
                            <strong>Open Palm:</strong> Show an open palm to stop the current lesson.
                        </div>
                    </div>
                </div>
                
                <div style="background: rgba(255, 107, 53, 0.1); border: 2px solid rgba(255, 107, 53, 0.3); border-radius: 12px; padding: 1rem; margin-top: 1rem;">
                    <h4 style="color: var(--voice-active); margin-bottom: 0.5rem;">Tips for Best Results:</h4>
                    <ul style="color: var(--text-secondary); line-height: 1.6; margin-left: 1rem;">
                        <li>Keep your hand visible in the camera frame</li>
                        <li>Make clear, deliberate gestures</li>
                        <li>Ensure good lighting on your hands</li>
                        <li>Position yourself 2-3 feet from the camera</li>
                    </ul>
                </div>
            </div>

            <!-- Planet Information Tab -->
            <div class="tab-content" id="info">
                <div class="planet-info" id="planetInfo">
                    <div class="planet-name" id="planetName">Point at a Planet</div>
                    <div class="planet-type" id="planetType">Use hand gestures to select a planet</div>
                    
                    <div id="planetStats" style="margin-top: 1rem;">
                        <p style="color: var(--text-secondary); text-align: center; padding: 2rem;">
                            Point your finger at any planet in the solar system to learn about it through voice lessons and interactive content.
                        </p>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        class HandGestureSpaceTutor {
            constructor() {
                this.solarCanvas = document.getElementById('solarCanvas');
                this.solarCtx = this.solarCanvas.getContext('2d');
                
                this.currentPlanet = null;
                this.currentLesson = null;
                this.isVoicePlaying = false;
                this.speechSynthesis = window.speechSynthesis;
                this.currentUtterance = null;
                this.currentLessonSegment = 0;
                this.planetHoverTime = 0;
                this.lastHoveredPlanet = null;
                this.hoverThreshold = 2000; // 2 seconds to select
                this.gestureCheckInterval = 500; // Check gestures every 500ms
                
                this.zoom = 1;
                this.panX = 0;
                this.panY = 0;
                
                this.solarSystem = {
                    planets: {
                        sun: { x: 0, y: 0, radius: 30, color: '#FFD700', name: 'Sun' },
                        mercury: { x: 80, y: 0, radius: 8, color: '#8C7853', name: 'Mercury' },
                        venus: { x: 120, y: 0, radius: 12, color: '#FFBF00', name: 'Venus' },
                        earth: { x: 160, y: 0, radius: 14, color: '#4169E1', name: 'Earth' },
                        mars: { x: 200, y: 0, radius: 10, color: '#CD5C5C', name: 'Mars' },
                        jupiter: { x: 280, y: 0, radius: 28, color: '#D2691E', name: 'Jupiter' },
                        saturn: { x: 350, y: 0, radius: 25, color: '#FAD5A5', name: 'Saturn' },
                        uranus: { x: 420, y: 0, radius: 20, color: '#A5F3FC', name: 'Uranus' },
                        neptune: { x: 480, y: 0, radius: 20, color: '#1E40AF', name: 'Neptune' }
                    }
                };
                
                this.time = 0;
                this.init();
            }
            
            init() {
                this.setupCanvas();
                this.setupEventListeners();
                this.startAnimation();
                this.startGestureTracking();
            }
            
            setupCanvas() {
                const resizeCanvas = () => {
                    this.solarCanvas.width = this.solarCanvas.offsetWidth;
                    this.solarCanvas.height = this.solarCanvas.offsetHeight;
                };
                
                resizeCanvas();
                window.addEventListener('resize', resizeCanvas);
            }
            
            setupEventListeners() {
                // Tab switching
                document.querySelectorAll('.tab').forEach(tab => {
                    tab.addEventListener('click', (e) => {
                        this.switchTab(e.target.dataset.tab);
                    });
                });
                
                // Voice controls
                document.getElementById('playLesson').addEventListener('click', () => {
                    this.startVoiceLesson();
                });
                
                document.getElementById('pauseLesson').addEventListener('click', () => {
                    this.toggleVoicePause();
                });
                
                document.getElementById('nextSegment').addEventListener('click', () => {
                    this.nextLessonSegment();
                });
            }
            
            startAnimation() {
                const animate = () => {
                    this.time += 0.01;
                    this.drawSolarSystem();
                    requestAnimationFrame(animate);
                };
                animate();
            }
            
            startGestureTracking() {
                setInterval(() => {
                    this.checkHandGestures();
                }, this.gestureCheckInterval);
            }
            
            async checkHandGestures() {
                try {
                    const response = await fetch('/api/hand-gestures');
                    const data = await response.json();
                    
                    this.updateHandStatus(data);
                    this.processGestures(data);
                } catch (error) {
                    console.error('Error checking hand gestures:', error);
                }
            }
            
            updateHandStatus(gestureData) {
                const handDetected = gestureData.hand_detected;
                const gesture = gestureData.current_gesture;
                
                // Update hand detection indicator
                document.getElementById('handDetectedText').textContent = handDetected ? 'Yes' : 'No';
                const indicator = document.getElementById('handIndicator');
                indicator.className = handDetected ? 'hand-indicator active' : 'hand-indicator';
                
                // Update gesture type
                document.getElementById('gestureType').textContent = gesture || 'None';
                
                // Update hand status panel
                const handStatus = document.getElementById('handStatus');
                handStatus.className = handDetected ? 'hand-status tracking' : 'hand-status';
            }
            
            processGestures(gestureData) {
                if (!gestureData.hand_detected) {
                    this.resetPlanetHover();
                    return;
                }
                
                const gesture = gestureData.current_gesture;
                const fingerPos = gestureData.finger_position;
                
                if (gesture === 'pointing' && fingerPos.x > 0 && fingerPos.y > 0) {
                    this.handlePointingGesture(fingerPos);
                } else if (gesture === 'thumbs_up') {
                    this.handleThumbsUp();
                } else if (gesture === 'peace_sign') {
                    this.handlePeaceSign();
                } else if (gesture === 'open_palm') {
                    this.handleOpenPalm();
                } else {
                    this.resetPlanetHover();
                }
            }
            
            handlePointingGesture(fingerPos) {
                const hoveredPlanet = this.getPlanetAtPosition(fingerPos.x, fingerPos.y);
                
                if (hoveredPlanet) {
                    if (hoveredPlanet === this.lastHoveredPlanet) {
                        this.planetHoverTime += this.gestureCheckInterval;
                        
                        if (this.planetHoverTime >= this.hoverThreshold) {
                            this.selectPlanet(hoveredPlanet);
                            this.resetPlanetHover();
                        }
                    } else {
                        this.lastHoveredPlanet = hoveredPlanet;
                        this.planetHoverTime = 0;
                    }
                    
                    this.showPlanetHover(hoveredPlanet);
                    document.getElementById('planetHover').textContent = this.solarSystem.planets[hoveredPlanet].name;
                } else {
                    this.resetPlanetHover();
                }
            }
            
            handleThumbsUp() {
                if (this.currentLesson) {
                    this.toggleVoicePause();
                    this.updateVoiceStatus('Thumbs up detected - toggling lesson!');
                }
            }
            
            handlePeaceSign() {
                if (this.currentLesson && this.isVoicePlaying) {
                    this.nextLessonSegment();
                    this.updateVoiceStatus('Peace sign detected - next segment!');
                }
            }
            
            handleOpenPalm() {
                if (this.isVoicePlaying) {
                    this.stopVoiceLesson();
                    this.updateVoiceStatus('Open palm detected - lesson stopped!');
                }
            }
            
            getPlanetAtPosition(x, y) {
                // Convert normalized coordinates to canvas coordinates
                const canvasX = x * this.solarCanvas.width;
                const canvasY = y * this.solarCanvas.height;
                
                const centerX = this.solarCanvas.width / 2 + this.panX;
                const centerY = this.solarCanvas.height / 2 + this.panY;
                
                // Check each planet
                for (const [key, planet] of Object.entries(this.solarSystem.planets)) {
                    let planetX, planetY;
                    
                    if (key === 'sun') {
                        planetX = centerX;
                        planetY = centerY;
                    } else {
                        const angle = this.time * (1 / Math.sqrt(planet.x));
                        planetX = centerX + Math.cos(angle) * planet.x * this.zoom;
                        planetY = centerY + Math.sin(angle) * planet.x * this.zoom;
                    }
                    
                    const distance = Math.sqrt(
                        Math.pow(canvasX - planetX, 2) + 
                        Math.pow(canvasY - planetY, 2)
                    );
                    
                    if (distance <= (planet.radius + 10) * this.zoom) {
                        return key;
                    }
                }
                
                return null;
            }
            
            resetPlanetHover() {
                this.lastHoveredPlanet = null;
                this.planetHoverTime = 0;
                document.getElementById('planetHover').textContent = 'None';
            }
            
            showPlanetHover(planetKey) {
                this.hoveredPlanet = planetKey;
            }
            
            drawSolarSystem() {
                const centerX = this.solarCanvas.width / 2 + this.panX;
                const centerY = this.solarCanvas.height / 2 + this.panY;
                
                this.solarCtx.clearRect(0, 0, this.solarCanvas.width, this.solarCanvas.height);
                
                // Draw orbital paths
                this.solarCtx.strokeStyle = 'rgba(255, 255, 255, 0.1)';
                this.solarCtx.lineWidth = 1;
                
                Object.entries(this.solarSystem.planets).forEach(([key, planet]) => {
                    if (key === 'sun') return;
                    
                    this.solarCtx.beginPath();
                    this.solarCtx.arc(centerX, centerY, planet.x * this.zoom, 0, 2 * Math.PI);
                    this.solarCtx.stroke();
                });
                
                // Draw planets
                Object.entries(this.solarSystem.planets).forEach(([key, planet]) => {
                    let x, y;
                    
                    if (key === 'sun') {
                        x = centerX;
                        y = centerY;
                    } else {
                        const angle = this.time * (1 / Math.sqrt(planet.x));
                        x = centerX + Math.cos(angle) * planet.x * this.zoom;
                        y = centerY + Math.sin(angle) * planet.x * this.zoom;
                    }
                    
                    // Planet glow effect
                    const gradient = this.solarCtx.createRadialGradient(x, y, 0, x, y, planet.radius * this.zoom * 2);
                    gradient.addColorStop(0, planet.color);
                    gradient.addColorStop(0.7, planet.color + '80');
                    gradient.addColorStop(1, 'transparent');
                    
                    this.solarCtx.fillStyle = gradient;
                    this.solarCtx.beginPath();
                    this.solarCtx.arc(x, y, planet.radius * this.zoom * 2, 0, 2 * Math.PI);
                    this.solarCtx.fill();
                    
                    // Draw Saturn's rings
                    if (key === 'saturn') {
                        this.solarCtx.strokeStyle = '#FAD5A5aa';
                        this.solarCtx.lineWidth = 3 * this.zoom;
                        this.solarCtx.beginPath();
                        this.solarCtx.ellipse(x, y, 40 * this.zoom, 40 * this.zoom * 0.4, 0, 0, 2 * Math.PI);
                        this.solarCtx.stroke();
                    }
                    
                    // Draw planet
                    this.solarCtx.fillStyle = planet.color;
                    this.solarCtx.beginPath();
                    this.solarCtx.arc(x, y, planet.radius * this.zoom, 0, 2 * Math.PI);
                    this.solarCtx.fill();
                    
                    // Highlight selected or hovered planet
                    if (this.currentPlanet === key || this.hoveredPlanet === key) {
                        this.solarCtx.strokeStyle = this.currentPlanet === key ? '#00ff88' : '#ff6b35';
                        this.solarCtx.lineWidth = 3;
                        this.solarCtx.beginPath();
                        this.solarCtx.arc(x, y, (planet.radius + 5) * this.zoom, 0, 2 * Math.PI);
                        this.solarCtx.stroke();
                        
                        // Pulsing effect for hovered planet
                        if (this.hoveredPlanet === key && this.planetHoverTime > 0) {
                            const progress = this.planetHoverTime / this.hoverThreshold;
                            const pulseRadius = (planet.radius + 15) * this.zoom * (1 + progress * 0.5);
                            this.solarCtx.strokeStyle = `rgba(255, 107, 53, ${0.8 - progress * 0.3})`;
                            this.solarCtx.lineWidth = 5;
                            this.solarCtx.beginPath();
                            this.solarCtx.arc(x, y, pulseRadius, 0, 2 * Math.PI);
                            this.solarCtx.stroke();
                        }
                    }
                });
                
                // Reset hover planet for next frame
                this.hoveredPlanet = null;
            }
            
            async selectPlanet(planetKey) {
                this.currentPlanet = planetKey;
                
                try {
                    // Fetch planet data
                    const response = await fetch(`/api/planet-data/${planetKey}`);
                    const planetData = await response.json();
                    
                    this.updatePlanetInfo(planetData);
                    
                    // Load lesson if available
                    const lessonResponse = await fetch(`/api/voice-lesson/${planetKey}`);
                    if (lessonResponse.ok) {
                        this.currentLesson = await lessonResponse.json();
                        this.updateLessonInterface();
                    }
                    
                    this.updateVoiceStatus(`Selected ${planetData.name}. Ready for voice lesson!`);
                    
                    // Auto-start lesson
                    setTimeout(() => {
                        this.startVoiceLesson();
                    }, 1000);
                    
                } catch (error) {
                    console.error('Error selecting planet:', error);
                    this.updateVoiceStatus('Error loading planet data. Please try again.');
                }
            }
            
            updatePlanetInfo(planetData) {
                document.getElementById('planetName').textContent = planetData.name || 'Unknown';
                document.getElementById('planetType').textContent = planetData.type || 'Unknown Type';
                
                const statsContainer = document.getElementById('planetStats');
                statsContainer.innerHTML = `
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
                        <div style="background: rgba(15, 23, 42, 0.6); padding: 0.75rem; border-radius: 8px; border-left: 4px solid var(--cosmic-cyan);">
                            <div style="font-size: 0.8rem; color: var(--text-secondary); margin-bottom: 0.25rem;">Type</div>
                            <div style="font-weight: 600; color: var(--text-primary);">${planetData.type || 'Unknown'}</div>
                        </div>
                        <div style="background: rgba(15, 23, 42, 0.6); padding: 0.75rem; border-radius: 8px; border-left: 4px solid var(--cosmic-cyan);">
                            <div style="font-size: 0.8rem; color: var(--text-secondary); margin-bottom: 0.25rem;">Radius</div>
                            <div style="font-weight: 600; color: var(--text-primary);">${planetData.radius_km ? `${planetData.radius_km.toLocaleString()} km` : 'Unknown'}</div>
                        </div>
                        <div style="background: rgba(15, 23, 42, 0.6); padding: 0.75rem; border-radius: 8px; border-left: 4px solid var(--cosmic-cyan);">
                            <div style="font-size: 0.8rem; color: var(--text-secondary); margin-bottom: 0.25rem;">Moons</div>
                            <div style="font-weight: 600; color: var(--text-primary);">${planetData.moons !== undefined ? planetData.moons : 'Unknown'}</div>
                        </div>
                        <div style="background: rgba(15, 23, 42, 0.6); padding: 0.75rem; border-radius: 8px; border-left: 4px solid var(--cosmic-cyan);">
                            <div style="font-size: 0.8rem; color: var(--text-secondary); margin-bottom: 0.25rem;">Temperature</div>
                            <div style="font-weight: 600; color: var(--text-primary);">${planetData.temperature_range ? `${planetData.temperature_range[0]}°C to ${planetData.temperature_range[1]}°C` : 'Variable'}</div>
                        </div>
                    </div>
                `;
            }
            
            updateLessonInterface() {
                if (!this.currentLesson) return;
                
                document.getElementById('lessonTitle').textContent = `${this.currentLesson.planet_name} Voice Lesson`;
                document.getElementById('lessonContent').innerHTML = `
                    <h4 style="color: var(--voice-active); margin-bottom: 1rem;">Lesson Overview</h4>
                    <p style="color: var(--text-primary); line-height: 1.6; margin-bottom: 1rem;">
                        ${this.currentLesson.introduction}
                    </p>
                    <div style="background: rgba(255, 107, 53, 0.1); padding: 1rem; border-radius: 8px; border-left: 4px solid var(--voice-active);">
                        <strong style="color: var(--voice-active);">Ready to begin!</strong> 
                        <span style="color: var(--text-secondary);">The lesson will start automatically.</span>
                    </div>
                `;
                
                this.currentLessonSegment = 0;
                this.updateProgressBar(0);
            }
            
            async startVoiceLesson() {
                if (!this.currentLesson) {
                    this.updateVoiceStatus('Please select a planet first!');
                    return;
                }
                
                if (this.isVoicePlaying) {
                    this.updateVoiceStatus('Lesson already in progress...');
                    return;
                }
                
                this.isVoicePlaying = true;
                this.currentLessonSegment = 0;
                this.updateVoiceStatus('Starting lesson...');
                this.activateVoiceAssistant();
                
                // Start with introduction
                await this.playLessonSegment('introduction');
            }
            
            async playLessonSegment(segmentType) {
                if (!this.currentLesson || !this.isVoicePlaying) return;
                
                let content = '';
                
                switch (segmentType) {
                    case 'introduction':
                        content = this.currentLesson.introduction;
                        this.currentLessonSegment = 1;
                        break;
                    case 'key_concepts':
                        if (this.currentLessonSegment - 2 < this.currentLesson.key_concepts.length) {
                            content = this.currentLesson.key_concepts[this.currentLessonSegment - 2];
                            this.currentLessonSegment++;
                        }
                        break;
                    case 'questions':
                        const questionIndex = this.currentLessonSegment - 2 - this.currentLesson.key_concepts.length;
                        if (questionIndex < this.currentLesson.interactive_questions.length) {
                            content = this.currentLesson.interactive_questions[questionIndex];
                            this.currentLessonSegment++;
                        }
                        break;
                    case 'conclusion':
                        content = this.currentLesson.conclusion;
                        break;
                }
                
                if (content) {
                    this.updateLessonContent(segmentType, content);
                    await this.speakText(content);
                    
                    // Auto-advance after speaking
                    if (this.isVoicePlaying) {
                        setTimeout(() => {
                            this.nextLessonSegment();
                        }, 1000);
                    }
                }
            }
            
            updateLessonContent(segmentType, content) {
                const contentDiv = document.getElementById('lessonContent');
                const typeColors = {
                    'introduction': 'var(--voice-active)',
                    'key_concepts': 'var(--cosmic-cyan)',
                    'questions': 'var(--spaceship-color)',
                    'conclusion': '#fbbf24'
                };
                
                contentDiv.innerHTML = `
                    <h4 style="color: ${typeColors[segmentType] || 'var(--text-primary)'}; margin-bottom: 1rem; text-transform: capitalize;">
                        ${segmentType.replace('_', ' ')}
                    </h4>
                    <p style="color: var(--text-primary); line-height: 1.6; font-size: 1rem;">
                        ${content}
                    </p>
                `;
                
                // Update progress
                const totalSegments = 1 + this.currentLesson.key_concepts.length + 
                                     this.currentLesson.interactive_questions.length + 1;
                const progress = (this.currentLessonSegment / totalSegments) * 100;
                this.updateProgressBar(progress);
            }
            
            nextLessonSegment() {
                if (!this.currentLesson || !this.isVoicePlaying) return;
                
                const totalConcepts = this.currentLesson.key_concepts.length;
                const totalQuestions = this.currentLesson.interactive_questions.length;
                
                if (this.currentLessonSegment === 1) {
                    this.playLessonSegment('key_concepts');
                } else if (this.currentLessonSegment <= 1 + totalConcepts) {
                    if (this.currentLessonSegment - 1 < totalConcepts) {
                        this.playLessonSegment('key_concepts');
                    } else {
                        this.playLessonSegment('questions');
                    }
                } else if (this.currentLessonSegment <= 1 + totalConcepts + totalQuestions) {
                    if (this.currentLessonSegment - 1 - totalConcepts < totalQuestions) {
                        this.playLessonSegment('questions');
                    } else {
                        this.playLessonSegment('conclusion');
                        this.currentLessonSegment++;
                    }
                } else {
                    this.completeLesson();
                }
            }
            
            completeLesson() {
                this.isVoicePlaying = false;
                this.updateVoiceStatus('Lesson complete! Point at another planet to continue exploring!');
                this.deactivateVoiceAssistant();
                this.updateProgressBar(100);
                
                document.getElementById('lessonContent').innerHTML = `
                    <div style="text-align: center; padding: 2rem;">
                        <h3 style="color: var(--spaceship-color); margin-bottom: 1rem;">Lesson Complete!</h3>
                        <p style="color: var(--text-primary); margin-bottom: 1rem;">
                            Congratulations! You've completed the voice lesson about ${this.currentLesson.planet_name}.
                        </p>
                        <p style="color: var(--text-secondary);">
                            Point at another planet to continue your space exploration journey!
                        </p>
                    </div>
                `;
            }
            
            toggleVoicePause() {
                if (this.speechSynthesis.speaking) {
                    if (this.speechSynthesis.paused) {
                        this.speechSynthesis.resume();
                        this.updateVoiceStatus('Resuming lesson...');
                        this.activateVoiceAssistant();
                    } else {
                        this.speechSynthesis.pause();
                        this.updateVoiceStatus('Lesson paused');
                        this.deactivateVoiceAssistant();
                    }
                } else {
                    this.isVoicePlaying = false;
                    this.updateVoiceStatus('No active lesson to pause');
                }
            }
            
            stopVoiceLesson() {
                this.speechSynthesis.cancel();
                this.isVoicePlaying = false;
                this.deactivateVoiceAssistant();
                this.updateVoiceStatus('Lesson stopped. Point at a planet to start a new lesson.');
            }
            
            speakText(text) {
                return new Promise((resolve) => {
                    if (this.currentUtterance) {
                        this.speechSynthesis.cancel();
                    }
                    
                    this.currentUtterance = new SpeechSynthesisUtterance(text);
                    this.currentUtterance.rate = 0.9;
                    this.currentUtterance.pitch = 1.0;
                    this.currentUtterance.volume = 0.8;
                    
                    // Try to use a more natural voice
                    const voices = this.speechSynthesis.getVoices();
                    const preferredVoice = voices.find(voice => 
                        voice.lang === 'en-US' && 
                        (voice.name.includes('Natural') || voice.name.includes('Neural'))
                    ) || voices.find(voice => voice.lang === 'en-US');
                    
                    if (preferredVoice) {
                        this.currentUtterance.voice = preferredVoice;
                    }
                    
                    this.currentUtterance.onend = () => {
                        resolve();
                    };
                    
                    this.currentUtterance.onerror = () => {
                        resolve();
                    };
                    
                    this.speechSynthesis.speak(this.currentUtterance);
                });
            }
            
            switchTab(tabName) {
                document.querySelectorAll('.tab').forEach(tab => {
                    tab.classList.remove('active');
                });
                document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');
                
                document.querySelectorAll('.tab-content').forEach(content => {
                    content.classList.remove('active');
                });
                document.getElementById(tabName).classList.add('active');
            }
            
            updateVoiceStatus(status) {
                document.getElementById('voiceStatus').textContent = status;
            }
            
            updateProgressBar(percentage) {
                document.getElementById('progressBar').style.width = percentage + '%';
            }
            
            activateVoiceAssistant() {
                document.getElementById('voiceAssistant').classList.add('speaking');
            }
            
            deactivateVoiceAssistant() {
                document.getElementById('voiceAssistant').classList.remove('speaking');
            }
        }
        
        // Initialize the platform when page loads
        document.addEventListener('DOMContentLoaded', () => {
            window.spacePlatform = new HandGestureSpaceTutor();
        });
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

# API Routes
@app.route('/api/hand-gestures')
def get_hand_gestures():
    """Return current hand gesture data"""
    try:
        gesture_data = {
            'hand_detected': len(hand_tracker.hand_landmarks) > 0,
            'current_gesture': None,
            'finger_position': {'x': 0, 'y': 0},
            'gesture_confidence': 0.0
        }
        
        # Determine current gesture
        if hand_tracker.gesture_state['pointing']:
            gesture_data['current_gesture'] = 'pointing'
            gesture_data['finger_position'] = {
                'x': hand_tracker.gesture_state['finger_position'][0],
                'y': hand_tracker.gesture_state['finger_position'][1]
            }
        elif hand_tracker.gesture_state['thumbs_up']:
            gesture_data['current_gesture'] = 'thumbs_up'
        elif hand_tracker.gesture_state['peace_sign']:
            gesture_data['current_gesture'] = 'peace_sign'
        elif hand_tracker.gesture_state['open_palm']:
            gesture_data['current_gesture'] = 'open_palm'
        
        return jsonify(gesture_data)
    except Exception as e:
        return jsonify({
            'error': str(e),
            'hand_detected': False,
            'current_gesture': None,
            'finger_position': {'x': 0, 'y': 0}
        }), 500

@app.route('/api/planet-data/<planet_name>')
def get_planet_data(planet_name):
    """Get detailed information about a specific planet"""
    try:
        planet_data = space_edu.get_planet_data(planet_name)
        if not planet_data:
            return jsonify({'error': 'Planet not found'}), 404
        return jsonify(planet_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/voice-lesson/<planet_name>')
def get_voice_lesson(planet_name):
    """Get voice lesson data for a specific planet"""
    try:
        lesson_data = space_edu.get_voice_lesson(planet_name)
        if not lesson_data:
            return jsonify({'error': 'Lesson not found'}), 404
        return jsonify(lesson_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/all-planets')
def get_all_planets():
    """Get basic information about all planets"""
    try:
        planets = {}
        for planet_name in space_edu.planets.keys():
            planet_data = space_edu.get_planet_data(planet_name)
            planets[planet_name] = {
                'name': planet_data.get('name', planet_name.capitalize()),
                'type': planet_data.get('type', 'Unknown'),
                'radius_km': planet_data.get('radius_km', 0),
                'moons': planet_data.get('moons', 0)
            }
        return jsonify(planets)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/system-status')
def get_system_status():
    """Get overall system status"""
    try:
        status = {
            'camera_active': hand_tracker.is_camera_active,
            'hand_tracking_available': hand_tracker.mp_hands is not None,
            'total_planets': len(space_edu.planets),
            'gesture_states': hand_tracker.gesture_state,
            'timestamp': datetime.now().isoformat()
        }
        return jsonify(status)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Cleanup function
def cleanup():
    """Clean up resources on app shutdown"""
    try:
        hand_tracker.stop_camera()
        print("Application cleanup completed")
    except Exception as e:
        print(f"Error during cleanup: {e}")

# Register cleanup function
import atexit
atexit.register(cleanup)

if __name__ == '__main__':
    try:
        print("=" * 60)
        print("🚀 VOICE AI SPACE TUTOR - HAND GESTURE CONTROL 🚀")
        print("=" * 60)
        print()
        print("✨ FEATURES:")
        print("   🖐️  Hand gesture recognition for planet selection")
        print("   🎤 Voice-guided educational content")
        print("   🌌 Interactive solar system visualization")
        print("   📹 Real-time camera feed with gesture overlay")
        print("   🎯 Point-and-learn interface")
        print()
        print("🎮 HAND GESTURES:")
        print("   👉 Point - Select planets")
        print("   👍 Thumbs Up - Play/Pause lessons")
        print("   ✌️  Peace Sign - Next segment")
        print("   🖐️  Open Palm - Stop lesson")
        print()
        print("📡 API ENDPOINTS:")
        print("   /api/hand-gestures - Current gesture data")
        print("   /api/planet-data/<name> - Planet information")
        print("   /api/voice-lesson/<name> - Educational content")
        print("   /api/all-planets - Overview of all celestial bodies")
        print("   /api/system-status - System health check")
        print()
        print("🌐 Access the application at: http://localhost:5000")
        print("📷 Make sure your camera is connected and permissions are granted.")
        print("💡 Position yourself 2-3 feet from the camera for best results.")
        print()
        print("=" * 60)
        
        # Start the Flask application
        app.run(debug=True, host='0.0.0.0', port=5000, threaded=True)
        
    except KeyboardInterrupt:
        print("\n🛑 Shutting down gracefully...")
        cleanup()
    except Exception as e:
        print(f"❌ Error starting application: {e}")
        cleanup()

# Requirements for installation:
"""
Required Python packages:
pip install flask opencv-python mediapipe numpy

Usage Instructions:
1. Save this code as 'space_tutor.py'
2. Install required packages: pip install flask opencv-python mediapipe numpy
3. Run: python space_tutor.py
4. Open browser to: http://localhost:5000
5. Allow camera permissions when prompted
6. Use hand gestures to interact with the solar system

Hand Gesture Controls:
- Point at planets to hover and select (hold for 2 seconds)
- Thumbs up to play/pause voice lessons
- Peace sign (two fingers) to skip to next lesson segment
- Open palm to stop current lesson

Educational Content:
- Comprehensive lessons for all planets and the Sun
- Introduction, key concepts, interactive questions, and conclusions
- Text-to-speech narration with natural voice selection
- Progress tracking and lesson management

Technical Features:
- MediaPipe for real-time hand tracking
- OpenCV for camera processing
- Flask web framework for the interface
- Canvas-based solar system animation
- RESTful API for data exchange
- Responsive design with space theme
"""
import cv2
import numpy as np
import random

class NewtonsLaws:
    """Interactive demo for Newton's Three Laws of Motion"""

    def __init__(self, width, height, menu_width):
        self.width = width
        self.height = height
        self.menu_width = menu_width
        self.objects = []
        self.current_law = 1
        self.selected_object = None
        self.mouse_pos = None
        self.dt = 0.016  # ~60 FPS
        self.last_time = cv2.getTickCount() / cv2.getTickFrequency()
        self.reset()

    def reset(self):
        """Initialize balls for simulation"""
        self.objects = []
        # Light, medium, heavy balls
        masses = [(1.0, (0,255,0)), (2.0, (0,150,255)), (3.0, (0,0,255))]
        for mass, color in masses:
            obj = {
                "pos": [random.randint(self.menu_width + 100, self.width - 100),
                        random.randint(100, self.height - 100)],
                "vel": [0.0, 0.0],
                "force": [0.0, 0.0],
                "radius": 25,
                "mass": mass,
                "color": color,
                "trail": []
            }
            self.objects.append(obj)

    def update_time(self):
        current = cv2.getTickCount() / cv2.getTickFrequency()
        self.dt = min(current - self.last_time, 0.033)
        self.last_time = current

    def handle_keypress(self, key):
        """Switch between laws"""
        if key == ord('1'):
            self.current_law = 1
        elif key == ord('2'):
            self.current_law = 2
        elif key == ord('3'):
            self.current_law = 3

    def handle_mouse(self, event, x, y, flags, param):
        """Mouse control of balls"""
        self.mouse_pos = (x, y)
        if event == cv2.EVENT_LBUTTONDOWN:
            for obj in self.objects:
                if np.linalg.norm(np.array(obj["pos"]) - np.array([x,y])) < obj["radius"]:
                    self.selected_object = obj
        elif event == cv2.EVENT_LBUTTONUP:
            self.selected_object = None

    def apply_damping(self, vel, damping=0.995):
        return [vel[0]*damping, vel[1]*damping]

    def clamp_position(self, x, y, margin=10):
        x = max(self.menu_width + margin, min(self.width - margin, x))
        y = max(margin, min(self.height - margin, y))
        return x, y

    def update(self):
        self.update_time()
        for obj in self.objects:
            # Reset force
            obj["force"] = [0.0, 0.0]

            # Mouse drag
            if self.selected_object is obj and self.mouse_pos:
                target = np.array(self.mouse_pos)
                pos = np.array(obj["pos"])
                direction = target - pos
                obj["force"] = (direction * 1.5).tolist()  # scale force

            # Acceleration = F/m
            acc = [obj["force"][0]/obj["mass"], obj["force"][1]/obj["mass"]]
            obj["vel"][0] += acc[0]*self.dt*60
            obj["vel"][1] += acc[1]*self.dt*60

            obj["vel"] = self.apply_damping(obj["vel"])
            obj["pos"][0] += obj["vel"][0]
            obj["pos"][1] += obj["vel"][1]

            obj["pos"][0], obj["pos"][1] = self.clamp_position(obj["pos"][0], obj["pos"][1])

            # Add to trail
            obj["trail"].append((int(obj["pos"][0]), int(obj["pos"][1])))
            if len(obj["trail"])>30:
                obj["trail"].pop(0)

        # Collisions
        self._handle_collisions()

    def _handle_collisions(self):
        for i in range(len(self.objects)):
            for j in range(i+1, len(self.objects)):
                o1,o2 = self.objects[i], self.objects[j]
                dx = o1["pos"][0] - o2["pos"][0]
                dy = o1["pos"][1] - o2["pos"][1]
                dist = np.hypot(dx, dy)
                if dist < o1["radius"] + o2["radius"]:
                    # Simple elastic collision
                    o1["vel"], o2["vel"] = o2["vel"], o1["vel"]

    def draw_grid(self, frame, spacing=50):
        for x in range(self.menu_width, self.width, spacing):
            cv2.line(frame,(x,0),(x,self.height),(50,50,50),1)
        for y in range(0,self.height,spacing):
            cv2.line(frame,(self.menu_width,y),(self.width,y),(50,50,50),1)

    def draw_vector(self, frame, start, vec, color=(255,0,255)):
        end = (int(start[0]+vec[0]), int(start[1]+vec[1]))
        cv2.arrowedLine(frame, (int(start[0]), int(start[1])), end, color, 2, tipLength=0.3)

    def render(self, frame):
        self.draw_grid(frame)

        for obj in self.objects:
            x,y = int(obj["pos"][0]), int(obj["pos"][1])
            # Trail
            for k in range(1,len(obj["trail"])):
                alpha = k/len(obj["trail"])
                color = tuple(int(c*alpha) for c in obj["color"])
                cv2.line(frame,obj["trail"][k-1],obj["trail"][k],color,2)

            cv2.circle(frame,(x,y),obj["radius"],obj["color"],-1)
            cv2.circle(frame,(x,y),obj["radius"],(255,255,255),2)
            cv2.putText(frame,f"m={obj['mass']}",(x-15,y-obj["radius"]-5),
                        cv2.FONT_HERSHEY_SIMPLEX,0.4,(255,255,255),1)

            # Draw velocity
            self.draw_vector(frame,(x,y),(obj["vel"][0]*5,obj["vel"][1]*5),(0,255,255))
            # Draw force
            self.draw_vector(frame,(x,y),(obj["force"][0]*0.1,obj["force"][1]*0.1),(255,0,255))

        self._draw_laws_explanation(frame)

    def _draw_laws_explanation(self, frame):
        laws = [
            "1st Law: Objects stay at rest/motion unless a force acts (Inertia)",
            "2nd Law: F = m * a (lighter balls accelerate more with same push)",
            "3rd Law: Action-Reaction (balls push each other on collision)"
        ]
        x,y,w,h = self.menu_width+10,50,600,130
        overlay = frame.copy()
        cv2.rectangle(overlay,(x,y),(x+w,y+h),(0,0,0),-1)
        cv2.addWeighted(overlay,0.6,frame,0.4,0,frame)

        for i,law in enumerate(laws):
            color = (0,255,0) if i+1==self.current_law else (200,200,200)
            cv2.putText(frame,law,(x+10,y+30+i*30),
                        cv2.FONT_HERSHEY_SIMPLEX,0.5,color,1)

# ---------------------- Main Loop ----------------------
if __name__=="__main__":
    WIDTH,HEIGHT=900,600
    MENU_WIDTH=150

    lesson = NewtonsLaws(WIDTH,HEIGHT,MENU_WIDTH)
    cv2.namedWindow("Newton's Laws Demo")
    cv2.setMouseCallback("Newton's Laws Demo", lesson.handle_mouse)

    while True:
        frame = 50*np.ones((HEIGHT,WIDTH,3),dtype=np.uint8)
        lesson.update()
        lesson.render(frame)

        cv2.imshow("Newton's Laws Demo",frame)
        key = cv2.waitKey(10) & 0xFF
        if key==27:
            break
        lesson.handle_keypress(key)

    cv2.destroyAllWindows()

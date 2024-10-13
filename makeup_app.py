import cv2
import mediapipe as mp
import itertools
import numpy as np
from scipy.interpolate import splev, splprep

class MakeupApplication:
    def __init__(self, min_detection_confidence=0.5, min_tracking_confidence=0.5):
        # Initialize mediapipe solutions
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(min_detection_confidence=min_detection_confidence,
                                                    min_tracking_confidence=min_tracking_confidence)

        # Precompute index lists for facial landmarks
        self.LEFT_EYE_INDEXES = list(set(itertools.chain(*self.mp_face_mesh.FACEMESH_LEFT_EYE)))
        self.RIGHT_EYE_INDEXES = list(set(itertools.chain(*self.mp_face_mesh.FACEMESH_RIGHT_EYE)))
        self.LIPS_INDEXES = list(set(itertools.chain(*self.mp_face_mesh.FACEMESH_LIPS)))
        self.LEFT_EYEBROW_INDEXES = list(set(itertools.chain(*self.mp_face_mesh.FACEMESH_LEFT_EYEBROW)))
        self.RIGHT_EYEBROW_INDEXES = list(set(itertools.chain(*self.mp_face_mesh.FACEMESH_RIGHT_EYEBROW)))    

    def apply_lipstick(self, image, landmarks, indexes, color, blur_kernel_size=(7, 7), blur_sigma=10, color_intensity=0.4):
        points = np.array([(int(landmarks[idx].x * image.shape[1]), int(landmarks[idx].y * image.shape[0])) for idx in indexes])

        mask = np.zeros(image.shape[:2], dtype=np.uint8)
        cv2.fillPoly(mask, [cv2.convexHull(points)], 255)

        boundary_mask = cv2.dilate(mask, np.ones((3, 3), np.uint8), iterations=1)

        colored_image = np.zeros_like(image)
        colored_image[:] = color

        lipstick_image = cv2.bitwise_and(colored_image, colored_image, mask=boundary_mask)
        lips_colored = cv2.addWeighted(image, 1, lipstick_image, color_intensity, 0)

        blurred = cv2.GaussianBlur(lips_colored, blur_kernel_size, blur_sigma)

        gradient_mask = cv2.GaussianBlur(boundary_mask, (15, 15), 0)
        gradient_mask = gradient_mask / 255.0
        lips_with_gradient = (blurred * gradient_mask[..., np.newaxis] + image * (1 - gradient_mask[..., np.newaxis])).astype(np.uint8)

        final_image = np.where(boundary_mask[..., np.newaxis] == 0, image, lips_with_gradient)
        return final_image

    def process_frame(self, frame):
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        rgb_frame.flags.writeable = False
        results = self.face_mesh.process(rgb_frame)
        rgb_frame.flags.writeable = True

        if results.multi_face_landmarks:
            for face_no, face_landmarks in enumerate(results.multi_face_landmarks):
        
                frame = self.apply_lipstick(frame, face_landmarks.landmark, self.LIPS_INDEXES, (0, 0, 255))

                cheek_indices = [234, 454]
                chin_index = 152

        return frame

    def start_video(self):
        cap = cv2.VideoCapture(0)
        while cap.isOpened():
            success, frame = cap.read()
            if not success:
                print("Ignoring empty camera frame.")
                continue

            frame = self.process_frame(frame)

            cv2.imshow('Makeup Application', frame)
            if cv2.waitKey(5) & 0xFF == 27:
                break

        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    makeup_app = MakeupApplication()
    makeup_app.start_video()

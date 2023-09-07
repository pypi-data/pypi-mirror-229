import time

import cv2
from cvzone.FaceMeshModule import FaceMeshDetector
from math import hypot
from time import sleep


class EyeDetector:
    def __init__(self):
        self.detector = FaceMeshDetector(maxFaces=1, minDetectionCon=0.75)

    def find_eye_points(self, img):
        img, faces = self.detector.findFaceMesh(img, draw=False)
        eye_points = []
        ratio = 0

        if faces:
            face = faces[0]

            left_right = face[243]
            left_left = face[130]
            left_up = face[27]
            left_down = face[23]

            cv2.circle(img, left_up, 2, (255, 0, 255), 2)
            cv2.circle(img, left_down, 2, (255, 0, 255), 2)
            cv2.circle(img, left_left, 2, (255, 0, 255), 2)
            cv2.circle(img, left_right, 2, (255, 0, 255), 2)

            horizontal_line = cv2.line(img, left_left, left_right, (0, 255, 0), 2)
            vertical_line = cv2.line(img, left_up, left_down, (0, 255, 0), 2)

            horizontal_line_length = hypot((left_left[0] - left_right[0]), (left_left[1] - left_right[1]))
            vertical_line_length = hypot((left_up[0] - left_down[0]), (left_up[1] - left_down[1]))

            ratio = horizontal_line_length / vertical_line_length

            eye_points = [
                left_right, left_up, left_down, left_left
            ]

        return img, eye_points, ratio


if __name__ == "__main__":
    cap = cv2.VideoCapture(0)
    eye_detector = EyeDetector()

    while True:
        success, img = cap.read()
        img, eye_points, ratio = eye_detector.find_eye_points(img)

        if eye_points:
            for point in eye_points:
                x, y = point
                cv2.circle(img, (x, y), 2, (255, 0, 255), cv2.FILLED)

        if ratio > 3:
            print("Blinking")
            time.sleep(1)

        cv2.imshow("Images", img)
        if cv2.waitKey(1) == 27:  # Press 'Esc' key to exit
            break

    cap.release()
    cv2.destroyAllWindows()

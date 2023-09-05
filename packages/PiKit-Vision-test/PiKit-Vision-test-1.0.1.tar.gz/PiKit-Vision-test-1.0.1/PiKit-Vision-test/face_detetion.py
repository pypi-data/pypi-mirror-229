import cv2
from . import *


face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')

cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=2, minSize=(100, 100))

    # 存储筛选后的人脸框
    filtered_faces = []

    for (x, y, w, h) in faces:
        # 计算当前人脸框的中心点坐标
        center_x = x + w // 2
        center_y = y + h // 2

        # 检查当前人脸框是否被其他人脸框包含
        is_inside = False
        for (fx, fy, fw, fh) in faces:
            # 计算其他人脸框的中心点坐标
            face_center_x = fx + fw // 2
            face_center_y = fy + fh // 2

            # 检查小框的中心点是否被大框框住，并且小框相对于大框来说较小
            if (fx < center_x < fx + fw) and (fy < center_y < fy + fh) and (w * h < fw * fh):
                is_inside = True
                break

        # 如果当前人脸框不被其他人脸框包含，则将其添加到筛选后的人脸框列表中
        if not is_inside:
            filtered_faces.append((x, y, w, h))

    for (x, y, w, h) in filtered_faces:
        cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
 
    cv2.imshow('Face Detection', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
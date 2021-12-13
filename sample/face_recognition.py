import cv2
import dlib
import config

class face_recognition ():

    # コンストラクタ
    def __init__(self) :
        self.detector = dlib.get_frontal_face_detector()
        self.landmark_predictor = dlib.shape_predictor(config.get_predictor_pass())

    # 画像の入力すると顔の位置を返す関数
    def get_face_position(self, frame) :

        # 処理高速化のためのグレイスケール化
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # 顔認証
        faces = self.detector(gray)

        # 顔の位置格納用配列
        face_position = []

        if len(faces) == 0:
            return face_position, False
        else:
            face = faces[0]
            face_position.append((face.left(),  face.top()))        # face_position[0]: 左上
            face_position.append((face.right(), face.top()))        # face_position[1]: 右上
            face_position.append((face.left(),  face.bottom()))     # face_position[2]: 左下
            face_position.append((face.right(), face.bottom()))     # face_position[3]: 右下
            return face_position, True

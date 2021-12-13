# -*- coding: utf-8 -*-
import tkinter
from tkinter.constants import TRUE
import cv2
import dlib
import numpy as np
import time
from PIL import Image, ImageTk

class VideoViewer(tkinter.Frame):

    #コンストラクタ
    def __init__(self, master=None):
        super().__init__(master)

        #サイズを決める
        master.geometry('600x500')

        #自身(tkinter.Frame)をmaster（mainで作ったroot）に配置
        self.master = master
        self.pack()

        # MainPanel を 全体に配置
        self.mainpanel = tkinter.Label(root)
        self.mainpanel.pack(expand=1)

        self.btngray  = tkinter.Button(root, text='land', command=self.vis_land)
        self.btncolor = tkinter.Button(root, text='rect', command=self.vis_rect)
        self.btngray.pack(side="left")
        self.btncolor.pack(side="left")

        self.rec_text = tkinter.StringVar()
        self.rec_text.set("FALSE")
        self.rec_label = tkinter.Label(root, textvariable=self.rec_text)
        self.rec_label.pack(side="right")

        self.spk_text = tkinter.StringVar()
        self.spk_text.set("")
        self.spk_label = tkinter.Label(root, textvariable=self.spk_text)
        self.spk_label.pack(side="right")

        self.scaler = 0.5
        self.detector = dlib.get_frontal_face_detector()
        self.landmark_predictor = dlib.shape_predictor('learned-models/shape_predictor_68_face_landmarks.dat')
        
        self.cap   = cv2.VideoCapture( 0 )
        ret, frame = self.cap.read()
        if ret == 0 :
            print("failed to webcam")
            exit()
        
        self.do_land = False
        self.do_rect = False

        self.close_time = time.time()
        self.close_flag = False
        self.close_buf = 1.0

    #ボタンが呼び出す関数を作成
    #インスタンス関数として億
    def vis_land(self):
        self.do_land = not self.do_land

    def vis_rect(self):
        self.do_rect = not self.do_rect

    def update_video(self):
        ret, frame = self.cap.read()
        self.master.geometry('600x500')
        frame = cv2.resize(frame, (600,450), interpolation=cv2.INTER_LANCZOS4)
        # frame = cv2.resize(frame, (int(frame.shape[1] * self.scaler), int(frame.shape[0] * self.scaler)), interpolation=cv2.INTER_LANCZOS4)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.detector(gray)

        if len(faces) == 0:
            self.rec_text.set("FALSE")
            self.spk_text.set("CLOSE")
        else:
            self.rec_text.set("TRUE")

            for face in faces:
                if self.do_rect:    # 長方形描画
                    frame = cv2.rectangle(frame, pt1=(face.left(), face.top()), pt2=(face.right(), face.bottom()), color=(255, 255, 255), lineType=cv2.LINE_AA, thickness=2)
                
                dlib_shape = self.landmark_predictor(gray ,face)
                shape_2d = np.array([[p.x, p.y] for p in dlib_shape.parts()])

                dist1 = []
                dist2 = []
                if self.do_land:
                    for s in shape_2d:
                        cv2.circle(frame, center=tuple(s), radius=1, color=(255, 255, 255), thickness=2, lineType=cv2.LINE_AA)
                        
                dist1.append(shape_2d[62])
                dist1.append(shape_2d[66])
                dist2.append(shape_2d[8])
                dist2.append(shape_2d[27])

                distance1 = ((dist1[0][0] - dist1[1][0])**2 + (dist1[0][1]-dist1[1][1])**2)**0.5
                distance2 = ((dist2[0][0] - dist2[1][0])**2 + (dist2[0][1]-dist2[1][1])**2)**0.5
                if distance1/distance2*100 > 10.0:
                    self.spk_text.set("OPEN")
                    self.close_flag = False
                else :
                    if self.close_flag:
                        if time.time() - self.close_time > self.close_buf:
                            self.spk_text.set("CLOSE")
                    else:
                        self.close_time = time.time()
                        self.close_flag = True

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        imgtk = ImageTk.PhotoImage(image=Image.fromarray(frame))
        self.mainpanel.imgtk = imgtk
        self.mainpanel.configure(image=imgtk)

        #66ms後に自分自身を呼ぶ
        self.mainpanel.after(10, self.update_video)

if __name__ == "__main__":
    root = tkinter.Tk()
    dlg = VideoViewer(master=root)
    dlg.update_video()
    dlg.mainloop()

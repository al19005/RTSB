# -*- coding: utf-8 -*-
import tkinter
from tkinter.constants import TRUE
from PIL import Image, ImageTk
import cv2
import face_recognition

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
        
        # face_recognitionクラスのインスタンス作成
        self.face_rec = face_recognition.face_recognition()

        self.cap   = cv2.VideoCapture( 0 )
        ret, frame = self.cap.read()
        if ret == 0 :
            print("failed to webcam")
            exit()
        

    #ボタンが呼び出す関数を作成
    def update_video(self):
        ret, frame = self.cap.read()
        self.master.geometry('600x500')
        frame = cv2.resize(frame, (600,450), interpolation=cv2.INTER_LANCZOS4)
        
        # ここが外部ファイルを使う部分------------------------------------------
        # 顔の位置(face_position), 顔認識の成功か失敗(face_rec)
        face_position, face_rec = self.face_rec.get_face_position(frame)

        if face_rec:        # 認識が成功したら( face_rec == True なら )
            # 長方形描画
            frame = cv2.rectangle(
                frame, 
                pt1=face_position[0], 
                pt2=face_position[3], 
                color=(255, 255, 255), 
                lineType=cv2.LINE_AA, 
                thickness=2)
        #----------------------------------------------------------------------

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

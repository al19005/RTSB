# -*- coding: utf-8 -*-
import tkinter
import cv2
import numpy as np
from PIL import Image, ImageTk, ImageFont, ImageDraw
# $dir C:\Windows\Fonts

FONT_PATH = "C:/Windows/Fonts/NotoSansJP-Regular.otf"
FONT_SIZE = 24
RECT_ALPHA = 0.7

class VideoViewer(tkinter.Frame):

    #コンストラクタ
    def __init__(self, master=None):
        super().__init__(master)
        #サイズを決める
        master.geometry('854x530')

        #自身(tkinter.Frame)をmaster（mainで作ったroot）に配置
        self.master = master
        self.pack()

        # MainPanel を 全体に配置
        self.mainpanel = tkinter.Label(root)
        self.mainpanel.pack(expand=1)

        #ボタンを作る（rootに紐づけし、押された時に起動する関数も指定）
        self.btngray  = tkinter.Button(root, text='gray', command=self.vis_gray)
        self.btncolor = tkinter.Button(root, text='color', command=self.vis_color)
        self.btngray.pack(side="left")
        self.btncolor.pack(side="left")

        #open web cam stream (複数webcamがある場合は，引数を変更する)
        self.cap   = cv2.VideoCapture( 0 )
        ret, frame = self.cap.read()
        if ret == 0 :
            print("failed to webcam")
            exit()
        self.do_gray = False
        
        #描画するフォントを設定
        self.font = ImageFont.truetype(FONT_PATH, FONT_SIZE)

    #ボタンが呼び出す関数を作成
    #インスタンス関数として億
    def vis_gray(self):
        self.do_gray = True

    def vis_color(self):
        self.do_gray = False

    def update_video(self):
        ret, frame = self.cap.read()

        self.master.geometry('854x530')
        frame = cv2.resize(frame, (854,480), interpolation=cv2.INTER_LANCZOS4)
        if self.do_gray :
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
        else :
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        #描画位置の設定
        text_loc_x, text_loc_y = 50, 100
        #長方形のサイズを設定
        rect_w, rect_h = 200, 250
        #長方形を用意
        rect_img = np.reshape( np.full(rect_w*rect_h*3, 255), (rect_h, rect_w, 3))
        #長方形を合成
        frame[text_loc_y:text_loc_y+rect_h, text_loc_x:text_loc_x+rect_w] = frame[text_loc_y:text_loc_y+rect_h, text_loc_x:text_loc_x+rect_w]*(1-RECT_ALPHA) + rect_img*RECT_ALPHA

        #テキストを描画
        frame = Image.fromarray(frame) #PIL型の画像に変換
        ImageDraw.Draw(frame).text((text_loc_x, text_loc_y), "ここに文字を描画", font=self.font, fill=(0, 0, 255, 0))
        frame = np.array(frame) #画像をNumPy型へ再変換
        
        #画像を表示
        imgtk = ImageTk.PhotoImage(image=Image.fromarray(frame))
        self.mainpanel.imgtk = imgtk
        self.mainpanel.configure(image=imgtk)

        #66ms後に自分自身を呼ぶ
        self.mainpanel.after(33, self.update_video)

if __name__ == "__main__":
    root = tkinter.Tk()
    dlg = VideoViewer(master=root)
    dlg.update_video()
    dlg.mainloop()

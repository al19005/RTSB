# -*- coding: utf-8 -*-
import tkinter
import cv2
import numpy as np
from PIL import Image, ImageTk, ImageFont, ImageDraw
# config ファイル
import config
import face_recognition, SpeechToTextGenerator

# $dir C:\Windows\Fonts
# 使うフォントのpath設定してください
FONT_PATH = config.get_font_pass()
FONT_SIZE = 11

pre_x, pre_y = 50,100

class VideoViewer(tkinter.Frame):

    RECT_ALPHA = 0.7
    
    #コンストラクタ
    def __init__(self, master=None):
        super().__init__(master)
        #サイズを決める
        master.geometry('600x500')

        #長方形のサイズを設定
        self.rect_w, self.rect_h = 150,200

        self.log = ""
        #self.updating_text = ""

        #自身(tkinter.Frame)をmaster（mainで作ったroot）に配置
        self.master = master
        self.pack()

        self.face_rec =face_recognition.face_recognition()

        # MainPanel を 全体に配置
        self.mainpanel = tkinter.Label(root)
        self.mainpanel.pack(expand=1)

        #ボタンを作る（rootに紐づけし、押された時に起動する関数も指定）
        self.btn_raise_alpha  = tkinter.Button(root, text='透過度を上げる', command=self.raise_alpha)
        self.btn_lower_alpha = tkinter.Button(root, text='透過度を下げる', command=self.lower_alpha)
        self.btn_raise_alpha.pack(side="left")
        self.btn_lower_alpha.pack(side="left")

        #open web cam stream (複数webcamがある場合は，引数を変更する)
        self.cap   = cv2.VideoCapture( 0 )
        ret, frame = self.cap.read()
        if ret == 0 :
            print("failed to webcam")
            exit()
        self.do_gray = False
        
        #描画するフォントを設定
        self.font = ImageFont.truetype(FONT_PATH, FONT_SIZE)
        self.dummy_draw = ImageDraw.Draw(Image.new("RGB", (0,0)))

        #音声を拾い文字起こしをする
        self.speechToTextGenerator = SpeechToTextGenerator.SpeechToTextGenerator()

    #マイクと音声認識を止める
    def exit_speechToTextGenerator(self):
        print("exit_speechToTextGenerator")
        self.speechToTextGenerator.exit()

    #ボタンが呼び出す関数を作成
    #インスタンス関数として億
    def raise_alpha(self):
        VideoViewer.RECT_ALPHA = min(VideoViewer.RECT_ALPHA+0.1, 1.0)

    def lower_alpha(self):
        VideoViewer.RECT_ALPHA = max(VideoViewer.RECT_ALPHA-0.1, 0.0)
    
    def get_textsize(self, text):
        font_w, font_h = self.dummy_draw.textsize(text, font=self.font)
        return font_w, int(1.1*font_h)

    def get_format_text(self, text):
        text_len = len(text)
        if text_len == 0:
            return ""
        text_w, text_h = self.get_textsize(text)
        line_size = int(self.rect_w / (text_w/text_len))
        format_text = ""
        i = 0
        #print(text_len, line_size)
        while text_len > i:
            format_text += text[i:min(i+line_size, text_len)] + "\n"
            i += line_size
        #print(format_text)
        return format_text


    def update_video(self):
        ret, frame = self.cap.read()

        self.master.geometry('600x500')
        frame = cv2.resize(frame, (600,450), interpolation=cv2.INTER_LANCZOS4)
        if self.do_gray :
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
        else :
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        #描画位置の設定(吹き出し)
        text_loc_x, text_loc_y = 50,100 #初期化
        face_position , face_rec= self.face_rec.get_face_position(frame) #顔の位置取得
        
        global pre_x
        global pre_y

        if face_rec:#顔認識成功時
            text_loc_x, text_loc_y = face_position[0]
            #位置調整
            text_loc_x = text_loc_x - 170
            text_loc_y = text_loc_y - 30
            #吹き出しの上下処理
            if text_loc_y < 0 :
                text_loc_y =0
            elif text_loc_y > 250:
                text_loc_y = 250
            #吹き出しの左右処理
            if text_loc_x < 0 :
                text_loc_x = text_loc_x + 340
            #顔認識成功時の位置を変数で保持
            pre_x = text_loc_x
            pre_y = text_loc_y

        else :   #顔認識失敗時
            text_loc_x = pre_x #最後の吹き出し位置を表示
            text_loc_y = pre_y

            
                
        
        #長方形を用意
        rect_img = np.reshape( np.full(self.rect_w*self.rect_h*3, 255), (self.rect_h, self.rect_w, 3))
        #長方形を合成
        frame[text_loc_y:text_loc_y+self.rect_h, text_loc_x:text_loc_x+self.rect_w] = frame[text_loc_y:text_loc_y+self.rect_h, text_loc_x:text_loc_x+self.rect_w]*(1-VideoViewer.RECT_ALPHA) + rect_img*VideoViewer.RECT_ALPHA

        #テキストを描画
        is_sentence_end, text = self.speechToTextGenerator.get_speech()
        if is_sentence_end :
            t = self.log + text
            #吹き出しのはみ出し処理
            t_len = len(t)
            #print(t_len)
            while t_len>169:
                t = t[13:t_len]
                t_len = t_len -13
            self.log = t
            text = ""
        


        frame = Image.fromarray(frame) #PIL型の画像に変換
        ImageDraw.Draw(frame).text((text_loc_x, text_loc_y), self.get_format_text(self.log + text), font=self.font, fill=(0, 0, 255, 0))
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
    dlg.exit_speechToTextGenerator()

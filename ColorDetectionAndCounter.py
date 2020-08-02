import tkinter
import numpy as np
import cv2
import PIL.Image, PIL.ImageTk
import datetime
import json
import time

class Application:
    def __init__(self, window=None):

        # init var
        self.update_delay = 15
        self.update_datetime_count = 0
        self.update_autosave_count = 0
        self.video_source = 0
        self.datetime_now = datetime.datetime.now()
        self.data_file_path = '/var/www/html/data.json'
        self.last_update_database = None
        self.database_key = None
        self.good_count = 0
        self.waste_count = 0
        self.app_startup = True

        # delay start up for RTC
        time.sleep(30)

        # create window
        self.window = window
        self.window.configure(bg="black")
        #self.window.iconbitmap('favicon.ico')
        self.window.title('SUKANTHA')
        #self.window.geometry('800x480')
        #self.window.resizable(True, True)
        self.window.attributes('-fullscreen', True)

        #===== TODO =====
        # init webcam video
        self.vid = MyVideoCapture(self.video_source)

        # init database file
        self.db = MyDatabase(self.data_file_path)
        self.db.read_database()
        
        # add webcam view
        self.cv_video = tkinter.Canvas(window, width=400, height=400)
        self.cv_video.place(x=0, y=0)

        # add image view
        self.cv_image = tkinter.Canvas(window, width=400, height=400)
        self.cv_image.place(x=400, y=0)
        self.image_file = PIL.ImageTk.PhotoImage(file='/home/pi/Kaotang/sukantha_logo.png')
        self.cv_image.create_image(0, 0, image=self.image_file, anchor=tkinter.NW)

        # add button snapshot
        self.btn_snapshot = tkinter.Button(window,
                                           text="วิเคราะห์",
                                           width=45,
                                           height=4,
                                           fg="light cyan" ,
                                           bg="DeepSkyBlue2",
                                           activebackground="DeepSkyBlue2",
                                           command=self.snapshot)
        self.btn_snapshot.place(x=400, y=410)

        # add button close window
        self.btn_close_window = tkinter.Button(window,
                                               text="ปิดระบบ",
                                               width=8,
                                               height=4,
                                               bg="red3",
                                               activebackground="red3",
                                               command=self.close_window)
        self.btn_close_window.place(x=729, y=410)

        # add datatime view
        self.lb_datetime = tkinter.Label(window,
                                         text="วัน-เวลา :",
                                         fg="gray95", bg="black")
        self.lb_datetime.place(x=5, y=445)
        
        self.lb_7seg_datetime = tkinter.Label(window,
                                              text="00-00-00   00:00:00",
                                              fg="DeepSkyBlue2", bg="black",
                                              font="DSEG14Classic 10 bold")
        self.lb_7seg_datetime.place(x=5, y=462)

        # add process view
        self.lb_total = tkinter.Label(window,
                                      text="รวม :",
                                      fg="gray95", bg="black")
        self.lb_total.place(x=284, y=412)
        
        self.lb_good = tkinter.Label(window,
                                     text="ดี     :",
                                     fg="gray95", bg="black")
        self.lb_good.place(x=284, y=435)

        self.lb_waste = tkinter.Label(window,
                                      text="เสีย  :",
                                      fg="gray95", bg="black")
        self.lb_waste.place(x=284, y=458)

        self.lb_7seg_total = tkinter.Label(window,
                                           text="00000",
                                           fg="yellow",
                                           bg="black",
                                           font="DSEG14Classic 14 bold")
        self.lb_7seg_total.place(x=315, y=410)
        
        self.lb_7seg_good = tkinter.Label(window,
                                          text="00000",
                                          fg="green",
                                          bg="black",
                                          font="DSEG14Classic 14 bold")
        self.lb_7seg_good.place(x=315, y=433)
        
        self.lb_7seg_waste = tkinter.Label(window,
                                           text="00000",
                                           fg="red",
                                           bg="black",
                                           font="DSEG14Classic 14 bold")
        self.lb_7seg_waste.place(x=315, y=456)

        #===== End TODO =====
        self.window.protocol("WM_DELETE_WINDOW", self.close_window)
        
        self.update()
        self.window.mainloop()

    def snapshot(self):
        hsv_img = cv2.cvtColor(self.crop_frame, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv_img, np.array([50, 40, 40], dtype=np.uint8), np.array([100, 250, 250], dtype=np.uint8))
        decontamination_mask = cv2.inRange(hsv_img, np.array([0, 50, 50], dtype=np.uint8), np.array([235, 173, 127], dtype=np.uint8))
        #decontamination_mask = cv2.inRange(hsv_img, np.array([30, 20, 20], dtype=np.uint8), np.array([70, 80, 80], dtype=np.uint8))

        # org
        obj_cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]
        if len(obj_cnts)>0:
            obj_area = max(obj_cnts, key=cv2.contourArea)
            (xg,yg,wg,hg) = cv2.boundingRect(obj_area)
            cv2.rectangle(self.crop_frame,(xg,yg),(xg+wg, yg+hg),(0,255,0),2)

        # decontamination
        decontamination_obj_cnts = cv2.findContours(decontamination_mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]
        if len(decontamination_obj_cnts)>0:
            obj_area = max(decontamination_obj_cnts, key=cv2.contourArea)
            (xg,yg,wg,hg) = cv2.boundingRect(obj_area)
            cv2.rectangle(self.crop_frame,(xg,yg),(xg+wg, yg+hg),(255,0,0),2)
  
        # view
        self.image_file = PIL.ImageTk.PhotoImage(image = PIL.Image.fromarray(self.crop_frame))
        self.cv_image.create_image(0, 0, image=self.image_file, anchor=tkinter.NW)

        if len(obj_cnts) > 0 and len(decontamination_obj_cnts) > 0 :
            self.waste_count += 1
        if len(obj_cnts) > 0 and len(decontamination_obj_cnts) == 0 :
            self.good_count += 1

        str_buff = str(self.good_count + self.waste_count)
        while len(str_buff) < 5 :
            str_buff = '0' + str_buff
        self.lb_7seg_total.config(text=str_buff)
        
        str_buff = str(self.good_count)
        while len(str_buff) < 5 :
            str_buff = '0' + str_buff
        self.lb_7seg_good.config(text=str_buff)

        str_buff = str(self.waste_count)
        while len(str_buff) < 5 :
            str_buff = '0' + str_buff
        self.lb_7seg_waste.config(text=str_buff)

        self.db.update_database(self.database_key, str(self.good_count), str(self.waste_count))

    def close_window(self):
        self.db.write_database()
        self.window.destroy()

    def update(self):
        #===== TODO =====
        # update video
        ret, frame = self.vid.get_frame()
        if ret:
            self.crop_frame = frame[40:440, 120:520]
            self.image_frame = PIL.ImageTk.PhotoImage(image = PIL.Image.fromarray(self.crop_frame))
            self.cv_video.create_image(0, 0, image = self.image_frame, anchor = tkinter.NW)

        # update datetime
        if (self.update_datetime_count > 2):
            self.datetime_now = datetime.datetime.now()
            str_datetime = self.datetime_now.strftime("%d")
            str_datetime += "-"
            str_datetime += self.datetime_now.strftime("%m")
            str_datetime += "-"
            str_datetime += self.datetime_now.strftime("%Y")
            str_datetime += "   "
            str_datetime += self.datetime_now.strftime("%H")
            str_datetime += ":"
            str_datetime += self.datetime_now.strftime("%M")
            str_datetime += ":"
            str_datetime += self.datetime_now.strftime("%S")

            # str_key for json_key
            self.database_key = str(self.datetime_now.strftime("%Y"))
            self.database_key += str(self.datetime_now.strftime("%m"))
            self.database_key += str(self.datetime_now.strftime("%d"))

            # update date time to display
            self.lb_7seg_datetime.config(text=str_datetime)
            
            # update counter
            self.update_datetime_count = 0
        else:
            self.update_datetime_count += 1

        # update database
        if self.last_update_database == None:
            self.last_update_database = str(self.database_key)
        if self.db.get_key(self.database_key) == False:
            self.db.update_database(self.database_key, '0', '0')
            self.good_count = 0
            self.waste_count = 0
        if self.app_startup == True:
            buff_1, buff_2 = self.db.get_values(self.database_key)
            if (buff_1 != None) and (buff_2 != None):
                self.good_count = int(buff_1)
                self.waste_count = int(buff_2)

                while len(buff_1) < 5 :
                    buff_1 = '0' + buff_1
                self.lb_7seg_good.config(text=buff_1)
                while len(buff_2) < 5 :
                    buff_2 = '0' + buff_2
                self.lb_7seg_waste.config(text=buff_2)
                buff_1 = str(self.good_count + self.waste_count)
                while len(buff_1) < 5 :
                    buff_1 = '0' + buff_1
                self.lb_7seg_total.config(text=buff_1)
                
                self.app_startup = False

        # auto save json file
        if self.update_autosave_count > 10000:
            self.db.write_database()
            self.update_autosave_count = 0
        else:
            self.update_autosave_count += 1
        
        #===== End TODO =====
        self.window.after(self.update_delay, self.update)

class MyVideoCapture:
    def __init__(self, video_source=0):
        self.vid = cv2.VideoCapture(video_source)
        if not self.vid.isOpened():
            raise ValueError("Unable to open video source", video_source)

    def get_frame(self):
        if self.vid.isOpened():
            ret, frame = self.vid.read()
            if ret:
                return (ret, cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            else:
                return (ret, None)
        else:
            return (ret, None)

    def get_width(self):
        return (self.vid.get(cv2.CAP_PROP_FRAME_WIDTH))

    def get_height(self):
        return (self.vid.get(cv2.CAP_PROP_FRAME_HEIGHT))

    def __del__(self):
        if self.vid.isOpened():
            self.vid.release()

class MyDatabase: 
    def __init__(self, file_path):
        self.file_path = file_path
        self.json_data = None
    
    def read_database(self):
        with open(self.file_path) as json_file:
            self.json_data = json.load(json_file)
            json_file.close()

    def write_database(self):
        with open(self.file_path, 'w', encoding='utf-8') as json_file:
            json.dump(self.json_data, json_file, ensure_ascii=False, indent=4)
            json_file.close()
        #print('Save')

    def update_database(self, str_key, str_good, str_waste):
        if str_key != None:
            db_key_update = False
            for p in self.json_data['data']:
                if str(p['date']) == str_key:
                    p['good']=str_good
                    p['waste']=str_waste
                    db_key_update = True

            if db_key_update != True:
                self.json_data['data'].append({
                    'date':str_key,
                    'good':str(str_good),
                    'waste':str(str_waste)
                    })

    def get_key(self, str_key):
        if str_key == None:
            return False
        for p in self.json_data['data']:
            if str(p['date']) == str_key:
                return True
        return False

    def get_values(self, str_key):
        if str_key == None:
            return None, None
        for p in self.json_data['data']:
            if str(p['date']) == str_key:
                return str(p['good']), str(p['waste'])
        return None, None

    def print_database(self):
        print('======= data.json=========')
        for p in self.json_data['data']:
            print('date = ' + str(p['date']))
            print('good = ' + str(p['good']))
            print('waste = ' + str(p['waste']))
        print('==========================')
            
    def __del__(self):
        pass

if __name__ == "__main__":
    app = Application(tkinter.Tk())

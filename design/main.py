import os
import sys
import pickle
import json
import pandas as pd
import numpy as np
import itertools
from itertools import combinations
from PyQt5.QtWidgets import QApplication, QMainWindow,QWidget,QComboBox
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QGraphicsPixmapItem, QGraphicsScene
from main_ui import Ui_Form
class MyMainForm(QWidget,Ui_Form):
    def __init__(self, parent=None,imgs_path=None,path_res=None,path_eve= None,path_eves = None):
        super(MyMainForm, self).__init__(parent)
        self.setupUi(self)
        self.verb_b_list=[self.verb0,self.verb1,self.verb2,self.verb3,self.verb4]
        self.eve_b_list=[self.event0,self.event1,self.event2,self.event3,self.event4]
        self.sen_b_list = [self.sen0,self.sen1,self.sen2,self.sen3,self.sen4]
        self.data_e = self.load_eve(path_eve)
        self.load_eves(path_eves)
        self.load_list(imgs_path)
        self.pointer = 1
        self.res = pd.DataFrame()
        self.len_res = 0
        self.connects()
        self.get_datas()
    def connects(self):
        self.reload.clicked.connect(lambda:self.re_load())
        self.updata.clicked.connect(lambda:self.load_con(path_res))
        self.save.clicked.connect(lambda:self.save_res(path_res))
        self.next_img.clicked.connect(lambda:self.next_pointer())
        self.previous_img.clicked.connect(lambda:self.last_pointer())
        self.jump_img.clicked.connect(lambda:self.jump_pointer(self.jump_list.currentIndex()))
    def load_list(self,path):#load the img_list
        listimg0 = os.listdir(os.path.join(path,'train2014'))
        self.trains = []
        for file in listimg0:
                new=file.split('_')[2][5:11]
                self.trains.append(new)
        listimg1 = os.listdir(os.path.join(path,'val2014'))
        self.val = []
        for file in listimg1:
                new=file.split('_')[2][5:11]
                self.val.append(new)
        # self.label.setText()
        # return listimg
    def load_eve(self,path_eve):# load the events 
        with open(path_eve,'rb') as fo:
            datas_eve = pickle.load(fo)
            fo.close()
        imgs = list(datas_eve['imgid'])
        imgs2 = [k for k, g in itertools.groupby(imgs)]
        self.imgs = imgs2
        return datas_eve
    def load_eves(self,path_eves):# load the events for every verb
        with open(path_eves,'r') as fo:
                verb_eves = json.load(fo)
                fo.close()
        self.verb_eves = verb_eves
    def load_con(self,path_res):# load the last result to continue
        with open(path_res,'rb') as fo:
            loaders = pickle.load(fo)
            fo.close()
        try:
            self.pointer = len(set(loaders['imgid']))
            self.len_res = self.pointer
            self.res = loaders
        except KeyError:
            self.pointer = 1
            self.res = pd.DataFrame()
        self.get_datas()
    def re_load(self): # start the test from zero
        self.pointer = 1
        self.len_res = 0
        self.res = pd.DataFrame()
        self.get_datas()
    def save_res(self,path_res): # save the lastest result to the path_res
        with open(path_res,'wb') as fo:
            pickle.dump(self.res,fo)
            fo.close()
        self.label.setText('this result have been saved')
    def save_imm(self,events):
        count = 0
        if self.len_res <self.pointer:
            for iter in events.itertuples(): #update the events of the img select
                    self.data_e.loc[iter[0],'verbs'] = [[self.verb_b_list[count].currentText()]]
                    self.data_e.loc[iter[0],'event'] = self.eve_b_list[count].currentText()
                    count = count + 1
            self.res = pd.concat([self.res,events])
            self.len_res = self.len_res + 1
        else:
            for iter in events.itertuples():
                self.res.loc[iter[0],'verbs'] = [[self.verb_b_list[count].currentText()]]
                self.res.loc[iter[0],'event'] = self.eve_b_list[count].currentText()
                count = count + 1
    def get_datas(self): # change the show of img and events
        img_id = self.imgs[self.pointer-1]
        acc_id = img_id.zfill(12)
        if acc_id in self.trains:
            img_name = 'COCO_train2014_'+acc_id+'.jpg'
            label_now = 'train2014'
        else:
            img_name = 'COCO_val2014_'+acc_id+'.jpg'
            label_now = 'val2014'
        self.label.setText(img_name)
        self.jump_show(img_name)
        if self.pointer <= self.len_res:
            datas = self.res.loc[self.res['imgid']==str(img_id)]
        else:
            datas = self.data_e.loc[self.data_e['imgid']==str(img_id)]
        self.imm = datas
        self.show_img(label_now,img_name)
        self.show_all(datas)
    def next_pointer(self): # exchange next
        self.save_imm(self.imm)
        self.pointer = self.pointer +1
        self.get_datas()
    def last_pointer(self):
        self.save_imm(self.imm)
        if self.pointer >1:# exchange last
            self.pointer = self.pointer-1
            self.get_datas()
    def jump_show(self,img_name):
        if self.pointer >self.len_res:
            self.jump_list.addItem(img_name)
    def jump_pointer(self,index_id):# exchange the select
        self.save_imm(self.imm)
        self.pointer = index_id+1
        self.get_datas()

    def show_img(self,label,img_now):# change img
        # img_now = self.img_list[self.pointer]
        frame = QImage(os.path.join(path_img,label,img_now))
        pix = QPixmap.fromImage(frame)
        item = QGraphicsPixmapItem(pix)
        scene = QGraphicsScene()
        scene.addItem(item)
        self.img.setScene(scene)
    def show_all(self,events):# change events
        # set the None for the events
        for index1 in range(5):
            self.verb_b_list[index1].clear()
            self.eve_b_list[index1].clear()
            self.sen_b_list[index1].setText('')
        count = 0
        for iter in events.itertuples():
            list_verbs = self.get_verbs(iter[3])
            self.verb_b_list[count].addItems(list_verbs)
            # self.verb_b_list[count].addItems(list_verbs)
            self.verb_b_list[count].setEditable(True)
            self.eve_b_list[count].addItem(iter[4])
            self.eve_b_list[count].setEditable(True)
            self.eve_b_list[count].addItems(self.get_event(list_verbs))
            self.sen_b_list[count].setText(iter[2])
            count = count + 1
    def get_verbs(self,verblist):# get the verbs in the sen
        list_v = []
        list_v1 = []
        for i in verblist:
            list_v.append(i[0])
        if len(list_v)==0:
            list_v1.append('None')
        return list_v
    def get_event(self,verbs): # get the event of the verbs select
        list_e = []
        for i in verbs:
            if i in self.verb_eves:
                list_e = list_e + self.verb_eves[i]
        if len(list_e)==0:
            list_e.append('lack')
        return list_e
    def exchange(self,verb):#exchange the event to the event of the verb select(need to complete)
        list_r = []
        list_r = list_r + self.verb_eves[verb]
        if len(list_r)==0:
            list_r.append('None')
        return list_r


if __name__ == "__main__":
    path_img = '/home/student/DB/COCO/coco2014'# img postion
    path_lab = 'design\database\event_coco.pkl'# event postion
    path_eves ='/home/student/testgit/VSR-guided-CIC/gui_elmo/design/verb_eve.json'
    path_res = '/home/student/testgit/VSR-guided-CIC/gui_elmo/design/results/results.pkl'# result postion
    app = QApplication(sys.argv)
    myWin = MyMainForm(imgs_path=path_img,path_eve=path_lab,path_res=path_res,path_eves= path_eves)
    myWin.show()
    sys.exit(app.exec_())


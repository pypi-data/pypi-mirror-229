# -*- coding:utf-8 -*-
from . import face_detetion
import cv2 

def imshow(img):
    cv2.imshow('123', img)

class VideoCapture:
    def __init__(self,device_id) -> None: 
        self.cap = cv2.VideoCapture(device_id)
    def read(self): 
        _,frame = self.cap.read()
        return frame
    def release(self) -> None: 
        self.cap.release
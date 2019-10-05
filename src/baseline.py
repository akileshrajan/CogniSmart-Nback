import numpy as np
import pandas as pd
import cv2, sys, os, datetime, re, time


import Sensorshandler as sensors

data_path = "/media/akilesh/data/fatigue_fitbit"
raw_input("Are you ready to run the baseline data collection?")
User_ID = raw_input("Enter User ID:")
Block_Id = "Baseline"
path_usr = os.path.join(data_path,'user_'+User_ID,Block_Id)

# Start each sensor in a separate thread. No sensor recording for practice block.
bsp_thread = sensors.SensorsHandler("Plux", path_usr, User_ID, Block_Id)
bsp_thread.start()
bsp_thread.start_sensor()  # Start recording BSP

cam_thread = sensors.SensorsHandler("Camera", path_usr, User_ID, Block_Id)
cam_thread.start()
cam_thread.start_sensor()

muse_thread = sensors.SensorsHandler("Muse", path_usr, User_ID, Block_Id)
muse_thread.start()
muse_thread.start_sensor()  # Start recording Muse

time.sleep(60)
print("A minuite left")
time.sleep(60)
print("Fini")

bsp_thread.close_sensor()
muse_thread.close_sensor()
cam_thread.close_sensor()
import kivy
from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.core.audio import SoundLoader
from kivy.clock import Clock
from functools import partial
import numpy as np
import cv2
import sys,os
import _pickle as cPickle
from threading import Thread
import datetime
from kivy.config import Config
import keyboard
kivy.require('1.9.0')

# from levels import main_game,original_game
import src.MUSE_Server as msc


def main(game,user,stimuli,data_path):
    """
    This is the main function of the game. THe starting point.

    :param game: Type of game. Two possible inputs. 0-back = '0', 2-back = '2'
    :param user: User ID. dtype = str. eg: 'test_user', '0', '1', '2'...
    :param stimuli: Type of Stimuli. Two possible stimuli. Visual = 'v', audio '0'
    :param data_path: Location to store the data. In my case "/media/akilesh/data/fatigue_fitbit"
    :return: No return value.
    """

    global user_id, email, modality, round_set, round_id, quit, game_type, store_data_path
    Config.set('graphics', 'width', str(1000))
    Config.set('graphics', 'height', str(1000))

    # Parameter initialization
    store_data_path =data_path
    game_type = game
    round_set = 0
    quit = False


if __name__ == '__main__':
   main('m','test_user','v','/media/akilesh/data/fatigue_fitbit')
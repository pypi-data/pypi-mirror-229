# FDR Client Utility Functions

# Libraries
from os import system, name
from ..classes.DatasetManager import DatasetManager
from termcolor import cprint
from tkinter import filedialog
import tkinter as tk
import keyboard
import shutil
import time
import os


def welcome_message():
    """
    FDR welcome message
    """
    cprint('\nWelcome to FaradAI Repository\n', 'cyan', attrs=['bold'])

def clear():
    """
    Clear FDR client
    """
    if name == 'nt':
        # windows
        _ = system('cls')
    else:
        # linux, macos
        _ = system('clear')

def clear_terminal_input():
    """
    Clear terminal input text
    """
    keyboard.press_and_release('esc')

def print_lines_per_terminal_size():
    """
    Get current terminal size
    """
    terminal_width, _ = shutil.get_terminal_size(fallback=(80, 24))
    dash_length = terminal_width - 1
    print(dash_length*"_")

def progress_update(pbar, threshold):
    """
    Smooth progress bar update
    """
    for _ in range(threshold):
        time.sleep(0.05)  
        pbar.update(1)

def dir_picking(message:str):
    """
    GUI to pick dir and return path
    """
    root = tk.Tk()
    root.withdraw() 
    folder_msg = f'{message}'
    folder_path = filedialog.askdirectory(title=folder_msg)
    root.destroy()
    return folder_path

def check_dvc_file(folder_path):
    """
    Check existence of .dvc file in a path
    """
    for filename in os.listdir(folder_path):
        if filename.endswith('.dvc'):
            return True
    return False

def sample_data():
    """
    Sample datasets
    """
    # Sample data
    data = [
        {"ID": "1", "DATASET": "dataset 1", "VERSION": "1.0", "DATE": "5/5"},
        {"ID": "2", "DATASET": "dataset 2", "VERSION": "2.1", "DATE": "8/7"},
        {"ID": "3", "DATASET": "fire_smoke", "VERSION": "8.0", "DATE": "8/7"},
        {"ID": "4", "DATASET": "big_test", "VERSION": "2.0", "DATE": "12/7"}
    ]
    return data

def sample_headers():
    """
    Sample headers
    """
    # Sample headers
    return ["ID", "DATASET", "VERSION", "DATE"]

def get_datasets(header_show:bool, header_color:str):
    """
    FDR get datasets
    """
    dataset_manager = DatasetManager(data=sample_data(), headers=sample_headers())
    if header_color=='cyan' and header_show:
        cprint('\nLoading FaradAI Datasets\n', header_color, attrs=['bold'])
    elif header_show:
        cprint('\nLoading FaradAI Datasets\n', "yellow", attrs=['bold'])

    # progress bar
    dataset_manager.display_loading()

    # datasets
    dataset_manager.display_dataframe()
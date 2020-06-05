import filecmp
import os
import shutil
from datetime import datetime as dt
from os import listdir
from os import path
from os.path import isfile, join

from util.logger import Logger

data_path = "data/"


def backup_databases():
    only_files = [f for f in listdir(data_path) if isfile(join(data_path, f))]
    for file in only_files:
        backup_file(file)


def backup_file(filename: str):
    date = dt.now()
    folder_name = "backups"
    subfolder_name = f"{date.strftime('%m%d%y')}"
    backup_name = f"{folder_name}/{subfolder_name}/{filename}"
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

    if not os.path.exists(f"{folder_name}/{subfolder_name}"):
        os.makedirs(f"{folder_name}/{subfolder_name}")

    if path.exists(f"{data_path}{filename}") and path.exists(backup_name):
        if filecmp.cmp(f"{data_path}{filename}", backup_name):
            # print(f"{filename} is same as {backup_name}, skipping...")
            return

    shutil.copyfile(f"{data_path}{filename}", backup_name)
    Logger.info(f"Backed up {data_path}{filename} to {backup_name}")

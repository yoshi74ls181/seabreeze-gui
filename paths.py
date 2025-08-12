from os import mkdir
from os.path import isdir
from datetime import date

data = "./data/"
logs = "./logs/"

def return_folder(folder):
	if not isdir(folder):
		mkdir(folder)
	return folder

def today():
    return return_folder("./data/" + date.today().strftime("%Y%m%d") + "/")

from tkinter import *
from tkinter import filedialog

root = Tk()
#root.filename =  filedialog.askopenfilename(initialdir= "/", title = "Select file",filetypes = (("jpeg files","*.jpg"),("all files","*.*")))
root.directory = filedialog.askdirectory()
print (root.directory)

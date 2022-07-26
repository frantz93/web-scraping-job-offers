# Now we will build a interface for interacting with the program
from tkinter import Tk
from tkinter import Label  #we will use tkinter library

root = Tk()
myLabel = Label(root, text="Welcome to my jobsearch program")
myLabel.pack()
root.mainloop()
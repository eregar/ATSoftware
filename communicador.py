#import serial
import tkinter

#x=input("serial plz")
#ser = serial.Serial('COM'+x, 115200)
#ser.write(b"AT\r")

#response =  ser.readline()
#ser.close()

#print (response)

m=tkinter.Tk(className="AT reciever")
w=tkinter.Canvas(m,width=300,height=300)
boton1= tkinter.Button(m,text='stop',width=25,command=m.destroy)
boton1.pack()
m.mainloop()
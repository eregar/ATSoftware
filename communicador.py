import serial
import tkinter
import threading
import time
import constants
import comClass

#variables globales
puertos=[]
butons=[]
app=tkinter.Tk(className="AT reciever")


def COMThread(comNumber):
    pass

def test(numero):
    print("quiero el lock alvv")
    printear(numero)
    print("ganeee uwu")

def printear(variable):
    #print(testo2.get(1.0,tkinter.END))
    loc.acquire()
    print(variable)
    time.sleep(1)
    loc.release()

for port in constants.PORTNUMBERS:
    puertos.append(comClass.Com(port))
    #puertos.append(threading.Thread(target=test,args=(port),daemon=True))
    butons.append(tkinter.Label(master=app,text=str(port)))

loc=threading.Lock()
#w=tkinter.Canvas(m,width=100,height=100)
#boton1= tkinter.Button(app,text='stop',width=25,command=app.destroy)
#boton2= tkinter.Button(app,text='print',width=25,command= lambda : printear("holaa"))
testo2=tkinter.Text(app,width=50,height=10)
testo2.grid(row=0,column=0,sticky=tkinter.W,columnspan=2)
const=1
for boton in butons:
    tkinter.Label(master=app,text='COM'+boton['text']).grid(row=const,column=0,sticky=tkinter.W)
    boton['text']='Status: OFFLINE'
    boton.grid(row=const,column=1,sticky=tkinter.W)
    const+=1
#boton1.grid(row=1,column=0,sticky=tkinter.W)
#boton2.grid(row=1,column=1,sticky=tkinter.E)

app.mainloop()

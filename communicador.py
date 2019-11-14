import tkinter
from tkinter.messagebox import showinfo
import time
import constants
import comClass
import threading

#variables globales
puertos=[]
statuses=[]
telefonos=[]
checkBoxes=[]

app=tkinter.Tk(className="AT reciever")
writeFrame=tkinter.Frame(app)
comFrame=tkinter.Frame(app)
telFrame=tkinter.Frame(app)
chosen='3315528889'
minutos=60

def startPorts():
    for puerto in range(len(puertos)):
        puertos[puerto].zoneSerial()
        statuses[puerto]['text']=puertos[puerto].status
def crossDial():
    print('calling')
    temp=[]  
    for x in range(len(checkBoxes)):
        if checkBoxes[x].get()!=0:
            temp.append(x)
    print(len(temp)//2)
    for puerto in range(len(temp)//2):
        print('metsuketaaa')
        half=puerto+len(temp)//2
        #statuses[temp[puerto]]['text']=constants.DIALING
        s=puertos[temp[puerto]].dial(telefonos[temp[half]].get(),minutos)
        if s:
            #statuses[temp[half]]['text']=constants.RECIEVING
            r=puertos[temp[half]].ans('3315528889')
            if not r:
                puertos[temp[puerto]].hang(0)
                #statuses[temp[half]]['text']=constants.ERROR
            #statuses[temp[puerto]]['text']=constants.ERROR
    if len(temp) % 2!=0:
        indexsobrante=temp[-1]
        puertos[indexsobrante].dial(chosen,minutos)
    print('done')

def constantCheck():
    while True:
        for puerto in range(len(puertos)):
            statuses[puerto]['text']=puertos[puerto].status
        time.sleep(1)


for port in constants.PORTNUMBERS:
    puertos.append(comClass.Com(port))
    statuses.append(tkinter.Label(master=comFrame,text=str(port)))

#AT+CMGF
#AT+CMGR=INDEX
#AT+CPMS="SM"
#cuadro de mensajes
cuadro=tkinter.Text(writeFrame,width=50,height=10)
cuadro.grid(row=0,column=0,sticky=tkinter.N,columnspan=2,rowspan=10)
t=threading.Thread(target=constantCheck,daemon=True)
tkinter.Button(master=comFrame,text='connect',command= startPorts ).grid(
    row=0,column=1)

#tkinter.Scrollbar(master=comFrame).grid(column=2,rowspan=10)

writeFrame.grid(row=0,column=0,sticky=tkinter.N)
comFrame.grid(row=0,column=1)
telFrame.grid(row=0,column=2,sticky=tkinter.W)
const=1
for boton in statuses:
    checkBoxes.append(0)
    checkBoxes[const-1]=tkinter.IntVar()
    tkinter.Checkbutton(master=comFrame,text='COM'+boton['text'],height=1
        ,variable=checkBoxes[const-1],onvalue=1,offvalue=0).grid(row=const,column=0,sticky=tkinter.W)
    
    telefonos.append(tkinter.Entry(master=telFrame,width=10,bd=4))
    telefonos[const-1].grid(row=const,column=2,sticky=tkinter.W)

    boton['text']=puertos[0].status
    boton.grid(row=const,column=1,sticky=tkinter.W)
    const+=1

tkinter.Button(master=comFrame,text='Dial',command= crossDial ).grid(
    row=const,column=1)

t.start()
app.mainloop()


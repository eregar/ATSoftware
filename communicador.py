import tkinter
from tkinter.messagebox import showinfo
import time
import constants
import opener
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

def startPorts():
    connectb['state']='disabled'
    for puerto in range(len(puertos)):
        puertos[puerto].zoneSerial()
        statuses[puerto]['text']=puertos[puerto].status
    time.sleep(0.5)
    connectb['state']='normal'
    
def crossDial():
    print('calling')
    temp=[]  
    for x in range(len(checkBoxes)):
        if checkBoxes[x].get()!=0 and telefonos[x].get()!='':
            temp.append(x)
    for puerto in range(len(temp)//2):
        half=puerto+len(temp)//2
        s=puertos[temp[puerto]].dial(telefonos[temp[half]].get(),int(segundos.get()))
        if s:
            r=puertos[temp[half]].ans('3315528889')#va el entry
            if not r:
                puertos[temp[puerto]].hang(0)
            else:
                print('calling back')
                puertos[temp[half]].dial(telefonos[temp[puerto]].get(),int(segundos.get()))
                puertos[temp[puerto]].ans('3315528889')#va el entry

    if len(temp) % 2!=0:
        indexsobrante=temp[-1]
        puertos[indexsobrante].dial(chosen,int(segundos.get()))
    print('done')

def constantCheck():
    while True:
        for puerto in range(len(puertos)):
            statuses[puerto]['text']=puertos[puerto].status
        time.sleep(1)

def changeImei():
    msg='no se encontraron los siguientes numeros:\n'
    msg2='no se pudieron cambiar los siguientes IMEI:\n'
    flag2=False
    flag=False
    if opener.abrir(arch.get()):
        for x in range(len(telefonos)):
            s=telefonos[x].get()
            if s!='':
                ans=opener.buscar(telefonos[x].get())
                if ans!='0':
                    if not puertos[x].setIMEI(ans):
                        flag2=True
                        msg2+='COM%d: %s\n' %(puertos[x].comNumber,s)
                else:
                    flag=True
                    msg+='COM%d: %s\n' %(puertos[x].comNumber,s)
        if flag:
            showinfo(title='hola',message=msg)
        if flag2:
            showinfo(title='hola',message=msg2)
    else:
        showinfo(title='hola',message='no se encontro el archivo')
def setExtra():
    global chosen
    x=ch.get()
    if len(x)==10:
        chosen=x

for port in constants.PORTNUMBERS:
    puertos.append(comClass.Com(port))
    statuses.append(tkinter.Label(master=comFrame,text=str(port)))

#AT+CMGF
#AT+CMGR=INDEX
#AT+CPMS="SM"
#AT + EGMR = 1, 7, "your imei number here"
#AT+CGSN IMEI
#cuadro de mensajes
cuadro=tkinter.Text(writeFrame,width=50,height=10)
cuadro.grid(row=0,column=0,sticky=tkinter.N,columnspan=2,rowspan=10)
t=threading.Thread(target=constantCheck,daemon=True)
connectb=tkinter.Button(master=comFrame,text='connect',command= startPorts )
connectb.grid(row=0,column=1)

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
tkinter.Button(master=writeFrame,text='IMEI',command=changeImei).grid(row=11,column=0)
arch=tkinter.Entry(master=writeFrame,width=20,bd=4)
arch.grid(row=11,column=1)
tkinter.Button(master=writeFrame,text='setExtra',command=setExtra).grid(row=12,column=0)
ch=tkinter.Entry(master=writeFrame,width=10,bd=4)
ch.grid(row=12,column=1)
segundos=tkinter.Entry(master=comFrame,width=3,bd=4,)
segundos.grid(row=0,column=0)
segundos.insert(0,'60')
t.start()
app.mainloop()


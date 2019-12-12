import tkinter
from tkinter import messagebox as mb,simpledialog as sd,filedialog as fd
import time
import constants
import opener
import comClass
import threading
import mensaje

#variables globales
puertos=[]
statuses=[]
imeis=[]
ccids=[]
telefonos=[]
checkBoxes=[]
messageList=[]

app=tkinter.Tk(className="AT reciever")
callWindow=tkinter.Frame(app)
menu=tkinter.Frame(app)
writeFrame=tkinter.Frame(callWindow)
comFrame=tkinter.Frame(callWindow)
telFrame=tkinter.Frame(callWindow)
msgFrame=tkinter.Frame(callWindow)
rcvFrame=tkinter.Frame(callWindow)
#frame para message box, entry de destinatario, boton de mandar mensaje
#frame para ver mensajes recividos
chosen=''

def startPorts():
    connectb['state']='disabled'
    __zoneSerial()
    connectb['state']='normal'

def __getIMEIS():
    for puerto in range(len(puertos)):
        if puertos[puerto].status==constants.OK:
            imeis[puerto]['text']=puertos[puerto].getIMEI()

def __zoneSerial():
        threads=[]
        for puerto in range(len(puertos)):
            threads.append(threading.Thread(target=puertos[puerto].startSerial,daemon=True))
            threads[puerto].start()
        for th in threads:
            th.join()
        __getIMEIS()
        __getCCIDs()
    
def crossDial():
    temp=[]  
    for x in range(len(checkBoxes)):
        if checkBoxes[x].get()!=0 and telefonos[x].get()!='':
            temp.append(x)
    for puerto in range(len(temp)//2):
        half=puerto+len(temp)//2
        s=puertos[temp[puerto]].dial(telefonos[temp[half]].get().strip(),__getSeconds())
        if s:
            r=puertos[temp[half]].ans()#va el entry
            if not r:
                puertos[temp[puerto]].hang(0)
            else:
                time.sleep(1)
                puertos[temp[half]].dial(telefonos[temp[puerto]].get().strip(),__getSeconds())
                puertos[temp[puerto]].ans()#va el entry

    if len(temp) % 2!=0:
        global chosen
        indexsobrante=temp[-1]
        if chosen=='':
            setExtra()
            if chosen=='':
                chosen=__askForNumber(
                    "hola","porfavor inserte un numero de telefono extra\n para recibir una llamada")
        if chosen!='':
            puertos[indexsobrante].dial(chosen,__getSeconds())
    print('done')

def constantCheck():
    global statuses
    global puertos
    while True:
        try:
            for puerto in range(len(puertos)):
                statuses[puerto]['text']=puertos[puerto].status
            time.sleep(1)
        except RuntimeError:
            break

def selectAll():
    checked=False
    for j in checkBoxes:
        if j.get()==1:
            j.set(0)
        else:
            checked=True
            break
    if checked:
        for j in checkBoxes:
            j.set(1)        


def __askForNumber(titulo='hola',asunto='inserte un numero'):
    res=''
    while len(res.strip())!=10:
        res=sd.askstring(titulo,asunto)
        if res is None:
            return ''
        try:
            int(res.strip())
        except:
            pass
    return res.strip()

def __getCCIDs():
    for puerto in range(len(puertos)):
        if puertos[puerto].status==constants.OK:
            ccids[puerto]['text']=puertos[puerto].getCCID()


def changeImei():
    msg='no se encontraron los siguientes CCIDs:\n'
    msg2='no se pudieron cambiar los siguientes IMEI:\n'
    flag2=False
    flag=False
    h=fd.askopenfile(title="hola",filetypes=(('csv files','*.csv'),('text files','*.txt')))
    if opener.readArchivo(h):
        for x in range(len(puertos)):
            if puertos[x].status==constants.OK:
                s=puertos[x].getCCID()
                if s is not None:
                    numero,imei=opener.buscar(s)
                    if (numero is not None) :
                        if (imei is not None):
                            if not puertos[x].setIMEI(imei):
                                flag2=True
                                print("no cambio imei")
                                msg2+='COM%d: %s\n' %(puertos[x].comNumber,s)
                            else:
                                telefonos[x].delete(0,tkinter.END)
                                telefonos[x].insert(0,numero)
                        else:
                            telefonos[x].delete(0,tkinter.END)
                            telefonos[x].insert(0,numero)
                    else:
                        flag=True
                        print("no encontro numero")
                        msg+='COM%d: %s\n' %(puertos[x].comNumber,s)
                
        if flag:
            mb.showinfo(title='hola',message=msg)
        if flag2:
            mb.showinfo(title='hola',message=msg2)
        __getIMEIS()
    else:
        mb.showinfo(title='hola',message='no se encontro el archivo')

def changeNumbers():
    h=fd.askopenfile(title="DEBEN DE ESTAR EN ORDEN",filetypes=(('csv files','*.csv'),('text files','*.txt')))
    if opener.readArchivo(h):
        numb=opener.listNumbers()
        for x in range(len(numb)):
            telefonos[x].delete(0,tkinter.END)
            telefonos[x].insert(0,numb[x])


def setExtra():
    global chosen
    x=ch.get()
    if len(x)==10:
        chosen=x

def __getSeconds():
    try:
        x=int(segundos.get())
        return x
    except ValueError:
        mb.showinfo(title='hola',message='segundos no validos')
        segundos.delete(0,tkinter.END)
        segundos.insert(0,'60')
        return 60

def setFrame(frameNo : int):
    if frameNo==1:
        rcvFrame.forget()
        msgFrame.forget()
        comFrame.forget()
        #telFrame.grid(row=0,column=2,sticky=tkinter.S)
        telFrame.pack(side=tkinter.RIGHT,expand=1,fill=tkinter.BOTH)
        comFrame.pack(side=tkinter.RIGHT,fill=tkinter.BOTH,expand=1,padx=50)
        writeFrame.pack(side=tkinter.LEFT,expand=1,fill=tkinter.BOTH)
    elif frameNo==2:
        telFrame.forget()
        writeFrame.forget()
        comFrame.forget()
        #msgFrame.grid(row=0,column=0,sticky=tkinter.N)
        msgFrame.pack(side=tkinter.LEFT,fill=tkinter.BOTH,expand=1)
        comFrame.pack(side=tkinter.RIGHT,fill=tkinter.BOTH,expand=1,padx=50)

def sendMessages():
    temp=[]  
    comCounter=0
    for x in range(len(checkBoxes)):
        if checkBoxes[x].get()!=0:
            temp.append(x)
    if len(temp)>0:
        for x in mensajes.curselection():
            #messagelist[x]
            print('msg',mensajes.get(x),'to com',puertos[temp[comCounter]].comNumber)
            #send the message (thread?)
            comCounter= (comCounter+1) % len(temp)

#max 160 char
#AT+CMGF
#AT+CMGR=2
#AT+CMGL="ALL"
#AT+CMGR=INDEX
#AT+CPMS="SM"
#AT + EGMR = 1, 7, "your imei number here"
#AT+CGSN IMEI
#AT+CUSD=1,"#999#",15


#listas necesarias
for port in constants.PORTNUMBERS:
    puertos.append(comClass.Com(port))
    statuses.append(tkinter.Label(master=comFrame,text=str(port)))
    imeis.append(tkinter.Label(master=comFrame,width=15))
    ccids.append(tkinter.Label(master=comFrame,width=20))


cuadro=tkinter.Text(msgFrame,width=50,height=10,bd=4)
cuadro.grid(row=1,column=0,sticky=tkinter.N,columnspan=2,rowspan=10)
connectb=tkinter.Button(master=comFrame,text='connect',command= startPorts )
connectb.grid(row=0,column=1)

menu.pack()
tkinter.Button(menu,text="CALLING",command=lambda: setFrame(1)).pack(side=tkinter.LEFT)
tkinter.Button(menu,text="MESSAGING",command=lambda: setFrame(2)).pack(side=tkinter.LEFT)

callWindow.pack(side=tkinter.TOP,fill=tkinter.BOTH,expand=1)
setFrame(1)
const=1
for boton in statuses:
    checkBoxes.append(0)
    checkBoxes[const-1]=tkinter.IntVar()
    tkinter.Checkbutton(master=comFrame,text='COM'+boton['text'],height=1
        ,variable=checkBoxes[const-1],onvalue=1,offvalue=0).grid(row=const,column=0,sticky=tkinter.W)
    imeis[const-1].grid(row=const,column=3)
    ccids[const-1].grid(row=const,column=4)

    telefonos.append(tkinter.Entry(master=telFrame,width=10,bd=4))#,state="disabled"))
    telefonos[const-1].grid(row=const,column=0,sticky=tkinter.W)

    boton['text']=puertos[0].status
    boton.grid(row=const,column=1,sticky=tkinter.W)
    const+=1

tkinter.Button(master=writeFrame,text='Dial',command= crossDial ).grid(
    row=13,column=0)
tkinter.Button(master=writeFrame,text='Set from database..',command=changeImei).grid(row=11,column=0)
tkinter.Button(master=writeFrame,text='setExtra',command=setExtra).grid(row=12,column=0)
ch=tkinter.Entry(master=writeFrame,width=10,bd=4)
ch.grid(row=12,column=1)
segundos=tkinter.Entry(master=writeFrame,width=3,bd=4,)
segundos.grid(row=13,column=1)
segundos.insert(0,'60')

tkinter.Button(master=comFrame,text='select all',command=selectAll).grid(row=0,column=0)
tkinter.Label(master=comFrame,text='IMEI').grid(row=0,column=3)
tkinter.Label(master=comFrame,text='CCID').grid(row=0,column=4)
tkinter.Label(master=telFrame,text='Numero').grid(row=0,column=0)


tkinter.Button(master=msgFrame,text='add+').grid(row=0,column=1)
tkinter.Label(master=msgFrame,text='Address:').grid(row=0,column=0)
destino=tkinter.Entry(master=msgFrame,width=40,bd=4)
destino.grid(row=0,column=1)

cajon=tkinter.Frame(msgFrame)
cajon.grid(row=11,column=0,columnspan=2,rowspan=5,pady=10)
scroll=tkinter.Scrollbar(cajon)
scroll.pack(side=tkinter.RIGHT,fill=tkinter.Y)
mensajes=tkinter.Listbox(master=cajon,yscrollcommand=scroll.set,width=60,selectmode=tkinter.EXTENDED)
scroll.config(command=mensajes.yview)
mensajes.pack(side=tkinter.LEFT,fill=tkinter.BOTH)
#tkinter list of messages to send
tkinter.Button(master=msgFrame,text='SEND',padx=10,pady=10,command=sendMessages).grid(row=16,column=0)
tkinter.Button(master=msgFrame,text='CLONE',pady=5).grid(row=12,column=3)
tkinter.Button(master=msgFrame,text='DELETE X',pady=5).grid(row=13,column=3)

for x in range(30):
    mensajes.insert(tkinter.END,'hola'*(x%3))
t=threading.Thread(target=constantCheck,daemon=True)
t.start()

app.mainloop()
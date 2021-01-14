import tkinter
from tkinter import messagebox as mb,simpledialog as sd,filedialog as fd
import time
import constants
from opener import Opener
import comClass
import threading
import mensaje
import random

#variables globales
puertos=[]
statuses=[]
imeis=[]
ccids=[]
telefonos=[]
checkBoxes=[]
messageList=[]
reversa=False

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
tempSendMsg=fd.askopenfile(title="hola",filetypes=(('csv files','*.csv'),('text files','*.txt')))
opin=Opener()
if not opin.readArchivo(tempSendMsg):
    print("could not initialize opin")

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
        if checkBoxes[x].get()!=0 and telefonos[x].get()!='': #aqui
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
    op=Opener()
    if op.readArchivo(h):
        
        for x in range(len(puertos)):
            if puertos[x].status==constants.OK:
                s=puertos[x].getCCID()
                if s is not None:
                    numero,imei=op.buscarIccid(s)
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
        telFrame.forget()
        writeFrame.forget()
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
    #elif frameNo==3:
    #    rcvFrame.forget()
    #    msgFrame.forget()
    #    comFrame.forget()
    #    writeFrame.forget()
    #    telFrame.forget()
    #    telFrame.pack(side=tkinter.RIGHT,expand=1,fill=tkinter.BOTH)
    #    comFrame.pack(side=tkinter.RIGHT,fill=tkinter.BOTH,expand=1,padx=50)


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
#AGREGADO
def rcvMessages():
    temp=[]
    for x in range(len(checkBoxes)):
        if checkBoxes[x].get()!=0:
            temp.append(x)
    for puerto in range(len(temp)):
        mensajes=puertos[temp[puerto]].getSMS().split('+CMGL:')
        for men in mensajes:
            if "PASA TIEMPO" in men: #REC
                print(men)
#AGREGADO
def __threadmandarMSG(puerto, destinatario :str, contenido :str):
    puerto.sendSMS(destinatario,contenido)
    
def __threadrecibirMSG():
    pass

def reverse():
    global reversa,reversaso1,reversaso2
    if reversa:
        reversaso1['state']='disabled'
        reversaso2['state']='normal'
        reversa=False
    else:
        reversaso1['state']='normal'
        reversaso2['state']='disabled'
        reversa=True

def pasarSaldos():
    temp=[]  
    global reversa
    if reversa:
        for x in range(len(checkBoxes),0,-1):
            if checkBoxes[x-1].get()!=0:
                temp.append(x-1)
    else:
        for x in range(len(checkBoxes)):
            if checkBoxes[x].get()!=0:
                temp.append(x)
    if len(temp)>0 and len(temp)%2==0:
        res=mb.askyesno(title='hola',message='son '+str(len(temp)//2)+", empezando por pos "+str(temp[0])+"\ncontinuar?")
        if res:
            threads=[]
            for puerto in range(len(temp)//2):
                half=puerto+len(temp)//2
                threads.append(threading.Thread(
                    target=__threadmandarMSG,args=(puertos[temp[puerto]],"7373",telefonos[temp[half]].get()+" "+saldo.get())
                    ,daemon=True))
                threads[puerto].start()
            for t in threads:
                t.join(timeout=10)
            if saldo.get()=="9":
                print("dumping")
                for puerto in range(len(temp)//2):
                    puertos[temp[puerto]].sendSMS("7373",constants.DUMPNUMBERS[puerto]+" 23")
            aumentarSaldo()
            reverse()
            res=mb.askyesno(title='hola',message='termino de pasar, mandar mensaje?')
            if res:
                threads=[]
                #acomodated
                r = random.Random()
                for puerto in range(len(temp)//2):
                    #this one needs to change
                    tempnum=opin.getLine(r.randint(0,5992)).split(',')[1].strip('\n').strip()
                    print(tempnum)
                    threads.append(
                        threading.Thread(target=__threadmandarMSG,args=(puertos[temp[puerto]],tempnum,"conoce nuestras ofertas Telcel!")))
                    threads[puerto].start()
                for t in threads:
                    t.join(timeout=10)
    else:
        mb.showinfo(title='hola',message="no cumple con los requisitos")

def aumentarSaldo():
    current=int(saldo.get())
    saldo.delete(0,tkinter.END)
    if current>=33:
        saldo.insert(0,'9')
    else:
        saldo.insert(0,str(current+4))

def __vnSendDTMFCode(dialNumber:str,commandList:str):#tkinter button to put this one
    threads=[]
    if(dialNumber=="" or commandList==""):
        print("se necesitan telefonos, destino e instrucciones para ejecutar")
        return
    stuff = [10,5,0.8,11,22]
    for port in range(len(puertos)):
        tel=telefonos[port].get().strip()
        if(puertos[port].status==constants.OK and tel!=''):
            temp=threading.Thread(target=puertos[port].dialWithCode,args=(dialNumber,commandList,tel,stuff),daemon=True)
            threads.append(temp)
            temp.start()
    print("mandando comando",commandList, "hacia",dialNumber)

def __ussdChangePlan(ussdCode:str,commandList:str):#tkinter button to put this one
    threads=[]
    for port in range(len(puertos)):
        if(puertos[port].status==constants.OK):
            temp=threading.Thread(target=puertos[port].sendUssd,args=(ussdCode,commandList),daemon=True)
            threads.append(temp)
            temp.start()
    print("mandando comando",commandList, "hacia",ussdCode)
    for th in threads:
        th.join()

def dialUssd():
    pass

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
tkinter.Button(master=writeFrame,text='Dial w/ Code:',
    command=lambda: __vnSendDTMFCode(dialUssdNumber.get(),instructions.get())).grid(row=14,column=0)
#tkinter.Button(master=writeFrame,text='USSDDial',command=dialUssd).grid(row=15,column=0)
tkinter.Label(master=writeFrame,text='instructions:').grid(row=17,column=0)
instructions=tkinter.Entry(master=writeFrame,width=15,bd=4,)
instructions.grid(row=17,column=1)
tkinter.Label(master=writeFrame,text='dial to:').grid(row=16,column=0)
dialUssdNumber=tkinter.Entry(master=writeFrame,width=6,bd=4,)
dialUssdNumber.grid(row=16,column=1)


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
#AGREGADO
tkinter.Button(master=msgFrame,text='RECIEVE',padx=10,pady=10,command=rcvMessages).grid(row=16,column=1)
tkinter.Button(master=msgFrame,text='pasar saldo',padx=10,pady=10,command=pasarSaldos).grid(row=16,column=2)
reversaso1=tkinter.Button(master=msgFrame,text='first to last',pady=5,command=reverse)
reversaso1.grid(row=15,column=2)
reversaso2=tkinter.Button(master=msgFrame,text='last to first',pady=5,command=reverse)
reversaso2.grid(row=15,column=3)
tkinter.Button(master=msgFrame,text='Set from..',command=changeImei).grid(row=11,column=3)




saldo=tkinter.Entry(master=msgFrame,width=3,bd=4,)
saldo.grid(row=16,column=3)
saldo.delete(0,tkinter.END)
saldo.insert(0,'0')


tkinter.Button(master=msgFrame,text='CLONE',pady=5).grid(row=12,column=3)
tkinter.Button(master=msgFrame,text='DELETE X',pady=5).grid(row=13,column=3)

for x in range(30):
    mensajes.insert(tkinter.END,'hola'*(x%3))
t=threading.Thread(target=constantCheck,daemon=True)
t.start()

##inyection


app.mainloop()
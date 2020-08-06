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
reversa=False

app=tkinter.Tk(className="AT reciever")
callWindow=tkinter.Frame(app)
menu=tkinter.Frame(app)
writeFrame=tkinter.Frame(callWindow)
comFrame=tkinter.Frame(callWindow)
telFrame=tkinter.Frame(callWindow)
#msgFrame=tkinter.Frame(callWindow)
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

def __threadmandarMSG(puerto, destinatario :str, contenido :str):
    puerto.sendSMS(destinatario,contenido)
    
def __threadrecibirMSG():
    pass


def __vnSendDTMFCode(dialNumber:str,commandList:str):#tkinter button to put this one
    threads=[]
    if(dialNumber=="" or commandList==""):
        mb.showinfo(title='hola',message="se necesitan numeros de telefono, destino e instrucciones para ejecutar")
        return
    for port in range(len(puertos)):
        tel=telefonos[port].get().strip()
        if(puertos[port].status==constants.OK and tel!=''):
            timestamps=[]
            for x in entries:
                timestamps.append(int(x.get()))
            temp=threading.Thread(target=puertos[port].dialWithCode,args=(dialNumber,commandList,tel,timestamps),daemon=True)
            threads.append(temp)
            temp.start()
    print("mandando comando",commandList, "hacia",dialNumber)

def __ussdChangePlan(ussdCode:str,commandList:str):#tkinter button to put this one
    threads=[]
    if(ussdCode=="" or commandList==""):
        mb.showinfo(title='hola',message="se necesitan telefonos y destino para ejecutar")
        return
    for port in range(len(puertos)):
        if(puertos[port].status==constants.OK):
            temp=threading.Thread(target=puertos[port].sendUssd,args=(ussdCode,commandList),daemon=True)
            threads.append(temp)
            temp.start()
    print("mandando comando",commandList, "hacia",ussdCode)
    for th in threads:
        th.join()



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


#cuadro=tkinter.Text(msgFrame,width=50,height=10,bd=4)
#cuadro.grid(row=1,column=0,sticky=tkinter.N,columnspan=2,rowspan=10)
connectb=tkinter.Button(master=comFrame,text='connect',command= startPorts )
connectb.grid(row=0,column=1)

menu.pack()

callWindow.pack(side=tkinter.TOP,fill=tkinter.BOTH,expand=1)
telFrame.pack(side=tkinter.RIGHT,expand=1,fill=tkinter.BOTH)
comFrame.pack(side=tkinter.RIGHT,fill=tkinter.BOTH,expand=1,padx=50)
writeFrame.pack(side=tkinter.LEFT,expand=1,fill=tkinter.BOTH)
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


tkinter.Button(master=writeFrame,text='Set from database..',command=changeImei).grid(row=11,column=0)

tkinter.Button(master=writeFrame,text='Dial w/ Code:',
    command=lambda: __vnSendDTMFCode(dialUssdNumber.get(),instructions.get())).grid(row=16,column=0)
tkinter.Button(master=writeFrame,text='USSDDial',
    command=lambda: __ussdChangePlan(dialUssdNumber.get(),instructions.get())).grid(row=17,column=0)
tkinter.Label(master=writeFrame,text='instructions:').grid(row=15,column=0)
instructions=tkinter.Entry(master=writeFrame,width=15,bd=4,)
instructions.grid(row=15,column=1)
tkinter.Label(master=writeFrame,text='dial to:').grid(row=14,column=0)
dialUssdNumber=tkinter.Entry(master=writeFrame,width=6,bd=4,)
dialUssdNumber.grid(row=14,column=1)

entries=[]
for x in range(5):
    entries.append(tkinter.Entry(master=writeFrame,width=6,bd=4))
    entries[x].grid(row=18+x,column=1)

tkinter.Button(master=comFrame,text='select all',command=selectAll).grid(row=0,column=0)
tkinter.Label(master=comFrame,text='IMEI').grid(row=0,column=3)
tkinter.Label(master=comFrame,text='CCID').grid(row=0,column=4)
tkinter.Label(master=telFrame,text='Numero').grid(row=0,column=0)


t=threading.Thread(target=constantCheck,daemon=True)
t.start()


app.mainloop()
import threading
import time
import constants
import comClass

puertos=[]

def __zoneSerial():
    threads=[]
    for puerto in range(len(puertos)):
        threads.append(threading.Thread(target=puertos[puerto].startSerial,daemon=True))
        threads[puerto].start()
    print("iniciando puertos")
    for th in threads:
        th.join()

def __ussdChangePlan(ussdCode:str,commandList):
    threads=[]
    for port in range(len(puertos)):
        threads.append(threading.Thread(target=puertos[port].sendUssd,args=(ussdCode,commandList),daemon=True))
        threads[port].start()
    print("mandando comando",commandList, "hacia",ussdCode)
    for th in threads:
        th.join()

for port in constants.PORTNUMBERS:
    puertos.append(comClass.Com(port))

proceed='Y'
while('Y' in proceed):
    __zoneSerial()
    for port in puertos:
        print("COM",port.comNumber,port.status)
    proceed=input("reintentar conexion de puertos?(y/n)\n").upper()

proceed=''
while (proceed==''):
    print("el codigo USSD es %s \nla secuencia de instrucciones es: %s"%(constants.USSD,constants.INSTRUCTIONS))
    proceed=input("cambiar?(y/n) ENTER para salir\n").upper()
    if('N' in proceed):
        print("realizando..")
        __ussdChangePlan(constants.USSD,constants.INSTRUCTIONS)
    elif('Y' in proceed):
        ussdInput= input("ingrese el codigo USSD. ej:#999#, ENTER para saltarse este paso\n")
        instructionsInput=input("ingrese las instrucciones, ENTER para saltarse este paso\n")
        if(ussdInput!=""):
            constants.USSD=ussdInput
        if(instructionsInput!=""):
            constants.INSTRUCTIONS=instructionsInput
        proceed=''
    else:
        proceed='n'


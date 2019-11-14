import constants
import serial
import time
import threading
class Com(object):
    
    def __init__(self,comNumber: int):
        super(Com,self).__init__()
        self.comNumber=comNumber
        self.status=constants.OFFLINE
        self.puerto=serial.Serial()


    def autoAnswer(self,origen):
        try:
            while True:
                bytesToRead=self.puerto.inWaiting()
                if bytesToRead!=0:
                    x=self.read(bytesToRead)
                    if 'RING' in str(x):
                        self.send(b'ATA\r\n')
                    elif 'CARRIER' in str(x):
                        print('me colgo')
                        self.changeState(constants.OK)
                        break
                    else:
                        print(x)
                time.sleep(1)
        except serial.SerialException:
            self.puerto.close()
            self.changeState(constants.OFFLINE)
    
    def hang(self,tiempo):
        time.sleep(tiempo)
        self.send(b'ATH\r\n')
        self.read()
        self.changeState(constants.OK)

    def ans(self,origen):
        self.startSerial()
        if self.status==constants.OK:
            answer=threading.Thread(target=self.autoAnswer, daemon=True)
            answer._args=(origen,)
            answer.start()
            self.changeState(constants.DIALING)
            return True
        else:
            return False
    
    def zoneSerial(self):
        x=threading.Thread(target=self.startSerial,daemon=True)
        x.start()

    def startSerial(self):
        try:
            self.puerto.close()
            self.changeState(constants.OFFLINE)
            self.puerto=serial.Serial('COM'+str(self.comNumber),baudrate=constants.BAUDRATE,
                timeout=constants.WAITINGTIME)
        except serial.serialutil.SerialException:
            pass
        else:
            self.send(b"AT\r\n")
            if('OK' in str(self.read(6))):
                self.changeState(constants.OK)

    def dial(self,numero: str,seconds: int):
        self.startSerial()
        if self.status==constants.OK:
            self.send(b'ATD'+numero.encode("utf-8")+b';\r\n')
            if('OK' in self.read()):
                self.changeState(constants.DIALING)
            else:
                return False
            print('done waiting')
            calling=threading.Thread(target=self.hang,args=(60),daemon=True)
            calling._args=(seconds+10,)
            calling.start()
            return True
        else:
            return False
    
    def changeState(self,estado: str):
        #signalChange(self,estado)
        self.status=estado
        
    def send(self, msg: bytes):
        self.puerto.write(msg)

    def read(self,byteNumber=0):
        if byteNumber==0:
            buffer=''
            timeout=0
            time.sleep(0.2)
            while timeout<=constants.WAITINGTIME:
                byteNumber=self.puerto.inWaiting()
                if byteNumber!=0:
                    buffer+=str(self.puerto.read(byteNumber))
                if'OK' in buffer:
                    break
                timeout+=1
                time.sleep(1)
            if buffer=='':
                self.changeState(constants.OFFLINE)
                self.puerto.close()
            return buffer
        else:
            return self.puerto.read(byteNumber)
    
    def getIMEI(self):
        pass
    def setIMEI(self):
        pass
import constants
import serial
import time
class Com(object):
    
    def __init__(self,comNumber: int):
        super(Com,self).__init__()
        self.comNumber=comNumber
        self.status=constants.OFFLINE
        self.puerto=serial.Serial()
    
    def startSerial(self):
        self.puerto=serial.Serial('COM'+str(self.comNumber),baudrate=constants.BAUDRATE,
            timeout=constants.WAITINGTIME)
        self.send(b"AT\r\n")
        self.read(2)
        self.status=constants.OK

    def dial(self,numero: str):
        self.send(b'ATD'+numero+'\r\n')
        self.read(2)
        time.sleep(5)
        self.send(b'ATH\r\n')
        
    def send(self, msg: bytes):
        self.puerto.write(msg)

    def read(self,byteNumbers):
        return self.puerto.read(byteNumbers)
    
    def getIMEI(self):
        pass
    def setIMEI(self):
        pass
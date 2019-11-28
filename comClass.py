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
        self.candado=threading.Lock()
        self.reading=threading.Lock()


    def autoAnswer(self):
        self.candado.acquire()
        print('%d voy a contestar' % self.comNumber)
        trt=1
        timeout=0
        time.sleep(8)
        try:
            while timeout<12:
                bytesToRead=self.puerto.inWaiting()
                if bytesToRead!=0:
                    x=self.sendRead(bits=bytesToRead)
                    if 'RING' in x: 
                        self.sendRead(b'ATA\r\n','OK')
                        #startingTime=time.time()
                        print("%d contestando" %self.comNumber)
                        trt=0
                    elif 'CARRIER' in x:
                        print("%d me colgo" %self.comNumber)
                        #print('%d me colgo, dure %ds' %(self.comNumber,time.time()-startingTime))
                        break
                    else:
                        print(x)
                timeout+=trt
                time.sleep(1)
            if timeout>=20:
                print('nadie llamo a',self.comNumber)
            self.changeState(constants.OK)
        except serial.SerialException as e:
            self.puerto.close()
            self.changeState(constants.OFFLINE)
            print('%d error contestando: %s' %(self.comNumber,str(e)))
        finally:
            self.candado.release()
    
    def hang(self,tiempo,numero=''):
        if tiempo!=0:
            self.candado.acquire()
        try:
            print('%d voy a llamar' % self.comNumber)
            if numero!='':
                if('OK' in self.sendRead(b'ATD'+numero.encode("utf-8")+b';\r\n','OK')):
                    self.changeState(constants.DIALING)
            time.sleep(tiempo)
            self.sendRead(b'ATH\r\n')
            print(self.comNumber,'colgue')
            self.changeState(constants.OK)
        except serial.SerialException:
            self.puerto.close()
            self.changeState(constants.OFFLINE)
            print('%d error llamando' %self.comNumber)

        finally:
            if tiempo!=0:
                self.candado.release()

    def ans(self):
        if self.status!=constants.DIALING:
            self.startSerial()
        if self.status==constants.OK or self.status==constants.DIALING:
            answer=threading.Thread(target=self.autoAnswer)
            answer.start()
            self.changeState(constants.DIALING)
            return True
        else:
            return False

    def startSerial(self):
        try:
            self.puerto.close()
            time.sleep(0.1)
            self.changeState(constants.OFFLINE)
            self.puerto=serial.Serial('COM'+str(self.comNumber),baudrate=constants.BAUDRATE,
                timeout=constants.WAITINGTIME)
        except serial.serialutil.SerialException:
            pass
        else:
            if('OK' in self.sendRead(b"AT\r\n",'OK',6)):
                self.changeState(constants.OK)

    def dial(self,numero: str,seconds: int):
        if self.status!=constants.DIALING:
            self.startSerial()
        if self.status==constants.OK or self.status==constants.DIALING:
            self.changeState(constants.DIALING)
            calling=threading.Thread(target=self.hang,args=(60,numero))
            calling._args=(seconds+10,numero)
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
        self.startSerial()
        result=self.sendRead(b'AT+CGSN\r\n')
        if 'OK' in result:
            #TRUENA CON UN RING
            return result[6:21]

    def setIMEI(self,imei: str):
        self.startSerial()
        if self.status==constants.OK:
            if('OK' in self.sendRead(b'AT+EGMR=1,7,"'+imei.encode('utf-8')+b'"\r\n','OK')):
                return True
            else:
                return False
    
    def getCCID(self):
        self.startSerial()
        result=self.sendRead(b'AT+CCID\r\n')
        if 'OK' in result:
            res=""
            flag=False
            for x in result:
                if x=='"':
                    flag = not flag 
                elif flag:
                    res+=x
                elif res!="":
                    break
            return res
        else:
            return None

    
    def sendRead(self,msg=b'',expected='',bits=0):
        self.reading.acquire()
        if msg != b'':
            self.send(msg)
        x=self.read(bits)
        if expected!='':
            if(expected in str(x)):
                self.reading.release()
                return expected
            else:
                self.reading.release()
                return str(x)
        else:
            self.reading.release()
            return str(x)

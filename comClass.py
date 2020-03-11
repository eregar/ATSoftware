import constants
import serial
import time
import threading
class Com(object):
    #implementar sendread con mas tiempo de espera
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
            startingTime=0
            while timeout<12:
                bytesToRead=self.puerto.inWaiting()
                if bytesToRead!=0:
                    x=self.sendRead(bits=bytesToRead)
                    if 'RING' in x: 
                        self.sendRead(b'ATA\r\n','OK')
                        startingTime=time.time()
                        print("%d contestando" %self.comNumber)
                        trt=0
                    elif 'CARRIER' in x:
                        print('%d me colgo, duracion: %dseg' %(self.comNumber,time.time()-startingTime))
                        break
                    else:
                        print(self.comNumber,x)
                timeout+=trt
                time.sleep(1)
            print(timeout)
            if timeout>=12:
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
            calling.join()
            return True
        else:
            return False
    
    def changeState(self,estado: str):
        #signalChange(self,estado)
        self.status=estado
        
    def send(self, msg: bytes):
        self.puerto.write(msg)

    def read(self,byteNumber=0,expected='OK'):
        if byteNumber==0:
            buffer=''
            timeout=0
            time.sleep(0.2)
            while timeout<=constants.WAITINGTIME:
                byteNumber=self.puerto.inWaiting()
                if byteNumber!=0:
                    buffer+=str(self.puerto.read(byteNumber))
                if 'OK' in buffer or expected in buffer:
                    break
                timeout+=1
                time.sleep(1)
            if buffer=='':
                print('%d didnt respond'%self.comNumber)
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
            return res[:-1]
        else:
            return None
    
    def sendUssd(self,ussdCode:str="#999#",stepstoFollow:str="0"):
        #Cancel session
        # #AT+CUSD=2
        #AT+CUSD=1,"#999#",15 
        #15= codigo de GSM
        #AT+CUSD=1,"1"
        self.startSerial()
        if self.status==constants.OK:
            self.sendRead(b'AT+CUSD=1,'+ussdCode.encode('utf-8')+b',15\r\n','OK')
            time.sleep(0.5)
            print(self.sendRead(expected=''))
            stepstoFollow=stepstoFollow.strip()
            for x in stepstoFollow:
                #self.sendRead(b'AT+CUSD=1,'+bytes([x])+b'\r\n','OK')
                self.sendRead(b'AT+CUSD=1,'+x.encode('utf-8')+'\r\n','OK')
                time.sleep(0.5)
                print(self.sendRead(expected=''))

    def dialWithCode(self,dialNumber:str="*264",stepstoFollow:str="0",numberToCode="0"):
        TIEMPOADP=15
        TIEMPOENTREINSTRUCCIONES=5
        TIEMPOENTRENUMERO=0.8
        TIEMPOCONFIRMACION=10
        TIEMPOCOLGAR=20
        self.startSerial()
        if self.status==constants.OK:
            self.sendRead(b'ATD'+dialNumber.encode('utf-8')+b';\r\n','OK')
            self.status=constants.DIALING
            stepstoFollow=stepstoFollow.strip()
            print("saltando aviso de privacidad")
            time.sleep(TIEMPOADP)
            for x in stepstoFollow:
                time.sleep(TIEMPOENTREINSTRUCCIONES+5*(int(x)))
                print("ingresando",x)
                self.sendRead(b'at+vts='+x.encode('utf-8')+b'\r\n','OK')
            time.sleep(TIEMPOENTREINSTRUCCIONES-1)#maybe 10
            print("ingresando numero")
            for x in numberToCode:
                time.sleep(TIEMPOENTRENUMERO)
                self.sendRead(b'at+vts='+x.encode('utf-8')+b'\r\n','OK')
            print("esperando confirmacion")
            time.sleep(TIEMPOCONFIRMACION)
            print("esperando colgar")
            self.sendRead(b'at+vts=1\r\n','OK')#confirmar
            time.sleep(TIEMPOCOLGAR)
            self.sendRead(b'ATH\r\n')
            print(self.comNumber,"instrucciones completadas")
        else:
            print(self.comNumber,"algo salio mal")
            



        

    def sendSMS(self,destino:str,contenido:str):
        if self.status==constants.OK:
            self.startSerial()
        if self.status==constants.OK:
            print("cambiando flag")
            self.sendRead(b'AT+CMGF=1\r\n','OK')
            print("cambiando storage")
            self.sendRead(b'AT+CPMS="SM"\r\n','OK')
            print("enviando")
            self.sendRead(b'AT+CMGS="'+destino.encode('utf-8')+b'"\r\n','>')
            print("poniendo contenido")
            result=self.sendRead(contenido.encode('utf-8')+b'\r\n'+b'\x1a')
            if 'OK' in result:
                #find ':' +2 espacios=numero de mensaje
                print(result)
            else:
                print(self.comNumber,'no ok',result)

    def getSMS(self):
        if self.status==constants.OK:
            self.startSerial()
        if self.status==constants.OK:
            self.sendRead(b'AT+CMGF=1\r\n','OK')
            self.sendRead(b'AT+CPMS="SM"\r\n','OK')
            print("COM",self.comNumber,":") #ERASE LATER
            result=self.sendRead(b'AT+CMGL="ALL"\r\n')
            if 'OK' in result:
                return result
            else:
                print(self.comNumber,'fasho')
                return result
    
    def sendRead(self,msg=b'',expected='',bits=0):
        self.reading.acquire()
        if msg != b'':
            self.send(msg)
        if expected!='':
            x=self.read(bits,expected)
            if(expected in str(x)):
                self.reading.release()
                return expected
            else:
                self.reading.release()
                return str(x)
        else:
            x=self.read(bits)
            self.reading.release()
            return str(x)

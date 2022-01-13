class Opener:
    def __init__(self):
        self.lines=''
        self.imeiC=-1
        self.numberC=-1
        self.iccidC=-1

    def readArchivo(self,arch):
        if arch:
            self.lines=arch.readlines()
            arch.close()
            if self._setColumns():
                return True
        return False

    def getLines(self):
        return self.lines

    def getLine(self, line:int):
        if(line<len(self.lines)):
            return self.lines[line]
        else: return self.lines[0]

    def _setColumns(self,separator=','):
        if self.numberC ==-1 or self.iccidC == -1:
            l=self.lines[0].split(separator)
            for s in range(len(l)):
                if len(l[s].strip('\n').strip())==10: 
                    self.numberC=s
                elif len(l[s].strip('\n').strip())==19:
                    self.iccidC=s
                elif len(l[s].strip('\n').strip())==15:
                    self.imeiC=s
            if self.iccidC == -1:
                print("no se encuentra un iccid aceptable en el archivo")
                return False
            if self.numberC == -1:
                print("no se encuentra un numero aceptable en el archivo")
                return False
            if self.imeiC == -1:
                self.imeiC = 0
        return True
        

    def buscarIccid(self,ccid: str,separator=','):
        for l in self.lines:
            l=l.split(separator)
            if ccid in l[self.iccidC]:
                if len(l[self.numberC].strip('\n').strip())!=10:
                    print("Error: el numero del archivo no es del tamanio correcto")
                    print(l[self.numberC])
                    return(None,None)
                if len(l)>=3:
                    if len(l[self.imeiC].strip('\n').strip())!=15:
                        print("Warning: el imei no es del tamanio suficiente")
                        return(l[self.numberC],None)
                    return(l[self.numberC].strip('\n').strip(),l[self.imeiC].strip('\n').strip())
                else:
                    return(l[self.numberC].strip('\n').strip(),None)
        return(None,None)
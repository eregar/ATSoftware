archivo=""
IMEI=1
NUMERO=2
CCID=3

def abrir(arch: str):
    global archivo
    try:
        archivo=open(arch,'r').readlines()
    except FileNotFoundError:
        return False
    else:
        return True

def readArchivo(arch):
    global archivo
    if arch:
        archivo=arch.readlines()
        arch.close()
        return True
    else:
        return False

def listNumbers():
    global archivo
    res=[]
    for l in archivo:
        l=l.split(',')
        if len(l)!=3:
            l=l[0].split(';')
        for p in l:
            try:
                int(p)
                if len(p.strip())==10:
                    res.append(p.strip())
            except:
                continue
    return res


def buscar(ccid: str):
    global archivo
    imeiC=0
    numberC=1
    ccidC=2

    for l in archivo:
        l=l.split(',')
        if len(l)!=3:
            l=l[0].split(';')
            if len(l)!=3:
                print("numero incorrecto de columnas, se necesita IMEI,NUMERO,ICCID")
                return (None,None)
        if ccid in l[ccidC]:
            if len(l[numberC])!=10:
                print("un numero no es del tamanio correcto, se necesita IMEI,NUMERO,ICCID")
                return (None,None)
            if len(l[imeiC])!=15:
                print("Warning: un imei no es del tamanio suficiente")
                return(l[numberC],None)

            return (l[numberC],l[imeiC])

    return (None,None)


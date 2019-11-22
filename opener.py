archivo=""


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
        for p in l:
            try:
                int(p)
                if len(p.strip())==10:
                    res.append(p.strip())
            except:
                continue
    return res

def buscar(numero: str):
    global archivo
    imeiC=0
    numberC=1
    muestra=archivo[0].split(',')
    if ('IMEI' in muestra[0].upper() or len(muestra[0])==15):
        imeiC=0
        numberC=1
    elif('IMEI' in muestra[1].upper() or len(muestra[1])==15):
        numberC=0
        imeiC=1

    for l in archivo:
        l=l.split(',')
        if numero in l[numberC]:
            if len(l[imeiC])==15:
                return l[imeiC]
            else:
                print("un imei no es del tamanio suficiente")
                return '0'
    return '0'


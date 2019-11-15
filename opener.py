archivo=''


def abrir(arch: str):
    global archivo
    try:
        archivo=open(arch,'r').readlines()
    except FileNotFoundError:
        return False
    else:
        return True

def buscar(numero: str):
    global archivo
    for l in archivo:
        l=l.split(',')
        if numero in l[1]:
            if len(l[0])==15:
                return l[0]
            else:
                return '0'
    return '0'


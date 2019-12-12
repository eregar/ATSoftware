

class Mensaje(object):
    
    def __init__(self, destinatario: str, contenido: str):
        super(Mensaje,self).__init__()
        self.__destinatario=destinatario
        self.__contenido=contenido

    def getDestinatario(self):
        return self.__destinatario

    def getContenido(self):
        return self.__contenido

    @classmethod
    def obtenerSMS(cls,texto:str):
        pass


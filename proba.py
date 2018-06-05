from DZ2idiot import *
separatori = [Tokeni.OOTV, Tokeni.OZATV, Tokeni.UOTV, Tokeni.UZATV, Tokeni.VOTV, Tokeni.VZATV,
     Tokeni.ZAREZ, Tokeni.DVOTOCKA]

def sranje():
    znak = ';'
    #for token in separatori:
        #print (token)
    #    if(token == Tokeni(znak)):
    #        return token
    return (token for token in separatori if token == Tokeni(znak))

lista = sranje()
print(lista)
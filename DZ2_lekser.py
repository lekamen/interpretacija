
from string import hexdigits
from pj import *
from collections import ChainMap
from DZ2idiot import *

separatoriZnakovi = '()[]{},;'
escapeZnakovi = ['\n', '\t', '\v', '\b', '\r', '\f', '\a', '\'', '\"', '\\']
escapeChars = ['n', 't', 'v', 'b', 'r', 'f', 'a', "'", '"', '\\']
tipoviPodataka = {'int', 'bool', 'char', 'string'}
assignOperators = {Tokeni.PLUSEQ, Tokeni.MINUSEQ, Tokeni.ZVJEQ, Tokeni.SLASHEQ, Tokeni.MODEQ, Tokeni.LSHIFTEQ, Tokeni.RSHIFTEQ, Tokeni.ASSIGN, Tokeni.ANDEQ, Tokeni.POTEQ, Tokeni.CRTAEQ}
#ESCAPE ZNAKOVE VIDI TREBAS LI ZASEBNO

#rezervirane riječi
Void = Token(Tokeni.IDENTIFIER, 'void')
Struct = Token(Tokeni.IDENTIFIER, 'struct')
Typedef = Token(Tokeni.IDENTIFIER, 'typedef')
If = Token(Tokeni.IDENTIFIER, 'if')
Else = Token(Tokeni.IDENTIFIER, 'else')
While = Token(Tokeni.IDENTIFIER, 'while')
For = Token(Tokeni.IDENTIFIER, 'for')
Continue = Token(Tokeni.IDENTIFIER, 'continue')
Break = Token(Tokeni.IDENTIFIER, 'break')
Return = Token(Tokeni.IDENTIFIER, 'return')
Assert = Token(Tokeni.IDENTIFIER, 'assert')
Alloc = Token(Tokeni.IDENTIFIER, 'alloc')
Alloc_array = Token(Tokeni.IDENTIFIER, 'alloc_array')

def isxdigit(znak):
    """Provjerava je li znak hex znamenka"""
    return znak != '' and (znak.isdigit() or znak in 'ABCDEFabcdef')

def isidentifier(znak):
    """Provjerava je li znak nešto što ide u identifier"""
    return znak.isalpha() or znak.isdigit() or znak == '_'

def isNChar(znak):
    """Provjerava je li znak nchar"""
    p = re.compile('^[ -~]$')
    if (p.match(znak) is None or znak == '"'):
        return False
    return True

def isSChar(znak):
    """Provjerava je li znak schar"""
    if (isNChar(znak) or znak in escapeZnakovi):
        return True
    return False

def isLChar(znak):
    """Provjerava je li znak lchar"""
    p = re.compile('^[ -~]$')
    if (p.match(znak) is None or znak == '>'):
        return False
    return True

def Lekser(kôd):
    lex = Tokenizer(kôd)
    citamString = False

    for znak in iter(lex.čitaj, ''):
        if (citamString):
            if znak == '\\':
                idući = lex.čitaj()
                if (idući not in escapeChars):
                    lex.greška("Neispravan string")
            elif isNChar(znak):
                continue
            elif znak == '"':
                citamString = False
                yield lex.token(Tokeni.STRLIT)
            else:
                lex.greška("Neispravan string")
        elif znak == ' ': 
            lex.token(E.PRAZNO) #enter i tabulator su nam tokeni
        elif znak == '"': #prelazimo u stanje citanja stringa
            citamString = True
            continue
        elif znak == 'i':
            sljedeći = lex.pogledaj()
            if sljedeći == 'f':
                # probaj pročitati if
                lex.čitaj()
                ssljedeći = lex.pogledaj()
                if ssljedeći.isspace():
                    yield lex.token(Tokeni.IF)
                else:
                # ako ne uspije, vrati glavu nazad
                    lex.vrati()

        elif znak.isalpha() or znak == '_':
            # onda je identifier
            lex.zvijezda(identifikator)
            if lex.sadržaj in {'true', 'false'}: yield lex.token(Tokeni.BOOLEAN)
            elif (lex.sadržaj == 'NULL'): yield lex.token(Tokeni.NULL)
            elif (lex.sadržaj in tipoviPodataka): yield lex.token(Tokeni(lex.sadržaj))
            else:
                yield lex.token(Tokeni.IDENTIFIER)
        elif znak.isdigit(): 
            # onda je dec ili hex
            if znak == '0': 
                sljedeći = lex.pogledaj()
                if sljedeći == 'x' or sljedeći == 'X':
                    # onda je hex
                    lex.čitaj()
                    lex.plus(isxdigit)
                    yield lex.token(Tokeni.HEKSADEKADSKI)
                elif sljedeći.isdigit():
                    lex.greška('očekujem x ili X')
                    
                else:
                    yield lex.token(Tokeni.DECIMALNI)
                        
            else:
                lex.pogledaj()
                # onda je dec
                lex.zvijezda(str.isdigit)
                yield lex.token(Tokeni.DECIMALNI)

        # TODO: liblit se MORA prepoznavati u parseru!!!
        # je li chrlit?
        elif znak == "'":
            idući = lex.čitaj()
            if (not isNChar(idući) and not idući in escapeZnakovi and not idući == '"' and not idući == '\0'):
                raise RuntimeError("Neispravan chrlit")
            kraj = lex.čitaj()
            if (kraj == "'"):
                yield lex.token(Tokeni.CHRLIT)
            else:
                raise RuntimeError("Neispravan chrlit")           
        #je li escape sekvenca ili separator?
        elif znak in separatoriZnakovi:
            yield lex.token(Tokeni(znak))
        elif znak in escapeZnakovi:
            if (znak.isspace()):
                lex.token(Tokeni(znak))
            else:
                yield lex.token(Tokeni(znak))
        # je li operator?
        # !, !=
        elif znak == '!':
            sljedeći = lex.pogledaj()
            if sljedeći == '=':
                lex.čitaj()
                yield lex.token(Tokeni.DISEQ)
            else:
                yield lex.token(Tokeni.USKL)
        # ~
        elif znak == '~':
            yield lex.token(Tokeni.TILDA)
        # *, *=
        elif znak == '*':
            sljedeći = lex.pogledaj()
            if sljedeći == '=':
                lex.čitaj()
                yield lex.token(Tokeni.ZVJEQ)
            elif sljedeći == '/':
                lex.čitaj()
                yield lex.token(Tokeni.COM_END)
            else: 
                yield lex.token(Tokeni.ZVJ)
        # .
        elif znak == '.':
            yield lex.token(Tokeni.TOCKA)
        # -, ->, -=, --
        elif znak == '-':
            sljedeći = lex.pogledaj()
            if sljedeći == '>':
                lex.čitaj()
                yield lex.token(Tokeni.STRELICA)
            elif sljedeći == '=':
                lex.čitaj()
                yield lex.token(Tokeni.MINUSEQ)
            elif sljedeći == '-':
                lex.čitaj()
                yield lex.token(Tokeni.DECR)
            else:
                yield lex.token(Tokeni.MINUS)
        # /, /=
        elif znak == '/':
            sljedeći = lex.pogledaj()
            if sljedeći == '=':
                lex.čitaj()
                yield lex.token(Tokeni.SLASHEQ)
            elif sljedeći == '/':
                lex.čitaj()
                yield lex.token(Tokeni.COMMENT)
            elif sljedeći == '*':
                lex.čitaj()
                yield lex.token(Tokeni.COM_BEGIN)
            else:
                yield lex.token(Tokeni.SLASH)
        # %, %=
        elif znak == '%':
            sljedeći = lex.pogledaj()
            if sljedeći == '=':
                lex.čitaj()
                yield lex.token(Tokeni.MODEQ)
            else:
                yield lex.token(Tokeni.MOD)
        
        # +, +=, ++
        elif znak == '+':
            sljedeći = lex.pogledaj()
            if sljedeći == '=':
                lex.čitaj()
                yield lex.token(Tokeni.PLUSEQ)
            elif sljedeći == '+':
                lex.čitaj()
                yield lex.token(Tokeni.INCR)
            else:
                yield lex.token(Tokeni.PLUS)
        #neki od operatora <, <<, <<=, <=?
        elif znak == '<':
            sljedeći = lex.pogledaj()

            if sljedeći == '<':
                lex.čitaj()
                ssljedeći = lex.pogledaj()
                if ssljedeći == '=':
                    lex.čitaj()
                    yield lex.token(Tokeni.LSHIFTEQ)
                else:
                    yield lex.token(Tokeni.LSHIFT)
            elif sljedeći == '=':
                lex.čitaj()
                yield lex.token(Tokeni.LESSEQ)
            else:
                yield lex.token(Tokeni.LESS)
        # >, >>, >>=, >=
        elif znak == '>':
            sljedeći = lex.pogledaj()
            if sljedeći == '>':
                lex.čitaj()
                ssljedeći = lex.pogledaj()
                if ssljedeći == '=':
                    lex.čitaj()
                    yield lex.token(Tokeni.RSHIFTEQ)
                else:
                    yield lex.token(Tokeni.RSHIFT)
            elif sljedeći == '=':
                lex.čitaj()
                yield lex.token(Tokeni.GRTEQ)
            else:
                yield lex.token(Tokeni.GRT)
        # =, ==
        elif znak == '=':
            sljedeći = lex.pogledaj()
            if sljedeći == '=':
                lex.čitaj()
                yield lex.token(Tokeni.EQ)
            else:
                yield lex.token(Tokeni.ASSIGN)
        # &, &=, &&
        elif znak == '&':
            sljedeći = lex.pogledaj()
            if sljedeći == '=':
                lex.čitaj()
                yield lex.token(Tokeni.ANDEQ)
            elif sljedeći == '&':
                lex.čitaj()
                yield lex.token(Tokeni.LAND)
            else:
                yield lex.token(Tokeni.BITAND)
        # |, |=, ||
        elif znak == '|':
            sljedeći = lex.pogledaj()
            if sljedeći == '=':
                lex.čitaj()
                yield lex.token(Tokeni.CRTAEQ)
            elif sljedeći == '|':
                lex.čitaj()
                yield lex.token(Tokeni.LOR)
            else:
                yield lex.token(Tokeni.BITOR)
        # ^, ^=
        elif znak == '^':
            sljedeći = lex.pogledaj()
            if sljedeći == '=':
                lex.čitaj()
                yield lex.token(Tokeni.POTEQ)
            else:
                yield lex.token(Tokeni.BITEXCLOR)
        # ?
        elif znak == '?':
            yield lex.token(Tokeni.CONDQ)
        # :
        elif znak == ':':
            yield lex.token(Tokeni.CONDDOT)


osnovniIzrazi = {Tokeni.DECIMALNI, Tokeni.HEKSADEKADSKI, Tokeni.STRLIT, Tokeni.CHRLIT,
            Tokeni.BOOLEAN, Tokeni.IDENTIFIER, Tokeni.NULL}
class C0Parser(Parser):

    def stmt(self):
        print(" u naredbi ")
        #ovdje prvo ispitat jesu tokeni if, while, for, return, assert, error
        if self >> Tokeni.VOTV:
            blok = self.stmt()
            self.pročitaj(Tokeni.VZATV)
            return blok
        else:
            simple = self.simple()
            self.pročitaj(Tokeni.SEP)
            return simple


    def simple(self):
        #ostali.....
        if self >> {Tokeni.INT, Tokeni.BOOL, Tokeni.STRING, Tokeni.CHAR}:
            tip = self.zadnji
            varijabla = self.pročitaj(Tokeni.IDENTIFIER)
            print("Jesmo ovdje")
            print(tip)
            print(varijabla)
            if self >> Tokeni.ASSIGN:
                var = Varijabla(tip, varijabla)
                desna = self.expression()
                return Pridruživanje(var, desna)
            else:
                return Varijabla(tip, varijabla)
        else:
            return self.expression()

    def expression(self):
        print ("u izrazu")
        print (self.pogledaj())

        trenutni = self.logički()

        while True:
            if self >> Tokeni.CONDQ:
                prviUvjet = self.expression()
                self.pročitaj(Tokeni.CONDDOT)
                drugiUvjet = self.expression()
                #možda ovdje promijenit jer je drukčija asocijativnost !?
                trenutni = TernarniOperator(trenutni, prviUvjet, drugiUvjet)
            else: return trenutni

        # if self >> Tokeni.IDENTIFIER:
        #     var = self.zadnji
        #     idući = self.pogledaj()
        #     print(idući)
        #     if idući ** Tokeni.OOTV:
        #         self.pročitaj(Tokeni.OOTV)
        #         konstruktor_argumenti = []
        #         while True:
        #             sljedeći = self.pogledaj()
        #             print(sljedeći)
        #             if sljedeći ** Tokeni.OZATV:
        #                 self.pročitaj(Tokeni.OZATV)
        #                 break
        #             else:
        #                 ssljedeći = self.expression()
        #                 konstruktor_argumenti.append(ssljedeći)
        #                 zarez = self.pogledaj()
        #                 if zarez ** Tokeni.ZAREZ:
        #                     self.pročitaj(Tokeni.ZAREZ)
        #                 print("daddy attention" + str(zarez))
        #         return Konstrukcija(var, konstruktor_argumenti)

        else:
            #do ovdje su odrađeni svi slučajevi gramatike gdje
            #prvi član pravila nije expression
            self.greška()
            #može se dogoditi i da stoji samo jedan izraz, mora se i to obraditi

    def logički(self):
        trenutni = self.bitwise()
        while True:
            if self >> {Tokeni.LAND, Tokeni.LOR}:
                operacija = self.zadnji
                trenutni = LogičkaOperacija(trenutni, self.bitwise(), operacija)
            else: return trenutni

    def bitwise(self):
        trenutni = self.equality()
        while True:
            if self >> {Tokeni.BITAND, Tokeni.BITEXCLOR, Tokeni.BITOR}:
                operacija = self.zadnji
                trenutni = BitwiseOperacija(trenutni, self.equality(), operacija)
            else: return trenutni

    def equality(self):
        trenutni = self.comparison()
        while True:
            if self >> {Tokeni.EQ, Tokeni.DISEQ}:
                operacija = self.zadnji
                trenutni = Equality(trenutni, self.comparison(), operacija)
            else: return trenutni

    def comparison(self):
        trenutni = self.shifts()
        while True:
            if self >> {Tokeni.LESS, Tokeni.LESSEQ, Tokeni.GRT, Tokeni.GRTEQ}:
                operacija = self.zadnji
                trenutni = Comparison(trenutni, self.shifts(), operacija)
            else: return trenutni

    def shifts(self):
        trenutni = self.add()
        while True:
            if self >> {Tokeni.LSHIFT, Tokeni.RSHIFT}:
                operacija = self.zadnji
                trenutni = BinarnaOperacija(trenutni, self.add(), operacija)
            else: return trenutni

    def add(self):
        trenutni = self.factor()
        while True:
            if self >> {Tokeni.PLUS, Tokeni.MINUS}:
                operacija = self.zadnji
                trenutni = BinarnaOperacija(trenutni, self.factor(), operacija)
            else: return trenutni

    def factor(self):
        trenutni = self.assign()
        while True:
            if self >> {Tokeni.ZVJ, Tokeni.SLASH, Tokeni.MOD}:
                operacija = self.zadnji
                trenutni = BinarnaOperacija(trenutni, self.unaries(), operacija)
                
            else: return trenutni
    def assign(self):
        trenutni = self.unaries()
        while True:
            if self >> assignOperators:
                operacija = self.zadnji
                trenutni = Assignment(trenutni, self.expression(), operacija)
            else: return trenutni

    def unaries(self):
        #fali zvjezdica
        if self >> Tokeni.USKL:
            iza = self.expression()
            return Negacija(iza)
        if self >> Tokeni.TILDA:
            iza = self.expression()
            return Tilda(iza)
        if self >> Tokeni.MINUS:
            iza = self.expression()
            return Minus(iza)

        baza = self.base()
        return baza

    def base(self):
        #odradit operatore, pozvat expression
        if self >> Tokeni.OOTV:
            u_zagradi = self.expression()
            self.pročitaj(Tokeni.OZATV)
            return u_zagradi
        if self >> osnovniIzrazi:
            trenutni = self.zadnji
        return trenutni


    def start(self):
        naredbe = [self.stmt()]
        while not self >> E.KRAJ:
            naredbe.append(self.stmt())
        return Program(naredbe)

class Program(AST('naredbe')):
    def vrijednost(self):
        tipovi = ChainMap()
        vrijednosti = ChainMap()
        rezultati = []
        for naredba in self.naredbe: 
            rezultati.append(naredba.vrijednost(tipovi, vrijednosti))
        return tipovi, vrijednosti, rezultati

class Varijabla(AST('tip ime')):
    def vrijednost(izraz, imena, vrijednosti):
        imena[izraz.ime] = izraz.tip
        return izraz.ime

class Pridruživanje(AST('varijabla vrijedn')):
    """Pridruživanje u inicijalizaciji varijable. Podržava samo operator '='."""
    # zasad ne podržava izraze oblika int a = b = 3;
    # baca nekompatibilne tipove
    def vrijednost(izraz, imena, vrijednosti):

        izraz.varijabla.vrijednost(imena, vrijednosti)
        if izraz.varijabla.tip ** Tokeni.INT:
            if (type(izraz.vrijedn.vrijednost(imena, vrijednosti)) is not int):
                raise ValueError("Nekompatibilni tipovi")
            else: 
                vrijednosti[izraz.varijabla.ime] = izraz.vrijedn
                return int(izraz.vrijedn.sadržaj)

        elif izraz.varijabla.tip ** Tokeni.CHAR:
            if (not isinstance(izraz.vrijedn.vrijednost(imena, vrijednosti), str) or len(izraz.vrijedn.vrijednost(imena, vrijednosti)) != 1):
                raise ValueError("Nekompatibilni tipovi")
            else:
                vrijednosti[izraz.varijabla.ime] = izraz.vrijedn
                return izraz.vrijedn.sadržaj[1:-1]

        elif izraz.varijabla.tip ** Tokeni.BOOL:
            if (not isinstance(izraz.vrijedn.vrijednost(imena, vrijednosti), bool)):
                raise ValueError("Nekompatibilni tipovi")
            else:
                vrijednosti[izraz.varijabla.ime] = izraz.vrijedn
                return bool(izraz.vrijedn.sadržaj)

        elif izraz.varijabla.tip ** Tokeni.STRING:
            if (not isinstance(izraz.vrijedn.vrijednost(imena, vrijednosti), str)):
                raise ValueError("Nekompatibilni tipovi")
            else:
                vrijednosti[izraz.varijabla.ime] = izraz.vrijedn
                return izraz.vrijedn.sadržaj

class Assignment(AST('lijevaStrana desnaStrana operator')):
    """Pridruživanje van inicijalizacije varijabli. Podržava sve operatore pridruživanja"""
    def vrijednost(izraz, imena, vrijednosti):

        if (izraz.lijevaStrana in imena):
            lijevi = vrijednosti[izraz.lijevaStrana].vrijednost(imena, vrijednosti)
            print("prvi if")
        else:
            lijevi = izraz.lijevaStrana.vrijednost(imena, vrijednosti)
            print("prvi else")

        if (izraz.desnaStrana in imena):
            desni = vrijednosti[izraz.desnaStrana].vrijednost(imena, vrijednosti)
            print("drugi if")
        else:
            desni = izraz.desnaStrana.vrijednost(imena, vrijednosti)
            print("drugi else")
        print("dobro pogledaj vedrane")
        print(lijevi)
        print(desni)
        print(isinstance(lijevi, int))
        print(isinstance(desni, int))
        if (isinstance(lijevi, int)):
            if (not isinstance(desni, int)):
                raise ValueError("Nekompatibilni tipovi")
            else: 
                Assignment.pridruži(izraz.lijevaStrana, desni, izraz.operator, vrijednosti)
                return int(vrijednosti[izraz.lijevaStrana].sadržaj)

        #elif (isinstance(lijevi, str) and len(lijevi) == 1):
        #    if (not (isinstance(lijevi, str) and len(lijevi) == 1)):
        #        raise ValueError("Nekompatibilni tipovi")
        #    else:
        #        Assignment.pridruži(vrijednosti[izraz.lijevaStrana.ime], desni, izraz.operator)
        #        return vrijednosti[izraz.lijevaStrana.ime][1:-1]

        #elif isinstance(lijevi, bool):
        #    if (not isinstance(desni, bool)):
        #        raise ValueError("Nekompatibilni tipovi")
        #    else:
        #        Assignment.pridruži(vrijednosti[izraz.lijevaStrana.ime], desni, izraz.operator)
        #        return bool(vrijednosti[izraz.lijevaStrana.ime])

        #elif isinstance(lijevi, str):
        #    if (not isinstance(desni, str)):
        #        raise ValueError("Nekompatibilni tipovi")
        #    else:
        #        Assignment.pridruži(vrijednosti[izraz.lijevaStrana.ime], vrijednosti[izraz.desnaStrana.ime], izraz.operator)
        #        return vrijednosti[izraz.lijevaStrana.ime]
        else:
            raise ValueError("Ne znam assignati operande ovog tipa!")

    def pridruži(lijevo, desno, operator, vrijednosti):
        lijevo_val = int(vrijednosti[lijevo].sadržaj)
        if operator ** Tokeni.ASSIGN:
            lijevo_val = desno
        elif operator ** Tokeni.PLUSEQ:
            lijevo_val = lijevo_val + desno
        elif operator ** Tokeni.MINUSEQ:
            lijevo_val = lijevo_val - desno
        elif operator ** Tokeni.ZVJEQ:
            lijevo_val = lijevo_val * desno
        elif operator ** Tokeni.SLASHEQ:
            lijevo_val = int(lijevo_val/desno)
        elif operator ** Tokeni.MODEQ:
            lijevo_val = lijevo_val % desno
        elif operator ** Tokeni.LSHIFTEQ:
            lijevo_val = lijevo_val << desno
        elif operator ** Tokeni.RSHIFTEQ:
            lijevo_val = lijevo_val >> desno
        elif operator ** Tokeni.ANDEQ:
            lijevo_val = lijevo_val & desno
        elif operator ** Tokeni.POTEQ:
            lijevo_val = lijevo_val ^ desno
        elif operator ** Tokeni.CRTAEQ:
            lijevo_val = lijevo_val | desno

        lijevo_val = str(lijevo_val)
        vrijednosti[lijevo] = Token(Tokeni.DECIMALNI, lijevo_val)


        

class Comparison(AST('lijevaStrana desnaStrana operator')):
    def vrijednost(izraz, imena, vrijednosti):

        if (izraz.lijevaStrana in imena):
            lijevi = vrijednosti[izraz.lijevaStrana].vrijednost(imena, vrijednosti)
        else:
            lijevi = izraz.lijevaStrana.vrijednost(imena, vrijednosti)

        if (izraz.desnaStrana in imena):
            desni = vrijednosti[izraz.desnaStrana].vrijednost(imena, vrijednosti)
        else:
            desni = izraz.desnaStrana.vrijednost(imena, vrijednosti)

        #dozvoljeni su samo int i char
        if ((isinstance(lijevi, int) and isinstance(desni, int))
            or (isinstance(lijevi, str) and len(lijevi) == 1 and
             isinstance(desni, str) and len(desni) == 1)):
        
            if (type(lijevi) != type(desni)):
                raise ValueError("neispravno uspoređivanje")

            if izraz.operator ** Tokeni.LESS: return lijevi < desni
            elif izraz.operator ** Tokeni.LESSEQ: return lijevi <= desni
            elif izraz.operator ** Tokeni.GRT: return lijevi > desni
            elif izraz.operator ** Tokeni.GRTEQ: return lijevi >= desni
            else: assert not 'slučaj'
        else:
            raise ValueError("neispravna usporedba")
        

class Equality(AST('lijevaStrana desnaStrana operator')):
    def vrijednost(izraz, imena, vrijednosti):

        if (izraz.lijevaStrana in imena):
            lijevi = vrijednosti[izraz.lijevaStrana].vrijednost(imena, vrijednosti)
        else:
            lijevi = izraz.lijevaStrana.vrijednost(imena, vrijednosti)

        if (izraz.desnaStrana in imena):
            desni = vrijednosti[izraz.desnaStrana].vrijednost(imena, vrijednosti)
        else:
            desni = izraz.desnaStrana.vrijednost(imena, vrijednosti)
        
        if (type(lijevi) != type(desni)):
            raise ValueError("neispravno uspoređivanje")

        if izraz.operator ** Tokeni.EQ: return lijevi == desni
        elif izraz.operator ** Tokeni.DISEQ: return lijevi != desni
        else: assert not 'slučaj'

class BinarnaOperacija(AST('lijevaStrana desnaStrana operacija')):
    def vrijednost(izraz, imena, vrijednosti):
        try:
            if (izraz.lijevaStrana in imena):
                lijevi = vrijednosti[izraz.lijevaStrana].vrijednost(imena, vrijednosti)
            else:
                lijevi = int(izraz.lijevaStrana.vrijednost(imena, vrijednosti))

            if (izraz.desnaStrana in imena):
                desni = vrijednosti[izraz.desnaStrana].vrijednost(imena, vrijednosti)
            else:
                desni = int(izraz.desnaStrana.vrijednost(imena, vrijednosti))
        except ValueError:
            raise ValueError("neispravna binarna operacija")
        
        if izraz.operacija ** Tokeni.PLUS:
            rezultat = lijevi + desni
        elif izraz.operacija ** Tokeni.MINUS:
            rezultat = lijevi - desni
        elif izraz.operacija ** Tokeni.ZVJ:
            rezultat = lijevi * desni
        elif izraz.operacija ** Tokeni.SLASH:
            rezultat = int(lijevi / desni)
        elif izraz.operacija ** Tokeni.MOD:
            rezultat = lijevi % desni
        elif izraz.operacija ** Tokeni.LSHIFT:
            rezultat = lijevi << desni
        elif izraz.operacija ** Tokeni.RSHIFT:
            rezultat = lijevi >> desni                

        return rezultat

class BitwiseOperacija(AST('lijevaStrana desnaStrana operacija')):
    def vrijednost(izraz, imena, vrijednosti):
        # pretty much copy paste binarne operacije, uz mini izmjene
        try:
            if (izraz.lijevaStrana in imena):
                lijevi = vrijednosti[izraz.lijevaStrana].vrijednost(imena, vrijednosti)
            else:
                lijevi = (izraz.lijevaStrana.vrijednost(imena, vrijednosti))

            if (izraz.desnaStrana in imena):
                desni = vrijednosti[izraz.desnaStrana].vrijednost(imena, vrijednosti)
            else:
                desni = (izraz.desnaStrana.vrijednost(imena, vrijednosti))
        except ValueError:
            raise ValueError("neispravna bitwise operacija")
        
        if izraz.operacija ** Tokeni.BITAND:
            rezultat = lijevi & desni
        elif izraz.operacija ** Tokeni.BITOR:
            rezultat = lijevi | desni 
        elif izraz.operacija ** Tokeni.BITEXCLOR:
            rezultat = lijevi ^ desni

        return rezultat

class LogičkaOperacija(AST('lijevaStrana desnaStrana operacija')):
    def vrijednost(izraz, imena, vrijednosti):
        # pretty much copy paste binarne operacije, uz mini izmjene
        try:
            if (izraz.lijevaStrana in imena):
                lijevi = vrijednosti[izraz.lijevaStrana].vrijednost(imena, vrijednosti)
                print("l: " + str(lijevi))
            else:
                lijevi = bool(izraz.lijevaStrana.vrijednost(imena, vrijednosti))

            if (izraz.desnaStrana in imena):
                desni = vrijednosti[izraz.desnaStrana].vrijednost(imena, vrijednosti)
                print("d: " + str(desni))
            else:
                desni = bool(izraz.desnaStrana.vrijednost(imena, vrijednosti))
        except ValueError:
            raise ValueError("neispravna logička operacija")
        
        if izraz.operacija ** Tokeni.LAND:
            rezultat = bool(lijevi and desni)
        elif izraz.operacija ** Tokeni.LOR:
            rezultat = bool(lijevi or desni)             

        return rezultat  

class TernarniOperator(AST('lijevaStrana prviUvjet drugiUvjet')):
    def vrijednost(izraz, imena, vrijednosti):
        return

class Negacija(AST('iza')):
    """Negacija izraza."""
    def vrijednost(izraz, imena, vrijednosti):
        return not izraz.iza.vrijednost()


class Tilda(AST('iza')):
    """Bitwise unary complement"""
    def vrijednost(izraz, imena, vrijednosti):
        return ~izraz.iza.vrijednost()

class Minus(AST('iza')):
    def vrijednost(izraz, imena, vrijednosti):
        return - izraz.iza.vrijednost()

class Konstrukcija(AST('objekt argumenti')):
    """Konstrukcija objekta s argumentima za konstruktor"""
    # zasad konstruktor podržava samo primitivne tipove
    def vrijednost(izraz, imena, vrijednosti):
        o = izraz.objekt.vrijednost()
        a = izraz.argumenti
        for argument in a:
            o = argument.vrijednost()
        return o
        

if __name__ == '__main__':
    #lista = list(Lekser("1 _nesto0 () ; * -> += <lib\"char  0x23 \n \t \v alo \' ' '\0'"))
    #lista = list(Lekser("1 _nesto0 () ; * //-> += <lib\"char0x23 bla_b<<=bl\" ba"))
    #ulaz = r'probaa "ha \n \"  \\ ha \v " nakon stringa '
    #ulaz = r'0x23 NULL      '
    # ulaz = r"""NULL; !true; ~5;  -5; int a = 2;  a(6); char c = 'a'; a('b'); 3 < 5; 
    #         a >= 10; a == true; b != false;
    #         a+5;
    #         a & 4;
    #         4&a;
    #         5+a;
    #         true && a;
    #         a || false;
    #         true ? true : false;
    #         a == true ? a : false;"""
    ulaz = r"""
       

        int b = 4;
        int a = 3;
        int c = 1;
        a = b = c;
        a == 1;
        b ==1;
        c ==1;

    """
    #TODO: konstrukcija ponovno uklopit
    #a * 3 + 5 * 7
    #vrati ovo    
    tokeni = list(Lekser(ulaz))
    print(*tokeni)
    program = C0Parser.parsiraj(tokeni)
    print(program)
    print(program.vrijednost())
    
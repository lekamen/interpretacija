from string import hexdigits
from pj import *
from collections import ChainMap
from DZ2idiot import *

separatoriZnakovi = '()[]{},;'
escapeZnakovi = ['\n', '\t', '\v', '\b', '\r', '\f', '\a', '\'', '\"', '\\']
escapeChars = ['n', 't', 'v', 'b', 'r', 'f', 'a', "'", '"', '\\']
naredbe = {'if', 'else', 'while', 'for', 'assert', 'error', 'print'}

assignOperators = {Tokeni.PLUSEQ, Tokeni.MINUSEQ, Tokeni.ZVJEQ, Tokeni.SLASHEQ, Tokeni.MODEQ, Tokeni.LSHIFTEQ, Tokeni.RSHIFTEQ, Tokeni.ASSIGN, Tokeni.ANDEQ, Tokeni.POTEQ, Tokeni.CRTAEQ}

def isxdigit(znak):
    """Provjerava je li znak hex znamenka"""
    return znak != '' and (znak.isdigit() or znak in 'ABCDEFabcdef')

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
        elif znak.isalpha() or znak == '_':
            # onda je identifier
            lex.zvijezda(identifikator)
            if lex.sadržaj in {'true', 'false'}: yield lex.token(Tokeni.BOOLEAN)
            elif (lex.sadržaj == 'NULL'): yield lex.token(Tokeni.NULL)
            elif (lex.sadržaj in naredbe): yield lex.token(Tokeni(lex.sadržaj))
            elif (lex.sadržaj == 'break'): yield lex.token(Tokeni.BREAK)
            elif (lex.sadržaj == 'continue'): yield lex.token(Tokeni.CONTINUE)
            elif (lex.sadržaj == 'return'): yield lex.token(Tokeni.RETURN)
            elif (lex.sadržaj == 'int'): yield lex.token(Tokeni.INT)
            elif (lex.sadržaj == 'bool'): yield lex.token(Tokeni.BOOL)
            elif (lex.sadržaj == 'char'): yield lex.token(Tokeni.CHAR)
            elif (lex.sadržaj == 'string'): yield lex.token(Tokeni.STRING)
            elif (lex.sadržaj == 'void'): yield lex.token(Tokeni.VOID)
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
        # je li chrlit?
        elif znak == "'":
            idući = lex.čitaj()
            if (not isNChar(idući) and not idući in escapeZnakovi and not idući == '"' and not idući == '\0'):
                raise LeksičkaGreška("Neispravan chrlit")
            kraj = lex.čitaj()
            if (kraj == "'"):
                yield lex.token(Tokeni.CHRLIT)
            else:
                raise LeksičkaGreška("Neispravan chrlit")           
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

                lex.zvijezda(lambda znak: znak != '\n')
                lex.pročitaj('\n')
                lex.token(Tokeni.COMMENT)
            elif sljedeći == '*': #komentari tipa /* */
                lex.pročitaj('*')
                while not (lex.čitaj() == '*' and lex.pogledaj() == '/'): pass
                lex.pročitaj('/')
                lex.token(Tokeni.COMMENT)
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
        #operatori <, <<, <<=, <=
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
            Tokeni.BOOLEAN, Tokeni.NULL}
class C0Parser(Parser):

    def prog(self):
        if self >> {Tokeni.INT, Tokeni.BOOL, Tokeni.STRING, Tokeni.CHAR, Tokeni.VOID}:
            tip = self.zadnji
            ime = self.pročitaj(Tokeni.IDENTIFIER)
            self.pročitaj(Tokeni.OOTV)

            varijable = []
            while not self >> Tokeni.OZATV:
                if (not self >> {Tokeni.INT, Tokeni.BOOL, Tokeni.STRING, Tokeni.CHAR}):
                    raise SintaksnaGreška("pogrešna inicijalizacija")

                tipVar = self.zadnji
                imeVar = self.pročitaj(Tokeni.IDENTIFIER)
                if (not self.pogledaj() ** Tokeni.OZATV):
                    self.pročitaj(Tokeni.ZAREZ)
                
                varijable.append(Varijabla(tipVar, imeVar))

            if (self.pogledaj() ** Tokeni.SEP): #samo deklaracija funkcije
                self.pročitaj(Tokeni.SEP)
                return DeklaracijaFunkcije(tip, ime, varijable)


            self.pročitaj(Tokeni.VOTV)
            tijelo = []
            while not self >> Tokeni.VZATV: tijelo.append(self.stmt())
            return DefinicijaFunkcije(tip, ime, varijable, tijelo)

    def stmt(self):
        if self >> Tokeni.IF:
            self.pročitaj(Tokeni.OOTV)
            uvjet = self.expression()
            self.pročitaj(Tokeni.OZATV)
            tijeloIf = self.stmt()
            idući = self.pogledaj()
            if idući ** Tokeni.ELSE:
                self.pročitaj(Tokeni.ELSE)
                tijeloElse = self.stmt()
                return IfElse(uvjet, tijeloIf, tijeloElse)
            else:
                return If(uvjet, tijeloIf)
        if self >> Tokeni.WHILE:
            self.pročitaj(Tokeni.OOTV)
            uvjet = self.expression()
            self.pročitaj(Tokeni.OZATV)
            tijeloWhile = self.stmt()
            return While(uvjet, tijeloWhile)

        if self >> Tokeni.FOR:
            self.pročitaj(Tokeni.OOTV)
            deklaracija = ""
            if (not self.pogledaj() ** Tokeni.SEP):
                deklaracija = self.simple()
            self.pročitaj(Tokeni.SEP)
            uvjet = self.expression()
            self.pročitaj(Tokeni.SEP)
            
            inkrement = ""
            if (not self.pogledaj() ** Tokeni.OZATV):
                inkrement = self.simple()
 
            self.pročitaj(Tokeni.OZATV)
            tijeloFor = self.stmt()
            return For(deklaracija, uvjet, inkrement, tijeloFor)
        if self >> Tokeni.RETURN:
            povratnaVrijednost = ""
            if (not self.pogledaj() ** Tokeni.SEP):
                povratnaVrijednost = self.expression()
            self.pročitaj(Tokeni.SEP)
            return Return(povratnaVrijednost)
        if self >> Tokeni.BREAK:
            br = self.zadnji
            self.pročitaj(Tokeni.SEP)
            return br
        if self >> Tokeni.CONTINUE:
            con = self.zadnji
            self.pročitaj(Tokeni.SEP)
            return con
        if self >> Tokeni.ASSERT:
            self.pročitaj(Tokeni.OOTV)
            izraz = self.expression()
            self.pročitaj(Tokeni.OZATV)
            self.pročitaj(Tokeni.SEP)
            return Assert(izraz)

        if self >> Tokeni.ERROR:
            self.pročitaj(Tokeni.OOTV)
            izraz = self.expression()
            self.pročitaj(Tokeni.OZATV)
            self.pročitaj(Tokeni.SEP)
            return Error(izraz)

        if self >> Tokeni.VOTV:
            blok = []
            while not self >> Tokeni.VZATV: blok.append(self.stmt())
            return Blok(blok)
        else:
            simple = self.simple()
            self.pročitaj(Tokeni.SEP)
            return simple


    def simple(self):
        if self >> {Tokeni.INT, Tokeni.BOOL, Tokeni.STRING, Tokeni.CHAR}:
            tip = self.zadnji
            varijabla = self.pročitaj(Tokeni.IDENTIFIER)

            if self >> Tokeni.ASSIGN:
                var = Varijabla(tip, varijabla)
                desna = self.expression()
                return Deklaracija(var, desna)
            else:
                return Varijabla(tip, varijabla)
        else:
            return self.expression()

    def expression(self):
        trenutni = self.logički()

        while True:
            if self >> Tokeni.CONDQ:
                prviUvjet = self.expression()
                self.pročitaj(Tokeni.CONDDOT)
                drugiUvjet = self.expression()
                trenutni = TernarniOperator(trenutni, prviUvjet, drugiUvjet)
            else: return trenutni

        else:
            self.greška()

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
            else: break
        while True:
            if self >> Tokeni.INCR:
                trenutni = Inkrement(trenutni)
            elif self >> Tokeni.DECR:
                trenutni = Dekrement(trenutni)
            else: break
        return trenutni


    def unaries(self):
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
        if self >> Tokeni.OOTV:
            u_zagradi = self.expression()
            self.pročitaj(Tokeni.OZATV)
            return u_zagradi
        if self >> Tokeni.IDENTIFIER:
            #može biti identifier, može biti poziv funkcije ako slijedi otvorena zagrada iza
            ime = self.zadnji
            if (self.pogledaj() ** Tokeni.OOTV):
                self.pročitaj(Tokeni.OOTV)
                varijable = []
                while not self >> Tokeni.OZATV:
                    imeVar = self.expression()
                    if (not self.pogledaj() ** Tokeni.OZATV):
                        self.pročitaj(Tokeni.ZAREZ)
                
                    varijable.append(imeVar)
                return IzvrijedniFunkciju(ime, varijable)
            else:
                return ime
        if self >> Tokeni.PRINT:
            #print funkcija
            self.pročitaj(Tokeni.OOTV)
            varijable = []
            while not self >> Tokeni.OZATV:
                imeVar = self.expression()
                if (not self.pogledaj() ** Tokeni.OZATV):
                    self.pročitaj(Tokeni.ZAREZ)
                
                varijable.append(imeVar)
            return PrintFunkcija(varijable)
        if self >> osnovniIzrazi:
            trenutni = self.zadnji
        return trenutni


    def start(self):
        naredbe = [self.prog()]
        while not self >> E.KRAJ:
            naredbe.append(self.prog())
        return Program(naredbe)

class Program(AST('naredbe')):
    def izvrši(self):

        tipovi = ChainMap()
        vrijednosti = ChainMap()

        rezultati = []
        for naredba in self.naredbe: 
            rezultati.append(naredba.izvrši(tipovi, vrijednosti))

        for tip in tipovi:
            if(tip.sadržaj == 'main'  and tipovi[tip].tip.vrijednost(None, None) == int):
                tipovi[tip].izvrijedni(tipovi, vrijednosti, [])
                return

        raise GreškaIzvođenja("nema main funkcije")

class PrintFunkcija(AST('print')):
    def izvrši(izraz, imena, vrijednosti):
        for p in izraz.print:
            print (p, p.vrijednost(imena, vrijednosti))

class DeklaracijaFunkcije(AST('tip ime varijable')):
    def izvrši(izraz, imena, vrijednosti):

        #ako već postoji od prije, provjeri slažu li se argumenti
        if (izraz.ime in imena):
            izraz.provjeri(imena, vrijednosti)
        else:
            #registriraj sebe u function and variable namespace
            imena[izraz.ime] = izraz
            #funkcija = Funkcija(izraz.tip, izraz.ime, izraz.varijable, "")
            #funkcija.izvrši(imena, vrijednosti)

    def izvrijedni(izraz, imena, vrijednosti, argumenti):
        raise GreškaIzvođenja("ne može se izvrijedniti samo deklarirana funkcija")

    def provjeri(izraz, imena, vrijednosti):
        postojeća = imena[izraz.ime]
        if (izraz.tip != postojeća.tip):
            raise GreškaIzvođenja("nisu kompatibilni povratni tipovi iste funkcije")
        if (len(izraz.varijable) != len(postojeća.varijable)):
            raise GreškaIzvođenja("različiti broj argumenata za istu funkciju")
        for i in range (0, len(izraz.varijable)):
            if (izraz.varijable[i].tip != postojeća.varijable[i].tip):
                raise GreškaIzvođenja("nekompatibilni tipovi argumenata iste funkcije")
        
class DefinicijaFunkcije(AST('tip ime varijable tijelo')):
    def izvrši(izraz, imena, vrijednosti):
        if (izraz.ime in imena and isinstance(imena[izraz.ime], DefinicijaFunkcije)):
            raise GreškaIzvođenja("Ne smiju postojati dvije definicije iste funkcije!")
        else:
            #registriraj sebe u function and variable namespace
            imena[izraz.ime] = izraz

            izraz.funkcija = Funkcija(izraz.tip, izraz.ime, izraz.varijable, izraz.tijelo)
            izraz.funkcija.izvrši(imena, vrijednosti)
    def izvrijedni(izraz, imena, vrijednosti, argumenti):
        return izraz.funkcija.izvrijedni(imena, vrijednosti, argumenti)

class Funkcija(AST('tip ime varijable tijelo')):
    def izvrši(izraz, imena, vrijednosti):

        #svaka funkcija ima svoj scope
        varijableUFunkciji = ChainMap()
        vrijednostiUFunkciji = ChainMap()
        #dodaj sve već postojeće funkcije u scope
        for key in imena.keys():
            varijableUFunkciji[key] = imena[key]
        
        for varijabla in izraz.varijable:
            varijabla.izvrši(varijableUFunkciji, vrijednostiUFunkciji)
            

        izraz.varijableF = varijableUFunkciji
        izraz.vrijednostiF = vrijednostiUFunkciji

    def izvrijedni(izraz, imena, vrijednosti, argumenti):
        if (len(argumenti) != len(izraz.varijable)):
            raise SemantičkaGreška("neispravan broj argumenata kod poziva funkcije")
        for i in range(0, len(argumenti)):
            if (not isinstance(argumenti[i], izraz.varijable[i].tip.vrijednost(izraz.varijableF, izraz.vrijednostiF))):
                raise SemantičkaGreška("neispravan tip argumenta")
            izraz.vrijednostiF[izraz.varijable[i].ime] = argumenti[i]

        for naredba in izraz.tijelo:
            try:
                naredba.izvrši(izraz.varijableF, izraz.vrijednostiF)
            except ReturnException as ex:
                #provjera još jel ispravan povratni tip
                povratna = ex.message
                if (povratna is None):
                    if (not izraz.tip ** Tokeni.VOID):
                        raise SemantičkaGreška("povratna vrijednost funkcije mora biti void")
                else: #tip povratne vrijednosti se mora slagati s tipom povratne vrijednosti funkcije

                    if (not isinstance(povratna, izraz.tip.vrijednost(izraz.varijableF, izraz.vrijednostiF))):
                        raise SemantičkaGreška("nekompatibilni povratni tip s povratnim tipom funkcije")
                return povratna
            

class IzvrijedniFunkciju(AST('imeFunkcije argumenti')):
    def izvrši(izraz, imena, vrijednosti):
        #funkcija mora biti deklarirana prije poziva
        if (not izraz.imeFunkcije in imena):
            raise SemantičkaGreška("poziv nepostojeće funkcije!")
        evaluiraniArgumenti = []
        for argument in izraz.argumenti:
            evaluiraniArgumenti.append(argument.vrijednost(imena, vrijednosti)) #možda još ovo promijeniti

        return imena[izraz.imeFunkcije].izvrijedni(imena, vrijednosti, evaluiraniArgumenti) 

    def vrijednost(izraz, imena, vrijednosti):
        return izraz.izvrši(imena, vrijednosti)

class If(AST('uvjet naredba')):
    def izvrši(izraz, imena, vrijednosti):
        if (izraz.uvjet.vrijednost(imena, vrijednosti)): #ako je vrijednost ovog true, izvršava se tijelo if-a
            izraz.naredba.izvrši(imena, vrijednosti)

        if (isinstance(izraz.naredba, Deklaracija)): #pobriši ju iz namespace-a
            del vrijednosti[izraz.naredba.varijabla.ime]
            del imena[izraz.naredba.varijabla.ime]
        


class IfElse(AST('uvjet naredbaIf naredbaElse')):
    def izvrši(izraz, imena, vrijednosti):
        if (izraz.uvjet.vrijednost(imena, vrijednosti)): #ako je vrijednost ovog true, izvršava se tijelo if-a
            izraz.naredbaIf.izvrši(imena, vrijednosti)

            if (isinstance(izraz.naredbaIf, Deklaracija)): #pobriši ju iz namespace-a
                del vrijednosti[izraz.naredbaIf.varijabla.ime]
                del imena[izraz.naredbaIf.varijabla.ime]
        else:
            izraz.naredbaElse.izvrši(imena, vrijednosti)

            if (isinstance(izraz.naredbaElse, Deklaracija)): #pobriši ju iz namespace-a
                del vrijednosti[izraz.naredbaElse.varijabla.ime]
                del imena[izraz.naredbaElse.varijabla.ime]
        
class Assert(AST('uvjet')):
    def izvrši(izraz, imena, vrijednosti):
        value = izraz.uvjet.vrijednost(imena, vrijednosti)
        if (not isinstance(value, bool)):
            raise GreškaIzvođenja("u assert statement mora ići izraz koji ima bool vrijednost")
        if (not value):
            print("Provjera izraza nije prošla!", izraz)
            raise GreškaIzvođenja()

class Error(AST('poruka')):
    def izvrši(izraz, imena, vrijednosti):
        message = izraz.poruka.vrijednost(imena, vrijednosti)
        if (not isinstance(message, str)):
            raise GreškaIzvođenja("u error može ići samo string")
        print (message)
        raise GreškaIzvođenja()

class Blok(AST('blok')):
    def izvrši(izraz, imena, vrijednosti):
        #uđi jednu razinu niže sa scope-om
        novaImena = imena.new_child()

        #izvrši svaku od naredbi u bloku
        for naredba in izraz.blok:
            naredba.izvrši(novaImena, vrijednosti)

        #pobriši iz vrijednosti sve parove koji se ne pojavljuju u imenima
        for key in novaImena.keys():
            if (not key in imena):
                del vrijednosti[key]

class While(AST('uvjet tijeloWhile')):
    def izvrši(izraz, imena, vrijednosti):
        while (izraz.uvjet.vrijednost(imena, vrijednosti)):
            try:
                izraz.tijeloWhile.izvrši(imena, vrijednosti)
            except BreakException: break
            except ContinueException: continue

class For(AST('s1 e s2 s3')):
    def izvrši(izraz, imena, vrijednosti):

        if (not izraz.s1 == ""):
            if (isinstance(izraz.s1, Deklaracija)):
                ime = izraz.s1.varijabla.ime
            izraz.s1.izvrši(imena, vrijednosti)

        while (izraz.e.vrijednost(imena, vrijednosti)):
            try:
                izraz.s3.izvrši(imena, vrijednosti)
                if (not izraz.s2 == ""):
                    if (isinstance(izraz.s2, Deklaracija)):
                        raise SemantičkaGreška("nije dopušteno deklarirati varijablu")
                    izraz.s2.izvrši(imena, vrijednosti)
            except BreakException: break
            except ContinueException: 
                if (not izraz.s2 == ""):
                    if (isinstance(izraz.s2, Deklaracija)):
                        raise SemantičkaGreška("nije dopoušteno deklarirati varijablu")
                    izraz.s2.izvrši(imena, vrijednosti)
                continue
            except ReturnException as e:
                if (not izraz.s1 == "" and isinstance(izraz.s1, Deklaracija)):
                    del vrijednosti[ime]
                    del imena[ime]
                raise ReturnException(e.message)

        if (not izraz.s1 == "" and isinstance(izraz.s1, Deklaracija)):
            del vrijednosti[ime]
            del imena[ime]


            
class Return(AST('povratnaVrijednost')):
    def vrijednost(izraz, imena, vrijednosti):
        if (izraz.povratnaVrijednost == ""):
            return None
        else:
            try:
                return izraz.povratnaVrijednost.vrijednost(imena, vrijednosti)
            except SemantičkaGreška: raise GreškaIzvođenja("varijabla nije nigdje inicijalizirana", izraz.povratnaVrijednost)
    
    def izvrši(izraz, imena, vrijednosti):
        raise ReturnException(izraz.vrijednost(imena, vrijednosti))


class Varijabla(AST('tip ime')):
    def izvrši(izraz, imena, vrijednosti):

        #ako već postoji ova varijabla, digni grešku
        if (izraz.ime in imena):
            izraz.ime.redeklaracija()

        imena[izraz.ime] = izraz.tip
        #svakoj se varijabli daje defaultna vrijednost
        if izraz.tip ** Tokeni.INT:
            vrijednosti[izraz.ime] = 0
        elif izraz.tip ** Tokeni.CHAR:
            vrijednosti[izraz.ime] = '\0'
        elif izraz.tip ** Tokeni.STRING:
            vrijednosti[izraz.ime] = ""
        elif izraz.tip ** Tokeni.BOOL:
            vrijednosti[izraz.ime] = False

    def vrijednost(izraz, iena, vrijednosti): 
        return izraz


class Deklaracija(AST('varijabla vrijedn')):
    def izvrši(izraz, imena, vrijednosti):

        izraz.varijabla.izvrši(imena, vrijednosti)

        #vidi da li se evaluirati izraz na lijevoj strani
        izraz.varijabla.ime.vrijednost(imena, vrijednosti)

        value = izraz.vrijedn.vrijednost(imena, vrijednosti)

        if (not isinstance(value, izraz.varijabla.tip.vrijednost(imena, vrijednosti))):
                raise SemantičkaGreška("nekompatibilni tipovi")

        if izraz.varijabla.tip ** Tokeni.CHAR: #provjeri još duljinu
            if (len(value) != 1):
                raise SemantičkaGreška("Nekompatibilni tipovi")

        vrijednosti[izraz.varijabla.ime] = value    

class Assignment(AST('lijevaStrana desnaStrana operator')):
    """Pridruživanje van inicijalizacije varijabli. Podržava sve operatore pridruživanja"""
    def vrijednost(izraz, imena, vrijednosti):

        lijevi = izraz.lijevaStrana.vrijednost(imena, vrijednosti)
        desni = izraz.desnaStrana.vrijednost(imena, vrijednosti)

        if (isinstance(lijevi, int)):
            if (not isinstance(desni, int)):
                raise SemantičkaGreška("Nekompatibilni tipovi")
            else: 
                Assignment.pridruži(izraz.lijevaStrana, desni, izraz.operator, vrijednosti, True)
                return vrijednosti[izraz.lijevaStrana]

        elif (isinstance(lijevi, str) and len(lijevi) == 1):
            if (not (isinstance(lijevi, str) and len(lijevi) == 1)):
                raise SemantičkaGreška("Nekompatibilni tipovi")
            else:
                Assignment.pridruži(izraz.lijevaStrana, desni, izraz.operator, vrijednosti, False)
                return vrijednosti[izraz.lijevaStrana][1:-1]

        elif isinstance(lijevi, bool):
            if (not isinstance(desni, bool)):
                raise SemantičkaGreška("Nekompatibilni tipovi")
            else:
                Assignment.pridruži(izraz.lijevaStrana, desni, izraz.operator, vrijednosti, False)
                return bool(vrijednosti[izraz.lijevaStrana])

        elif isinstance(lijevi, str):
            if (not isinstance(desni, str)):
                raise SemantičkaGreška("Nekompatibilni tipovi")
            else:
                Assignment.pridruži(izraz.lijevaStrana, desni, izraz.operator, vrijednosti, False)
                return vrijednosti[izraz.lijevaStrana]
        else:
            raise SemantičkaGreška("Ne znam assignati operande ovog tipa!")

    def izvrši(izraz, imena, vrijednosti):
        izraz.vrijednost(imena, vrijednosti)

    def pridruži(lijevo, desno, operator, vrijednosti, je_int):
        lijevo_val = vrijednosti[lijevo]
        if operator ** Tokeni.ASSIGN:
            lijevo_val = desno
        elif je_int:
            if operator ** Tokeni.PLUSEQ:
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
        else: 
            raise SemantičkaGreška("Ovaj tip ne podržava operator " + operator.sadržaj + ".")

        vrijednosti[lijevo] = lijevo_val

class Comparison(AST('lijevaStrana desnaStrana operator')):
    def vrijednost(izraz, imena, vrijednosti):
        lijevi = izraz.lijevaStrana.vrijednost(imena, vrijednosti)
        desni = izraz.desnaStrana.vrijednost(imena, vrijednosti)

        #dozvoljeni su samo int i char
        if ((isinstance(lijevi, int) and isinstance(desni, int))
            or (isinstance(lijevi, str) and len(lijevi) == 1 and
             isinstance(desni, str) and len(desni) == 1)):
        
            if (type(lijevi) != type(desni)):
                raise SemantičkaGreška("neispravno uspoređivanje")

            if izraz.operator ** Tokeni.LESS: return lijevi < desni
            elif izraz.operator ** Tokeni.LESSEQ: return lijevi <= desni
            elif izraz.operator ** Tokeni.GRT: return lijevi > desni
            elif izraz.operator ** Tokeni.GRTEQ: return lijevi >= desni
            else: assert not 'slučaj'
        else:
            raise SemantičkaGreška("neispravna usporedba")
    def izvrši(izraz, imena, vrijednosti):
        izraz.vrijednost(imena, vrijednosti)
        

class Equality(AST('lijevaStrana desnaStrana operator')):
    def vrijednost(izraz, imena, vrijednosti):

        lijevi = izraz.lijevaStrana.vrijednost(imena, vrijednosti)
        desni = izraz.desnaStrana.vrijednost(imena, vrijednosti)
        
        if (type(lijevi) != type(desni)):
            raise SemantičkaGreška("neispravno uspoređivanje")

        if izraz.operator ** Tokeni.EQ: return lijevi == desni
        elif izraz.operator ** Tokeni.DISEQ: return lijevi != desni
        else: assert not 'slučaj'
    
    def izvrši(izraz, imena, vrijednosti):
        izraz.vrijednost(imena, vrijednosti)


class BinarnaOperacija(AST('lijevaStrana desnaStrana operacija')):
    def vrijednost(izraz, imena, vrijednosti):
        try:
            lijevi = izraz.lijevaStrana.vrijednost(imena, vrijednosti)
            desni = izraz.desnaStrana.vrijednost(imena, vrijednosti)

        except ValueError:
            raise SemantičkaGreška("neispravna binarna operacija")
        
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
    def izvrši(izraz, imena, vrijednosti):
        izraz.vrijednost(imena, vrijednosti)

class BitwiseOperacija(AST('lijevaStrana desnaStrana operacija')):
    def vrijednost(izraz, imena, vrijednosti):
        try:
            lijevi = izraz.lijevaStrana.vrijednost(imena, vrijednosti)
            desni = izraz.desnaStrana.vrijednost(imena, vrijednosti)
        except ValueError:
            raise SemantičkaGreška("neispravna bitwise operacija")
        
        if izraz.operacija ** Tokeni.BITAND:
            rezultat = lijevi & desni
        elif izraz.operacija ** Tokeni.BITOR:
            rezultat = lijevi | desni 
        elif izraz.operacija ** Tokeni.BITEXCLOR:
            rezultat = lijevi ^ desni

        return rezultat

    def izvrši(izraz, imena, vrijednosti):
        izraz.vrijednost(imena, vrijednosti)

class LogičkaOperacija(AST('lijevaStrana desnaStrana operacija')):
    def vrijednost(izraz, imena, vrijednosti):
        # prvo evaluiraj lijevu stranu, ovisno o njenoj vrijednosti evaluiraj desnu
        lijevi = izraz.lijevaStrana.vrijednost(imena, vrijednosti)
        if(not isinstance(lijevi, bool)):
            raise SemantičkaGreška("neispravna logička operacija")

        if izraz.operacija ** Tokeni.LAND:
            if (lijevi is False): return False

        elif izraz.operacija ** Tokeni.LOR:
            if (lijevi is True): return True
            
        desni = izraz.desnaStrana.vrijednost(imena, vrijednosti)
        if(not isinstance(desni, bool)):
            raise SemantičkaGreška("neispravna logička operacija")
        
        if izraz.operacija ** Tokeni.LAND:
            rezultat = bool(lijevi and desni)
        elif izraz.operacija ** Tokeni.LOR:
            rezultat = bool(lijevi or desni)             

        return rezultat  
    def izvrši(izraz, imena, vrijednosti):
        izraz.vrijednost(imena, vrijednosti)
    

class TernarniOperator(AST('lijevaStrana prviUvjet drugiUvjet')):
    def vrijednost(izraz, imena, vrijednosti):
        if (izraz.lijevaStrana.vrijednost(imena, vrijednosti)): 
            return izraz.prviUvjet.vrijednost(imena, vrijednosti)
        else:
            return izraz.drugiUvjet.vrijednost(imena, vrijednosti)
    def izvrši(izraz, imena, vrijednosti):
        izraz.vrijednost(imena, vrijednosti)

class Negacija(AST('iza')):
    """Negacija izraza."""
    def vrijednost(izraz, imena, vrijednosti):
        value = izraz.iza.vrijednost(imena, vrijednosti)
        if (not isinstance(value, bool)):
            raise SemantičkaGreška("unarna negacija se izvršava samo na boolu")
        return not value
    def izvrši(izraz, imena, vrijednosti):
        izraz.vrijednost(imena, vrijednosti)


class Tilda(AST('iza')):
    """Bitwise unary complement"""
    def vrijednost(izraz, imena, vrijednosti):
        value = izraz.iza.vrijednost(imena, vrijednosti)
        if (not isinstance(value, int)):
            raise SemantičkaGreška("bitwise unary complement se izvršava samo na intu")
        return ~value
    def izvrši(izraz, imena, vrijednosti):
        izraz.vrijednost(imena, vrijednosti)

class Minus(AST('iza')):
    def vrijednost(izraz, imena, vrijednosti):
        value = izraz.iza.vrijednost(imena, vrijednosti)
        if (not isinstance(value, int)):
            raise SemantičkaGreška("unarni minus se izvršava samo na intu")
        return -value
    def izvrši(izraz, imena, vrijednosti):
        izraz.vrijednost(imena, vrijednosti)

class Inkrement(AST('broj')):
    """Postfix inkrement, vraća inkrementirani broj"""
    def vrijednost(izraz, imena, vrijednosti):
        lijevi = izraz.broj.vrijednost(imena, vrijednosti)
        vrijednosti[izraz.broj] = lijevi + 1
        return lijevi + 1
    def izvrši(izraz, imena, vrijednosti):
        izraz.vrijednost(imena, vrijednosti)

class Dekrement(AST('broj')):
    """Postfix dekrement, vraća dekrementirani broj"""
    def vrijednost(izraz, imena, vrijednosti):
        lijevi = izraz.broj.vrijednost(imena, vrijednosti)
        vrijednosti[izraz.broj] = lijevi - 1
        return lijevi - 1
    def izvrši(izraz, imena, vrijednosti):
        izraz.vrijednost(imena, vrijednosti)

#Lista programa se leksira, parsira i interpretira
#svaki program mora imati main funkciju, svaka funkcija ima svoj doseg
#definirana je pomoćna print funkcija, može primiti više izraza (npr. print(a, b)),
#a za svaki izraz ispiše njega i njegovu vrijednost
#za provjeru vrijednosti se također može koristiti i assert
if __name__ == '__main__':
    programi = []
   
    program = r"""

    int piUsingIsPrime(int a); //Deklaracija funkcije

    bool isPrime(int n) {
    if (n < 2) return false;
    if (n == 2) return true;
    if (n % 2 == 0) return false;
    for (int factor = 3; factor <= n/factor; factor += 2) {
        if (n % factor == 0)
        return false;
    }
    return true;
    }
    /* Funkcija koja za broj n vraća broj prostih brojeva od 1 do n */
    int piUsingIsPrime(int n) {
    int primeCount = 0;
    for (int i = 2; i <= n; i++)
        if (isPrime(i) == true) //Poziv funkcije isPrime, deklarirane gore
        primeCount++;
    return primeCount;
    }
    //Funkcija vraća reverz broja
    int reverseInt(int n) {
        int reversedNumber = 0;
        int remainder;
        while(n != 0)
        {
            remainder = n%10;
            reversedNumber = reversedNumber*10 + remainder;
            n /= 10;
        }
        return reversedNumber;
    }

    int main() {
           int a;
           int b;
           int c;
           c += a += 8;

        assert(c == 8);
        assert(reverseInt(257) == 752);
        print(piUsingIsPrime(10));
       return 2;
    }
    """
    programi.append(program)

    program = r"""

    int x(bool a);

    int x(bool aaa); //dozvoljena redeklaracija, nije bitno što su različita imena argumenata

    int x(bool a) {}

    int x(bool a) {} //greška, nije dozvoljena redefinicija

    int main() {
        return 0;
    }
    """
    programi.append(program)

    program = r"""
    int main() {
        int a;
        {
            int a = 0; //greška, redeklaracija varijable
        }
        return 0;
    }
    """
    programi.append(program)

    program = r"""
    int main() {
        int a;
        {
            int c;
        }
        c = 3; //greška, izvan dosega
        return 0;
    }
    """
    programi.append(program)

    program = r"""
    int main() {
        int a;
        for ( ; a < 4; a++) {   //dozvoljeno je izostaviti i prvi i treći argument
            if (a == 3) break;
            for(int b = 0; b < 3; ) {
                if (b % 2 == 0) {
                    b += 1;
                }
                else {
                    print(a, b);
                    b += 1;
                }
            }
        }
        return 0;
    }
    """
    programi.append(program)

    program = r"""
    int main() {
        int a; //svakoj je varijabli automatski dodijeljena defaultna vrijednost
        int c;
        while (a < 5) {
            if (a % 2 == 0) {
                c = ~c;
            }
            else c = c << a;
            print(c);
            a++;
        }
        //return 'c'; //greška
    } //funkcija ne mora imati povratu vrijednost, bitno je da nije pogrešnog tipa
    """
    programi.append(program)

    program = r""" 
        int main() { //prioriteti operatora
            //bool b = "b";  greška
            bool a = true;
            int c = a ? 2 : -1;
            print(c);
            int d = c == 2 ? 2 + 6*3 : 8;
            print(d);

            if (c == 2 && d == 20)
                string f = "van dosega";

            //print(f); //greška
            string f;
            if (c == 2 && d == 20)
                print(f = "u dosegu");
        }
    """
    programi.append(program)

    for program in programi:
        try:
            print("IZVRŠAVANJE PROGRAMA")
            tokeni = list(Lekser(program))
            #print(*tokeni)
            program = C0Parser.parsiraj(tokeni)
            #print(program)
            program.izvrši()
            print("------------")
        except Greška as ex:
            print(ex)
            print("------------")

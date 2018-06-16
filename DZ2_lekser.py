
from pj import *
from collections import ChainMap
from DZ2idiot import *
from uuid import uuid1

separatoriZnakovi = '()[]{},;'
escapeZnakovi = ['\n', '\t', '\v', '\b', '\r', '\f', '\a', '\'', '\"', '\\']
escapeChars = ['n', 't', 'v', 'b', 'r', 'f', 'a', "'", '"', '\\']
naredbe = {'if', 'else', 'while', 'for', 'assert', 'error'}

assignOperators = {Tokeni.PLUSEQ, Tokeni.MINUSEQ, Tokeni.ZVJEQ, Tokeni.SLASHEQ, Tokeni.MODEQ, Tokeni.LSHIFTEQ, Tokeni.RSHIFTEQ, Tokeni.ASSIGN, Tokeni.ANDEQ, Tokeni.POTEQ, Tokeni.CRTAEQ}
primitivniTipovi = {Tokeni.INT, Tokeni.BOOL, Tokeni.STRING, Tokeni.CHAR, Tokeni.POINTER, Tokeni.ARRAY}
#ESCAPE ZNAKOVE VIDI TREBAS LI ZASEBNO

#rezervirane riječi
Struct = Token(Tokeni.IDENTIFIER, 'struct')
Typedef = Token(Tokeni.IDENTIFIER, 'typedef')
Return = Token(Tokeni.IDENTIFIER, 'return')
Assert = Token(Tokeni.IDENTIFIER, 'assert')
Alloc = Token(Tokeni.IDENTIFIER, 'alloc')
Alloc_array = Token(Tokeni.IDENTIFIER, 'alloc_array')
Main = Token(Tokeni.IDENTIFIER, 'main')

def isxdigit(znak):
    """Provjerava je li znak hex znamenka"""
    return znak != '' and (znak.isdigit() or znak in 'ABCDEFabcdef')

def isidentifier(znak):
    """Provjerava je li znak nešto što ide u identifier"""
    return znak.isalpha() or znak.isdigit() or znak == '_'

def isuzatv(znak):
    """Provjerava je li znak UZATV"""
    return znak ==']'

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

def isSpace(znak):
    """Provjerava je li znak ' ', '\\t' ili '\\n'"""
    return znak in {' ', '\t', '\n'}

def isZvijezda(znak):
    """Provjerava je li znak '*'"""
    return znak == '*'

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
            elif (lex.sadržaj == 'alloc'): yield lex.token(Tokeni.ALLOC)
            elif (lex.sadržaj == 'alloc_array'): yield lex.token(Tokeni.ALLOCA)
            elif (lex.sadržaj == 'int'): 
                sljedeći = lex.pogledaj()
                if sljedeći == '*':
                    lex.čitaj()
                    yield lex.token(Tokeni.POINTER)
                elif sljedeći == '[':
                    lex.čitaj()
                    lex.pročitaj(']')
                    yield lex.token(Tokeni.ARRAY)
                else: yield lex.token(Tokeni.INT)
            elif (lex.sadržaj == 'bool'): 
                sljedeći = lex.pogledaj()
                if sljedeći == '*':
                    lex.čitaj()
                    yield lex.token(Tokeni.POINTER)
                elif sljedeći == '[':
                    lex.čitaj()
                    lex.pročitaj(']')
                    yield lex.token(Tokeni.ARRAY)
                yield lex.token(Tokeni.BOOL)
            elif (lex.sadržaj == 'char'): 
                sljedeći = lex.pogledaj()
                if sljedeći == '*':
                    lex.čitaj()
                    yield lex.token(Tokeni.POINTER)
                elif sljedeći == '[':
                    lex.čitaj()
                    lex.pročitaj(']')
                    yield lex.token(Tokeni.ARRAY)
                yield lex.token(Tokeni.CHAR)
            elif (lex.sadržaj == 'string'): 
                sljedeći = lex.pogledaj()
                if sljedeći == '*':
                    lex.čitaj()
                    yield lex.token(Tokeni.POINTER)
                elif sljedeći == '[':
                    lex.čitaj()
                    lex.pročitaj(']')
                    yield lex.token(Tokeni.ARRAY)
                yield lex.token(Tokeni.STRING)
            elif (lex.sadržaj == 'void'): 
                sljedeći = lex.pogledaj()
                if sljedeći == '*':
                    lex.čitaj()
                    yield lex.token(Tokeni.POINTER)
                elif sljedeći == '[':
                    lex.čitaj()
                    lex.pročitaj(']')
                    yield lex.token(Tokeni.ARRAY)
                yield lex.token(Tokeni.VOID)
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
            Tokeni.BOOLEAN, Tokeni.NULL}
class C0Parser(Parser):

    def gdefn(self):
        print("gdefn")
        if self >> {Tokeni.INT, Tokeni.BOOL, Tokeni.STRING, Tokeni.CHAR, Tokeni.VOID}:
            tip = self.zadnji
            ime = self.pročitaj(Tokeni.IDENTIFIER)
            self.pročitaj(Tokeni.OOTV)
            varijable = []
            while not self >> Tokeni.OZATV:
                if (not self >> {Tokeni.INT, Tokeni.BOOL, Tokeni.STRING, Tokeni.CHAR}):
                    raise ValueError("pogrešna inicijalizacija")

                tipVar = self.zadnji
                imeVar = self.pročitaj(Tokeni.IDENTIFIER)
                if (not self.pogledaj() ** Tokeni.OZATV):
                    self.pročitaj(Tokeni.ZAREZ)
                
                varijable.append(Varijabla(tipVar, imeVar))

            self.pročitaj(Tokeni.VOTV)
            tijelo = []
            while not self >> Tokeni.VZATV: tijelo.append(self.stmt())
            return Funkcija(tip, ime, varijable, tijelo)
        

    def stmt(self):
        #ovdje jošassert, error
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
        if self >> Tokeni.VOTV:
            blok = []
            while not self >> Tokeni.VZATV: blok.append(self.stmt())
            return Blok(blok)
        else:
            simple = self.simple()
            self.pročitaj(Tokeni.SEP)
            return simple


    def simple(self):
        #ostali.....
 
        if self >> primitivniTipovi:
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
                trenutni = BinarnaOperacija(trenutni, self.assign(), operacija)
                
            else: return trenutni
    def assign(self):
        trenutni = self.allocate()

        while True:
            if self >> assignOperators:
                operacija = self.zadnji
                trenutni = Assignment(trenutni, self.expression(), operacija)
            else: break
        
        return trenutni
    
    def allocate(self):
        trenutni = self.allocarray()
        if self >> Tokeni.ALLOC:
            self.pročitaj(Tokeni.OOTV)
            if self >> primitivniTipovi:
                tip = self.zadnji
                self.pročitaj(Tokeni.OZATV)
                trenutni = Alociraj(tip) 
            else:
               self.zadnji.neočekivan()
              
        return trenutni         

    def allocarray(self):
        trenutni = self.unaries()
        if self >> Tokeni.ALLOCA:
            self.pročitaj(Tokeni.OOTV)
            if self >> primitivniTipovi:
                tip = self.zadnji
                self.pročitaj(Tokeni.ZAREZ)
                koliko = self.expression()
                self.pročitaj(Tokeni.OZATV)
                trenutni = AlocirajArray(tip, koliko)
            else:
                self.zadnji.neočekivan()
        return trenutni

    def unaries(self):
        #više ne fali zvjezdica
        if self >> Tokeni.USKL:
            iza = self.expression()
            return Negacija(iza)
        if self >> Tokeni.TILDA:
            iza = self.expression()
            return Tilda(iza)
        if self >> Tokeni.MINUS:
            iza = self.expression()
            return Minus(iza)
        if self >> Tokeni.ZVJ:
            iza = self.base()
            trenutni = Dereferenciraj(iza)
            return trenutni
       
 #       if self >> Tokeni.ZVJ:
  #          iza = self.expression()
   #         trenutni = Dereferenciraj(iza)
  #          print("LAKSHGLAKSHGALS", trenutni)
#return trenutni            
        
        baza = self.base()
        return baza

    def base(self):
        #odradit operatore, pozvat expression
        print("base", self.zadnji)
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
            
            if (self.pogledaj() ** Tokeni.INCR or self.pogledaj() ** Tokeni.DECR):
                trenutni = self.zadnji
                while True:
                    if self >> Tokeni.INCR:
                        trenutni = Inkrement(trenutni)
                    elif self >> Tokeni.DECR:
                        trenutni = Dekrement(trenutni)
                    else: 
                        break
                return trenutni

            if self >> Tokeni.UOTV:
                trenutni = self.expression()
                self.pročitaj(Tokeni.UZATV)
                trenutni = Dohvati(ime, trenutni)
                return trenutni

            else:
                return ime
        if self >> osnovniIzrazi:
            trenutni = self.zadnji
            return trenutni



    def start(self):
        naredbe = [self.gdefn()]
        while not self >> E.KRAJ:
            naredbe.append(self.gdefn())
        return Program(naredbe)

class Program(AST('naredbe')):
    def izvrši(self):

        tipovi = ChainMap()
        vrijednosti = ChainMap()
        rezultati = []
        for naredba in self.naredbe: 
            rezultati.append(naredba.izvrši(tipovi, vrijednosti))


        for tip in tipovi:
            if(tip.sadržaj == 'main'):
                povrat = tipovi[tip].izvrijedni(tipovi, vrijednosti, [])

        print(tipovi, vrijednosti)
        print ("ovdje" ,povrat)



class Funkcija(AST('tip ime varijable tijelo')):
    def izvrši(izraz, imena, vrijednosti):
        #registriraj sebe u function and variable namespace
        imena[izraz.ime] = izraz

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
            raise ValueError("neispravan broj argumenata kod poziva funkcije")
        for i in range(0, len(argumenti)):
            if (not isinstance(argumenti[i], izraz.varijable[i].tip.vrijednost(izraz.varijableF, izraz.vrijednostiF))):
                raise ValueError("neispravan tip argumenta")
            izraz.vrijednostiF[izraz.varijable[i].ime] = argumenti[i]

        for naredba in izraz.tijelo:
            try:
                naredba.izvrši(izraz.varijableF, izraz.vrijednostiF)
            except ReturnException as ex:
                #provjera još jel ispravan povratni tip
                povratna = ex.message
                temp = povratna
                if (povratna is None):
                    if (not izraz.tip ** Tokeni.VOID):
                        raise ValueError("povratna vrijednost funkcije mora biti void")
                else: #tip povratne vrijednosti se mora slagati s tipom povratne vrijednosti funkcije
                    if(isinstance (povratna, list)):
                        temp = povratna[0]
                    if (not isinstance( temp, izraz.tip.vrijednost(izraz.varijableF, izraz.vrijednostiF))):
                            raise ValueError("nekompatibilni povratni tip s povratnim tipom funkcije")
                return povratna
            

class IzvrijedniFunkciju(AST('imeFunkcije argumenti')):
    def izvrši(izraz, imena, vrijednosti):

        #funkcija mora biti deklarirana prije poziva
        if (not izraz.imeFunkcije in imena):
            raise ValueError("poziv nepostojeće funkcije!")
        evaluiraniArgumenti = []
        for argument in izraz.argumenti:
            if (isinstance(argument.vrijednost(imena, vrijednosti), list)): 
                evaluiraniArgumenti.append(argument.vrijednost(imena, vrijednosti)[0]) #možda još ovo promijeniti
            else: 
                evaluiraniArgumenti.append(argument.vrijednost(imena, vrijednosti))
        return imena[izraz.imeFunkcije].izvrijedni(imena, vrijednosti, evaluiraniArgumenti) 
    def vrijednost(izraz, imena, vrijednosti):
        
        return izraz.izvrši(imena, vrijednosti)

class If(AST('uvjet naredba')):
    def izvrši(izraz, imena, vrijednosti):
        if (izraz.uvjet.istina(imena, vrijednosti)): #ako je vrijednost ovog true, izvršava se tijelo if-a
            izraz.naredba.izvrši(imena, vrijednosti)


class IfElse(AST('uvjet naredbaIf naredbaElse')):
    def izvrši(izraz, imena, vrijednosti):
        if (izraz.uvjet.istina(imena, vrijednosti)): #ako je vrijednost ovog true, izvršava se tijelo if-a
            izraz.naredbaIf.izvrši(imena, vrijednosti)
        else:
            izraz.naredbaElse.izvrši(imena, vrijednosti)

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


#TODO: vidjeti isto za return ovdje u while kao i u foru
#TODO: također u if, else, while, for kad nema bloka, onelinere se pobrinut da se ta varijabla pobriše
class While(AST('uvjet tijeloWhile')):
    def izvrši(izraz, imena, vrijednosti):
        while (izraz.uvjet.istina(imena, vrijednosti)):
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

        while (izraz.e.istina(imena, vrijednosti)):
            try:
                izraz.s3.izvrši(imena, vrijednosti)
                if (not izraz.s2 == ""):
                    if (isinstance(izraz.s2, Deklaracija)):
                        raise ValueError("nije dopoušteno deklarirati varijablu")
                    izraz.s2.izvrši(imena, vrijednosti)
            except BreakException: break
            except ContinueException: 
                if (not izraz.s2 == ""):
                    if (isinstance(izraz.s2, Deklaracija)):
                        raise ValueError("nije dopoušteno deklarirati varijablu")
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
            except SemantičkaGreška: raise ValueError("varijabla nije nigdje inicijalizirana", izraz.povratnaVrijednost)
    
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
            vrijednosti[izraz.ime] = [0]
        elif izraz.tip ** Tokeni.CHAR:
            vrijednosti[izraz.ime] = ['\0']
        elif izraz.tip ** Tokeni.STRING:
            vrijednosti[izraz.ime] = [""]
        elif izraz.tip ** Tokeni.BOOL:
            vrijednosti[izraz.ime] = [False]
        elif izraz.tip ** Tokeni.POINTER:
            # N kao NULL
            vrijednosti[izraz.ime] = [['N' + izraz.tip.sadržaj]]
        elif izraz.tip ** Tokeni.ARRAY:
            # NP kao NULL polje
            vrijednosti[izraz.ime] = [0, [izraz.tip.sadržaj]]

class Deklaracija(AST('varijabla vrijedn')):
    def izvrši(izraz, imena, vrijednosti):

        izraz.varijabla.izvrši(imena, vrijednosti)

        #vidi da li se evaluirati izraz na lijevoj strani
        izraz.varijabla.ime.vrijednost(imena, vrijednosti)

        value = izraz.vrijedn.vrijednost(imena, vrijednosti)
        print("VALUE")
        print(value)
        print(izraz.varijabla.ime.vrijednost)
        
        print("pointer")
        if (isinstance(value, list)):
            value = value[0]

        if izraz.varijabla.tip ** Tokeni.INT:
            if (type(value) is not int):
                raise ValueError("Nekompatibilni tipovi")

        elif izraz.varijabla.tip ** Tokeni.CHAR:
            if (not isinstance(value, str) or len(value) != 1):
                raise ValueError("Nekompatibilni tipovi")

        elif izraz.varijabla.tip ** Tokeni.BOOL:
            if (not isinstance(value, bool)):
                raise ValueError("Nekompatibilni tipovi")

        elif izraz.varijabla.tip ** Tokeni.STRING:
            if (not isinstance(value, str)):
                raise ValueError("Nekompatibilni tipovi")    

        elif izraz.varijabla.tip ** Tokeni.POINTER:
            try:
                value = value[0]
            except: raise ValueError("Neispravna adresa")
            # provjeri tip pointera
            tip = izraz.varijabla.tip.sadržaj
            if(tip == 'int*'):
                if(not isinstance(value, int)):
                    raise ValueError("Nekompatibilan tip pointera, očekujem " + tip)
            elif(tip == 'char*'):
                if(not isinstance(value, str) or len(value)!=1):
                    raise ValueError("Nekompatibilan tip pointera, očekujem " + tip)
            elif(tip == 'bool*'):
                if(not isinstance(value, bool)):
                    raise ValueError("Nekompatibilan tip pointera, očekujem " + tip)
            elif(tip == 'string*'):
                if(not isinstance(value, str)):
                    raise ValueError("Nekompatibilan tip pointera, očekujem " + tip)
            else: raise ValueError("Nepoznat tip pointera")
            value = [value]

        elif izraz.varijabla.tip ** Tokeni.ARRAY:
            print("ovo!!!!")
            print (izraz.varijabla.tip)

            
        vrijednosti[izraz.varijabla.ime][0] = value



class Assignment(AST('lijevaStrana desnaStrana operator')):
    """Pridruživanje van inicijalizacije varijabli. Podržava sve operatore pridruživanja"""
    def vrijednost(izraz, imena, vrijednosti):

        lijevi = izraz.lijevaStrana.vrijednost(imena, vrijednosti)
        if isinstance(lijevi, list) and len(lijevi) < 2:
            lijevi = lijevi[0]
        
        desni = izraz.desnaStrana.vrijednost(imena, vrijednosti)
        if isinstance(desni, list) and len(desni) < 2:
            desni = desni[0]
        
        print("assign: ", lijevi, desni)
        if(isinstance(izraz.lijevaStrana, Dohvati)):
            nešto = izraz.lijevaStrana.odakle.vrijednost(imena, vrijednosti)
            print(nešto)

        if (isinstance(lijevi, int)):
            if (not isinstance(desni, int)):
                raise ValueError("Nekompatibilni tipovi")
            else: 
                print("int sam i ušao sam u else")
                left = izraz.lijevaStrana.vrijednost(imena, vrijednosti)
                print("novi lijevi", left)
                print(izraz.lijevaStrana.vrijednost(imena, vrijednosti))
                print(izraz.lijevaStrana, desni, izraz.operator,imena, vrijednosti)
                Assignment.pridruži(izraz.lijevaStrana, desni, izraz.operator,imena, vrijednosti, True)
                return izraz.lijevaStrana.vrijednost(imena, vrijednosti)

        elif (isinstance(lijevi, str) and len(lijevi) == 1):
            if (not (isinstance(lijevi, str) and len(lijevi) == 1)):
                raise ValueError("Nekompatibilni tipovi")
            else:
                Assignment.pridruži(izraz.lijevaStrana, desni, izraz.operator,imena,  vrijednosti, False)
                return [izraz.lijevaStrana.vrijednost(imena, vrijednosti)[1:-1]]

        elif isinstance(lijevi, bool):
            if (not isinstance(desni, bool)):
                raise ValueError("Nekompatibilni tipovi")
            else:
                Assignment.pridruži(izraz.lijevaStrana, desni, izraz.operator,imena,  vrijednosti, False)
                return bool(izraz.lijevaStrana.vrijednost(imena, vrijednosti)[0])

        elif isinstance(lijevi, str):
            if (not isinstance(desni, str)):
                raise ValueError("Nekompatibilni tipovi")
            else:
                Assignment.pridruži(izraz.lijevaStrana, desni, izraz.operator,imena,  vrijednosti, False)
                return izraz.lijevaStrana.vrijednost(imena, vrijednosti)
        elif isinstance(lijevi, list) and len(lijevi) >= 2:
            # onda je array
            print("ušao sam u polje", lijevi)
            if(not isinstance(desni, list) or len(desni) < 2):
                raise ValueError("Nekompatibilni tipovi")
            else:
                # dohvati tip polja
                try:
                    tipl = izraz.lijevaStrana.vrijednost(imena, vrijednosti)[1][0][:-2]
                    print (izraz.lijevaStrana.vrijednost(imena, vrijednosti))
                except: tipl = type(izraz.lijevaStrana.vrijednost(imena, vrijednosti)[1][0]).__name__

                try:
                    tipr = izraz.desnaStrana.vrijednost(imena, vrijednosti)[1][0][:-2]
                except: tipr= type(izraz.desnaStrana.vrijednost(imena, vrijednosti)[1][0]).__name__
                
                # provjeri da su isti s lijeve i desne strane
                if(tipl != tipr):
                    raise ValueError("Nekompatibilan tip polja, očekujem " + tipl + "[], dobio " + tipr + "[].")
                Assignment.pridruži(izraz.lijevaStrana, desni, izraz.operator, imena, vrijednosti, False)
                return izraz.lijevaStrana.vrijednost(imena, vrijednosti)     


        elif isinstance(lijevi, list):
            if (not isinstance(desni, list)):
                raise ValueError("Nekompatibilni tipovi")
            else:
                # provjeri tip pointera
                try:
                    tipl = izraz.lijevaStrana.vrijednost(imena, vrijednosti)[0][0][1:-1]
                except: tipl = izraz.lijevaStrana.tip.sadržaj

                try:
                    tipr = izraz.desnaStrana.vrijednost(imena, vrijednosti)[0][0][1:-1]
                except: tipr = izraz.desnaStrana.tip.sadržaj

                if(tipl != tipr):
                    raise ValueError("Nekompatibilan tip pointera, očekujem " + tipl + "*, dobio " + tipr + "*.")
                Assignment.pridruži(izraz.lijevaStrana, desni, izraz.operator,imena,  vrijednosti, False)
                return izraz.lijevaStrana.vrijednost(imena, vrijednosti)
        else:
            raise ValueError("Ne znam assignati operande ovog tipa!")

    def izvrši(izraz, imena, vrijednosti):
        izraz.vrijednost(imena, vrijednosti)

    def pridruži(lijevo, desno, operator,imena,  vrijednosti, je_int):
        lijevo_val = lijevo.vrijednost(imena, vrijednosti)
        print("ajshgkjasgh",lijevo_val)
        if(len(lijevo_val) < 2):
            lijevo_val = lijevo_val[0]
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
            raise ValueError("Ovaj tip ne podržava operator " + operator.sadržaj + ".")
        if(len(lijevo.vrijednost(imena, vrijednosti)) < 2):
            print("blabla",lijevo_val)
            lijevo.vrijednost(imena, vrijednosti)[0] = lijevo_val
            print("blabla2",lijevo.vrijednost(imena, vrijednosti))
        else: 
            print("ulazim u pogrešni else")
            lijevo.vrijednost(imena, vrijednosti)[:] = lijevo_val[:]

class Comparison(AST('lijevaStrana desnaStrana operator')):
    def istina(izraz, imena, vrijednosti):
        lijevi = izraz.lijevaStrana.vrijednost(imena, vrijednosti)
        if (isinstance(lijevi, list)):
            lijevi = lijevi[0]
        desni = izraz.desnaStrana.vrijednost(imena, vrijednosti)
        if (isinstance(desni, list)):
            desni = desni[0]

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
    def istina(izraz, imena, vrijednosti):

        lijevi = izraz.lijevaStrana.vrijednost(imena, vrijednosti)
        if (isinstance(lijevi, list)):
            lijevi = lijevi[0]
        desni = izraz.desnaStrana.vrijednost(imena, vrijednosti)
        if (isinstance(desni, list)):
            desni = desni[0]
        
        if (type(lijevi) != type(desni)):
            raise ValueError("neispravno uspoređivanje")

        if izraz.operator ** Tokeni.EQ: return lijevi == desni
        elif izraz.operator ** Tokeni.DISEQ: return lijevi != desni
        else: assert not 'slučaj'

    def vrijednost(izraz, imena, vrijednosti):
        return izraz.istina(imena, vrijednosti)
    
    def izvrši(izraz, imena, vrijednosti):
        izraz.vrijednost(imena, vrijednosti)


class BinarnaOperacija(AST('lijevaStrana desnaStrana operacija')):
    def vrijednost(izraz, imena, vrijednosti):
        try:
            lijevi = izraz.lijevaStrana.vrijednost(imena, vrijednosti)
            if(isinstance(lijevi, list)):
                lijevi = lijevi[0]
            desni = izraz.desnaStrana.vrijednost(imena, vrijednosti)
            if(isinstance(desni, list)):
                desni = desni[0]

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
            lijevi = izraz.lijevaStrana.vrijednost(imena, vrijednosti)
            lijevi = lijevi[0]
            desni = izraz.desnaStrana.vrijednost(imena, vrijednosti)
            desni = desni[0]
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
            lijevi = izraz.lijevaStrana.vrijednost(imena, vrijednosti)
            lijevi = lijevi[0]
            desni = izraz.desnaStrana.vrijednost(imena, vrijednosti)
            desni = desni[0]
        except ValueError:
            raise ValueError("neispravna logička operacija")
        
        if izraz.operacija ** Tokeni.LAND:
            rezultat = bool(lijevi and desni)
        elif izraz.operacija ** Tokeni.LOR:
            rezultat = bool(lijevi or desni)             

        return rezultat  

class TernarniOperator(AST('lijevaStrana prviUvjet drugiUvjet')):
    def istina(izraz, imena, vrijednosti):
        
        if ((izraz.lijevaStrana.vrijednost(imena, vrijednosti))[0]): # ili izvrši?
            return (izraz.prviUvjet.vrijednost(imena, vrijednosti))[0]
        else:
            return (izraz.drugiUvjet.vrijednost(imena, vrijednosti))[0]

    def vrijednost(izraz, imena, vrijednosti):
        return [izraz.istina(imena, vrijednosti)]

class Negacija(AST('iza')):
    """Negacija izraza."""
    def vrijednost(izraz, imena, vrijednosti):
        return [not (izraz.iza.vrijednost(imena, vrijednosti))[0]]


class Tilda(AST('iza')):
    """Bitwise unary complement"""
    def vrijednost(izraz, imena, vrijednosti):
        return [~((izraz.iza.vrijednost(imena, vrijednosti))[0])]

class Minus(AST('iza')):
    def vrijednost(izraz, imena, vrijednosti):
        if(isinstance(izraz.iza.vrijednost(imena, vrijednosti), list)):
            return [- ((izraz.iza.vrijednost(imena, vrijednosti))[0])]
        else:
            return [-izraz.iza.vrijednost(imena, vrijednosti)]
    def izvrši(izraz, imena, vrijednosti):
        izraz.vrijednost(imena, vrijednosti)

class Dereferenciraj(AST('iza')):
    def vrijednost(izraz, imena, vrijednosti):
        argument = izraz.iza.vrijednost(imena, vrijednosti)
        if(isinstance(argument, list)):
            argument = argument[0]
        else: raise ValueError("Ne znam dereferencirati nešto što nije pointer!")

        if(isinstance(argument, list)):
            if len(argument) == 0:
                raise ValueError("Ne znam dereferencirati NULL!")
            return (izraz.iza.vrijednost(imena, vrijednosti))[0]
        else: raise ValueError("Ne znam dereferencirati nešto što nije pointer!")
    
    def izvrši(izraz, imena, vrijednosti):
        izraz.vrijednost(imena, vrijednosti)

class Dohvati(AST('odakle koga')):
    def vrijednost(izraz, imena, vrijednosti):
        if(int(izraz.koga.sadržaj) >= izraz.odakle.vrijednost(imena, vrijednosti)[0]):
            raise RuntimeError("Indeks izvan granica array-a")
        print("hrr", int(izraz.koga.sadržaj)+1, (izraz.odakle.vrijednost(imena, vrijednosti))[int(izraz.koga.sadržaj)+1])
        return (izraz.odakle.vrijednost(imena, vrijednosti))[int(izraz.koga.sadržaj)+1]
    
    def izvrši(izraz, imena, vrijednosti):
        izraz.vrijednost(imena, vrijednosti)

class Inkrement(AST('broj')):
    """Postfix inkrement, vraća inkrementirani broj"""
    def izvrši(izraz, imena, vrijednosti):
        lijevi = izraz.broj.vrijednost(imena, vrijednosti)
        vrijednosti[izraz.broj][0] = lijevi[0] + 1
        return lijevi[0] + 1

class Dekrement(AST('broj')):
    """Postfix dekrement, vraća dekrementirani broj"""
    def izvrši(izraz, imena, vrijednosti):
        lijevi = izraz.broj.vrijednost(imena, vrijednosti)
        vrijednosti[izraz.broj][0] = lijevi[0] - 1
        return lijevi[0] - 1
        
class Alociraj(AST('tip')):
    def vrijednost(izraz, imena, vrijednosti):
        if izraz.tip ** Tokeni.INT:
            return [[0]]
        elif izraz.tip ** Tokeni.CHAR:
            return [['\0']]
        elif izraz.tip ** Tokeni.STRING:
            return [[""]]
        elif izraz.tip ** Tokeni.BOOL:
            return [[False]]
        elif izraz.tip ** Tokeni.POINTER:
            return [[0]]
        else: raise TypeError("Nepoznat tip!")

class AlocirajArray(AST('tip koliko')):
    # nema polja pointera
    def vrijednost(izraz, imena, vrijednosti):
        temp_list =[int(izraz.koliko.sadržaj)]

        if izraz.tip ** Tokeni.INT:
            print( izraz.koliko.sadržaj)
            for i in range(int(izraz.koliko.sadržaj)): temp_list.append([0])
            #return [int(izraz.koliko.sadržaj)] + [[0]]*int(izraz.koliko.sadržaj)
            return temp_list
        elif izraz.tip ** Tokeni.CHAR:
            for i in range(int(izraz.koliko.sadržaj)): temp_list.append(['\0'])
        elif izraz.tip ** Tokeni.STRING:
            for i in range(int(izraz.koliko.sadržaj)): temp_list.append([""])
        elif izraz.tip ** Tokeni.BOOL:
            for i in range(int(izraz.koliko.sadržaj)): temp_list.append([False])
        #elif izraz.tip ** Tokeni.POINTER:
        #    return [[[0]]*izraz.koliko]
        else: raise TypeError("Nepoznat tip!")

        return temp_list

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
    #
    #
    #     for( ; c < 5; ){
    #     c = c + 1;
    #     if (c == 6)
    #         break;
    # }
    #
    #    
    #
    #int main() {
    #    
    #    int* a;
    #    int b = 6;
    #    int c = 3;
    #    a = alloc(int);
    #    *a = b;
    #    return *a;
    #}




   
    ulaz = r"""
        int main() {
            int[] a ;
            int b =6;
            a = alloc_array(int, 7);
            a[0] = 6;
            a[5] += 3;
            return b;
        }
    """
  
    tokeni = list(Lekser(ulaz))
    print(*tokeni)
    program = C0Parser.parsiraj(tokeni)
    print(program)

    program.izvrši()


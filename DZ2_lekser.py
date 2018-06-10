
from string import hexdigits
from pj import *
from collections import ChainMap
from DZ2idiot import *

separatori = [Tokeni.OOTV, Tokeni.OZATV, Tokeni.UOTV, Tokeni.UZATV, Tokeni.VOTV, Tokeni.VZATV,
     Tokeni.ZAREZ, Tokeni.SEP]
escapeovi = [Tokeni.NRED, Tokeni.NTAB, Tokeni.NVERTTAB, Tokeni.BACKSP, Tokeni.RET, Tokeni.FFEED,
     Tokeni.ALERT,  Tokeni.QUOTE, Tokeni.DBLQUOTE, Tokeni.ESCSLASH]
separatoriZnakovi = '()[]{},;'
escapeZnakovi = ['\n', '\t', '\v', '\b', '\r', '\f', '\a', '\'', '\"', '\\']
escapeChars = ['n', 't', 'v', 'b', 'r', 'f', 'a', "'", '"', '\\']
tipoviPodataka = {'int', 'bool', 'char', 'string'}
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
        print("znak")
        print(znak)
        print(citamString)
        if (citamString):
            if znak == '\\':
                idući = lex.čitaj()
                if (idući not in escapeChars):
                    lex.greška("Neispravan string")
            elif isNChar(znak):
                continue
            elif znak == '"':
                citamString = False
                print (lex.sadržaj)
                print (lex.sadržaj[1 : len(lex.sadržaj) - 1])
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
            print("identifikator....")
            print(lex.sadržaj)
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
                else:
                    if(sljedeći.isspace()):
                        yield lex.token(Tokeni.DECIMALNI)
                    else:
                        lex.greška('očekujem x ili X')
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
        elif znak in escapeZnakovi or znak in separatoriZnakovi:
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

        
#globalni spremnik korištenih varijabli u programu
globalneVarijable = ChainMap()
globalneVarijableTipovi = ChainMap()

osnovniIzrazi = { Tokeni.STRLIT, Tokeni.NULL}
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
                desna = self.expression()
                return Pridruživanje(tip, varijabla, desna)
            else:
                return Varijabla(tip, varijabla)
        else:
            return self.expression()

    def expression(self):
        print ("u izrazu")
        print (self.pogledaj())

        if self >> Tokeni.OOTV:
            u_zagradi = self.expression()
            self.pročitaj(Tokeni.OZATV)
            return u_zagradi
        if self >> osnovniIzrazi:
            return self.zadnji
        if self >> Tokeni.BOOLEAN:
            lijevaStrana = self.zadnji
            if self >> {Tokeni.EQ, Tokeni.DISEQ}:
                isJednako = True if self.zadnji ** Tokeni.EQ else False
                desnaStrana = self.expression()
                return JednakoRazlicito(lijevaStrana, desnaStrana, isJednako)
            else:
                return lijevaStrana

        if self >> Tokeni.IDENTIFIER:
            #ako nakon njega slijedi pridruživanje, vratit varijablu
            var = self.zadnji
            idući = self.pogledaj()
            print(idući)
            if idući ** Tokeni.ASSIGN:
                self.pročitaj(Tokeni.ASSIGN)
                vrijednost = self.expression()
                return self.odrediVarijablu(var, vrijednost)
            elif idući ** Tokeni.OOTV:
                self.pročitaj(Tokeni.OOTV)
                konstruktor_argumenti = []
                while True:
                    sljedeći = self.pogledaj()
                    print(sljedeći)
                    if sljedeći ** Tokeni.OZATV:
                        self.pročitaj(Tokeni.OZATV)
                        break
                    else:
                        ssljedeći = self.expression()
                        konstruktor_argumenti.append(ssljedeći)
                        zarez = self.pogledaj()
                        if zarez ** Tokeni.ZAREZ:
                            self.pročitaj(Tokeni.ZAREZ)
                        print("daddy attention" + str(zarez))
                return Konstrukcija(var, konstruktor_argumenti)
            #vidi jel operator uspoređivanja iza
            if self >> {Tokeni.LESS, Tokeni.LESSEQ}: 
                isManjeJednako = True if self.zadnji ** Tokeni.LESSEQ else False
                desnaStrana = self.expression()
                return ManjeJednako(var, desnaStrana, isManjeJednako)
            elif self >> {Tokeni.GRT, Tokeni.GRTEQ}:
                isVeceJednako = True if self.zadnji ** Tokeni.GRTEQ else False
                desnaStrana = self.expression()
                return VeceJednako(var, desnaStrana, isVeceJednako)
            elif self >> {Tokeni.EQ, Tokeni.DISEQ}:
                isJednako = True if self.zadnji ** Tokeni.EQ else False
                desnaStrana = self.expression()
                return JednakoRazlicito(var, desnaStrana, isJednako)
            else:
                return var
                        
        if self >> {Tokeni.DECIMALNI, Tokeni.HEKSADEKADSKI, Tokeni.CHRLIT}:
            lijevaStrana = self.zadnji
            #vidi jel operator uspoređivanja iza
            if self >> {Tokeni.LESS, Tokeni.LESSEQ}: 
                isManjeJednako = True if self.zadnji ** Tokeni.LESSEQ else False
                desnaStrana = self.expression()
                return ManjeJednako(lijevaStrana, desnaStrana, isManjeJednako)
            elif self >> {Tokeni.GRT, Tokeni.GRTEQ}:
                isVeceJednako = True if self.zadnji ** Tokeni.GRTEQ else False
                desnaStrana = self.expression()
                return VeceJednako(lijevaStrana, desnaStrana, isVeceJednako)
            elif self >> {Tokeni.EQ, Tokeni.DISEQ}:
                isJednako = True if self.zadnji ** Tokeni.EQ else False
                desnaStrana = self.expression()
                return JednakoRazlicito(lijevaStrana, desnaStrana, isJednako)
            else:
                return lijevaStrana
        #unarni operatori
        if self >> Tokeni.USKL:
            iza = self.expression()
            print (iza)
            return Negacija(iza)
        if self >> Tokeni.TILDA:
            iza = self.expression()
            return Tilda(iza)
        if self >> Tokeni.MINUS:
            iza = self.expression()
            return Minus(iza)
        #if self >> Tokeni.ZVJ:
        #    #TODO: neam pojma šta ovdje
        else:
            #do ovdje su odrađeni svi slučajevi gramatike gdje
            #prvi član pravila nije expression
            self.greška()
            #može se dogoditi i da stoji samo jedan izraz, mora se i to obraditi


    def start(self):
        naredbe = [self.stmt()]
        while not self >> E.KRAJ:
            print ("jel ovo zadnje")
            naredbe.append(self.stmt())
        return Program(naredbe)

class Program(AST('naredbe')):
    def vrijednost(self):
        imena = {}
        for naredba in self.naredbe: 
            print (naredba.vrijednost())
            naredba.vrijednost()
        return imena

class Varijabla(AST('tip ime')):
    def vrijednost(izraz):
        return

class Pridruživanje(AST('tip ime vrijedn')):
    def vrijednost(izraz):

        if izraz.tip == 'int':
            if (not isinstance(izraz.vrijedn.vrijednost(), int)):
                raise ValueError("Nekompatibilni tipovi")

        elif izraz.tip == 'char':
            if (not isinstance(izraz.vrijedn.vrijednost(), str) or len(izraz.vrijedn.vrijednost()) != 1):
                raise ValueError("Nekompatibilni tipovi")

        elif izraz.tip == 'bool':
            if (not isinstance(izraz.vrijedn.vrijednost(), bool)):
                raise ValueError("Nekompatibilni tipovi")

        elif izraz.tip == 'string':
            if (not isinstance(izraz.vrijedn.vrijednost(), str)):
                raise ValueError("Nekompatibilni tipovi")
        
        #mem[self.ime.sadržaj] = self.pridruženo.vrijednost(mem)

#ovdje svugdje provjera jesu jednake strane i provjera šta je desna strana
class ManjeJednako(AST('lijevaStrana desnaStrana isManjeJednako')):
    def vrijednost(izraz):
        return

class VeceJednako(AST('lijevaStrana desnaStrana isVeceJednako')):
    def vrijednost(izraz):
        return

class JednakoRazlicito(AST('lijevaStrana desnaStrana isJednako')):
    def vrijednost(izraz):
        return

class Negacija(AST('iza')):
    """Negacija izraza."""
    def vrijednost(izraz):
        return not izraz.iza.vrijednost()


class Tilda(AST('iza')):
    """Bitwise unary complement"""
    def vrijednost(izraz):
        return ~izraz.iza.vrijednost()

class Minus(AST('iza')):
    def vrijednost(izraz):
        return - izraz.iza.vrijednost()
class Konstrukcija(AST('objekt argumenti')):
    """Konstrukcija objekta s argumentima za konstruktor"""
    # zasad konstruktor podržava samo primitivne tipove
    def vrijednost(izraz):
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
    ulaz = r"NULL; !true; ~5;  -5; int a = 2;  char c = 'a'; 3 < 5; a >= 10; a == true; b != false;"
    #vrati ovo    
    #print (ulaz)
    #lista = list(Lekser(ulaz))
    #print (*lista)
    #print (ulaz)


    tokeni = list(Lekser(ulaz))
    print(*tokeni)
    program = C0Parser.parsiraj(tokeni)
    print(program)
    #print (program.vrijednost())
    
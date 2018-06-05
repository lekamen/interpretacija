import string.hexdigits
from DZ2idiot import *

escapeZnakovi = [Tokeni.NRED, Tokeni.NTAB, Tokeni.NVERTTAB, Tokeni.BACKSP, Tokeni.RET, Tokeni.FFEED, 
    Tokeni.ALERT, Tokeni.QUOTE, Tokeni.DBLQUOTE, Tokeni.ESCSLASH]
separatori = [Tokeni.OOTV, Tokeni.OZATV, Tokeni.UOTV, Tokeni.UZATV, Tokeni.VOTV, Tokeni.VZATV,
     Tokeni.ZAREZ, Tokeni.SEP]

def isxdigit(self, znak):
    """Provjerava je li znak hex znamenka"""
    return znak.isdigit() or znak in string.hexdigits

def isidentifier(self, znak):
    """Provjerava je li znak nešto što ide u identifier"""
    return znak.isalpha() or znak.isdigit() or znak == '_'

def isNChar(znak):
    """Provjerava je li znak nchar"""
    p = re.compile('^[ -~]$')
    if (p.match(znak) is None or znak == '"'):
        return False
    return True

def isSChar(self, znak):
    """Provjerava je li znak schar"""
    if (isNChar or znak in escapeZnakovi):
        return True
    return False

def isLChar(self, znak):
    """Provjerava je li znak lchar"""
    p = re.compile('^[ -~]$')
    if (p.match(znak) is None or znak == '<'):
        return False
    return True

def getZnakSeparator(znak):
    for token in separatori:
        if(token == Tokeni(znak)):
            return token
    return None
           

def Lekser(kôd):
    lex = Tokenizer(kôd)

    for znak in iter(lex.čitaj, ''):
        if znak.isalpha or znak == '_':
            # onda je identifier
            lex.plus(str.isidentifier)
            yield lex.token(Tokeni.IDENTIFIER)
        elif znak.isdigit(): 
            # onda je dec ili hex
            if znak == '0': 
                sljedeći = lex.čitaj()
                if sljedeći == 'x' or sljedeći == 'X':
                    # onda je hex
                    lex.plus(isxdigit)
                    yield lex.token(Tokeni.HEKSADEKADSKI)
                else: lex.greška('očekujem x ili X')
            else:
                # onda je dec
                lex.zvijezda = lex.token(str.isdigit)
                yield lex.token(Tokeni.DECIMALNI)
        # je li escape sequence?
        elif znak == '\\' :
            sljedeći = lex.čitaj()
            if sljedeći == 'n':
                yield lex.token(Tokeni.NRED)
            elif sljedeći == 't':
                yield lex.token(Tokeni.NTAB)
            elif sljedeći == 'v':
                yield lex.token(Tokeni.NVERTTAB)
            elif sljedeći == 'b':
                yield lex.token(Tokeni.BACKSP)
            elif sljedeći == 'r':
                yield lex.token(Tokeni.RET)
            elif sljedeći == 'f':
                yield lex.token(Tokeni.FFEED)
            elif sljedeći == 'a':
                yield lex.token(Tokeni.ALERT)
            elif sljedeći == '\'':
                yield lex.token(Tokeni.QUOTE)
            elif sljedeći == '\"':
                yield lex.token(Tokeni.DBLQUOTE)
            elif sljedeći == '\\':
                yield lex.token(Tokeni.ESCSLASH)
        # je li unarni operator?
        elif znak == '!':
            yield lex.token(Tokeni.USKL)
        elif znak == '~':
            yield lex.token(Tokeni.TILDA)
        elif znak == '-':
            yield lex.token(Tokeni.MINUS)
        elif znak == '*':
            yield lex.token(Tokeni.ZVJ)
        # je li binarni operator?


        # je li chrlit?
        elif znak == '\'':
            idući = lex.čitaj()
            if (not isNChar(idući) and not idući in escapeZnakovi and not idući == '"' and not idući == '\0'):
                raise RuntimeError("Neispravan chrlit")
            kraj = lex.čitaj()
            if (kraj == '\''):
                yield lex.token(Tokeni.CHRLIT)
            raise RuntimeError("Neispravan chrlit")
        # je li strlit?
        elif znak == '"':
            lex.zvijezda(isSChar)
            kraj = lex.čitaj()
            if (kraj == '"'):
                yield lex.token(Tokeni.STRLIT)
            raise RuntimeError("Neispravan strlit")
        #je li liblit?
        elif znak == '<':
            lex.zvijezda(isLChar)
            kraj = lex.čitaj()
            if (kraj == '>'):
                yield lex.token(Tokeni.LIBLIT)
        #je li znak separator?
        elif znak in separatori:
            t = getZnakSeparator(znak)
            if (t is not None):
                yield t
            raise RuntimeError("Neispravan separator")



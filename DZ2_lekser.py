
from string import hexdigits
from pj import *
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
            lex.plus(isidentifier)
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
        # <, <<, <<=, <=
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
from pj import *
import re

# GRAMATIKA (puna)
# decimalni     -> 0 | [1-9][0-9]*
# separator     -> ( | ) | [ | ] | { | } | , | ;
# unarni_op     -> ! | ~ | - | *
# binarni_op    -> . | -> | * | / | % | + | - | << | >> |
#                  < | <= | >= | > | == | != | & | ^ | | |
#                  && | || | ? | :
# op_priruz     -> = | += | -= | *= | /= | %= | <<= | >>=
#               -> &= | ^= | |=
# postfix_op    -> -- | ++
# escape        -> \n | \t | \v | \b | \r | \f | \a |
#                  \\ | \' | \"
# identifier    -> [A-Za-z_][A-Za-z0-9_]*    
# broj          -> decimalni | heksadekadski
# heksadekadski -> 0[xX][0-9a-fA-F]+
# nchar         -> (normalni znak osim ")
# lchar         -> (normalni znak osim >)

#sve iznad je u Tokenima, ispod je za lexer
# library       -> <lchar*>
# schar         -> nchar | escape
# cchar         -> nchar | escape | " | \0
# string        -> "schar*"
# char          -> 'cchar'

class BreakException(Exception): pass
class ContinueException(Exception): pass

class Tokeni(enum.Enum):
    #separatori
    OOTV, OZATV, UOTV, UZATV, VOTV, VZATV, ZAREZ = '()[]{},'
    SEP = ';'
    #unarni operatori
    USKL, TILDA, MINUS, ZVJ = '!~-*'
    #binarni operatori bez zvjezdice!!!
    TOCKA, STRELICA, SLASH, MOD, PLUS, LSHIFT, RSHIFT = '.', '->', '/', '%', '+', '<<', '>>'
    LESS, LESSEQ, GRTEQ, GRT, EQ, DISEQ, BITAND, BITEXCLOR, BITOR = '<', '<=', '>=', '>', '==', '!=', '&', '^', '|'
    LAND, LOR, CONDQ, CONDDOT = '&&', '||', '?', ':'
    #operatori pridruzivanja
    PLUSEQ, MINUSEQ, ZVJEQ, SLASHEQ, MODEQ, LSHIFTEQ, RSHIFTEQ, ASSIGN = '+=', '-=', '*=', '/=', '%=', '<<=', '>>=', '='
    ANDEQ, POTEQ, CRTAEQ = '&=', '^=', '|='
    #postfiksni operatori
    DECR, INCR = '--', '++'
    #escape sekvence
    NRED, NTAB, NVERTTAB, BACKSP, RET, FFEED, ALERT = '\n', '\t', '\v', '\b', '\r', '\f', '\a'
    QUOTE, DBLQUOTE, ESCSLASH = '\'', '\"', '\\'
    #komentari
    COMMENT, COM_BEGIN, COM_END = '//', '/*', '*/'
    #tipovi podataka
    INT, BOOL, CHAR, STRING = 'int', 'bool', 'char', 'string'
    #polja
    INTARR, BOOLARR, CHARARR, STRINGARR
    #statementi
    IF, ELSE, WHILE, FOR, RETURN, ASSERT, ERROR = 'if', 'else', 'while', 'for', 'return', 'assert', 'error'

    class IDENTIFIER(Token):
        def vrijednost(self, imena, vrijednosti): 
            try: return vrijednosti[self]
            except KeyError: self.nedeklaracija()
    class DECIMALNI(Token):
        def vrijednost(self, imena, vrijednosti): 
            return int(self.sadržaj)
    class HEKSADEKADSKI(Token):
        def vrijednost(self, imena, vrijednosti):
            return hex(self.sadržaj) #isprobati!!
    class CHRLIT(Token):
        def vrijednost(self, imena, vrijednosti):
            return self.sadržaj[1 : len(self.sadržaj) - 1] #testiraj jel 'znak'
    class STRLIT(Token):
        def vrijednost(self, imena, vrijednosti):
            return self.sadržaj[1 : len(self.sadržaj) - 1]#testiraj jel "string"
    class LIBLIT(Token):
        def vrijednost(self):
            return self.sadržaj#testiraj jel <string>
    class BOOLEAN(Token):
        def vrijednost(self, imena, vrijednosti):
            return self.sadržaj == 'true'
    class NULL(Token):
        def vrijednost(self, imena, vrijednosti):
            return None
    class BREAK(Token):
        def izvrši(self, imena, vrijednosti):
            raise BreakException
    class CONTINUE(Token):
        def izvrši(self, imena, vrijednosti):
            raise ContinueException
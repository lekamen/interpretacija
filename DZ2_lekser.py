import string.hexdigits

def isxdigit(self, znak):
    """Provjerava je li znak hex znamenka"""
    return znak.isdigit() or znak in string.hexdigits

def isidentifier(self, znak):
    """Provjerava je li znak nešto što ide u identifier"""
    return znak.isalpha() or znak.isdigit() or znak == '_'

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
                    lex.plus(str.isxdigit)
                    yield lex.token(Tokeni.HEKSADEKADSKI)
                else: lex.greška('očekujem x ili X')
            else:
                # onda je dec
                lex.zvijezda = lex.token(str.isdigit)
                yield lex.token(Tokeni.DECIMALNI)
        # je li escape sequence?
        elif znak == '\' :
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
            
            

    else: yield lex.token(operator(AN, znak) or lex.greška())

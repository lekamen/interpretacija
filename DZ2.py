# GRAMATIKA (puna)
# identifier    -> [A-Za-z_][A-Za-z0-9_]*
# broj          -> decimalni | heksadekadski
# decimalni     -> 0 | [1-9][0-9]*
# heksadekadski -> 0[xX][0-9a-fA-F]+
# string        -> "schar*"
# char          -> 'cchar'
# library       -> <lchar*>
# schar         -> nchar | escape
# cchar         -> nchar | escape | " | \0
# nchar         -> (normalni znak osim ")
# lchar         -> (normalni znak osim >)
# escape        -> \n | \t | \v | \b | \r | \f | \a |
#                  \\ | \' | \" 
# separator     -> ( | ) | [ | ] | { | } | , | ;
# unarni_op     -> ! | ~ | - | *
# binarni_op    -> . | -> | * | / | % | + | - | << | >> |
#                  < | <= | >= | > | == | != | & | ^ | | |
#                  && | || | ? | :
# op_priruz     -> = | += | -= | *= | /= | %= | <<= | >>=
#               -> &= | ^= | |=
# postfix_op    -> -- | ++



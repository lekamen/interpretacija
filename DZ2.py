# GRAMATIKA (puna)
# broj          -> decimalni | heksadekadski
# decimalni     -> 0 | [1-9][0-9]*
# heksadekadski ->
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

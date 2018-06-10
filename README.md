# interpretacija
druga zadaća iz interpretacije


funkcija će bit AST, kak je to stablo može imati i podstabla i tu se spremaju sve informacije o funkciji - broj parametara i povratni tip (nije nužno za minimalne bodove xD)

: vraćanje vrijednosti iz funkcije? 
return a -> trebala bi se izvrijednit varijabla a, i onda stavit na stack !?
return se ne izvršava sam po sebi, treba ić "uzvodno" uz stack


: break i continue naredbe kak se izvršavaju?
for ima metodu izvrši, break nema


=> kako ić uzvodno -> eception handling, rad s izuzecima!!!
umjesto da se poziva rekurzivno, iskonstruira se exception objekt, time se uvjetuje putovanje uz stack
f  {
  g ()
 }
  
  
  g {
  
      h ()
      
     }
  h {
  
      raise Exception
  }
      -> prvo se ide unutar h jel ima neki except tj. catch blok, i onda se putuje gore, gleda se jel u g ima neki except
      -> na taj se način implementira i break, i continue, i return!

chainmap iz python collections za scope

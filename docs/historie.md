# Historie vývoje (shrnutí konverzace v Claude, 18. 11. 2026)

Tohle je shrnutí původního rozhovoru, ve kterém aplikace vznikla. Nejde o doslovný přepis.

## 1. Zadání
Uživatel chtěl interaktivní edukativní „hračku“ inspirovanou Windy/Ventusky: posouvat a měnit tlakové
výše a níže nad Evropou (např. výše nad Tureckem blokující přísun vzduchu z jihu) a okamžitě vidět,
jak se změní proudění. Nemusí být fyzikálně přesná, ale rozumně věrná, a hlavně svižná.

## 2. Návrh
Klíčová myšlenka: vítr se z tlakového pole dá **odvodit diagnosticky** (geostrofie → gradientový vítr → tření),
není potřeba simulace v čase. Navrženy úrovně: parametrické systémy, štětec, reálný podklad;
částice, trajektorie, pasivní stopovače, rozklad sil v bodě.

Upřesnění od uživatele:
- doména: Evropa + oblasti s výrazným vlivem (Azory, Island, Sahara, Turecko, západní Rusko);
- žádný samovolný pohyb, jediný vliv má uživatel;
- co by zatěžovalo výkon, zjednodušit; jinak co nejvíc fyziky.

## 3. Verze 1 – vítr
Tlak z eliptických gaussovských systémů, tři režimy větru (geostrofický, gradientový, přízemní 10 m),
částice, izobary, sonda s diagramem sil a trajektoriemi 72 h, stopovače teploty a saharského prachu,
10 předvoleb (omega blokáda, Rexova blokáda, Vb cyklóna, jižní advekce, …).
Uživatel: „běží to výborně“, saharský prach se líbil jako ukázka posunu vzduchových hmot.

## 4. Diskuse o oblačnosti
Problém: mraky potřebují vertikální pohyb, přízemní tlak sám nestačí → 2½D model.
Doporučeno zafixovat chladné pololetí. Zdroje výstupu: Q-vektory (fronty, teplá advekce), Ekmanovo čerpání,
orografie. Vlhkost + kondenzace (velkoprostorové schéma). Fronty mají vznikat samy frontogenezí
a detekovat se automaticky. Otevřená otázka (zpětná vazba termického větru na advekci) rozhodnuta:
**bez zpětné vazby**, priorita je ovladatelnost a pochopitelnost („pohnu něčím a vidím efekt, jehož příčina je jasná“).

## 5. Verze 2 – oblačnost, srážky, fronty
Implementováno vše výše + štětec vzduchových hmot, slidery polární fronty a teploty moří, jet 300 hPa,
vrstva vertikálních pohybů s rozkladem na příčiny, sonda „proč?“ se slovním vysvětlením.
Kalibrační kontroly: Vb → srážky na SZ straně níže nad DE/PL/CZ a Alpami, Středomoří +4 K → +~50 % srážek;
arktický vpád → přeháňkové buňky nad Norským/Severním mořem; jižní Norsko při JZ proudění → sníh z orografického výstupu.
Opravy během ladění: fronty kolem stacionárních studených jader (vyřešeno filtrem frontogeneze), artefakty
na okrajích (taper RHS), přestřelený subtropický jet (podlaha f, cap), pravidelný vzor přeháňkových buněk (měřítko šumu).

## 6. Otevřené body
Viz sekce „Známá omezení / nápady“ v CLAUDE.md.

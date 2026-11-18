# Tlak → vítr → oblačnost (interaktivní edukační model)

Jednostránková webová aplikace (čisté HTML + JS + WebGL2, bez závislostí a bez serveru).
Uživatel tahá tlakové výše/níže nad Evropou a okamžitě vidí proudění, vzduchové hmoty,
oblačnost, srážky a fronty, a sonda vysvětlí **proč** je někde zataženo/jasno.
Komunikuj s uživatelem česky. Kontext a historie rozhodnutí: `docs/historie.md`.

## Cíle a zásady (od uživatele)
- Edukace pro nadšence a studenty: pochopit principy, ne předpovídat počasí.
- „Pohnu něčím a vidím pochopitelný efekt“ – a musí být jasné, co ho způsobilo.
- Fyzika zjednodušená, ale ne špatně. Co je výkonově drahé, raději zjednodušit/omezit.
- **Svižnost v běžném prohlížeči je priorita.** Žádné dlouhé přepočty.
- Tlakové pole je stacionární, žádný samovolný pohyb systémů; jediný „řidič“ je uživatel.
- Teplotu a vlhkost unáší jen vítr z uživatelova tlakového pole (bez zpětné vazby termického větru) – kvůli ovladatelnosti.
- Zafixované chladné pololetí (frontální/vrstevnatá oblačnost; letní konvekce není).

## Struktura
- `src/template.html` – veškerý kód (CSS + JS + GLSL). Místo dat obsahuje placeholder `/*GEO*/`.
- `data/geo.json` – pobřeží a jezera (Natural Earth 1:50m), už promítnutá do roviny [km], delta-kódovaná.
- `tools/build.py` – vloží geo.json do šablony → `index.html` (to je výsledná stránka; needitovat ručně).
- `tools/prep_geo.py` – regenerace geo.json z Natural Earth GeoJSON (`ne_50m_land.geojson`, `ne_50m_lakes.geojson` do složky `natural-earth/`).
- `tools/screenshot.py` – headless test přes Playwright (screenshot + chyby konzole).
- `docs/v1-template-jen-vitr.html` – první verze (jen vítr), pro srovnání.

Workflow: edituj `src/template.html` → `python tools/build.py` → otevři `index.html` v prohlížeči.

## Model (stručně)
- Projekce: šikmá stereografická, střed 10° v. d. / 50° s. š.; rovina X ∈ [−3800, 3800] km, Y ∈ [−2850, 2700] km; mřížka 50 km (153 × 112 uzlů); `HS` = měřítkový faktor.
- Tlak: 1013 hPa + zonální pozadí + eliptické gaussovské systémy (`S.systems`).
- Vítr: geostrofický `UG/VG`; gradientový `UR/VR` (zakřivení izobar `KAP`, anomální řešení → `ANOM`);
  přízemní: lineární tření `KFR` (moře < nížina < hory) → stočení `atan(k/f)` a zeslabení `cos α` (`UB/VB`), 10 m ještě × `S10` (`US/VS`).
- Jet 300 hPa: `UG + 1.204·(R/f)·k×∇T` (f s podlahou 30°, cap 95 m/s). 700 hPa obdobně s 0.357.
- Vzduchové hmoty (`tracerStep`, krok 30 min, semi-Lagrange s monotónní kubickou interpolací): T850 (`T`, relaxace k `TEQ` s polární frontou, τ 6 d), vlhkost `QV`, oblačná voda `CW`, výška výstupu `ZL`, prach `DU`, konvekce `CV`; srážky `PR` [mm/h].
- Vertikální pohyb `WT = WD + WE + WO`:
  - `WD` – QG omega rovnice v Q-vektorové formě, Helmholtz `(σ∇² − f²(π/Δp)²)ω = −2∇·Q`, red-black SOR, σ = 2e-6, Δp = 750 hPa;
  - `WE` – Ekmanovo čerpání `−1000 m · ∇·V_bl`;
  - `WO` – orografie `0.6 · V_bl·∇h` (terén = ručně zadané elipsy pohoří, nejde o DEM).
- Kondenzace: `q_s,eff = q_s(T850)·exp(−γ·Z)`, γ = 4.5e-4 /m; nadbytek → `CW`; `CW > 0.06 g/kg` vypadává; vypařování při podsycení.
- Moře: SST podle regionů (`REG`: Atlantik, Středozemní, Černé, Baltské, Severní, Kaspické, Rudé; odchylka pro každé zvlášť); výpar a ohřev tím silnější, čím je vzduch studenější než moře; přeháňky při `SST − T850 > ~13 K`.
- Fronty: osy maxima |∇T| (TFP-like), filtr `|∇T| > 1.4 K/100 km`, **frontogeneze > 0.6 K/100 km/den** (aby se nekreslily kruhy kolem stacionárních studených jader), okraj 5 buněk mimo; typ podle advekce (teplá/studená/kvazistac.).
- Vykreslení: 2D canvas (raster vrstev, izobary/izotermy marching squares, částice s fade trails) + WebGL2 shader pro „družicový“ vzhled (flow-advected noise ve dvou fázích). Pokud je WebGL pomalé (EMA > 28 ms), automaticky `glSlow = true` → jednoduchý raster.

## UI (rozložení à la Photoshop)
- Pravidlo: **nástroj = věc, se kterou pracuji přímo v mapě**; kontextová lišta nahoře = jeho doladění (nebo parametry vybraného systému).
- Nástroje vlevo (`S.tool`, klávesy 1–6): Tlak (klik přidá V/N, táhnutí, kolečko; klik do prázdna při výběru jen zruší výběr; v liště i Západní proudění = `S.bg`),
  Teplota a Vlhkost (štětce, přepínač studený/teplý resp. vlhký/suchý + velikost), Pol. fronta (táhnutí = šířka, kolečko = kontrast), Moře (táhnutí nahoru/dolů kdekoli = posun SST všech moří, kolečko nad mořem = jen to moře; volba „Všechna“ v liště; každé moře zvlášť: `SEAS`/`SEA_ANOM` indexované `REG`, vč. Rudého a Kaspického), Sonda (klik/táhnutí).
- Nástroj si přepne podklad (`TOOL_LAYER` → `S.toolLayer`), klik na dlaždici to přebije (podklad se mění jen klikem, ne najetím). `lay()` = toolLayer > layer.
- Vpravo: titulek + výběr situace, Podklad, Vítr (Hladina 10 m / 1,5 km / 9 km, Výpočet Úplný / Geostrofický → `S.mode`; zobrazit Částice / Šipky), Čáry a značky, záložky Sonda / O modelu. Dole lišta času (mezerník = pauza; pauza zastaví i částice).

## Výkon (orientačně, headless bez GPU)
compute() ~10–17 ms (jen při změně tlaku), tracerStep ~10 ms (12×/s při 6 h/s), updateDyn ~2 ms, 2D draw ~1.6 ms.

## Známá omezení / nápady na další kroky
- Nemám ověřeno vizuálně WebGL vykreslení na skutečné GPU (testováno jen headless → fallback).
- Fronty jsou místy roztříštěné; nevyvíjejí se (tlak je stacionární).
- Chybí: inverzní oblačnost/mlhy ve výších, latentní teplo, skutečný DEM, zoom/posun mapy.
- Navržené další kroky: svislý řez přes frontu (Sawyer–Eliassen cirkulace), porovnávací režim (uložit stav → změnit → rozdíl), zoom.

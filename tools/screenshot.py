"""Headless test: otevře index.html, uloží screenshot a vypíše chyby z konzole.

Použití (z kořene projektu, vyžaduje `pip install playwright && playwright install chromium`):
    python tools/screenshot.py                      # jen výchozí stav -> shot.png
    python tools/screenshot.py "await pg.select_option('#preset','5'); await pg.wait_for_timeout(1500); await pg.screenshot(path='vb.png')"

Každý argument je kus async kódu; středníky s mezerou se rozdělí na řádky, k dispozici je `pg` (Playwright Page).
Pozn.: v headless Chromiu bez GPU je WebGL emulované a pomalé, takže aplikace sama přepne
na zjednodušené vykreslení mraků (glSlow = true). Na běžném desktopu s GPU se to stát nemá.
"""
import asyncio
import sys
from pathlib import Path

from playwright.async_api import async_playwright

ROOT = Path(__file__).resolve().parent.parent


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        pg = await browser.new_page(viewport={"width": 1500, "height": 880})
        logs = []
        pg.on("console", lambda m: logs.append(f"{m.type}: {m.text}"))
        pg.on("pageerror", lambda e: logs.append(f"PAGE ERROR: {e}"))
        await pg.goto((ROOT / "index.html").as_uri())
        await pg.wait_for_timeout(2500)
        await pg.screenshot(path="shot.png")
        for action in sys.argv[1:]:
            ns = {}
            exec("async def _f(pg):\n    " + action.replace("; ", "\n    "), globals(), ns)
            await ns["_f"](pg)
        ms = await pg.evaluate(
            "(()=>{const t0=performance.now();for(let i=0;i<10;i++){compute();}return (performance.now()-t0)/10})()"
        )
        print(f"compute(): {ms:.1f} ms")
        print("\n".join(logs[:30]) or "(konzole bez zpráv)")
        await browser.close()


asyncio.run(main())

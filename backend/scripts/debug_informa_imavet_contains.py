#!/usr/bin/env python3
import os
import sys
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from services.informacolombia_scraper import InformaColombiaScraper

name = "AYUDAS DIAGNOSTICAS VETERINARIAS IMAVET S.A.S."
city = "MANIZALES"
nit = "901096205"

s = InformaColombiaScraper()
s.driver = s._get_browser()
if not s.driver:
    print('NO_BROWSER')
    raise SystemExit(2)

try:
    data = s.scrape_company(name, city, nit)
    print('DATA', data)
    html = s.driver.execute_script("return document.body.innerHTML || ''") or ''
    text = s.driver.execute_script("return document.body.innerText || ''") or ''

    needles = [
        'CARRERA 19 B 52 A 03 PISO 1',
        'MANIZALES',
        'CALDAS',
        '3006182981',
        '3269270',
        'AYUDAS DIAGNOSTICAS VETERINARIAS IMAVET',
    ]
    for needle in needles:
        print(needle, 'HTML=', needle.lower() in html.lower(), 'TEXT=', needle.lower() in text.lower())
finally:
    if s.driver:
        s.driver.quit()

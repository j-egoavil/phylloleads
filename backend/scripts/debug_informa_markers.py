#!/usr/bin/env python3
import os
import sys
import re

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from services.informacolombia_scraper import InformaColombiaScraper

name = "ASESORIAS VETERINARIAS INTEGRALES S.A.S"
city = "BOGOTA"

s = InformaColombiaScraper()
if not s.driver:
    s.driver = s._get_browser()

if not s.driver:
    print("No se pudo iniciar navegador")
    raise SystemExit(2)

try:
    data = s.scrape_company(name, city)
    print("data:", data)

    html = s.driver.execute_script("return document.body.innerHTML || ''") or ""
    text = s.driver.execute_script("return document.body.innerText || ''") or ""

    checks = {
        "showMapEmp": html.count("showMapEmp"),
        "DireccionActual": html.lower().count("dirección actual") + html.lower().count("direccion actual"),
        "la_direccion": html.lower().count("la dirección") + html.lower().count("la direccion"),
    }
    print("markers:", checks)

    for marker in ["showMapEmp", "dirección actual", "direccion actual", "la dirección", "la direccion"]:
        m = re.search(re.escape(marker), html, re.IGNORECASE)
        if m:
            start = max(0, m.start() - 120)
            end = min(len(html), m.end() + 200)
            print(f"snippet[{marker}]:", html[start:end].replace("\n", " "))

    # Mostrar lo que extrae el helper directo
    addr = s._extract_address_from_informa_html(html)
    print("parsed_address:", addr)

    # Extraer por regex de texto plano como control
    m_text = re.search(r"Direcci[oó]n\s+Actual\s*([A-Z0-9ÁÉÍÓÚÑa-záéíóúñ#\-\.\s,]{8,220})", text, re.IGNORECASE)
    print("plain_text_regex_address:", m_text.group(1).strip() if m_text else None)

finally:
    if s.driver:
        s.driver.quit()

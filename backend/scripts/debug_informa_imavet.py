#!/usr/bin/env python3
import os
import re
import sys
import time

from bs4 import BeautifulSoup

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from services.informacolombia_scraper import InformaColombiaScraper

name = "AYUDAS DIAGNOSTICAS VETERINARIAS IMAVET S.A.S."
city = "MANIZALES"
nit = "901096205"

s = InformaColombiaScraper()
if not s.driver:
    s.driver = s._get_browser()
if not s.driver:
    print("No se pudo iniciar navegador")
    raise SystemExit(2)

try:
    s.driver.get(s.BASE_URL)
    time.sleep(2)

    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC

    search_input = WebDriverWait(s.driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder='Buscar empresa']"))
    )
    s.driver.execute_script(
        "arguments[0].value = arguments[1]; arguments[0].dispatchEvent(new Event('input', { bubbles: true })); arguments[0].dispatchEvent(new Event('change', { bubbles: true }));",
        search_input,
        name,
    )
    btn = WebDriverWait(s.driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Buscar')]"))
    )
    btn.click()
    time.sleep(3)

    list_html = s.driver.page_source
    soup = BeautifulSoup(list_html, 'html.parser')

    print("=== RESULTADOS (primeros 10 links de perfil) ===")
    count = 0
    for a in soup.find_all('a', href=True):
        href = a['href'].strip()
        if '/directorio-empresas/informacion-empresa/' in href:
            txt = a.get_text(' ', strip=True)
            print(f"{count+1}. text={txt} | href={href}")
            count += 1
            if count >= 10:
                break

    data = s.scrape_company(name, city, nit)
    print("\n=== DATA SCRAPER ===")
    print(data)
    cur_url = s.driver.current_url
    print("profile_url:", cur_url)

    page_html = s.driver.execute_script("return document.body.innerHTML || ''") or ''
    page_text = s.driver.execute_script("return document.body.innerText || ''") or ''

    print("\n=== MARCADORES ===")
    print("showMapEmp:", page_html.count("showMapEmp"))
    print("direccion actual (html):", page_html.lower().count("dirección actual") + page_html.lower().count("direccion actual"))

    phone_candidates = re.findall(r"(?:\+57\s*)?(?:3\d{9}|\d{7,10})", page_text)
    print("phones_text_candidates:", list(dict.fromkeys(phone_candidates))[:10])

    for marker in ["NIT", "Dirección", "Teléfono", "Ciudad", "Departamento", "showMapEmp"]:
        m = re.search(re.escape(marker), page_text, re.IGNORECASE)
        if m:
            snippet = page_text[max(0, m.start()-120):m.start()+180]
            print(f"\n[{marker}] snippet:\n{snippet}")

finally:
    if s.driver:
        s.driver.quit()

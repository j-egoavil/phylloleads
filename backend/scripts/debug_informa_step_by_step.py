#!/usr/bin/env python3
import os
import sys
import time
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from services.informacolombia_scraper import InformaColombiaScraper

COMPANY_ID = int(sys.argv[1]) if len(sys.argv) > 1 else 722
NAME = os.getenv('SCRAPE_NAME', 'AYUDAS DIAGNOSTICAS VETERINARIAS IMAVET S.A.S.')
CITY = os.getenv('SCRAPE_CITY', 'MANIZALES')
NIT = os.getenv('SCRAPE_NIT', '901096205')


def pause(label: str):
    print(f"\n=== {label} ===")
    input("Presiona Enter para continuar...")


s = InformaColombiaScraper()
s.driver = s._get_browser(headless=False)
if not s.driver:
    print('No se pudo abrir navegador visible')
    raise SystemExit(2)

try:
    print(f"Empresa objetivo: {NAME} | Ciudad: {CITY} | NIT: {NIT} | ID: {COMPANY_ID}")
    pause('1. Navegador abierto')

    s.driver.set_page_load_timeout(30)
    s.driver.get(s.BASE_URL)
    time.sleep(2)
    print('URL actual:', s.driver.current_url)
    print('Título:', s.driver.title)
    pause('2. Página base de Informa cargada')

    search_input = WebDriverWait(s.driver, 15).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder='Buscar empresa']"))
    )
    search_input.clear()
    s.driver.execute_script(
        "arguments[0].value = arguments[1]; arguments[0].dispatchEvent(new Event('input', { bubbles: true })); arguments[0].dispatchEvent(new Event('change', { bubbles: true }));",
        search_input,
        NAME,
    )
    print('Texto escrito en buscador')
    pause('3. Nombre escrito en buscador')

    search_button = WebDriverWait(s.driver, 15).until(
        EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Buscar')]"))
    )
    search_button.click()
    time.sleep(3)
    print('URL tras buscar:', s.driver.current_url)
    print('Título tras buscar:', s.driver.title)
    pause('4. Resultados de búsqueda visibles')

    soup = BeautifulSoup(s.driver.page_source, 'html.parser')
    profile_link = None
    print('Primeros enlaces de perfil encontrados:')
    shown = 0
    for a in soup.find_all('a', href=True):
        href = a['href'].strip()
        if '/directorio-empresas/informacion-empresa/' in href:
            print('-', a.get_text(' ', strip=True), '|', href)
            if not profile_link:
                profile_link = href if href.startswith('http') else s._absolute_url(href)
            shown += 1
            if shown >= 5:
                break

    print('Perfil elegido:', profile_link)
    if not profile_link:
        print('No se encontró link de perfil')
        raise SystemExit(3)
    pause('5. Antes de entrar al perfil')

    s.driver.get(profile_link)
    time.sleep(3)
    print('URL perfil:', s.driver.current_url)
    print('Título perfil:', s.driver.title)
    pause('6. Perfil abierto')

    page_text = s.driver.execute_script("return document.body.innerText || ''") or ''
    page_html = s.driver.execute_script("return document.body.innerHTML || ''") or ''
    print('showMapEmp:', 'showMapEmp' in page_html)
    print('Dirección Actual:', 'Dirección Actual' in page_text or 'Direccion Actual' in page_text)
    print('NIT:', 'NIT' in page_text)
    print('Ciudad:', 'Ciudad' in page_text)
    print('Departamento:', 'Departamento' in page_text)
    print('Teléfono 3006182981:', '3006182981' in page_text)
    print('Teléfono 3269270:', '3269270' in page_text)
    pause('7. Revisar contenido del perfil')

finally:
    s.driver.quit()
    print('Navegador cerrado')

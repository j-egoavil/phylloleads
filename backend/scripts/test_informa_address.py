#!/usr/bin/env python3
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from backend.services.informacolombia_scraper import InformaColombiaScraper

s = InformaColombiaScraper()

html_showmap = "onclick=\"showMapEmp('es','Calle 123 #45-67, Bogotá, Colombia', 10, -74)\""
html_para = "<p>La empresa tiene la dirección, Calle 45 #12-34 en la ciudad de Bogotá, y presta servicios.</p>"
html_full = "<html><body>" + html_showmap + "</body></html>"

print('=== Test: showMapEmp pattern ===')
print(s._extract_address_from_informa_html(html_full))
print('\n=== Test: paragraph pattern ===')
print(s._extract_address_from_informa_html(html_para))

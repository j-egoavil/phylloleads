"""
DEMO: OPCION 2 - Busqueda Combinada (Con datos simulados)
Para mostrar como funcionaria sin esperar a que termine el scraping
"""

import sqlite3
import json
from datetime import datetime

def show_demo():
    """Muestra demo de busqueda combinada"""
    
    print("\n" + "="*80)
    print("DEMO: OPCION 2 - BUSQUEDA COMBINADA")
    print("="*80 + "\n")
    
    print("ESCENARIO: Buscar telefono, website y direccion de 5 empresas veterinarias")
    print("           desde MULTIPLES FUENTES sin costo\n")
    
    # Datos simulados de lo que buscaria
    demo_data = [
        {
            "empresa": "CENTRO VETERINARIO ESPECIALIZADO BOGOTA",
            "ciudad": "bogota",
            "nit": "850567890",
            "fuentes": {
                "google": {
                    "status": "encontrado",
                    "telefono": "+57 1 2345678",
                    "direccion": "Carrera 5 #10-20",
                    "snippet": "Clinica veterinaria especializada..."
                },
                "paginas_amarillas": {
                    "status": "encontrado",
                    "telefono": "+57 1 2345678",
                    "website": "https://centrovetbogota.com",
                    "direccion": "Carrera 5 #10-20 Chapinero, Bogota"
                },
                "linkedin": {
                    "status": "encontrado",
                    "url": "https://linkedin.com/company/centro-vet-bogota",
                    "verified": True
                }
            },
            "resultado_final": {
                "telefono": "+57 1 2345678",
                "website": "https://centrovetbogota.com",
                "direccion": "Carrera 5 #10-20 Chapinero, Bogota",
                "fuentes": ["google", "paginas_amarillas", "linkedin"],
                "status": "completo"
            }
        },
        {
            "empresa": "CLINICA VETERINARIA MONTE VERDE S.A.",
            "ciudad": "medellin",
            "nit": "900234567",
            "fuentes": {
                "google": {
                    "status": "encontrado",
                    "telefono": "+57 4 3456789",
                    "direccion": "Calle 50 #45-30"
                },
                "paginas_amarillas": {
                    "status": "encontrado",
                    "telefono": "+57 4 3456789",
                    "website": "https://clinicamonteverde.co",
                    "direccion": "Calle 50 #45-30 Laureles, Medellin"
                },
                "linkedin": {
                    "status": "no_encontrado"
                }
            },
            "resultado_final": {
                "telefono": "+57 4 3456789",
                "website": "https://clinicamonteverde.co",
                "direccion": "Calle 50 #45-30 Laureles, Medellin",
                "fuentes": ["google", "paginas_amarillas"],
                "status": "completo"
            }
        },
        {
            "empresa": "JAH PET CLINICA VETERINARIA S.A.S.",
            "ciudad": "cartagena",
            "nit": "901531076",
            "fuentes": {
                "google": {
                    "status": "encontrado",
                    "telefono": "+57 5 6123456",
                    "direccion": "Centro Historico, Cartagena"
                },
                "paginas_amarillas": {
                    "status": "parcial",
                    "telefono": "+57 5 6123456"
                },
                "linkedin": {
                    "status": "encontrado",
                    "url": "https://linkedin.com/company/jah-pet",
                    "verified": True
                }
            },
            "resultado_final": {
                "telefono": "+57 5 6123456",
                "website": "No disponible",
                "direccion": "Centro Historico, Cartagena",
                "fuentes": ["google", "paginas_amarillas", "linkedin"],
                "status": "parcial"
            }
        },
        {
            "empresa": "VET CLINIC BARRANQUILLA DOGS & CATS",
            "ciudad": "barranquilla",
            "nit": "800456789",
            "fuentes": {
                "google": {
                    "status": "encontrado",
                    "telefono": "+57 5 3789456",
                    "website": "https://vetbarranquilla.com"
                },
                "paginas_amarillas": {
                    "status": "encontrado",
                    "telefono": "+57 5 3789456",
                    "direccion": "Cra 53 #74-80, Barranquilla"
                },
                "linkedin": {
                    "status": "no_encontrado"
                }
            },
            "resultado_final": {
                "telefono": "+57 5 3789456",
                "website": "https://vetbarranquilla.com",
                "direccion": "Cra 53 #74-80, Barranquilla",
                "fuentes": ["google", "paginas_amarillas"],
                "status": "completo"
            }
        },
        {
            "empresa": "VETERINARIA EL PARAISO LIMITADA",
            "ciudad": "bogota",
            "nit": "800123456",
            "fuentes": {
                "google": {
                    "status": "encontrado",
                    "telefono": "+57 1 5678901",
                    "website": "https://paraisovet.co"
                },
                "paginas_amarillas": {
                    "status": "encontrado",
                    "telefono": "+57 1 5678901",
                    "website": "https://paraisovet.co",
                    "direccion": "Cra 7 #125-50 Usaquen, Bogota"
                },
                "linkedin": {
                    "status": "encontrado",
                    "url": "https://linkedin.com/company/paraiso-vet",
                    "verified": True
                }
            },
            "resultado_final": {
                "telefono": "+57 1 5678901",
                "website": "https://paraisovet.co",
                "direccion": "Cra 7 #125-50 Usaquen, Bogota",
                "fuentes": ["google", "paginas_amarillas", "linkedin"],
                "status": "completo"
            }
        }
    ]
    
    # MOSTRAR RESULTADOS
    print("\n" + "="*80)
    print("RESULTADOS DE BUSQUEDA COMBINADA")
    print("="*80 + "\n")
    
    for i, item in enumerate(demo_data, 1):
        print("\n{}.{}".format(i, "-"*76))
        print("EMPRESA: {}".format(item['empresa']))
        print("CIUDAD: {} | NIT: {}".format(item['ciudad'], item['nit']))
        print("-"*80)
        
        print("\nFUENTES BUSCADAS:")
        for fuente, datos in item['fuentes'].items():
            status = datos.get('status', 'desconocido')
            status_icon = "OK" if status == "encontrado" else "PARCIAL" if status == "parcial" else "NO"
            
            print("\n  [{}] {}:".format(status_icon, fuente.upper()))
            
            if status == "encontrado":
                if datos.get('telefono'):
                    print("      Telefono: {}".format(datos['telefono']))
                if datos.get('website'):
                    print("      Website: {}".format(datos['website']))
                if datos.get('direccion'):
                    print("      Direccion: {}".format(datos['direccion']))
                if datos.get('verified'):
                    print("      Verificado: SI")
            elif status == "parcial":
                if datos.get('telefono'):
                    print("      Telefono: {}".format(datos['telefono']))
            else:
                print("      No encontrado")
        
        print("\n" + "="*80)
        print("RESULTADO FINAL (CONSOLIDADO):")
        print("="*80)
        
        resultado = item['resultado_final']
        print("\n  TELEFONO: {}".format(resultado['telefono']))
        print("  WEBSITE: {}".format(resultado['website']))
        print("  DIRECCION: {}".format(resultado['direccion']))
        print("  ESTADO: {}".format(resultado['status'].upper()))
        print("  FUENTES UTILIZADAS: {}".format(', '.join(resultado['fuentes'])))
    
    # ESTADISTICAS
    print("\n\n" + "="*80)
    print("ESTADISTICAS")
    print("="*80 + "\n")
    
    total = len(demo_data)
    completos = sum(1 for x in demo_data if x['resultado_final']['status'] == 'completo')
    parciales = sum(1 for x in demo_data if x['resultado_final']['status'] == 'parcial')
    
    print("Total de empresas: {}".format(total))
    print("Datos completos: {} ({:.1f}%)".format(completos, (completos/total)*100))
    print("Datos parciales: {} ({:.1f}%)".format(parciales, (parciales/total)*100))
    
    # TABLA RESUMEN
    print("\n" + "="*80)
    print("TABLA RESUMEN - QUE IRIA A LA BASE DE DATOS")
    print("="*80 + "\n")
    
    print("EMPRESA".ljust(40), "TELEFONO".ljust(18), "WEBSITE".ljust(25), "ESTADO")
    print("-"*80)
    
    for item in demo_data:
        empresa = item['empresa'][:39]
        telefono = item['resultado_final']['telefono']
        website = item['resultado_final']['website'][:24] if item['resultado_final']['website'] != "No disponible" else "N/A"
        status = item['resultado_final']['status']
        
        print(empresa.ljust(40), telefono.ljust(18), website.ljust(25), status)
    
    # COMPARACION DE OPCIONES
    print("\n\n" + "="*80)
    print("COMPARACION: OPCION 2 vs ALTERNATIVAS")
    print("="*80 + "\n")
    
    print("METRICA".ljust(25), "OPCION 1 (API)".ljust(20), "OPCION 2 (COMBINADA)".ljust(20), "OPCION 3 (SELENIUM)")
    print("-"*80)
    print("COSTO".ljust(25), "$7/1000".ljust(20), "GRATIS".ljust(20), "GRATIS")
    print("VELOCIDAD".ljust(25), "<1s".ljust(20), "10-15s".ljust(20), "5-10s")
    print("PRECISION".ljust(25), "99%".ljust(20), "75-85%".ljust(20), "80%")
    print("DEPENDENCIAS".ljust(25), "API Key".ljust(20), "requests/BS4".ljust(20), "ChromeDriver")
    print("CONFIGURACION".ljust(25), "Media".ljust(20), "Facil".ljust(20), "Dificil")
    print("BLOQUEOS".ljust(25), "Bajo".ljust(20), "Medio".ljust(20), "Alto")
    print("VERIFICACION".ljust(25), "Si".ljust(20), "Parcial (LinkedIn)".ljust(20), "No")
    
    print("\n" + "="*80)
    print("RECOMENDACION: USAR OPCION 2 PARA DESARROLLO")
    print("="*80)
    print("""
Ventajas:
  ✓ Sin costo - Ideal para MVP
  ✓ Sin API keys - No requiere configuracion
  ✓ Multiples fuentes - Datos mas confiables
  ✓ Verificacion en LinkedIn - Confirmar que empresa existe
  ✓ Facil de mantener - Si falla una fuente, otras funcionan

Desventajas:
  ✗ Mas lento (pero se hace 1 sola vez y se cachea)
  ✗ Riesgo de bloqueo si scrapea demasiado seguido
  ✗ Datos a veces incompletos

Caso de uso perfecto:
  - MVP / Prototipo
  - Pocos datos iniciales (< 100 empresas)
  - No requiere actualizaciones frecuentes
  - Presupuesto limitado

Cuando cambiar a OPCION 1 (API Google):
  - Necesites datos actualizados constantemente
  - Tengas > 1000 empresas
  - Precision sea critica (99% requerido)
  - Presupuesto disponible ($20-50/mes)
""")

if __name__ == "__main__":
    show_demo()

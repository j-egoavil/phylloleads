"""
Comparación Visual de Opciones
"""

comparacion = """

╔══════════════════════════════════════════════════════════════════════════════╗
║                    PHYLLOLEADS - SCRAPER AUTOMÁTICO                          ║
║                    Comparación de 3 Opciones de Ejecución                    ║
╚══════════════════════════════════════════════════════════════════════════════╝


┌──────────────────────────────────────────────────────────────────────────────┐
│ OPCIÓN 1: MENÚ INTERACTIVO                                                   │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│  Comando:    python menu.py                                                  │
│                                                                               │
│  ✅ VENTAJAS:                                                                 │
│     • Interface visual fácil de usar                                         │
│     • Opciones numeradas (1-5)                                               │
│     • No necesita memorizar comandos                                         │
│     • Interactivo y amigable                                                 │
│     • Ideal para principiantes                                               │
│                                                                               │
│  ⚙️  OPCIONES EN EL MENÚ:                                                    │
│     1. Ejecutar scraper completo                                             │
│     2. Iniciar API (http://localhost:8000/docs)                             │
│     3. Paso a paso (depuración)                                              │
│     4. Ver datos actuales                                                    │
│     5. Actualizar datos manualmente                                          │
│                                                                               │
│  ⏱️  TIEMPO: ~10 min (incluyendo interacción)                                 │
│                                                                               │
└──────────────────────────────────────────────────────────────────────────────┘


┌──────────────────────────────────────────────────────────────────────────────┐
│ OPCIÓN 2: TERMINAL DIRECTA (RECOMENDADO)                                     │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│  Comando:    python run_scraper_maestro.py                                   │
│                                                                               │
│  ✅ VENTAJAS:                                                                 │
│     • Un solo comando                                                        │
│     • Automatiza TODO                                                        │
│     • Muestra estadísticas al final                                          │
│     • No requiere interacción                                                │
│     • MÁS RÁPIDO                                                             │
│                                                                               │
│  🔄 QUÉ HACE:                                                                │
│     [1/3] Extrae empresas de La República                                    │
│     [2/3] Busca datos en Google Maps + DuckDuckGo + Páginas Amarillas        │
│     [3/3] Muestra datos enriquecidos                                         │
│     [4/4] Genera estadísticas finales                                        │
│                                                                               │
│  📊 RESULTADO:                                                                │
│     Total empresas: 6                                                        │
│     Con teléfono:   5 (83.3%)                                                │
│     Con website:    5 (83.3%)                                                │
│     Con dirección:  5 (83.3%)                                                │
│                                                                               │
│  ⏱️  TIEMPO: ~5-10 min                                                        │
│                                                                               │
└──────────────────────────────────────────────────────────────────────────────┘


┌──────────────────────────────────────────────────────────────────────────────┐
│ OPCIÓN 3: API REST                                                           │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│  Comando 1:  python -m uvicorn main:app --reload                             │
│  Comando 2:  curl -X POST http://localhost:8000/api/scraper/enrich-auto...   │
│                                                                               │
│  ✅ VENTAJAS:                                                                 │
│     • Ejecución en background                                                │
│     • Monitoreable vía HTTP                                                  │
│     • Documentación automática (/docs)                                      │
│     • Ideal para integración                                                 │
│     • Escalable para múltiples usuarios                                      │
│                                                                               │
│  🔗 ENDPOINTS:                                                                │
│     POST /api/scraper/enrich-automatic → Ejecuta scraper                    │
│     GET  /api/scraper/status          → Ver estadísticas                    │
│     GET  /api/companies-with-details  → Ver datos enriquecidos              │
│                                                                               │
│  🌐 INTERFAZ VISUAL:                                                          │
│     http://localhost:8000/docs ← Swagger UI automático                      │
│     Todas las opciones están documentadas                                    │
│                                                                               │
│  ⏱️  TIEMPO: ~10 min (2 terminales)                                           │
│                                                                               │
└──────────────────────────────────────────────────────────────────────────────┘


╔══════════════════════════════════════════════════════════════════════════════╗
║                          COMPARACIÓN RÁPIDA                                   ║
╠═════════════════════════════╦═════════════════════════════╦═══════════════════╣
║ Aspecto                     ║ Opción 1: Menú             ║ Opción 2: Terminal║
╠═════════════════════════════╬═════════════════════════════╬═══════════════════╣
║ Facilidad de uso            ║ ⭐⭐⭐⭐⭐ (Muy fácil)       ║ ⭐⭐⭐ (Fácil)      ║
║ Velocidad                   ║ ⭐⭐⭐⭐ (~10 min)          ║ ⭐⭐⭐⭐⭐ (~5 min) ║
║ Automatización              ║ ⭐⭐⭐⭐ (Interactivo)       ║ ⭐⭐⭐⭐⭐ (Total)  ║
║ Ideal para principiantes    ║ ✓ SÍ                       ║ ✓ SÍ             ║
║ Ideal para integración      ║ ✗ No                       ║ ✓ Opción 3       ║
║ Requiere 2 terminales       ║ ✗ No                       ║ ✗ No (solo 1)     ║
╚═════════════════════════════╩═════════════════════════════╩═══════════════════╝


╔══════════════════════════════════════════════════════════════════════════════╗
║                      🎯 RECOMENDACIÓN                                         ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                               ║
║  PARA PRINCIPIANTES:                                                         ║
║  👉 Opción 1 (Menú) - Es más intuitivo                                       ║
║                                                                               ║
║  PARA MÁXIMA VELOCIDAD:                                                      ║
║  👉 Opción 2 (Terminal) - Todo automático en 5-10 minutos                   ║
║                                                                               ║
║  PARA INTEGRACIÓN / PRODUCCIÓN:                                              ║
║  👉 Opción 3 (API) - Endpoints HTTP reutilizables                           ║
║                                                                               ║
║  ⚡ INICIO RÁPIDO:                                                            ║
║  👉 Simplemente ejecuta:   python run_scraper_maestro.py                     ║
║                                                                               ║
╚══════════════════════════════════════════════════════════════════════════════╝


ARCHIVO DE DATOS GENERADO:
═══════════════════════════════════════════════════════════════════════════════

appdb.sqlite:
  └─ Tabla: companies (6 filas)
  └─ Tabla: company_details (5+ filas)
     ├─ phone:    +57 301 5052787
     ├─ website:  https://clinicamonteverde.co
     └─ address:  Centro Historico, Cartagena


ESTADÍSTICAS:
═══════════════════════════════════════════════════════════════════════════════

Total empresas:        6
Con teléfono:          5 (83.3%)
Con website:           5 (83.3%)
Con dirección:         5 (83.3%)

Sin intervención manual - TODO AUTOMÁTICO ✅


PRÓXIMOS PASOS:
═══════════════════════════════════════════════════════════════════════════════

1. Selecciona una opción (recomendado: Opción 2)
2. Ejecuta el comando
3. Espera 5-10 minutos
4. ¡Datos listos!

No más actualizaciones manuales. El scraper se ejecuta automáticamente.

═══════════════════════════════════════════════════════════════════════════════
"""

if __name__ == "__main__":
    print(comparacion)

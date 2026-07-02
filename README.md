# 🚌 GTFSSpain v2 — Visor de Transporte Público de España

> **v2.0** · Visor interactivo de datos GTFS reales · Click en líneas del mapa → horarios completos

---

## 📋 Resumen Ejecutivo

**GTFSSpain v2** es un visor web de transporte público que carga datos GTFS reales de España desde el Punto de Acceso Nacional (NAP) del Ministerio de Transportes. Permite buscar ubicaciones, explorar paradas cercanas, visualizar rutas en el mapa y **consultar horarios completos de cada línea** con un solo click.

### Novedades vs v1

| Característica | v1 | v2 |
|---|---|---|
| Click en líneas del mapa | ❌ Solo popup básico | ✅ Panel de ruta completo con horarios |
| Explorador de líneas | ❌ No existía | ✅ Pestaña "Líneas" con búsqueda |
| Panel de ruta detallado | ❌ No existía | ✅ Paradas ordenadas, timetable, direcciones |
| Click en chip de ruta | ❌ No hacía nada | ✅ Abre detalle de la ruta |
| Link ruta → desde parada | ❌ No existía | ✅ "Ver ruta completa" en cada card |
| Highlight de ruta en mapa | ❌ No existía | ✅ Al abrir detalle, la ruta se resalta |
| Horarios por dirección | ❌ Solo lista plana | ✅ Filtrado por headsign/dirección |
| UI con pestañas | ❌ Una sola vista | ✅ 3 pestañas: Buscar / Líneas / Datos |
| Datasets soportados | 25 max | 30 max |
| Radio por defecto | 200m | 500m |

---

## 🏗️ Arquitectura

```
┌──────────────────────────────────────────────────────────────┐
│  Header — GTFSSpain v2                                       │
├──────────┬───────────────────────────┬───────────────────────┤
│ Sidebar  │  Mapa Leaflet (IGN)       │  Panel de Ruta (rhs)  │
│          │                           │  ┌─────────────────┐  │
│ [Buscar] │  • Shapes clickeables     │  │ Badge + Nombre  │  │
│ [Líneas] │  • Paradas con colores    │  │ KPIs            │  │
│ [Datos]  │  • Círculo de radio       │  │ Direcciones     │  │
│          │  • Highlight al click     │  │ Paradas (orden) │  │
│          │                           │  │ Timetable       │  │
│          │                           │  └─────────────────┘  │
├──────────┴───────────────────────────┴───────────────────────┤
│  Panel de Horarios (bottom, para paradas)                     │
└──────────────────────────────────────────────────────────────┘
```

### Flujo de interacción

1. **Buscar ubicación** → geocodificación Nominatim → click en mapa
2. **Paradas en radio** → lista con chips de rutas → click en chip → **panel de ruta**
3. **Click en línea del mapa** → popup informativo → click → **panel de ruta completo**
4. **Panel de ruta** → paradas ordenadas + timetable + direcciones + highlight en mapa
5. **Explorador de líneas** → pestaña "Líneas" → buscar/filtrar → click → panel de ruta

---

## 📊 Datos

### Fuentes

- **Punto de Acceso Nacional (NAP)** — `transportes.gob.es`
- **37+ datasets GTFS** descargados y pre-cargados en `data/`
- **379 MB** de datos totales (ZIPs comprimidos)

### Contenido por dataset

Cada dataset GTFS puede contener:

| Archivo | Contenido | Uso en el visor |
|---|---|---|
| `routes.txt` | Líneas/rutas del operador | Lista de rutas, colores, tipo |
| `stops.txt` | Paradas con coordenadas | Marcadores en mapa |
| `trips.txt` | Viajes por ruta | Conteo de viajes, headsigns, shapes |
| `stop_times.txt` | Horarios por parada | Timetable completo |
| `shapes.txt` | Trazado geográfico de rutas | Polylines clickeables en mapa |
| `agency.txt` | Información del operador | Nombre del operador |

### Datasets incluidos

Incluye datos de: EMT Madrid, Metro Bilbao, Bizkaibus, TMB Barcelona, EMT Valencia, Tranvía de Zaragoza, ALSA, Renfe Cercanías, y muchos más operadores de toda España.

---

## 🚀 Uso

### Opción 1: Servidor local (recomendado)

```bash
# Windows
iniciar.bat

# Linux/Mac
cd visor
python server.py
```

Abre `http://localhost:8000` en tu navegador. Los ZIPs de `data/` se cargan automáticamente.

### Opción 2: Sin servidor (limitado)

Abre `visor/index.html` directamente en el navegador. Puedes arrastrar ZIPs GTFS manualmente, pero no se auto-cargan los datos del servidor.

---

## 🛠️ Funcionalidades detalladas

### 🔍 Búsqueda de ubicación

- Geocodificación vía Nominatim (OpenStreetMap)
- Autocompletado con debounce (800ms)
- Dropdown de resultados clickeables
- Solo direcciones en España (`countrycodes=es`)

### 🗺️ Mapa interactivo

- **Basemaps:** IGN Gris (recomendado), IGN Topográfica, CARTO Light
- **Círculo de radio** ajustable (50m - 2000m, default 500m)
- **Paradas:** marcadores con color por modo de transporte
- **Rutas:** polylines con color de la ruta, grosor 5px, hover 8px
- **Click en ruta:** abre panel de detalle con horarios completos
- **Highlight:** al ver detalle, la ruta se resalta en el mapa

### 📋 Panel de ruta (novedad v2)

Al clickar una línea en el mapa o un chip de ruta:

1. **Cabecera** con badge coloreado, nombre y operador
2. **KPIs:** viajes totales, paradas, direcciones
3. **Filtro por dirección** (headsign tabs)
4. **Lista de paradas** ordenadas con horario de primera salida
5. **Timetable completo** con filtrado por dirección

### 🚏 Panel de horarios (parada)

Al clickar una parada:

1. **Filtro de rutas** con chips clickeables
2. **Cards por ruta** expandibles con:
   - Número de viajes, primera/última salida
   - Tabla de horarios (llegada/salida)
   - Botón "Ver ruta completa" → abre panel de ruta

### 🚌 Explorador de líneas (novedad v2)

Pestaña "Líneas" en el sidebar:

- Lista todas las rutas cargadas ordenadas
- Búsqueda por nombre o número
- Click en cualquier ruta → panel de detalle

---

## 🎨 Diseño

- **Design System:** Kaizen v4.0 (corporativo Ineco)
- **Colores principales:** Azul #1A4488, Rojo #CB1823
- **Tipografía:** Inter (sistem fallback)
- **Responsive:** adaptable a móvil (column layout)
- **Animaciones:** transiciones suaves (150ms ease)

### Colores por modo de transporte

| Modo | Color |
|---|---|
| 🚌 Autobús | Azul #2563eb |
| 🚇 Metro / Subterráneo | Rojo #dc2626 |
| 🚃 Tranvía | Púrpura #7c3aed |
| 🚆 Ferrocarril | Verde #16a34a |
| 🚡 Teleférico | Violeta #a855f7 |
| 🚤 Barco | Cyan #0891b2 |
| 🚋 Tren ligero | Teal #0d9488 |

---

## 📁 Estructura del proyecto

```
GTFSSpain-v2/
├── README.md              ← Este informe
├── iniciar.bat            ← Launcher Windows
├── cron-update.sh         ← Script de actualización NAP
├── descargar-nap.py       ← Descargador de datasets del NAP
├── data/                  ← ZIPs GTFS (symlink al v1)
└── visor/
    ├── index.html         ← Visor completo (autocontenido)
    ├── server.py          ← Servidor HTTP mínimo
    └── list-zips.py       ← Listador de ZIPs disponibles
```

---

## 🔧 Tecnologías

- **Leaflet 1.9.4** — Mapas interactivos (CDN)
- **JSZip 3.10.1** — Descompresión ZIP en navegador (inline)
- **Nominatim** — Geocodificación OpenStreetMap
- **IGN WMTS** — Basemaps del Instituto Geográfico Nacional
- **Vanilla JS** — Sin frameworks, 100% navegador
- **Kaizen CSS** — Design System corporativo

---

## ⚠️ Pitfalls conocidos

1. **stop_times masivo** — Se limita a 150.000 registros por dataset para no bloquear el navegador
2. **localStorage** — Datos grandes (>5MB) pueden exceder el límite; se trabaja en memoria
3. **Nominatim rate limit** — 1 req/segundo; se usa debounce de 800ms
4. **CORS en descargas** — La mayoría de feeds GTFS no permiten CORS; se usa el servidor como proxy
5. **Embebido JSZip inline** — Nunca embeber como string; debe ser `<script>` independiente

---

## 📈 Métricas del v2

| Métrica | Valor |
|---|---|
| Líneas de código | ~920 (HTML + CSS + JS) |
| Tamaño total | 147 KB (HTML autocontenido) |
| JSZip inline | 97 KB |
| CSS | ~14 KB |
| JavaScript propio | ~35 KB |
| Funciones JS | 31 |
| Datasets soportados | 30 max |

---

## 🔗 Relación con otros proyectos

- **[GTFSSpain v1](https://github.com/Ntizar/GTFSSpain)** — Versión original (sin click en líneas)
- **[GBFSSpain](https://github.com/Ntizar/GBFSSpain)** — Visor de bicicletas compartidas (68 sistemas)
- **[ISOTime](https://github.com/Ntizar/ISOTime)** — Isócronas de movilidad en España
- **[TimeIneco](https://timeineco-ntizar-ntizar.apps.nan.builders/)** — Dashboard de movilidad laboral

---

## 👤 Autor

**David Antizar** · [github.com/Ntizar](https://github.com/Ntizar)

Hecho con ❤️ por David Antizar

---

*Última actualización: Julio 2026*

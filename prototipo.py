import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from openai import OpenAI
from supabase import create_client
import json
import re
import os
import datetime

# =============================================================================
# 1. CONFIGURACIÓN INICIAL DE LA PÁGINA
# =============================================================================
st.set_page_config(
    page_title="Divvy Analytics",
    page_icon="🚲",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# =============================================================================
# 2. SISTEMA DE DISEÑO Y CSS (Estética Premium Divvy/Lyft)
# =============================================================================
DIVVY_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

/* ── Base ── */
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}
.stApp {
    background: #0c0e14;
    color: #e8eaf0;
}

/* ── Header bar ── */
.divvy-header {
    background: linear-gradient(135deg, #141820 0%, #1a1f2e 100%);
    border-bottom: 2px solid #00bcd4;
    padding: 14px 32px;
    display: flex;
    align-items: center;
    gap: 16px;
    margin: -1rem -1rem 2rem -1rem;
    box-shadow: 0 4px 24px rgba(0,188,212,0.15);
}
.divvy-logo-text {
    font-size: 28px;
    font-weight: 800;
    letter-spacing: -1px;
    color: #ffffff;
}
.divvy-logo-text span {
    color: #00bcd4;
}
.divvy-subtitle {
    font-size: 13px;
    color: #8892a4;
    margin-top: 2px;
    font-weight: 400;
    letter-spacing: 0.3px;
}
.divvy-badge {
    background: linear-gradient(135deg, #00bcd4, #0097a7);
    color: white;
    font-size: 11px;
    font-weight: 600;
    padding: 3px 10px;
    border-radius: 20px;
    letter-spacing: 0.5px;
    margin-left: auto;
}

/* ── Chat messages ── */
.stChatMessage {
    background: #141820 !important;
    border: 1px solid #1e2535 !important;
    border-radius: 12px !important;
    margin-bottom: 12px !important;
}
[data-testid="stChatMessageContent"] {
    color: #e8eaf0 !important;
}

/* ── Chat input ── */
.stChatInputContainer {
    background: #141820 !important;
    border: 1px solid #1e2535 !important;
    border-radius: 12px !important;
}
.stChatInput textarea {
    background: transparent !important;
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
}

/* ── Buttons ── */
.stButton > button {
    background: linear-gradient(135deg, rgba(0,188,212,0.12), rgba(0,151,167,0.08));
    color: #e8eaf0;
    border: 1px solid rgba(0,188,212,0.25);
    border-radius: 16px;
    font-weight: 500;
    padding: 10px 20px;
    transition: all 0.25s ease;
}
.stButton > button:hover {
    transform: scale(1.03);
    box-shadow: 0 8px 24px rgba(0,188,212,0.25);
    background: linear-gradient(135deg, rgba(0,188,212,0.22), rgba(0,151,167,0.16)) !important;
    border-color: #00bcd4 !important;
    color: #ffffff !important;
}

/* ── Suggested Chips (Mobile) ── */
.stButton > button[key*="chip"] {
    font-size: 13px !important;
    padding: 12px !important;
    min-height: 60px !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    line-height: 1.2 !important;
    background: rgba(0, 188, 212, 0.1) !important;
    border: 1px solid #00bcd4 !important;
}

/* ── Text input (password) ── */
.stTextInput input {
    background: #141820 !important;
    border: 1px solid #1e2535 !important;
    border-radius: 10px !important;
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
}

/* ── Info boxes ── */
.info-chip {
    display: inline-block;
    background: rgba(0,188,212,0.12);
    border: 1px solid rgba(0,188,212,0.3);
    color: #00bcd4;
    font-size: 12px;
    font-weight: 500;
    padding: 4px 12px;
    border-radius: 20px;
}
.section-title {
    font-size: 22px;
    font-weight: 700;
    color: #ffffff;
    margin-bottom: 6px;
}
.section-sub {
    font-size: 14px;
    color: #8892a4;
    margin-bottom: 24px;
}

/* ── Mobile Optimization ── */
@media (max-width: 640px) {
    .divvy-header {
        padding: 12px 20px;
    }
    .divvy-logo-text {
        font-size: 24px;
    }
    .divvy-badge {
        display: none;
    }
    .section-title {
        font-size: 18px;
    }
    [data-testid="column"] {
        width: 100% !important;
        flex: 1 1 100% !important;
    }
    /* Fix para entrada de texto en móvil */
    .stChatInputContainer, .stChatInput textarea, [data-testid="stChatInput"] {
        background-color: #141820 !important;
    }
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: #0c0e14; }
::-webkit-scrollbar-thumb { background: #00bcd4; border-radius: 3px; }

/* ── Login animado ── */
@keyframes fadeSlideUp {
    from { opacity: 0; transform: translateY(30px); }
    to   { opacity: 1; transform: translateY(0); }
}
.login-wrapper {
    max-width: 560px;
    margin: 10vh auto;
    text-align: center;
}
.login-brand {
    font-size: 42px;
    font-weight: 900;
    letter-spacing: -2px;
    color: #ffffff;
    margin-bottom: 4px;
    animation: fadeSlideUp 0.5s ease both;
}
.login-brand span { color: #00bcd4; }
.login-tagline {
    font-size: 13px;
    color: #8892a4;
    margin-bottom: 40px;
    animation: fadeSlideUp 0.5s ease 0.1s both;
}
.role-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 20px;
    margin-bottom: 32px;
    animation: fadeSlideUp 0.5s ease 0.2s both;
}
.role-card {
    background: #141820;
    border: 1px solid #1e2535;
    border-radius: 20px;
    padding: 32px 24px;
    cursor: pointer;
    transition: all 0.25s ease;
    text-align: center;
}
.role-card:hover {
    transform: scale(1.05);
    border-color: #00bcd4;
    box-shadow: 0 8px 32px rgba(0,188,212,0.2);
    background: rgba(0,188,212,0.06);
}
.role-card.selected {
    border-color: #00bcd4 !important;
    background: rgba(0,188,212,0.12) !important;
    transform: scale(1.04) !important;
    box-shadow: 0 8px 32px rgba(0,188,212,0.25) !important;
}
.role-icon {
    font-size: 36px;
    margin-bottom: 12px;
}
.role-title {
    font-size: 16px;
    font-weight: 700;
    color: #ffffff;
    margin-bottom: 6px;
}
.role-desc {
    font-size: 12px;
    color: #8892a4;
    line-height: 1.5;
}
.login-form-area {
    animation: fadeSlideUp 0.4s ease both;
    background: #141820;
    border: 1px solid #1e2535;
    border-radius: 16px;
    padding: 24px;
}
/* Botón de acción principal */
div[data-testid="stButton"] button[kind="primary"],
.stButton > button[data-testid="baseButton-secondary"]:last-of-type {
    background: linear-gradient(135deg, #00bcd4, #0097a7) !important;
    color: white !important;
    border: none !important;
}
</style>
"""

st.markdown(DIVVY_CSS, unsafe_allow_html=True)

# =============================================================================
# 3. CONSTANTES Y RUTAS DE ARCHIVOS
# =============================================================================
MODEL_NAME = "gpt-4.1-mini"

DATA_DIR = os.path.dirname(os.path.abspath(__file__))

TEST_CASES_FILE = os.path.join(DATA_DIR, "test_cases.txt")

def load_test_cases() -> str:
    try:
        with open(TEST_CASES_FILE, "r", encoding="utf-8") as f:
            return f.read()
    except Exception:
        return ""

def get_time_slot(dt) -> str:
    """Traduce la hora en franjas horarias compatibles con el histórico."""
    if dt is None: return "Sin definir"
    hour = dt.hour
    if 0 <= hour < 6: return "Madrugada"
    elif 6 <= hour < 12: return "Mañana"
    elif 12 <= hour < 18: return "Tarde"
    else: return "Noche"

TEST_CASES_CONTEXT = load_test_cases()

# =============================================================================
# 4. CONFIGURACIÓN DEL ASISTENTE (System Prompt)
# =============================================================================
SYSTEM_PROMPT_TEMPLATE = """
Eres un asistente analítico experto en operaciones de Divvy, el sistema de bicicletas compartidas de Chicago operado por Lyft.

## Contexto del Problema y Usuario

### Problema que Resolvemos
Divvy opera un sistema de estaciones fijas. Los usuarios deciden dónde dejan las bicicletas, lo que genera un desequilibrio constante: algunas estaciones se llenan (no hay docks para devolver) y otras se vacían (no hay bicis para alquilar). Este desequilibrio es estructural y requiere redistribución manual continua por parte de equipos de campo con camiones.

### A quién Servimos
Tu usuario es un **OPERATIVO DE REBALANCEO** — una persona que conduce un camión con bicicletas y las redistribuye entre estaciones. NO es un usuario final que quiere alquilar una bici.

El operativo necesita saber:
- Dónde **DEJAR** bicis que lleva en el camión (busca estaciones con docks libres)
- Dónde **RECOGER** bicis para llevar a estaciones vacías (busca estaciones con exceso de bicis)
- Qué estaciones están en estado crítico (a punto de vaciarse o llenarse)
- Cómo priorizar su ruta cuando tiene varias paradas pendientes

> [!IMPORTANT]
> NUNCA asumas que el usuario quiere alquilar una bici o planificar una ruta personal. Toda pregunta debe interpretarse desde la perspectiva operativa de redistribución.

- **Dejar bicis** = descargar bicicletas del camión a una estación.
- **Recoger bicis** = cargar bicicletas de una estación al camión.
- **Tengo X bicis** = lleva X bicicletas en el camión para redistribuir.

## Datos Disponibles

Tienes acceso a un DataFrame de pandas llamado `df_merged` con información en tiempo real de las estaciones.

## Columnas Disponibles en `df_merged`

### Datos de Capacidad
| Columna | Tipo | Descripción |
|---|---|---|
| `station_id` | str | Identificador único UUID de la estación |
| `name` | str | Nombre completo de la estación (ej: {name_example}) |
| `short_name` | str | Código corto (ej: CHI00384) |
| `capacity` | int | Número total de docks (rango: {cap_min} - {cap_max}) |
| `lat` | float | Latitud geográfica |
| `lon` | float | Longitud geográfica |

### Estado Actual
| Columna | Tipo | Descripción |
|---|---|---|
| `num_bikes_available` | int | Bicicletas totales disponibles ahora |
| `num_ebikes_available` | int | Bicicletas eléctricas disponibles ahora |
| `num_classic_bikes` | int | Bicicletas clásicas (= bikes_available - ebikes_available) |
| `num_docks_available` | int | Amarres libres disponibles ahora |
| `num_bikes_disabled` | int | Bicicletas no operativas |
| `num_docks_disabled` | int | Docks no operativos |
| `is_returning` | int | 1 si acepta devoluciones, 0 si no |
| `docks_used` | int | Docks ocupados (= capacity - docks_available) |
| `occupancy_pct` | float | % de ocupación (= (capacity - docks_available) / capacity * 100) |

## Datos del Sistema

| Métrica | Valor |
|---|---|
| Total de estaciones | {total_stations} |
| Capacidad total | {total_capacity} docks |
| Bicicletas disponibles | {total_bikes} |
| E-bikes disponibles | {total_ebikes} |
| Rango de ocupación | {occ_min:.1f}% - {occ_max:.1f}% |
| Estaciones críticas (>85%) | {high_occ_count} |
| Estaciones críticas (<15%) | {low_occ_count} |
| Momento de consulta | {current_dt} |
| Franja horaria actual | {current_slot} |

## Geoprocesamiento (Distancias y Ubicaciones)

- Tienes acceso a un DataFrame llamado `df_distances` con columnas: `origin_id`, `destination_id`, `distance_km`.
- Úsalo para encontrar estaciones cercanas filtrando siempre `distance_km > 0`.
- **Lugares de Referencia**: Cuando el usuario pregunte por puntos de interés (Millennium Park, etc.), usa sus coordenadas. NO busques el nombre del lugar en `df_merged['name']`.

### Coordenadas de Referencia
| Lugar | Coordenadas (Lat, Lon) |
|---|---|
| Millennium Park | (41.8827, -87.6226) |
| Navy Pier | (41.8917, -87.6043) |
| Union Station | (41.8787, -87.6403) |
| Willis Tower | (41.8789, -87.6359) |
| The Bean (Cloud Gate) | (41.8826, -87.6233) |
| Art Institute | (41.8796, -87.6237) |
| Soldier Field | (41.8623, -87.6167) |
| Museum Campus | (41.8665, -87.6168) |
| Wrigley Field | (41.9484, -87.6553) |
| University of Chicago | (41.7886, -87.5987) |
| Lincoln Park Zoo | (41.9211, -87.6340) |
| O'Hare Airport | (41.9742, -87.9073) |
| Midway Airport | (41.7868, -87.7522) |
| McCormick Place | (41.8512, -87.6154) |
| United Center | (41.8807, -87.6742) |

### Ejemplo de Cálculo de Proximidad
```python
ref_lat, ref_lon = 41.8827, -87.6226
df_merged['dist_temp'] = np.sqrt((df_merged['lat'] - ref_lat)**2 + (df_merged['lon'] - ref_lon)**2)
closest = df_merged.loc[df_merged['dist_temp'].idxmin()]
resultado = f"{closest['name']} ({closest['short_name']})"
```

## Datos Históricos (Contexto Operativo)

Usa estos DataFrames adicionales para enriquecer tus recomendaciones:

| DataFrame | Propósito |
|---|---|
| `df_historico` | Patrón por estación: `dia_de_la_semana`, `franja_horaria`, `de_salidas`, `de_llegadas`, `balance_neto`. |
| `df_clima` | Condiciones meteorológicas actuales para entender el contexto ambiental. |
| `df_eventos` | Calendario de eventos para anticipar picos de demanda. |

## Reglas de Decisión

Sigue esta prioridad estricta:
1. **Estatus Actual**: Prioridad absoluta (`df_merged`).
2. **Datos Históricos**: Valida si la tendencia (`balance_neto`) apoya la elección.
3. **Proximidad**: Busca siempre las estaciones más cercanas.
4. **Equilibrio**: Reparte unidades para equilibrar la ocupación.

## Instrucciones Críticas

1. Responde SIEMPRE con un JSON válido y NADA MÁS.
2. **Formato Obligatorio**:
```json
{
  "tipo": "grafico" | "texto_analitico" | "fuera_de_alcance",
  "codigo": "código python...",
  "interpretacion": "análisis en español..."
}
```

## Reglas para el Código

- Acceso a: `df_merged`, `df_distances`, `pd`, `px`, `go`, `np`, `haversine`, `datetime`, `timedelta`.
- **NUNCA** uses `import` en el código generado.
- **Gráficos**: Guarda el resultado en la variable `fig` (usa Plotly con `template='plotly_dark'`).
- **Análisis**: Guarda el resultado en la variable `resultado`.
- **Colores**: Usa `#00bcd4` (principal) y `#0097a7` (secundario).
- **Strings**: Usa comillas simples `'string'` dentro del código para no romper el JSON.
- **Seguridad**: Verifica `if not df.empty` antes de usar `.iloc[0]`.

## Búsqueda Robusta de Estaciones

Los operativos escriben con errores. Usa siempre este patrón de búsqueda flexible:

```python
search_terms = 'LaSalle Washington'.lower().split()
mask = pd.Series([True] * len(df_merged))
for term in search_terms:
    mask = mask & df_merged['name'].str.lower().str.contains(term, na=False)
matches = df_merged[mask]
```

## Contexto Operativo

- **Umbral Crítico**: <15% de capacidad en bicis (riesgo de vaciarse) o <15% en docks (riesgo de llenarse).
- **Eventos**: Estadios y centros de interés alteran drásticamente la demanda.

## Guardrails

- Fuera de alcance: Temas no relacionados con Divvy Chicago.
- Usuarios finales: Si preguntan por tarifas o paseos, indica que es una herramienta para operativos.
- No inventes datos ni estaciones que no existan en los DataFrames.

## Formato Obligatorio de Datos por Estación

Cada vez que menciones una estación, incluye:
1. Nombre
2. Docks libres
3. Capacidad total
4. % de ocupación

**Estándar**: `[Nombre] — [X] docks libres de [Y] (ocupación: [Z]%)`
**Con distancia**: `[Nombre] — [X] docks libres de [Y] (ocupación: [Z]%) — a [D] metros`

## Reglas para la Interpretación

- Máximo 3 frases en español.
- **NUNCA** uses `{}` o variables en el texto.
- Aporta insights operativos (estaciones críticas, tendencias).
- Menciona siempre la **franja horaria actual**.

## Reglas para Respuestas Operativas

1. **Interpreta todo como operativo**: "¿Dónde hay bicis?" significa buscar exceso para recoger.
2. **Esquema de respuesta**:
   - Responde con datos concretos (sin repetirlos si ya están en el resultado).
   - Aconseja una acción inmediata.
   - Ofrece al menos 2-3 opciones de estaciones.
   - Usa lenguaje directo: "mueve X bicis", "prioriza Y".

## Ejemplos de Respuestas Ideales

{test_cases}
"""

# =============================================================================
# 5. MOTOR DE DATOS (Carga y Procesamiento)
# =============================================================================
@st.cache_resource
def get_supabase_client():
    return create_client(
        st.secrets["SUPABASE_URL"],
        st.secrets["SUPABASE_KEY"]
    )

@st.cache_data(ttl=300)
def load_data():
    supabase = get_supabase_client()

    df_estaciones = pd.DataFrame(
        supabase.table("estaciones").select("*").execute().data
    )
    df_status = pd.DataFrame(
        supabase.table("status_estaciones").select("*").execute().data
    )
    df_merged = pd.merge(
        df_status,
        df_estaciones[["station_id", "name", "lat", "lon"]],
        on="station_id",
        how="inner"
    )
    df_merged["num_classic_bikes"] = (
        df_merged["num_bikes_available"] - df_merged["num_ebikes_available"]
    ).clip(lower=0)
    df_merged["docks_used"] = (
        df_merged["capacity"] - df_merged["num_docks_available"]
    ).clip(lower=0)
    df_merged["occupancy_pct"] = df_merged["pct_ocupacion"]

    df_distances = pd.DataFrame(
        supabase.table("distancias").select("*").execute().data
    )
    df_historico = pd.DataFrame(
        supabase.table("historico").select("*").execute().data
    )
    df_historico = df_historico.rename(columns={
        "dia_semana":           "dia_de_la_semana",
        "salidas":              "de_salidas",
        "llegadas":             "de_llegadas",
        "variabilidad_balance": "variabilidad_balance_neto",
        "evento_soldier_field": "evento"
    })

    df_clima   = pd.DataFrame()
    df_eventos = pd.DataFrame()

    return df_merged, df_distances, df_historico, df_clima, df_eventos


def build_system_prompt(df_merged: pd.DataFrame, dt: datetime.datetime = None) -> str:
    """Inyecta métricas reales del dataset en el System Prompt pulsando siempre el template completo."""
    
    # Valores por defecto por si el DataFrame está vacío o fallan los cálculos
    metrics = {
        "name_example": "Millennium Park",
        "cap_min": 0, "cap_max": 0, "total_stations": 0, "total_capacity": 0,
        "total_bikes": 0, "total_ebikes": 0, "occ_min": 0.0, "occ_max": 0.0,
        "high_occ_count": 0, "low_occ_count": 0,
        "test_cases": TEST_CASES_CONTEXT,
        "current_dt": dt.strftime("%Y-%m-%d %H:%M:%S") if dt else "N/A",
        "current_slot": get_time_slot(dt)
    }

    if not df_merged.empty:
        try:
            metrics["name_example"]   = str(df_merged["name"].iloc[0]) if "name" in df_merged.columns else "Millennium Park"
            metrics["cap_min"]        = int(df_merged["capacity"].min()) if "capacity" in df_merged.columns else 0
            metrics["cap_max"]        = int(df_merged["capacity"].max()) if "capacity" in df_merged.columns else 0
            metrics["total_stations"] = len(df_merged)
            metrics["total_capacity"] = int(df_merged["capacity"].sum()) if "capacity" in df_merged.columns else 0
            metrics["total_bikes"]    = int(df_merged["num_bikes_available"].sum()) if "num_bikes_available" in df_merged.columns else 0
            metrics["total_ebikes"]   = int(df_merged["num_ebikes_available"].sum()) if "num_ebikes_available" in df_merged.columns else 0
            metrics["occ_min"]        = float(df_merged["occupancy_pct"].min()) if "occupancy_pct" in df_merged.columns else 0.0
            metrics["occ_max"]        = float(df_merged["occupancy_pct"].max()) if "occupancy_pct" in df_merged.columns else 0.0
            metrics["high_occ_count"] = int((df_merged["occupancy_pct"] > 85).sum()) if "occupancy_pct" in df_merged.columns else 0
            metrics["low_occ_count"]  = int((df_merged["occupancy_pct"] < 15).sum()) if "occupancy_pct" in df_merged.columns else 0
        except Exception:
            pass # Usar valores por defecto si algo falla en el cálculo puntual

    # SIEMPRE devolvemos el template completo para no perder las instrucciones JSON
    return SYSTEM_PROMPT_TEMPLATE.format(**metrics)


# =============================================================================
# 6. INTEGRACIÓN CON OpenAI (Generación de Código)
# =============================================================================
def get_openai_response(user_msg: str, system_prompt: str, chat_history: list = []) -> str:
    """Envía la pregunta al modelo GPT con historial de conversación y devuelve el texto de respuesta."""
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

    # Construir los mensajes incluyendo el historial previo
    messages = [{"role": "system", "content": system_prompt}]
    
    # Añadir historial (máximo últimos 6 mensajes para no inflar el contexto)
    for msg in chat_history[-6:]:
        if msg.get("role") == "user" and msg.get("content"):
            messages.append({
                "role": "user",
                "content": msg["content"]
            })
        elif msg.get("role") == "assistant" and msg.get("content"):
            # Limpiar el contenido del asistente para que no confunda el formato JSON
            content = msg["content"].replace("💡 ", "").strip()
            if content and len(content) < 300:  # Solo mensajes cortos de interpretacion
                messages.append({
                    "role": "assistant",
                    "content": content
                })
    
    # Añadir el mensaje actual
    messages.append({"role": "user", "content": user_msg})

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=messages,
        temperature=0.2,
    )
    return response.choices[0].message.content


# =============================================================================
# 7. UTILIDADES DE PARSING Y EJECUCIÓN
# =============================================================================
def parse_response(raw: str) -> dict:
    """Limpia backticks y parsea el JSON devuelto por el LLM con múltiples estrategias de rescate."""
    cleaned = raw.strip()
    
    # 1. Limpiar bloques de código markdown
    cleaned = re.sub(r"^```(?:json|python)?\s*", "", cleaned)
    cleaned = re.sub(r"\s*```$", "", cleaned)
    cleaned = cleaned.strip()
    
    # 2. Intento de parseo JSON estándar
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass
        
    # 3. Rescate: Extracción por regex independiente de cada campo
    # Buscamos "campo": "valor" con comillas dobles o simples
    def extract(field):
        # Busca el campo y captura el contenido entre la siguiente pareja de comillas
        pattern = rf'"{field}"\s*:\s*"(.*?)"(?:\s*[,}}])'
        match = re.search(pattern, cleaned, re.DOTALL)
        if not match:
            # Reintento con comillas simples si fallan las dobles
            pattern = rf"'{field}'\s*:\s*'(.*?)'(?:\s*[,}}])"
            match = re.search(pattern, cleaned, re.DOTALL)
        
        if match:
            val = match.group(1)
            # Limpiar escapes comunes de JSON si es necesario
            return val.replace('\\"', '"').replace('\\n', '\n').strip()
        return None

    tipo   = extract("tipo")
    interp = extract("interpretacion")
    
    # Para el código, intentamos capturar todo lo que hay entre "codigo": " y el final o el siguiente campo
    codigo_match = re.search(r'"codigo"\s*:\s*"(.*?)"\s*,\s*"interpretacion"', cleaned, re.DOTALL)
    if not codigo_match:
        codigo_match = re.search(r'"codigo"\s*:\s*"(.*)"', cleaned, re.DOTALL)
    
    codigo = codigo_match.group(1).replace('\\"', '"').replace('\\n', '\n') if codigo_match else ""

    if tipo or interp:
        return {
            "tipo"          : tipo if tipo else "texto_analitico",
            "codigo"        : codigo,
            "interpretacion": interp if interp else "No se pudo extraer la interpretación, pero se detectó el tipo.",
        }

    # 4. Último recurso: devolver como fuera de alcance si no se entiende nada
    return {
        "tipo"          : "fuera_de_alcance",
        "codigo"        : "",
        "interpretacion": "No se pudo interpretar la respuesta del modelo.",
        "raw_debug"     : raw # Guardamos el original para debug
    }


# ============================================================
# EJECUCIÓN DEL CÓDIGO GENERADO
# ============================================================
def execute_code(code: str, df_merged: pd.DataFrame, df_distances: pd.DataFrame, df_historico: pd.DataFrame, df_clima: pd.DataFrame, df_eventos: pd.DataFrame):
    """
    Ejecuta el código generado por el LLM en un contexto controlado.
    Devuelve (fig, resultado) - cualquiera puede ser None.
    """
    # Limpiar imports del código generado para evitar conflictos
    code = re.sub(r'^\s*import\s+\w+\s*$', '', code, flags=re.MULTILINE)
    code = re.sub(r'^\s*from\s+\w+\s+import\s+.*$', '', code, flags=re.MULTILINE)
    code = re.sub(r'\\\s*\n', '\n', code)

    def haversine(lat1, lon1, lat2, lon2):
        """Función auxiliar para calcular distancias entre coordenadas GPS."""
        R = 6371  # Radio de la Tierra en km
        p1, p2 = np.radians(lat1), np.radians(lat2)
        dp = np.radians(lat2 - lat1)
        dl = np.radians(lon2 - lon1)
        a = np.sin(dp/2)**2 + np.cos(p1) * np.cos(p2) * np.sin(dl/2)**2
        return 2 * R * np.arcsin(np.sqrt(a))
    
    # Adaptador para evitar errores de datetime en el LLM (maneja tanto datetime.now() como datetime.datetime.now())
    class SmartDatetime:
        def __call__(self, *args, **kwargs):
            return datetime.datetime(*args, **kwargs)
        def __getattr__(self, name): 
            return getattr(datetime.datetime, name)
        @property
        def datetime(self): return datetime.datetime
        @property
        def timedelta(self): return datetime.timedelta

    # Contexto global para la ejecución del código generado
    local_vars = {
        "df_merged"    : df_merged,
        "df_distances" : df_distances,
        "pd"           : pd,
        "px"           : px,
        "go"           : go,
        "np"           : np,
        "json"         : json,
        "datetime"     : SmartDatetime(),
        "timedelta"    : datetime.timedelta,
        "haversine"    : haversine,
        "df_historico" : df_historico,
        "df_clima"     : df_clima,
        "df_eventos"   : df_eventos,
    }
    exec(code, {}, local_vars)
    fig       = local_vars.get("fig", None)
    resultado = local_vars.get("resultado", None)
    return fig, resultado


# =============================================================================
# 8. GESTIÓN DE SEGURIDAD (Login)
# =============================================================================
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    if "login_role" not in st.session_state:
        st.session_state.login_role = None

    role = st.session_state.login_role

    st.markdown("""
    <div class="login-wrapper">
        <div class="login-brand">DIV<span>VY</span></div>
        <div class="login-tagline">Operations Intelligence Platform · Chicago, IL</div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2.4, 1])
    with col2:
        # ── Cards de selección de rol ──
        c1, c2 = st.columns(2)
        with c1:
            operario_selected = "selected" if role == "operario" else ""
            if st.button("🚛\n\n**Operario de Campo**\n\nAccede al asistente de rebalanceo en tiempo real",
                        key="btn_operario",
                        use_container_width=True):
                st.session_state.login_role = "operario"
                st.rerun()
            st.markdown(f"""
            <style>
            div[data-testid="stButton"] button[kind="secondary"]:first-of-type {{
                min-height: 140px;
                border-radius: 20px;
                font-size: 13px;
                line-height: 1.5;
                {'border: 1px solid #00bcd4 !important; background: rgba(0,188,212,0.12) !important;' if role == 'operario' else ''}
            }}
            </style>
            """, unsafe_allow_html=True)

        with c2:
            if st.button("📊\n\n**Equipo de Análisis**\n\nPanel de métricas y datos históricos del sistema",
                        key="btn_analisis",
                        use_container_width=True):
                st.session_state.login_role = "analisis"
                st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)

        # ── Formulario según rol seleccionado ──
        if role == "operario":
            pwd = st.text_input("", type="password", placeholder="🔐 Contraseña de acceso")
            if st.button("Entrar al Asistente →", use_container_width=True, key="btn_entrar"):
                if pwd == st.secrets["PASSWORD"]:
                    st.session_state.authenticated = True
                    st.session_state.user_role = "operario"
                    st.rerun()
                else:
                    st.error("❌ Contraseña incorrecta.")

        elif role == "analisis":
            st.markdown("""
            <div style="
                background: rgba(0,188,212,0.06);
                border: 1px solid rgba(0,188,212,0.2);
                border-radius: 16px;
                padding: 28px 24px;
                text-align: center;
                animation: fadeSlideUp 0.3s ease both;
            ">
                <div style="font-size:28px; margin-bottom:12px;">🔒</div>
                <div style="color:#ffffff; font-weight:600; font-size:15px; margin-bottom:8px;">
                    Acceso restringido
                </div>
                <div style="color:#8892a4; font-size:13px; line-height:1.6;">
                    El panel de análisis estará disponible próximamente.<br>
                    <span style="color:#00bcd4;">Contacta con tu supervisor para más información.</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

        else:
            st.markdown("""
            <div style="text-align:center; color:#8892a4; font-size:13px; padding:16px;">
                ↑ Selecciona tu perfil para continuar
            </div>
            """, unsafe_allow_html=True)

    st.stop()


# =============================================================================
# 9. INTERFAZ DE USUARIO PRINCIPAL (Layout y Simulación)
# =============================================================================


# ── Cargar datos ──
with st.spinner("Sincronizando estaciones..."):
    df_merged, df_distances, df_historico, df_clima, df_eventos = load_data()

current_dt = datetime.datetime.now()

# ── Header (Renderizado después de obtener current_dt) ──
slot_emoji = {"Madrugada": "🌙", "Mañana": "🌅", "Tarde": "☀️", "Noche": "🌆"}
current_slot = get_time_slot(current_dt)
emoji = slot_emoji.get(current_slot, "⏱️")
dt_str = pd.to_datetime(current_dt).strftime("%a %d/%m · %H:%M") if current_dt else "N/A"

st.markdown(f"""
<div class="divvy-header">
    <div>
        <div class="divvy-logo-text">DIV<span>VY</span></div>
        <div class="divvy-subtitle">Analytics Dashboard - Chicago, IL</div>
    </div>
    <div style="margin-left:auto; display:flex; align-items:center; gap:12px;">
        <div style="text-align:right;">
            <div style="font-size:11px; color:#8892a4;">Último snapshot</div>
            <div style="font-size:13px; color:#00bcd4; font-weight:600;">{emoji} {dt_str} · {current_slot}</div>
        </div>
        <div class="divvy-badge">LIVE DATA</div>
    </div>
</div>
""", unsafe_allow_html=True)


# ── Generar Prompt Dinámico (Contexto temporal para LLM) ──
system_prompt = build_system_prompt(df_merged, current_dt)


# =============================================================================
# 10. ASISTENTE ANALÍTICO (Conversacional)
# =============================================================================
st.markdown('<p class="section-title">Asistente Analítico</p>', unsafe_allow_html=True)
st.markdown('<p class="section-sub">Haz cualquier pregunta sobre las estaciones de Divvy en Chicago.</p>', unsafe_allow_html=True)

# ── Inicialización de session_state ──
if "messages" not in st.session_state:
    st.session_state.messages = []
if "chip_fired" not in st.session_state:
    st.session_state.chip_fired = False
if "pending_question" not in st.session_state:
    st.session_state.pending_question = None

# ── Chips de preguntas sugeridas ──
suggested = [
    "La estación Millennium Park está casi llena, ¿dónde puedo dejar 2 bicis cerca?",
    "Está lloviendo, ¿qué estaciones cerca de oficinas se vaciarán antes?",
    "Tengo 12 bicis en el camión. ¿Dónde las puedo dejar cerca de Millennium Park?",
]
cols_chips = st.columns(len(suggested))
for i, q in enumerate(suggested):
    with cols_chips[i]:
        if st.button(q, key=f"chip_{i}", use_container_width=True):
            st.session_state.pending_question = q
            st.session_state.chip_fired = True

# ── Procesar chip (una sola vez) ──
if st.session_state.chip_fired and st.session_state.pending_question:
    st.session_state.chip_fired = False        # apagar ANTES de procesar
    user_input_chip = st.session_state.pending_question
    st.session_state.pending_question = None

    st.session_state.messages.append({"role": "user", "content": user_input_chip})

    with st.chat_message("assistant"):
        status_placeholder = st.empty()
        status_placeholder.markdown(
            "<div style='color:#00bcd4; font-size:13px; padding:4px 0;'>⏳ Analizando datos en tiempo real...</div>",
            unsafe_allow_html=True
        )
        with st.spinner("Consultando estaciones..."):
            try:
                raw = get_openai_response(user_input_chip, system_prompt, st.session_state.messages[:-1])
                parsed = parse_response(raw)
                tipo   = parsed.get("tipo", "")
                codigo = parsed.get("codigo", "")
                
                fig, resultado = None, None
                if tipo == "fuera_de_alcance":
                    interp = parsed.get("interpretacion", "Lo siento, no puedo responder a eso.")
                    st.session_state.messages.append({
                        "role"      : "assistant", 
                        "content"   : interp,
                        "raw_debug" : parsed.get("raw_debug")
                    })
                else:
                    if codigo.strip():
                        fig, resultado = execute_code(codigo, df_merged, df_distances, df_historico, df_clima, df_eventos)

                    # Segunda llamada: generar interpretación coherente con el resultado real
                    resultado_str = str(resultado) if resultado is not None else "Sin resultado numérico"
                    interp_prompt = f"""El usuario preguntó: "{user_input_chip}"
El código generó este resultado: {resultado_str}
Basándote ÚNICAMENTE en este resultado real, escribe una interpretación operativa en máximo 2 frases.
NO uses {{}}, NO contradigas el resultado. Si el resultado dice 6 docks, di 6 docks."""

                    INTERP_SYSTEM = f"""Eres un asistente operativo de Divvy. Responde solo con la interpretación, sin JSON.
Aquí tienes ejemplos del tono y formato esperado:
{TEST_CASES_CONTEXT}"""
                    interp = get_openai_response(interp_prompt, INTERP_SYSTEM)
                    
                    st.session_state.messages.append({
                        "role"      : "assistant",
                        "content"   : f"💡 {interp}",
                        "fig"       : fig,
                        "resultado" : resultado,
                        "code"      : codigo,
                        "raw_debug" : parsed.get("raw_debug"),
                    })
            except Exception as e:
                st.session_state.messages.append({"role": "assistant", "content": f"Error: {e}"})
        status_placeholder.empty()
    
    st.rerun()

# ── Renderizar historial ──
if not st.session_state.messages:
    st.markdown("""
    <div style="text-align:center; padding: 48px 20px 32px 20px;">
        <div style="font-size:52px; margin-bottom:16px;">🚲</div>
        <div style="font-size:20px; font-weight:700; color:#ffffff; margin-bottom:8px;">
            Asistente de Rebalanceo Divvy
        </div>
        <div style="font-size:14px; color:#8892a4; max-width:420px; margin:0 auto; line-height:1.6;">
            Pregúntame dónde dejar o recoger bicis, qué estaciones están en estado crítico,
            o cuáles necesitan reposición urgente.
        </div>
    </div>
    """, unsafe_allow_html=True)

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        if msg.get("fig"):
            st.plotly_chart(msg["fig"], use_container_width=True)
        if msg.get("resultado") is not None:
            res = msg["resultado"]
            if isinstance(res, pd.DataFrame):
                st.dataframe(res, use_container_width=True)
            else:
                st.info(f"**Resultado:** {res}")
        if msg.get("content"):
            st.markdown(msg["content"])
        if msg.get("code"):
            with st.expander("🔍 Ver código generado", expanded=False):
                st.code(msg["code"], language="python")
        if msg.get("raw_debug"):
            with st.expander("🛠️ Debug: Respuesta original del modelo", expanded=False):
                st.text(msg["raw_debug"])

# Input del usuario
if user_input := st.chat_input("¿Dónde dejo las bicis? ¿Qué estación necesita reposición?"):
    st.session_state.messages.append({"role": "user", "content": user_input})

    # Generar respuesta
    with st.chat_message("assistant"):
        status_placeholder = st.empty()
        status_placeholder.markdown(
            "<div style='color:#00bcd4; font-size:13px; padding:4px 0;'>⏳ Analizando datos en tiempo real...</div>",
            unsafe_allow_html=True
        )
        with st.spinner("Consultando estaciones..."):
            try:
                raw = get_openai_response(user_input, system_prompt, st.session_state.messages[:-1])
                parsed = parse_response(raw)
                tipo   = parsed.get("tipo", "")
                codigo = parsed.get("codigo", "")

                fig, resultado = None, None
                if tipo == "fuera_de_alcance":
                    interp = parsed.get("interpretacion", "Lo siento, no puedo responder a eso.")
                    st.session_state.messages.append({
                        "role"      : "assistant", 
                        "content"   : interp,
                        "raw_debug" : parsed.get("raw_debug")
                    })
                else:
                    if codigo.strip():
                        fig, resultado = execute_code(codigo, df_merged, df_distances, df_historico, df_clima, df_eventos)

                    # Segunda llamada: generar interpretación coherente con el resultado real
                    resultado_str = str(resultado) if resultado is not None else "Sin resultado numérico"
                    interp_prompt = f"""El usuario preguntó: "{user_input}"
El código generó este resultado: {resultado_str}
Basándote ÚNICAMENTE en este resultado real, escribe una interpretación operativa en máximo 2 frases.
NO uses {{}}, NO contradigas el resultado. Si el resultado dice 6 docks, di 6 docks."""

                    INTERP_SYSTEM = f"""Eres un asistente operativo de Divvy. Responde solo con la interpretación, sin JSON.
Aquí tienes ejemplos del tono y formato esperado:
{TEST_CASES_CONTEXT}"""
                    interp = get_openai_response(interp_prompt, INTERP_SYSTEM)

                    st.session_state.messages.append({
                        "role"      : "assistant",
                        "content"   : f"💡 {interp}",
                        "fig"       : fig,
                        "resultado" : resultado,
                        "code"      : codigo,
                        "raw_debug" : parsed.get("raw_debug"),
                    })
            except Exception as e:
                st.session_state.messages.append({"role": "assistant", "content": f"Error: {e}"})
        status_placeholder.empty()
    
    st.rerun()

# Botón limpiar historial
if st.session_state.messages:
    if st.button("🗑️ Limpiar conversación"):
        st.session_state.messages = []
        st.rerun()
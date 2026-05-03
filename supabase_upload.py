import pandas as pd
import numpy as np
import json
from sklearn.metrics.pairwise import haversine_distances
from supabase import create_client

SUPABASE_URL = "https://ceveyrwosyllqkndmaqw.supabase.co"
SUPABASE_KEY = "sb_publishable_XnEQY21u0TmH4wg5SPjHJQ_sSlzJ41X"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
print("✅ Conectado a Supabase")

# =============================================================================
# 1. ESTACIONES
# =============================================================================
print("\n📤 Subiendo estaciones...")
df_info = pd.read_excel("info_estaciones_filtrado.xlsx")
df_info.columns = ['station_id', 'name', 'lon', 'lat']
df_info['lon'] = df_info['lon'].astype(float)
df_info['lat'] = df_info['lat'].astype(float)
records = json.loads(df_info.to_json(orient='records'))
supabase.table("estaciones").upsert(records).execute()
print(f"   ✅ {len(df_info)} estaciones subidas")

# =============================================================================
# 2. STATUS ESTACIONES
# =============================================================================
print("\n📤 Subiendo status estaciones...")
df_status = pd.read_excel("status_record_filtrado_capacidad.xlsx",
                          sheet_name='status_record_filtrado_capacida')
df_status.columns = [
    'station_id', 'num_docks_disabled', 'num_docks_available',
    'num_bikes_available', 'num_ebikes_available', 'num_bikes_disabled',
    'is_returning', 'dia', 'franja', 'capacity', 'pct_ocupacion'
]
df_status['dia'] = pd.to_datetime(df_status['dia']).dt.strftime('%Y-%m-%d')
df_status = df_status.replace([np.inf, -np.inf], np.nan)
records = json.loads(df_status.to_json(orient='records'))

for i in range(0, len(records), 500):
    batch = records[i:i+500]
    supabase.table("status_estaciones").upsert(batch).execute()
    print(f"   ✅ {min(i+500, len(records))}/{len(records)} subidos")

# =============================================================================
# 3. HISTORICO
# =============================================================================
print("\n📤 Subiendo histórico...")
df_hist = pd.read_excel("Historico.xlsx",
                        sheet_name='balance_por_dia_franja_estacion')
df_hist.columns = [
    'fecha', 'dia_semana', 'franja_horaria', 'estacion',
    'salidas', 'llegadas', 'balance_neto', 'variabilidad_balance',
    'temp_media_c', 'estado_temperatura', 'precip_total_mm',
    'intensidad_lluvia', 'evento_soldier_field'
]
df_hist['fecha'] = pd.to_datetime(df_hist['fecha']).dt.strftime('%Y-%m-%d')
df_hist = df_hist.replace([np.inf, -np.inf], np.nan)
df_hist['evento_soldier_field'] = df_hist['evento_soldier_field'].fillna(False).astype(bool)
records = json.loads(df_hist.to_json(orient='records'))

for i in range(0, len(records), 200):
    batch = records[i:i+200]
    supabase.table("historico").upsert(batch).execute()
    print(f"   ✅ {min(i+200, len(records))}/{len(records)} subidos")

# =============================================================================
# 4. DISTANCIAS
# =============================================================================
print("\n📤 Subiendo matriz de distancias...")
coords = df_info[['lat', 'lon']].values
coords_rad = np.radians(coords)
matriz = haversine_distances(coords_rad) * 6371
station_ids = df_info['station_id'].values

rows = []
for i, origin in enumerate(station_ids):
    for j, destination in enumerate(station_ids):
        if origin != destination:
            rows.append({
                'origin_id': str(origin),
                'destination_id': str(destination),
                'distance_km': float(round(matriz[i][j], 2))
            })

df_dist = pd.DataFrame(rows)
records = json.loads(df_dist.to_json(orient='records'))

for i in range(0, len(records), 500):
    batch = records[i:i+500]
    supabase.table("distancias").upsert(batch).execute()
    print(f"   ✅ {min(i+500, len(records))}/{len(records)} subidos")

print("\n🎉 ¡Todo subido correctamente a Supabase!")
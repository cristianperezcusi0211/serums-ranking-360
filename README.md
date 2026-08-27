# SERUMS RANKING 360 — prototipo

## Ejecutar localmente
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
export ADMIN_PASSWORD='TU_CLAVE_SEGURA'  # Windows PowerShell: $env:ADMIN_PASSWORD='TU_CLAVE_SEGURA'
export SECRET_KEY='OTRA_CLAVE_LARGA_Y_ALEATORIA'
python app.py
```
Abre `http://127.0.0.1:5000`.

Panel: `/admin/login`.

## Importante
Antes de publicar, cambia `ADMIN_PASSWORD` y `SECRET_KEY`. Para producción se recomienda desplegar con HTTPS y mover los secretos a variables de entorno.

La app usa `ranking.json`, generado desde `Ranking_Consolidado_SERUMS_2026_II_Comparacion_Desplazamientos.xlsx`.

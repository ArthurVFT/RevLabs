# RevLabs

Simulador de tuning para Gran Turismo 7: catálogo de peças, ajustes por peça,
física determinística e comparação de voltas com telemetria real.

O repositório contém **apenas o site Django** e os dados necessários para
rodá-lo localmente ou fazer deploy.

---

## Stack

- Python 3.14 + Django 6
- SQLite em desenvolvimento / PostgreSQL em produção (`DATABASE_URL`)
- WhiteNoise para estáticos
- Selenium para testes de fluxo (CI)

---

## Estrutura

```
RevLabs/
├── project/                  # settings, urls, wsgi
├── revlabs/
│   ├── models.py             # Car, Track, CarPart, PartAdjustment, TelemetryLap
│   ├── views.py              # landing, seleção, dashboard, APIs
│   ├── telemetry_import.py   # validação + import JSON (única entrada)
│   ├── telemetry_profile.py  # perfil de pilotagem e impacto de peças
│   ├── data/
│   │   └── telemetry_bundle.json   # seed de voltas (formato v1)
│   ├── templates/
│   └── static/
├── import_telemetry.py       # CLI de importação
├── setup.py                  # bootstrap de clone novo
├── TELEMETRY_FORMAT.md       # especificação do JSON de telemetria
├── GUIDE.md                  # guia detalhado de uso local
└── build.sh                  # build de deploy (Render)
```

---

## Quick start (Windows)

```powershell
cd RevLabs
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt
copy .env.example .env
.venv\Scripts\python setup.py
.venv\Scripts\python manage.py runserver
```

Acesse <http://127.0.0.1:8000>.

### `.env` mínimo

```env
ENVIRONMENT=development
SECRET_KEY=django-insecure-local-dev-key
```

Em produção, use `ENVIRONMENT=production`, `SECRET_KEY` forte e `DATABASE_URL`.

---

## Setup manual

```powershell
.venv\Scripts\python manage.py migrate
.venv\Scripts\python populate_data.py
.venv\Scripts\python populateparts.py
.venv\Scripts\python populate_gt7_parts.py
.venv\Scripts\python populate_adjustments.py
.venv\Scripts\python import_telemetry.py
.venv\Scripts\python manage.py createsuperuser
.venv\Scripts\python manage.py runserver
```

> Atenção: `populate_data.py` e `populateparts.py` recriam o catálogo e
> **apagam** registros existentes (inclusive voltas de telemetria em cascata).
> Use-os apenas no bootstrap de um banco vazio.

---

## Telemetria

A telemetria é um JSON próprio do RevLabs. Especificação completa:
**[TELEMETRY_FORMAT.md](TELEMETRY_FORMAT.md)**.

```powershell
# Importa o seed embutido
python import_telemetry.py

# Importa um arquivo específico
python import_telemetry.py minha_telemetria.json

# Via Django
python manage.py import_telemetry minha_telemetria.json
```

Pela web: dashboard → **IMPORT TELEMETRY (.JSON)**.

Regras principais:

- `car_code` e `track_id` precisam existir em `Car` / `Track`;
- setores são recalculados a partir dos frames quando disponíveis;
- apenas as 10 voltas mais rápidas por carro + pista são mantidas;
- importações repetidas são ignoradas por `external_id`.

---

## Deploy (Render)

1. Configure as variáveis de ambiente:
   - `ENVIRONMENT=production`
   - `SECRET_KEY=<chave forte>`
   - `DATABASE_URL=<postgres>`
2. Build command:
   ```bash
   ./build.sh
   ```
3. Release/first-run (uma vez, no shell do Render):
   ```bash
   python setup.py
   ```
   Ou, se o banco já estiver populado:
   ```bash
   python manage.py migrate
   python import_telemetry.py
   ```

`build.sh` roda `collectstatic` e `migrate` a cada deploy.

---

## Testes

```powershell
.venv\Scripts\python manage.py check
.venv\Scripts\python manage.py test
```

Os testes de fluxo usam Selenium/Chrome headless.

---

## Documentação

- [GUIDE.md](GUIDE.md) — uso local, arquitetura e troubleshooting
- [TELEMETRY_FORMAT.md](TELEMETRY_FORMAT.md) — formato JSON de telemetria

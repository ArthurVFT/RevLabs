# RevLabs — Guia de uso local

Este guia cobre a instalação, execução, importação de telemetria e
manutenção do banco. O repositório é autossuficiente e não requer
ferramentas externas de captura.

---

## 1. Instalação

Requisitos: Python 3.14+ e (opcional) Chrome para os testes Selenium.

```powershell
cd RevLabs

python -m venv .venv
.venv\Scripts\pip install -r requirements.txt
copy .env.example .env

# Bootstrap completo (migrate + seed + telemetria)
.venv\Scripts\python setup.py
```

O `setup.py` executa:

1. `manage.py migrate`
2. `populate_data.py` — carros e pistas
3. `populateparts.py` — catálogo base de peças
4. `populate_gt7_parts.py` — peças GT7 extras
5. `populate_adjustments.py` — parâmetros ajustáveis
6. `import_telemetry.py` — seed `revlabs/data/telemetry_bundle.json`
7. criação opcional de superusuário

Depois:

```powershell
.venv\Scripts\python manage.py runserver
```

Site em <http://127.0.0.1:8000>. Admin em `/admin/`.

---

## 2. Estrutura do projeto

```
project/
  settings.py          # SQLite em dev, PostgreSQL em produção
  urls.py
revlabs/
  models.py            # Car, Track, CarPart, PartAdjustment, TelemetryLap
  views.py             # landing, seleção, dashboard, APIs
  telemetry_import.py  # validação + import do JSON
  telemetry_profile.py # perfil de pilotagem + impacto de peças
  data/telemetry_bundle.json
  templates/
  static/
import_telemetry.py    # CLI de import
setup.py               # bootstrap
TELEMETRY_FORMAT.md    # spec do JSON
```

---

## 3. Importação de telemetria

### Formato

O único formato aceito é o JSON do RevLabs, documentado em
[TELEMETRY_FORMAT.md](TELEMETRY_FORMAT.md). Exemplo mínimo:

```json
{
  "format": "revlabs.telemetry",
  "version": 1,
  "laps": [
    {
      "external_id": "session-1-lap-4",
      "car_code": 3485,
      "track_id": 152,
      "lap_number": 4,
      "lap_time_ms": 101041,
      "sector_1_ms": 29016,
      "sector_2_ms": 43616,
      "sector_3_ms": 28409
    }
  ]
}
```

### Caminhos de importação

```powershell
# Seed embutido
python import_telemetry.py

# Arquivo específico
python import_telemetry.py dados.json

# Django
python manage.py import_telemetry dados.json
```

Web: dashboard → **IMPORT TELEMETRY (.JSON)**.

### Regras

- `car_code` e `track_id` precisam existir no banco;
- voltas duplicadas (`external_id`) são ignoradas;
- mantém as 10 voltas mais rápidas por carro + pista;
- setores são recalculados quando há frames 3D suficientes.

---

## 4. Setores

Setores podem vir prontos no JSON. Se `frames` for enviado:

1. calcula-se a distância acumulada entre `(position_x, position_y, position_z)`;
2. descarta-se o cálculo se a distância for < 80% de `Track.length_km`;
3. acha-se os índices em 1/3 e 2/3 da distância;
4. usa-se o `ts` de cada fronteira;
5. normaliza-se para `sector_1 + sector_2 + sector_3 == lap_time_ms`.

O **Best Projected Lap** exibido no dashboard é a soma dos melhores setores
entre as voltas importadas — não é o melhor tempo bruto.

---

## 5. Adicionar carro ou pista

```powershell
.venv\Scripts\python manage.py shell
```

```python
from revlabs.models import Car, Track

Car.objects.create(
    slug_id='ferrari-f40',
    name='Ferrari F40',
    base_avg_speed_kmh=180,
    power_hp=478,
    weight_kg=1100,
    image_path='img/cars/ferrari-f40.png',
    car_code=1234,
)

Track.objects.create(
    slug_id='monza',
    name='Monza',
    length_km=5.793,
    speed_multiplier=1.05,
    image_path='img/layout/monza.png',
    bg_image_path='img/bg/monza.jpg',
    track_id=456,
)
```

O `car_code` e o `track_id` são os identificadores GT7 usados no JSON.

IDs atualmente configurados:

| Item | ID |
|---|---|
| Porsche 911 GT3 RS (992) | `car_code=3539` |
| Mercedes-AMG GT Black Series '20 | `car_code=3485` |
| Interlagos | `track_id=152` |

---

## 6. Comandos úteis

```powershell
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py migrate
python manage.py createsuperuser
python manage.py collectstatic --noinput
python manage.py test
```

---

## 7. Deploy

Variáveis de ambiente:

```env
ENVIRONMENT=production
SECRET_KEY=<chave forte>
DATABASE_URL=postgres://...
```

Build: `./build.sh` (collectstatic + migrate).

Primeira execução em banco vazio:

```bash
python setup.py
```

> `populate_data.py` apaga carros/pistas existentes (e voltas em cascata).
> Em banco já populado, rode apenas `migrate` e `import_telemetry.py`.

---

## 8. Troubleshooting

| Problema | Solução |
|---|---|
| Import encontra 0 voltas | Verifique `car_code` / `track_id` e se o carro/pista existem no banco |
| "Nenhuma volta" com JSON válido | Confira se `laps` não está vazio e se os IDs batem |
| Setores ausentes | Envie `sector_*_ms` ou frames com posição 3D suficientes |
| Lap time errado | `lap_time_ms` é a fonte oficial; setores são normalizados a ele |
| Estáticos não aparecem em produção | Rode `collectstatic`; WhiteNoise já está configurado |
| Erro de banco no deploy | Confira `DATABASE_URL` e `ENVIRONMENT=production` |

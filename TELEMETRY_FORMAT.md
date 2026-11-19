# RevLabs Telemetry JSON — Formato v1

Este é o **único** formato de telemetria aceito pelo RevLabs. O site importa
dados neste formato, sem banco externo, caminho fixo no disco ou schema de
terceiros.

Arquivo de seed versionado no repositório:

```
revlabs/data/telemetry_bundle.json
```

---

## Estrutura do documento

```json
{
  "format": "revlabs.telemetry",
  "version": 1,
  "source": "bundle",
  "generated_at": "2026-11-19T12:00:00Z",
  "laps": []
}
```

| Campo | Obrigatório | Tipo | Descrição |
|---|---|---|---|
| `format` | recomendado | string | Deve ser `revlabs.telemetry`. Ausente = modo legado. |
| `version` | recomendado | inteiro | Deve ser `1`. |
| `source` | opcional | string | Rótulo livre da origem do arquivo (ex.: `manual`, `bundle`). |
| `generated_at` | opcional | string | Data ISO-8601 de geração. |
| `laps` | **sim** | array | Lista de voltas. Pode ser vazia. |

Chaves desconhecidas no topo são ignoradas (compatibilidade futura).

---

## Objeto de volta (`laps[]`)

```json
{
  "external_id": "session-3-lap-55",
  "car_code": 3485,
  "track_id": 152,
  "lap_number": 1,
  "lap_time_ms": 101041,
  "session_notes": "Setup inicial",
  "sector_1_ms": 29016,
  "sector_2_ms": 43616,
  "sector_3_ms": 28409,
  "stats": {
    "max_speed_kmh": 307.2,
    "min_speed_kmh": 58.1,
    "avg_speed_kmh": 151.6,
    "avg_throttle_pct": 47.4,
    "avg_brake_pct": 16.1,
    "max_rpm": 8400,
    "total_frames": 0
  },
  "frames": []
}
```

| Campo | Obrigatório | Tipo | Descrição |
|---|---|---|---|
| `external_id` | recomendado | string (≤200) | ID estável da volta **dentro do carro/pista**. Usado para evitar importações duplicadas. |
| `car_code` | **sim** | inteiro > 0 | Código GT7 do carro. Precisa existir em `Car.car_code`. |
| `track_id` | **sim** | inteiro > 0 | ID GT7 da pista. Precisa existir em `Track.track_id`. |
| `lap_number` | opcional | inteiro ≥ 0 | Número da volta na sessão. Padrão `0`. |
| `lap_time_ms` | **sim** | inteiro > 0 | Tempo oficial da volta em milissegundos. |
| `session_notes` | opcional | string | Observações livres. |
| `sector_1_ms` | opcional | inteiro ≥ 0 | Setor 1 em ms. |
| `sector_2_ms` | opcional | inteiro ≥ 0 | Setor 2 em ms. |
| `sector_3_ms` | opcional | inteiro ≥ 0 | Setor 3 em ms. |
| `stats` | opcional | objeto | Estatísticas agregadas (ver abaixo). |
| `frames` | opcional | array | Frames brutos para recálculo (ver abaixo). |

> Se os três setores forem informados e a soma divergir de `lap_time_ms` em
> mais de 250 ms, o import gera um **aviso** (não bloqueia).

### `stats`

Todos os campos são opcionais e numéricos (≥ 0):

- `max_speed_kmh`
- `min_speed_kmh`
- `avg_speed_kmh`
- `avg_throttle_pct` (0–100)
- `avg_brake_pct` (0–100)
- `max_rpm`
- `total_frames` (inteiro)

Se `frames` estiver presente, as estatísticas de velocidade/pedais/RPM são
**recalculadas a partir dos frames** e substituem `stats`.

### `frames[]`

```json
{
  "seq": 0,
  "ts": 12345.678,
  "speed_mps": 55.5,
  "throttle": 255,
  "brake": 0,
  "engine_rpm": 7800,
  "position_x": 1.0,
  "position_y": 2.0,
  "position_z": 3.0
}
```

| Campo | Obrigatório | Tipo | Descrição |
|---|---|---|---|
| `seq` | **sim** | inteiro | Ordem do frame dentro da volta. |
| `ts` | opcional | número | Timestamp em segundos. |
| `speed_mps` | opcional | número | Velocidade em m/s. |
| `throttle` | opcional | número | Acelerador bruto (0–255). |
| `brake` | opcional | número | Freio bruto (0–255). |
| `engine_rpm` | opcional | número | RPM. |
| `position_x/y/z` | opcional | número | Posição 3D. |

Frames são usados para:

1. calcular setores por distância acumulada (divisão em 1/3);
2. recalcular velocidade máxima/mínima/média, pedais e RPM.

### Cálculo de setores

- Só acontece se houver **≥ 10 frames** com `seq` e `position_x/y/z`.
- A distância acumulada precisa ser **≥ 80% de `Track.length_km`**. Caso
  contrário, o cálculo é descartado e os setores informados no JSON são usados.
- Os setores calculados são normalizados para somarem exatamente
  `lap_time_ms`.

---

## Deduplicação

1. Se `external_id` existir → chave: `(car, track, external_id)`.
2. Caso contrário → chave de fallback:
   `(car, track, lap_number, lap_time_ms)`.
3. Voltas já existentes são ignoradas (`skipped`).

> Recomendação: sempre envie `external_id`.

---

## Limite de voltas

Após cada importação, o RevLabs mantém apenas as **10 voltas mais rápidas por
carro + pista**. As demais são removidas (`trimmed`).

---

## Compatibilidade com arquivos antigos

O importador ainda aceita, para não quebrar arquivos já gerados:

| Legado | Equivalente atual |
|---|---|
| `export_version` | `version` |
| `sector1_ms` / `sector2_ms` / `sector3_ms` | `sector_1_ms` / `sector_2_ms` / `sector_3_ms` |
| `original_session_id` + `original_lap_id` | `external_id` = `session-{session}-lap-{lap}` |

Novos arquivos devem usar o formato v1 acima.

---

## Como importar

```powershell
# Seed embutido (padrão)
python import_telemetry.py

# Arquivo específico
python import_telemetry.py caminho/para/arquivo.json

# Via Django
python manage.py import_telemetry caminho/para/arquivo.json
```

Pela interface web: dashboard → **IMPORT TELEMETRY (.JSON)**.

O endpoint é `POST /api/import-telemetry/` (multipart, campo `file`, máximo
10 MB, apenas `.json`).

---

## Validação

O mesmo validador roda em todos os caminhos (CLI, management command e web).
Erros estruturais ou de campos obrigatórios **abortam** a importação e são
retornados na resposta. Avisos (setores divergentes, poucos frames, stats
desconhecidos) não bloqueiam.

Função pública:

```python
from revlabs.telemetry_import import validate_telemetry_payload

laps, errors, warnings = validate_telemetry_payload(data)
```

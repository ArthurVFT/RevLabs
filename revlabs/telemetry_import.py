"""
RevLabs telemetry importer.

This module is the single entry point for ingesting telemetry into the
RevLabs database. It only understands the first-party JSON format documented
in ``TELEMETRY_FORMAT.md``. There is no database coupling, no external tool
and no provider-specific schema.

Usage (standalone CLI)::

    python import_telemetry.py [path_to_file.json]

Usage (Django management command)::

    python manage.py import_telemetry [path_to_file.json]

Usage (web)::

    POST /api/import-telemetry/ with a multipart file field named ``file``.
"""
import json
from math import sqrt

from django.db import transaction

from revlabs.models import Car, Track, TelemetryLap

FORMAT_NAME = 'revlabs.telemetry'
FORMAT_VERSION = 1

# Keys accepted in the ``stats`` object of a lap.
STATS_KEYS = (
    'max_speed_kmh',
    'min_speed_kmh',
    'avg_speed_kmh',
    'avg_throttle_pct',
    'avg_brake_pct',
    'max_rpm',
    'total_frames',
)


class TelemetryFormatError(ValueError):
    """Raised when a telemetry payload does not match the documented format."""


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

def _is_int(value):
    return isinstance(value, int) and not isinstance(value, bool)


def _is_number(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _int_field(lap, key, errors, required=False, minimum=None):
    value = lap.get(key)
    if value is None:
        if required:
            errors.append(f"lap {lap.get('_index', '?')}: campo obrigatório '{key}' ausente")
        return None
    if not _is_int(value):
        errors.append(f"lap {lap.get('_index', '?')}: '{key}' deve ser inteiro")
        return None
    if minimum is not None and value < minimum:
        errors.append(f"lap {lap.get('_index', '?')}: '{key}' deve ser >= {minimum}")
        return None
    return value


def _number_field(value, label, errors, minimum=None):
    if value is None:
        return None
    if not _is_number(value):
        errors.append(f"{label} deve ser numérico")
        return None
    if minimum is not None and value < minimum:
        errors.append(f"{label} deve ser >= {minimum}")
        return None
    return float(value)


def _normalise_lap(lap, index, top_level_source, errors, warnings):
    """Validate one lap and return a normalised dict (or None on error)."""
    label = f"lap {index}"

    if not isinstance(lap, dict):
        errors.append(f"{label}: deve ser um objeto JSON")
        return None

    car_code = _int_field(lap, 'car_code', errors, required=True, minimum=1)
    track_id = _int_field(lap, 'track_id', errors, required=True, minimum=1)
    lap_time_ms = _int_field(lap, 'lap_time_ms', errors, required=True, minimum=1)

    lap_number = _int_field(lap, 'lap_number', errors, minimum=0) or 0

    external_id = lap.get('external_id')
    if external_id is not None and not isinstance(external_id, str):
        errors.append(f"{label}: 'external_id' deve ser texto")
        external_id = None
    if external_id and len(external_id) > 200:
        errors.append(f"{label}: 'external_id' deve ter no máximo 200 caracteres")
        external_id = None

    # Legacy compatibility: accept original_session_id / original_lap_id.
    if not external_id:
        original_lap_id = lap.get('original_lap_id')
        if original_lap_id is not None:
            if not _is_int(original_lap_id):
                errors.append(f"{label}: 'original_lap_id' deve ser inteiro")
            else:
                original_session_id = lap.get('original_session_id')
                if original_session_id is not None and not _is_int(original_session_id):
                    errors.append(f"{label}: 'original_session_id' deve ser inteiro")
                elif original_session_id is not None:
                    external_id = f"session-{original_session_id}-lap-{original_lap_id}"
                else:
                    external_id = f"lap-{original_lap_id}"

    notes = lap.get('session_notes')
    if notes is not None and not isinstance(notes, str):
        errors.append(f"{label}: 'session_notes' deve ser texto")
        notes = None

    source = lap.get('source') or top_level_source or ''
    if not isinstance(source, str):
        errors.append(f"{label}: 'source' deve ser texto")
        source = ''

    sectors = {}
    for key in ('sector_1_ms', 'sector_2_ms', 'sector_3_ms'):
        sectors[key] = _int_field(lap, key, errors, minimum=0)

    # Legacy compatibility: sector1_ms / sector2_ms / sector3_ms.
    for legacy_key, key in (
        ('sector1_ms', 'sector_1_ms'),
        ('sector2_ms', 'sector_2_ms'),
        ('sector3_ms', 'sector_3_ms'),
    ):
        if sectors[key] is None and lap.get(legacy_key) is not None:
            sectors[key] = _int_field(lap, legacy_key, errors, minimum=0)

    if any(v is not None for v in sectors.values()):
        if any(v is None for v in sectors.values()):
            warnings.append(f"{label}: setores incompletos; serão recalculados ou ignorados")
        elif lap_time_ms and abs(sum(sectors.values()) - lap_time_ms) > 250:
            warnings.append(
                f"{label}: soma dos setores ({sum(sectors.values())} ms) "
                f"difere do tempo de volta ({lap_time_ms} ms)"
            )

    stats = lap.get('stats')
    if stats is None:
        stats = {}
    if not isinstance(stats, dict):
        errors.append(f"{label}: 'stats' deve ser um objeto JSON")
        stats = {}

    for key, value in stats.items():
        if key not in STATS_KEYS:
            warnings.append(f"{label}: campo de stats desconhecido ignorado: '{key}'")
            continue
        if key == 'total_frames':
            if value is not None and not _is_int(value):
                errors.append(f"{label}: stats.total_frames deve ser inteiro")
        else:
            _number_field(value, f"{label}: stats.{key}", errors, minimum=0)

    frames = lap.get('frames', [])
    if frames is None:
        frames = []
    if not isinstance(frames, list):
        errors.append(f"{label}: 'frames' deve ser uma lista")
        frames = []
    else:
        for frame_index, frame in enumerate(frames, start=1):
            frame_label = f"{label}: frame {frame_index}"
            if not isinstance(frame, dict):
                errors.append(f"{frame_label} deve ser um objeto JSON")
                continue
            if not _is_int(frame.get('seq')):
                errors.append(f"{frame_label}: 'seq' deve ser inteiro")
            for key in (
                'ts', 'speed_mps', 'throttle', 'brake', 'engine_rpm',
                'position_x', 'position_y', 'position_z',
            ):
                value = frame.get(key)
                if value is not None and not _is_number(value):
                    errors.append(f"{frame_label}: '{key}' deve ser numérico")
        if frames and len(frames) < 10 and not all(v is not None for v in sectors.values()):
            warnings.append(f"{label}: poucos frames e sem setores; setores não serão calculados")

    return {
        'car_code': car_code,
        'track_id': track_id,
        'lap_number': lap_number,
        'lap_time_ms': lap_time_ms,
        'external_id': external_id or '',
        'source': source,
        'session_notes': notes or '',
        'sector_1_ms': sectors['sector_1_ms'],
        'sector_2_ms': sectors['sector_2_ms'],
        'sector_3_ms': sectors['sector_3_ms'],
        'stats': stats,
        'frames': frames,
        'original_session_id': lap.get('original_session_id'),
        'original_lap_id': lap.get('original_lap_id'),
    }


def validate_telemetry_payload(data):
    """
    Validate a decoded telemetry payload.

    Returns a tuple ``(laps, errors, warnings)``. ``laps`` is a list of
    normalised lap dictionaries and is only usable when ``errors`` is empty.

    Raises ``TelemetryFormatError`` for a structurally invalid document.
    """
    if not isinstance(data, dict):
        raise TelemetryFormatError("o arquivo deve conter um objeto JSON na raiz")

    fmt = data.get('format')
    version = data.get('version', data.get('export_version'))

    if fmt is not None and fmt != FORMAT_NAME:
        raise TelemetryFormatError(
            f"formato não reconhecido: {fmt!r} (esperado {FORMAT_NAME!r})"
        )

    if version is not None and version != FORMAT_VERSION:
        raise TelemetryFormatError(
            f"versão de formato não suportada: {version!r} (suportada: {FORMAT_VERSION})"
        )

    raw_laps = data.get('laps')
    if not isinstance(raw_laps, list):
        raise TelemetryFormatError("o arquivo deve conter a lista 'laps'")

    top_level_source = data.get('source')
    if top_level_source is not None and not isinstance(top_level_source, str):
        raise TelemetryFormatError("'source' deve ser texto")

    errors = []
    warnings = []
    laps = []

    if not raw_laps:
        warnings.append("o arquivo não contém voltas")

    for index, raw_lap in enumerate(raw_laps, start=1):
        errors_before = len(errors)
        lap = _normalise_lap(raw_lap, index, top_level_source, errors, warnings)
        if lap is not None and len(errors) == errors_before:
            laps.append(lap)

    return laps, errors, warnings


# ---------------------------------------------------------------------------
# Derived values
# ---------------------------------------------------------------------------

def estimate_speed_stats(frames):
    if not frames:
        return None, None, None
    speeds = [f.get('speed_mps') for f in frames if f.get('speed_mps')]
    if not speeds:
        return None, None, None
    speeds_kmh = [s * 3.6 for s in speeds]
    return max(speeds_kmh), min(speeds_kmh), sum(speeds_kmh) / len(speeds_kmh)


def estimate_avg_pedal(frames, key):
    vals = [f.get(key) for f in frames if f.get(key) is not None]
    if not vals:
        return None
    return sum(vals) / len(vals) / 255 * 100


def calculate_sectors(frames, lap_time_ms, track_length_km):
    """Split a lap into three equal-distance sectors using 3D positions."""
    if not frames or len(frames) < 10:
        return None, None, None

    fs = sorted(frames, key=lambda f: f['seq'])
    n = len(fs)

    cum_dist = [0.0]
    for i in range(1, n):
        dx = (fs[i].get('position_x') or 0) - (fs[i - 1].get('position_x') or 0)
        dy = (fs[i].get('position_y') or 0) - (fs[i - 1].get('position_y') or 0)
        dz = (fs[i].get('position_z') or 0) - (fs[i - 1].get('position_z') or 0)
        cum_dist.append(cum_dist[-1] + sqrt(dx * dx + dy * dy + dz * dz))

    total_dist = cum_dist[-1]
    if total_dist <= 0:
        return None, None, None

    track_length_m = track_length_km * 1000
    if total_dist < track_length_m * 0.8:
        return None, None, None

    s1_threshold = total_dist / 3.0
    s2_threshold = total_dist * 2.0 / 3.0

    s1_idx = next((i for i, d in enumerate(cum_dist) if d >= s1_threshold), None)
    s2_idx = next((i for i, d in enumerate(cum_dist) if d >= s2_threshold), None)

    if s1_idx is None or s2_idx is None:
        return None, None, None

    start_ts = fs[0].get('ts') or 0
    s1_ts = fs[s1_idx].get('ts') or start_ts
    s2_ts = fs[s2_idx].get('ts') or s1_ts
    end_ts = fs[-1].get('ts') or s2_ts

    raw_s1 = max(0, int((s1_ts - start_ts) * 1000))
    raw_s2 = max(0, int((s2_ts - s1_ts) * 1000))
    raw_s3 = max(0, int((end_ts - s2_ts) * 1000))
    raw_sum = raw_s1 + raw_s2 + raw_s3

    if raw_sum <= 0:
        return None, None, None

    scale = lap_time_ms / raw_sum
    s1 = int(raw_s1 * scale)
    s2 = int(raw_s2 * scale)
    s3 = lap_time_ms - s1 - s2

    return s1, s2, s3


def _frames_with_seq(frames):
    usable = []
    for frame in frames:
        if not isinstance(frame, dict):
            continue
        seq = frame.get('seq')
        if not _is_int(seq):
            continue
        usable.append(frame)
    return usable


# ---------------------------------------------------------------------------
# Import
# ---------------------------------------------------------------------------

def run_import_from_json_data(data, print_func=print):
    """
    Import laps from an already-decoded telemetry document.

    Returns a dict with ``imported``, ``skipped``, ``trimmed``, ``error``,
    ``errors``, ``warnings`` and ``results``.
    """
    try:
        laps, errors, warnings = validate_telemetry_payload(data)
    except TelemetryFormatError as exc:
        return {
            'imported': 0,
            'skipped': 0,
            'trimmed': 0,
            'error': str(exc),
            'errors': [str(exc)],
            'warnings': [],
            'results': [],
        }

    for warning in warnings:
        print_func(f"AVISO: {warning}")

    if errors:
        for error in errors:
            print_func(f"ERRO: {error}")
        return {
            'imported': 0,
            'skipped': 0,
            'trimmed': 0,
            'error': f"{len(errors)} erro(s) de validação",
            'errors': errors,
            'warnings': warnings,
            'results': [],
        }

    print_func(f"Arquivo contém {len(laps)} volta(s)")

    imported = 0
    skipped = 0
    skip_reasons = []

    with transaction.atomic():
        for lap in laps:
            car = Car.objects.filter(car_code=lap['car_code']).first()
            track = Track.objects.filter(track_id=lap['track_id']).first()
            if not car or not track:
                skipped += 1
                reason = (
                    f"car_code={lap['car_code']} / track_id={lap['track_id']} "
                    f"não cadastrados em RevLabs"
                )
                skip_reasons.append(reason)
                print_func(f"IGNORADA: {reason}")
                continue

            if lap['external_id']:
                existing = TelemetryLap.objects.filter(
                    car=car, track=track, source_lap_id=lap['external_id']
                ).exists()
            else:
                existing = TelemetryLap.objects.filter(
                    car=car,
                    track=track,
                    lap_number=lap['lap_number'],
                    lap_time_ms=lap['lap_time_ms'],
                ).exists()

            if existing:
                skipped += 1
                continue

            frames = _frames_with_seq(lap['frames'])
            stats = lap['stats']

            sector_1, sector_2, sector_3 = (None, None, None)
            if frames:
                sector_1, sector_2, sector_3 = calculate_sectors(
                    frames, lap['lap_time_ms'], track.length_km
                )

            if sector_1 is None:
                sector_1 = lap['sector_1_ms']
                sector_2 = lap['sector_2_ms']
                sector_3 = lap['sector_3_ms']

            if frames:
                max_speed, min_speed, avg_speed = estimate_speed_stats(frames)
                avg_throttle = estimate_avg_pedal(frames, 'throttle')
                avg_brake = estimate_avg_pedal(frames, 'brake')
                max_rpm = max((f.get('engine_rpm') or 0) for f in frames)
                total_frames = len(frames)
            else:
                max_speed = stats.get('max_speed_kmh')
                min_speed = stats.get('min_speed_kmh')
                avg_speed = stats.get('avg_speed_kmh')
                avg_throttle = stats.get('avg_throttle_pct')
                avg_brake = stats.get('avg_brake_pct')
                max_rpm = stats.get('max_rpm')
                total_frames = stats.get('total_frames')

            TelemetryLap.objects.create(
                car=car,
                track=track,
                lap_number=lap['lap_number'],
                lap_time_ms=lap['lap_time_ms'],
                lap_time_seconds=lap['lap_time_ms'] / 1000.0,
                is_complete=True,
                has_mods=False,
                avg_speed_kmh=avg_speed,
                max_speed_kmh=max_speed,
                min_speed_kmh=min_speed,
                max_rpm=max_rpm,
                avg_throttle_pct=avg_throttle,
                avg_brake_pct=avg_brake,
                session_notes=lap['session_notes'],
                source=lap['source'],
                source_lap_id=lap['external_id'] or None,
                original_session_id=lap['original_session_id'],
                original_lap_id=lap['original_lap_id'],
                total_frames=total_frames,
                sector_1_ms=sector_1,
                sector_2_ms=sector_2,
                sector_3_ms=sector_3,
            )
            imported += 1

        print_func(f"Importadas {imported} voltas, ignoradas {skipped}")

        trimmed = _trim_excess_laps(print_func)
        results = _collect_results(print_func)

    return {
        'imported': imported,
        'skipped': skipped,
        'trimmed': trimmed,
        'error': None,
        'errors': [],
        'warnings': warnings,
        'skip_reasons': skip_reasons,
        'results': results,
    }


def run_import_from_json(json_path, print_func=print):
    """Read a JSON file and import its laps. Kept as the public API."""
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        msg = f"ERRO: arquivo não encontrado: {json_path}"
        print_func(msg)
        return {
            'imported': 0,
            'skipped': 0,
            'trimmed': 0,
            'error': msg,
            'errors': [msg],
            'warnings': [],
            'results': [],
        }
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        msg = f"ERRO: JSON inválido: {exc}"
        print_func(msg)
        return {
            'imported': 0,
            'skipped': 0,
            'trimmed': 0,
            'error': msg,
            'errors': [msg],
            'warnings': [],
            'results': [],
        }

    return run_import_from_json_data(data, print_func=print_func)


def _trim_excess_laps(print_func=print):
    """Trim to top 10 per car+track combination. Returns count of deleted laps."""
    trimmed = 0
    combos = TelemetryLap.objects.filter(is_complete=True).values(
        'car_id', 'track_id'
    ).order_by('car_id', 'track_id').distinct()
    for combo in combos:
        laps_list = TelemetryLap.objects.filter(
            car_id=combo['car_id'], track_id=combo['track_id'], is_complete=True
        ).order_by('lap_time_ms')
        if laps_list.count() > 10:
            to_delete = laps_list[10:]
            for lap in to_delete:
                lap.delete()
            trimmed += len(to_delete)
    if trimmed:
        print_func(
            f"Removidas {trimmed} voltas extras "
            "(mantidas apenas top 10 por carro/pista)"
        )
    return trimmed


def _collect_results(print_func=print):
    """Collect summary results for all car+track combinations."""
    results = []
    combos = TelemetryLap.objects.filter(is_complete=True).values(
        'car_id', 'track_id'
    ).order_by('car_id', 'track_id').distinct()
    for combo in combos:
        car = Car.objects.get(id=combo['car_id'])
        track = Track.objects.get(id=combo['track_id'])
        laps_list = TelemetryLap.objects.filter(
            car=car, track=track, is_complete=True
        ).order_by('lap_time_ms')
        if laps_list.exists():
            best = laps_list.first()
            count = laps_list.count()
            top10_avg = sum(l.lap_time_seconds for l in laps_list) / count
            info = {
                'car': str(car),
                'track': str(track),
                'count': count,
                'best_time': best.lap_time_seconds,
                'avg_time': top10_avg,
                'max_speed': best.max_speed_kmh,
                'avg_speed': best.avg_speed_kmh,
                'sectors': {
                    's1': best.sector_1_ms,
                    's2': best.sector_2_ms,
                    's3': best.sector_3_ms,
                } if best.sector_1_ms else None,
            }
            results.append(info)
            print_func(f"\n{car.name} @ {track.name}:")
            print_func(f"  Total de voltas: {count}")
            print_func(f"  Melhor tempo: {best.lap_time_seconds:.3f}s")
            if best.sector_1_ms:
                proj = best.sector_1_ms + best.sector_2_ms + best.sector_3_ms
                print_func(
                    f"  Setores: {best.sector_1_ms} / {best.sector_2_ms} / "
                    f"{best.sector_3_ms} ms (projetado: {proj} ms)"
                )
            print_func(f"  Media top {count}: {top10_avg:.3f}s")
            print_func(f"  Vel max: {best.max_speed_kmh:.1f} km/h")
            print_func(f"  Vel media: {best.avg_speed_kmh:.1f} km/h")
    return results

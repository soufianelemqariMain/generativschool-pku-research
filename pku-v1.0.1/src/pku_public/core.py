# Copyright (c) 2026 Soufiane Lemqari. MIT.
"""Paired published summaries; no clinical inference and no reconstructed replicates."""
import csv
import hashlib
import json
import math
import statistics
import xml.etree.ElementTree as ET
from pathlib import Path

BUNDLE = Path(__file__).parent / 'bundle'
MODELS = ('zero_effect', 'train_mean', 'ridge_activity_alpha1')
WARNING = 'Calcul sur moyennes publiees PAH/GroEL-ES bacterien; aucune validation biologique ou recommandation therapeutique.'


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def write(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x', encoding='utf-8') as f:
        json.dump(value, f, ensure_ascii=False, indent=2, allow_nan=False)
        f.write('\n')


def verify_lock(bundle):
    lock = read(BUNDLE / 'lock.json')  # trusted installed release, never the candidate's own lock
    for name, expected in lock.items():
        f = Path(bundle) / name
        if not f.is_file() or digest(f) != expected:
            raise ValueError('Source/donnee/configuration alteree: ' + name)


def extract(xml):
    root = ET.parse(xml).getroot()
    permission = root.find('.//permissions')
    if permission is None or 'creativecommons.org/licenses/by/4.0/' not in ET.tostring(permission, encoding='unicode'):
        raise ValueError('Droits CC BY 4.0 absents')
    table = root.find(".//table-wrap[@id='genes-10-00459-t003']")
    if table is None:
        raise ValueError('Table 3 absente')
    rows = []
    def cell(s):
        parts = s.split('±')
        return float(parts[0]), float(parts[1]) if len(parts) == 2 else None
    for tr in table.findall('./table/tbody/tr'):
        c = [''.join(x.itertext()).strip() for x in tr.findall('td')]
        if len(c) != 9:
            raise ValueError('Structure du tableau inconnue')
        for intervention, offset in [('none', 0), ('GroEL_ES', 4)]:
            value, sd = cell(c[4 + offset]); tet, tsd = cell(c[2 + offset])
            rows.append(dict(source_id='S02', source_locator='Table 3', variant=c[0], protein_ref='NP_000268.1',
                system='E_coli_XL1_blue_MBP_PAH_purified', intervention=intervention, endpoint='activity_pct_WT',
                value=value, sd=sd, n_purifications=3, n_assays_total=9, tetramer_pct=tet, tetramer_sd=tsd,
                zero_semantics='not_detected_LOD_unreported' if value == 0 else '',
                conflict='section_3.3_84.6_sd48.4' if c[0] == 'p.Ile406Met' and intervention == 'none' else ''))
    return rows


def load_csv(path):
    with Path(path).open(encoding='utf-8', newline='') as f:
        rows = list(csv.DictReader(f))
    for r in rows:
        for k in ('value', 'sd', 'tetramer_pct', 'tetramer_sd'):
            r[k] = float(r[k]) if r[k] != '' else None
        for k in ('n_purifications', 'n_assays_total'):
            r[k] = int(r[k])
    return rows


def validate(rows, config):
    expected = read(BUNDLE / 'configs/study.json')
    for k in ('contract', 'source_id', 'doi', 'license', 'system', 'protein_ref', 'endpoint', 'unit', 'target_unit', 'alpha', 'scale'):
        if config.get(k) != expected[k]:
            raise ValueError('Contrat/droits/unite incompatible: ' + k)
    groups = {}
    for r in rows:
        for k in ('source_id', 'system', 'protein_ref', 'endpoint'):
            if r.get(k) != config[k]:
                raise ValueError('Melange de sources/endpoints/systemes: ' + k)
        if r.get('source_locator') != 'Table 3' or r.get('intervention') not in ('none', 'GroEL_ES'):
            raise ValueError('Provenance/condition inconnue')
        for k in ('value', 'sd', 'tetramer_pct', 'tetramer_sd'):
            v = r.get(k)
            if v is None and k in ('value', 'tetramer_pct'):
                raise ValueError('Mesure inconnue, pas zero: ' + k)
            if v is not None and (not math.isfinite(v) or v < 0):
                raise ValueError('Valeur invalide: ' + k)
        if (r['value'] == 0) != (r.get('zero_semantics') == 'not_detected_LOD_unreported'):
            raise ValueError('Semantique zero perdue')
        if r['n_purifications'] != 3 or r['n_assays_total'] != 9:
            raise ValueError('Effectifs source incoherents')
        conflict = 'section_3.3_84.6_sd48.4' if r['variant'] == 'p.Ile406Met' and r['intervention'] == 'none' else ''
        if r.get('conflict') != conflict:
            raise ValueError('Conflit source perdu/invente')
        g = groups.setdefault(r['variant'], {})
        if r['intervention'] in g:
            raise ValueError('Doublon variant/condition, risque de fuite')
        g[r['intervention']] = r
    if not groups or any(set(g) != {'none', 'GroEL_ES'} for g in groups.values()):
        raise ValueError('Paire incomplete')
    return groups


def audit(bundle=BUNDLE):
    bundle = Path(bundle)
    log = []
    try:
        verify_lock(bundle)
        log.append({'check': 'sha256_source_data_context_config_reference', 'status': 'admitted'})
        config = read(bundle / 'configs/study.json')
        rows = load_csv(bundle / 'data/activity_pairs.csv')
        groups = validate(rows, config)
        if len(rows) != 14 or len(groups) != 7:
            raise ValueError('Couverture D01 incorrecte')
        if rows != extract(bundle / 'sources/PMC6628251.xml'):
            raise ValueError('CSV divergent du tableau XML')
        log.extend({'variant': r['variant'], 'condition': r['intervention'], 'status': 'admitted', 'locator': r['source_locator'], 'conflict': r['conflict']} for r in rows)
        return {'status': 'admitted', 'observations': 14, 'variants': 7, 'log': log,
                'coverage': {'sources': ['S02'], 'systems': [config['system']], 'endpoints': [config['endpoint']]}, 'warning': WARNING}
    except (ValueError, OSError, KeyError, TypeError, ET.ParseError) as e:
        log.append({'status': 'rejected', 'reason': str(e)})
        return {'status': 'rejected', 'log': log, 'warning': WARNING}


def fit(train, held_out):
    if held_out in [p['variant'] for p in train] or len({p['variant'] for p in train}) != len(train):
        raise ValueError('Fuite par variant')
    xs = [r['baseline_activity_pct_WT']/100 for r in train]
    ys = [r['delta_pp'] for r in train]
    xm = statistics.mean(xs); ym = statistics.mean(ys)
    slope = sum((x-xm)*(y-ym) for x,y in zip(xs,ys))/(sum((x-xm)**2 for x in xs)+1.0)
    return {'alpha': 1.0, 'scale': 100.0, 'x_train_mean': xm, 'y_train_mean': ym,
            'ridge_slope': slope, 'ridge_intercept': ym-slope*xm, 'zero_effect': 0.0}


def evaluate(rows, config):
    groups = validate(rows, config)
    scenarios = []
    for scenario in config['source_scenarios']:
        pairs = []
        for name, g in groups.items():
            a = g['none']['value']; b = g['GroEL_ES']['value']
            if scenario == 'section3.3_Ile406Met' and name == 'p.Ile406Met':
                a = 84.6
            pairs.append({'variant': name, 'baseline_activity_pct_WT': a, 'treated_activity_pct_WT': b,
                          'delta_pp': b-a, 'baseline_sd': 48.4 if scenario != 'table3' and name == 'p.Ile406Met' else g['none']['sd'],
                          'treated_sd': g['GroEL_ES']['sd'], 'delta_uncertainty': None, 'conflict': g['none']['conflict']})
        out = []
        for p in pairs:
            train = [r for r in pairs if r['variant'] != p['variant']]
            params = fit(train, p['variant'])
            pred = params['y_train_mean'] + params['ridge_slope']*(p['baseline_activity_pct_WT']/100-params['x_train_mean'])
            out.append({'variant': p['variant'], 'train_variants': [r['variant'] for r in train],
                'observed_delta_pp': p['delta_pp'], 'zero_effect': 0.0, 'train_mean': params['y_train_mean'],
                'ridge_activity_alpha1': pred, 'parameters': params})
        metrics = {m: {'mae_pp': statistics.mean(abs(r[m]-r['observed_delta_pp']) for r in out),
                       'rmse_pp': math.sqrt(statistics.mean((r[m]-r['observed_delta_pp'])**2 for r in out))} for m in MODELS}
        scenarios.append({'scenario': scenario, 'n_variants': len(pairs), 'pairs': pairs, 'predictions': out, 'metrics': metrics})
    return {'status': 'executed_computational_not_biological_validation', 'validation': 'leave_one_variant_out',
            'warning': WARNING, 'calibrated_intervals': None, 'selected_model': None, 'scenarios': scenarios}


def compare(report, reference):
    errors = []
    actual = report['scenarios']; expected = reference['scenarios']
    if len(actual) != len(expected):
        raise ValueError('Nombre de scenarios divergent')
    for a, b in zip(actual, expected):
        if a['scenario'] != b['scenario'] or a['n_variants'] != b['n_variants']:
            raise ValueError('Scenario divergent')
        for model in MODELS:
            for metric in ('mae_pp', 'rmse_pp'):
                errors.append(abs(a['metrics'][model][metric]-b['metrics'][model][metric]))
        if len(a['predictions']) != len(b['predictions']):
            raise ValueError('Predictions manquantes')
        for x,y in zip(a['predictions'], b['predictions']):
            if x['variant'] != y['variant'] or x['train_variants'] != y['train_variants']:
                raise ValueError('Plis divergents')
            errors.extend(abs(x[k]-y[k]) for k in MODELS+('observed_delta_pp',))
    if any(not math.isfinite(x) or x > 1e-10 for x in errors):
        raise ValueError('Ecart au pilote > 1e-10')
    return {'status': 'passed', 'tolerance': 1e-10, 'max_abs_error': max(errors), 'numeric_comparisons': len(errors)}


def hypothesis(report):
    p = next(p for p in report['scenarios'][0]['pairs'] if p['variant'] == 'p.Ala342Pro')
    return {'status': 'design_only_not_executed', 'purpose': 'Selection de prochains essais; aucun classement de traitements',
        'published_observation': {'source': 'Pecimonova et al. 2019, DOI 10.3390/genes10060459, Table 3', **p},
        'hypothesis_to_refute': 'Le contraste publie Ala342Pro avec/sans GroEL/ES est reproductible dans le meme systeme bacterien.',
        'system': 'E. coli XL1 blue, MBP-PAH purifiee; selection de fractions selon section 2.3',
        'controls': ['WT avec et sans co-expression', 'Variant avec et sans co-expression', 'Blanc analytique et controle de detection', 'Suivi des lots et fractions de purification'],
        'collection_design': ['Conserver les mesures brutes de chaque purification et essai technique, sans pseudo-replication', 'Documenter limite de detection, denominateur WT, contexte et deviations', 'Pre-enregistrer analyse, seuil de pertinence et effectif sur precision visee; aucun seuil inferentiel deduit de sept moyennes', 'Ordre randomise et analyse masquee si faisables; validation par equipe competente avant execution'],
        'failure_criteria': ['Contraste non reproduit avec precision predefinie', 'Echec des controles analytiques ou denominateur non comparable', 'Changement de fraction/systeme empechant attribution a la co-expression'],
        'uncertainty': 'SD publies conserves; covariance et donnees brutes absentes, incertitude de delta inconnue.', 'warning': WARNING}

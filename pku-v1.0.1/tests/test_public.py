# Copyright (c) 2026 Soufiane Lemqari. MIT.
import copy
import shutil
import tempfile
import unittest
from pathlib import Path
from pku_public import core as c
from pku_public.cli import main, verify_run

class PublicTests(unittest.TestCase):
    def setUp(self):
        self.rows = c.load_csv(c.BUNDLE/'data/activity_pairs.csv')
        self.config = c.read(c.BUNDLE/'configs/study.json')
    def test_source_extraction_and_admission(self):
        self.assertEqual(self.rows, c.extract(c.BUNDLE/'sources/PMC6628251.xml'))
        self.assertEqual(c.audit()['status'], 'admitted')
    def test_incomplete_pair(self):
        with self.assertRaisesRegex(ValueError, 'incomplete'): c.validate(self.rows[:-1], self.config)
    def test_duplicate(self):
        with self.assertRaisesRegex(ValueError, 'Doublon'): c.validate(self.rows+self.rows[:1], self.config)
    def test_missing_not_zero(self):
        self.rows[0]['value'] = None
        with self.assertRaisesRegex(ValueError, 'inconnue'): c.validate(self.rows, self.config)
    def test_nonfinite(self):
        self.rows[0]['value'] = float('nan')
        with self.assertRaises(ValueError): c.validate(self.rows, self.config)
    def test_zero_semantics(self):
        self.rows[4]['zero_semantics'] = ''
        with self.assertRaisesRegex(ValueError, 'zero'): c.validate(self.rows, self.config)
    def test_conflict(self):
        self.rows[-2]['conflict'] = ''
        with self.assertRaisesRegex(ValueError, 'Conflit'): c.validate(self.rows, self.config)
    def test_unit(self):
        self.config['unit'] = 'fraction'
        with self.assertRaises(ValueError): c.validate(self.rows, self.config)
    def test_rights(self):
        self.config['license'] = 'unknown'
        with self.assertRaises(ValueError): c.validate(self.rows, self.config)
    def test_system_and_endpoint(self):
        for key in ('system', 'endpoint', 'source_id'):
            rows = copy.deepcopy(self.rows); rows[1][key] = 'incompatible'
            with self.subTest(key=key), self.assertRaises(ValueError): c.validate(rows, self.config)
    def test_fold_leak_guard(self):
        with self.assertRaisesRegex(ValueError, 'Fuite'): c.fit([{'variant':'x'}], 'x')
    def test_pilot_and_fold_parameters(self):
        r = c.evaluate(self.rows, self.config)
        self.assertEqual(c.compare(r,c.read(c.BUNDLE/'reference/pilot.json'))['max_abs_error'],0)
        for scenario in r['scenarios']:
            for p in scenario['predictions']:
                self.assertNotIn(p['variant'],p['train_variants'])
                self.assertEqual(len(p['train_variants']),6)
        # Mutating held-out treated target cannot affect its fitted parameters/prediction.
        changed = copy.deepcopy(self.rows); changed[1]['value'] += 100
        b = c.evaluate(changed,self.config)['scenarios'][0]['predictions'][0]
        a = r['scenarios'][0]['predictions'][0]
        self.assertEqual(a['parameters'], b['parameters'])
        self.assertEqual(a['ridge_activity_alpha1'], b['ridge_activity_alpha1'])
    def test_source_altered(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp)/'bundle'; shutil.copytree(c.BUNDLE,p)
            with (p/'sources/PMC6628251.xml').open('a') as f: f.write(' ')
            self.assertEqual(c.audit(p)['status'],'rejected')
            self.assertEqual(main(['audit','--bundle',str(p),'--out',str(Path(tmp)/'rejection.json')]),2)
    def test_rights_xml(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'source.xml'; p.write_text((c.BUNDLE/'sources/PMC6628251.xml').read_text().replace('creativecommons.org/licenses/by/4.0/', 'invalid'))
            with self.assertRaisesRegex(ValueError,'Droits'): c.extract(p)
    def test_restore_and_corruption(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'run'; restored=Path(tmp)/'restored'
            self.assertEqual(main(['evaluate','--out',str(p)]),0)
            self.assertEqual(main(['restore','--run',str(p),'--out',str(restored)]),0)
            self.assertEqual((p/'report.json').read_bytes(),(restored/'report.json').read_bytes())
            self.assertEqual(main(['evaluate','--out',str(p)]),2)
            (p/'report.json').write_text('{}')
            with self.assertRaisesRegex(ValueError,'altere'): verify_run(p)
    def test_hypothesis_boundaries(self):
        h=c.hypothesis(c.evaluate(self.rows,self.config))
        self.assertEqual(h['published_observation']['treated_activity_pct_WT'],9.9)
        self.assertIsNone(h['published_observation']['delta_uncertainty'])
        self.assertEqual(h['status'],'design_only_not_executed')
    def test_comparison_rejects_drift(self):
        r=c.evaluate(self.rows,self.config); r['scenarios'][0]['metrics']['zero_effect']['mae_pp']+=0.01
        with self.assertRaises(ValueError):c.compare(r,c.read(c.BUNDLE/'reference/pilot.json'))

if __name__=='__main__':unittest.main()

import json, os, subprocess, sys, unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from pipettecal.model import load_problem, ModelError
from pipettecal.calibrate import calibrate, verify
from pipettecal.report import build_report

class TestModel(unittest.TestCase):
    def test_basic(self):
        data = {"target_volume":1000.0,"unit":"uL","measurements":[{"mass_g":1.0,"temperature_c":20.0},{"mass_g":1.0,"temperature_c":20.0}]}
        p = load_problem(data)
        self.assertEqual(len(p.measurements),2)
    def test_too_few(self):
        with self.assertRaises(ModelError):
            load_problem({"target_volume":1000.0,"measurements":[{"mass_g":1.0,"temperature_c":20.0}]})
    def test_bad_unit(self):
        with self.assertRaises(ModelError):
            load_problem({"target_volume":1000.0,"unit":"g","measurements":[{"mass_g":1.0,"temperature_c":20.0},{"mass_g":1.0,"temperature_c":20.0}]})

class TestCalibrate(unittest.TestCase):
    def setUp(self):
        data = {"target_volume":1000.0,"unit":"uL","tolerance_percent":1.0,"max_cv_percent":0.5,
                "measurements":[{"mass_g":0.9985,"temperature_c":21.0},{"mass_g":0.9991,"temperature_c":21.2},
                               {"mass_g":0.9979,"temperature_c":21.1},{"mass_g":0.9988,"temperature_c":21.3}]}
        self.problem = load_problem(data)
    def test_calibrate(self):
        r = calibrate(self.problem)
        self.assertIn(r.status, ("pass","fail"))
        self.assertEqual(len(r.replicates_ml),4)
        self.assertGreater(r.mean_ml,0)
    def test_verify(self):
        r = calibrate(self.problem)
        rep = build_report(self.problem, r)
        ok, errs = verify(self.problem, rep)
        self.assertTrue(ok, errs)

class TestCLI(unittest.TestCase):
    def test_demo(self):
        rc = subprocess.run([sys.executable,"-m","pipettecal","demo"], cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(rc.returncode in (0,1), True, rc.stderr+rc.stdout)

if __name__ == "__main__":
    unittest.main()

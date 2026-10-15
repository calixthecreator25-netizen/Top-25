"""History must preserve dated snapshots and calculate movement across dates."""
import json, tempfile, unittest
from pathlib import Path
from scripts.archive_rankings import archive

class ArchiveTests(unittest.TestCase):
    def test_snapshot_is_immutable_and_movement_is_computed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);current=root/"current";history=root/"history";current.mkdir()
            def write(date, order):
                for division in ("fbs","fcs"):
                    teams=[{"id":str(i),"rank":n,"merit_score":60-n} for n,i in enumerate(order,1)]
                    (current/(division+".json")).write_text(json.dumps({"as_of":date,"teams":teams}))
            write("2026-10-05",[1,2])
            archive(current,history)
            write("2026-10-12",[2,1])
            archive(current,history)
            rows=json.loads((current/"fbs.json").read_text())["teams"]
            self.assertEqual(rows[0]["rank_change"],1)
            self.assertEqual(rows[1]["rank_change"],-1)
            self.assertEqual(json.loads((history/"2026-10-05"/"fbs.json").read_text())["teams"][0]["id"],"1")
            self.assertEqual(json.loads((history/"index.json").read_text())["dates"],["2026-10-12","2026-10-05"])
            write("2026-10-12",[1,2])
            archive(current,history)
            self.assertEqual(json.loads((history/"2026-10-12"/"fbs.json").read_text())["teams"][0]["id"],"2")

if __name__=="__main__":
    unittest.main()

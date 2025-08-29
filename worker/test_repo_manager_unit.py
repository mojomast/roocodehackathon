import os
import tempfile
from worker.repo_manager import RepoManager


def test_validate_repository_valid_and_invalid():
    rm = RepoManager()
    # invalid path
    res = rm.validate_repository("/no/such/path")
    assert res["valid"] is False
    # valid temp repo
    with tempfile.TemporaryDirectory() as d:
        os.makedirs(os.path.join(d, ".git"))
        with open(os.path.join(d, "a.py"), "w") as f:
            f.write("print('x')\n")
        out = rm.validate_repository(d)
        assert out["valid"] is True
        assert out["source_files_count"] >= 1
import subprocess


def test_flake8_clean():
    """Fail if any errors found"""
    res = subprocess.run(
        ["flake8", "scripts", "ml-workflow-template"],
        capture_output=True, text=True
    )
    assert res.returncode == 0, f"Lint errors:\n{res.stdout}"

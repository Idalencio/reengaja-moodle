from pathlib import Path
import subprocess
import sys

root = Path(__file__).resolve().parents[1]
(root / "test-results").mkdir(exist_ok=True)
(root / "evidencias").mkdir(exist_ok=True)
unit = subprocess.run([sys.executable, "-m", "pytest", "-q", "--cov", "--cov-report=term",
                       "--cov-report=json:test-results/coverage.json", "--junitxml=test-results/junit.xml"],
                      cwd=root, capture_output=True, text=True)
print(unit.stdout + unit.stderr, end="", flush=True)
(root / "test-results/unitarios.txt").write_text(unit.stdout + unit.stderr)
if unit.returncode:
    raise SystemExit(unit.returncode)
integration = subprocess.run([sys.executable, "scripts/integration.py"], cwd=root, capture_output=True, text=True)
print(integration.stdout + integration.stderr, end="", flush=True)
(root / "evidencias/integracao.log").write_text(integration.stdout + integration.stderr)
raise SystemExit(integration.returncode)

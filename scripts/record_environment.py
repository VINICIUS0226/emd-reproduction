from __future__ import annotations

import importlib.metadata
import json
import os
import platform
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "environment"


def package_version(name: str) -> str | None:
    try:
        return importlib.metadata.version(name)
    except importlib.metadata.PackageNotFoundError:
        return None


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    packages = [
        "pandas",
        "numpy",
        "scikit-learn",
        "PyYAML",
        "joblib",
        "matplotlib",
        "seaborn",
        "torch",
        "transformers",
        "openai",
    ]
    info = {
        "python": sys.version,
        "executable": sys.executable,
        "platform": platform.platform(),
        "system": platform.system(),
        "release": platform.release(),
        "version": platform.version(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "cpu_count": os.cpu_count(),
        "openai_api_key_set": bool(os.environ.get("OPENAI_API_KEY")),
        "packages": {name: package_version(name) for name in packages},
    }
    (OUT / "environment.json").write_text(json.dumps(info, indent=2), encoding="utf-8")
    lines = [
        "# Ambiente de execucao",
        "",
        f"- Python: `{info['python'].split()[0]}`",
        f"- Plataforma: `{info['platform']}`",
        f"- Maquina: `{info['machine']}`",
        f"- Processador: `{info['processor']}`",
        f"- CPUs logicas: `{info['cpu_count']}`",
        f"- OPENAI_API_KEY configurada: `{info['openai_api_key_set']}`",
        "",
        "## Pacotes",
        "",
        "| Pacote | Versao |",
        "| --- | --- |",
    ]
    for name, version in info["packages"].items():
        lines.append(f"| {name} | {version or 'nao instalado'} |")
    (OUT / "environment.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(info, indent=2))


if __name__ == "__main__":
    main()

import json
from pathlib import Path

class IndexManifestStore:

    def __init__(self, manifest_path: Path):
        self._manifest_path = manifest_path

    def load(self) -> dict[str, str]:
        if not self._manifest_path.exists():
            return {}
        try:
            data = json.loads(self._manifest_path.read_text(encoding='utf-8'))
        except (OSError, json.JSONDecodeError):
            return {}
        if isinstance(data, dict):
            return {str(key): str(value) for key, value in data.items()}
        return {}

    def save(self, manifest: dict[str, str]) -> None:
        self._manifest_path.parent.mkdir(parents=True, exist_ok=True)
        self._manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')

import subprocess
import sys
from pathlib import Path


def test_importing_application_does_not_import_bedrock_sdk_adapter() -> None:
    repository_root = Path(__file__).resolve().parents[1]
    code = (
        "import sys; "
        "import api_supplier.main; "
        "assert 'api_supplier.infrastructure.ai.bedrock_supplier_analyzer' "
        "not in sys.modules"
    )

    result = subprocess.run(
        [sys.executable, "-c", code],
        cwd=repository_root,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr

"""Pytest configuration for unit tests"""

from pathlib import Path
import sys

# Add repository root to Python path for imports like 'scripts.generate.generator'
REPO_ROOT = Path(__file__).parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
DOCS_DIR = REPO_ROOT / "blocknet-api-docs" / "source" / "includes"
XBRIDGE_DOC = DOCS_DIR / "_xbridge.md"
XROUTER_DOC = DOCS_DIR / "_xrouter.md"
TEST_OUTPUT_DIR = Path("/tmp/test_mcp_output")

TEST_XBRIDGE_DOC = XBRIDGE_DOC
TEST_XROUTER_DOC = XROUTER_DOC

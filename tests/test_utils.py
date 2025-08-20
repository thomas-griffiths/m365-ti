import sys
from pathlib import Path

# Ensure src directory is on sys.path
sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

from utils import contains_any


def test_contains_any_matches_exact_domain():
    assert contains_any("domain.com", ["domain.com"]) is True


def test_contains_any_ignores_similar_domains():
    needles = ["domain.com"]
    assert contains_any("sub.domain.com", needles) is False
    assert contains_any("domain.com.bad", needles) is False
    assert contains_any("notdomain.com", needles) is False

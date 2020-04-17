# Configuration for pytest to automatically collect types.
# Thanks to Guilherme Salgado.
import os
from typing import Any

import pytest  # type: ignore
from pyannotate_runtime import collect_types  # type: ignore


def pytest_collection_finish(session: Any) -> None:
    """Handle the pytest collection finish hook: configure pyannotate.
    Explicitly delay importing `collect_types` until all tests have
    been collected.  This gives gevent a chance to monkey patch the
    world before importing pyannotate.
    """
    collect_types.init_types_collection()


@pytest.fixture(autouse=True)  # type: ignore
def collect_types_fixture() -> Any:
    collect_types.start()
    yield
    collect_types.stop()


def pytest_sessionfinish(session: Any, exitstatus: Any) -> None:
    os.makedirs("build/", exist_ok=True)
    collect_types.dump_stats("build/type_info.json")

"""Tests tutorials individually.

Note that for easy debugging, you can just put a `pdb` trace
right before `importlib.import_module` in any of the tests,
and then `n` that will provide the full log trace.
"""
import importlib
import logging
import multiprocessing
import os
from pathlib import Path
import shutil
import time
from typing import Dict, Final, Generator, Optional

import jupytext
import nbformat
from nbformat import NotebookNode
import pytest
from pytest import MonkeyPatch, TempPathFactory, fixture

from bitfount import BitfountSchema
from bitfount.config import _PRODUCTION_ENVIRONMENT, _STAGING_ENVIRONMENT
from tests.integration.tutorials.notebook_logging import (
    _LOG_QUEUE_AUTH_KEY,
    _LOG_QUEUE_PORT,
    LogQueueManager,
)
from tests.integration.utils import (
    _patch_authentication_code,
    get_patched_authentication_code_nb,
)
from tests.utils.helper import (
    tutorial_2_test,
    tutorial_4_test,
    tutorial_6_test,
    tutorial_7_test,
    tutorial_8_test,
    tutorial_9_test,
    tutorial_11_test,
    tutorial_13_test,
    tutorial_15_test,
    tutorial_test,
)

# User details for running tests
logger = logging.getLogger(__name__)

# Establish if MPS support is available
# We do this here so that (a) it occurs before anything else causes problems with
# the LRU cache and (b) so that it is globally available between processes/tests
import torch  # noqa: E402

MPS_AVAILABLE = False

try:
    logger.info("Establishing torch MPS support")
    MPS_AVAILABLE = torch.backends.mps.is_available()
except AttributeError:
    pass

PASSWORD_ENVVAR: Final[str] = "BF_USER_PASSWORD"
ENVIRONMENT_ENVVAR: Final[str] = "BITFOUNT_ENVIRONMENT"
STAGING_USERNAME: Final[str] = "e2e_modeller"
PRODUCTION_USERNAME: Final[str] = "bitfount-rel"


MODELLER_TIMEOUT_PERIOD: Final[int] = 5 * 60  # 5 minutes
IMAGE_MODELLER_TIMEOUT_PERIOD: Final[int] = 12 * 60  # 12 minutes
MULTI_POD_MODELLER_TIMEOUT_PERIOD: Final[int] = 12 * 60  # 12 minutes
POD_TEST_TIMEOUT_PERIOD: Final[int] = 3 * 60  # 3 minutes

# This is the maximum time that a _background_ Pod will be running for.
# All tasks should comfortably be run in this time.
TUTORIALS_PATH: str = "tutorials"
POD_TIMEOUT_PERIOD: Final[int] = 45 * 60  # 45 minutes
POD_TUTORIALS_DIR = "Connecting Data & Creating Pods"
BASIC_DATA_SCIENCE_TUTORIALS_DIR = "Running Basic Data Science Tasks"
ADVANCED_DATA_SCIENCE_TUTORIALS_DIR = "Advanced Data Science Tasks"
PRIVACY_PRESERVING_TUTORIALS_DIR = "Privacy-Preserving Techniques"
TUTORIALS: Final[Dict[int, str]] = {
    1: f"{TUTORIALS_PATH}/{POD_TUTORIALS_DIR}/running_a_pod",
    2: f"{TUTORIALS_PATH}/{BASIC_DATA_SCIENCE_TUTORIALS_DIR}/querying_and_training_a_model",  # noqa: B950
    3: f"{TUTORIALS_PATH}/{POD_TUTORIALS_DIR}/running_a_pod_using_yaml",
    4: f"{TUTORIALS_PATH}/{BASIC_DATA_SCIENCE_TUTORIALS_DIR}/training_a_model_on_two_pods",  # noqa: B950
    5: f"{TUTORIALS_PATH}/{POD_TUTORIALS_DIR}/running_an_image_data_pod",
    6: f"{TUTORIALS_PATH}/{BASIC_DATA_SCIENCE_TUTORIALS_DIR}/training_on_images",
    7: f"{TUTORIALS_PATH}/{ADVANCED_DATA_SCIENCE_TUTORIALS_DIR}/training_a_custom_model",  # noqa: B950
    8: f"{TUTORIALS_PATH}/{ADVANCED_DATA_SCIENCE_TUTORIALS_DIR}/using_pretrained_models",  # noqa: B950
    9: f"{TUTORIALS_PATH}/{PRIVACY_PRESERVING_TUTORIALS_DIR}/differential_privacy",
    10: f"{TUTORIALS_PATH}/{POD_TUTORIALS_DIR}/running_a_segmentation_data_pod",
    11: f"{TUTORIALS_PATH}/{ADVANCED_DATA_SCIENCE_TUTORIALS_DIR}/training_a_custom_segmentation_model",  # noqa: B950
    12: f"{TUTORIALS_PATH}/{PRIVACY_PRESERVING_TUTORIALS_DIR}/private-set-intersection",
    13: f"{TUTORIALS_PATH}/{PRIVACY_PRESERVING_TUTORIALS_DIR}/private-set-intersection-2",  # noqa: B950
    14: f"{TUTORIALS_PATH}/{POD_TUTORIALS_DIR}/running_a_pod_with_sql_views",
    15: f"{TUTORIALS_PATH}/{BASIC_DATA_SCIENCE_TUTORIALS_DIR}/querying_a_sql_view_pod",  # noqa: B950
}

# Constants representing the names of the pods as in the tutorials
CENSUS_INCOME_POD_NAME: Final[str] = "census-income-demo"
CENSUS_INCOME_DATASET_NAME: Final[str] = "census-income-demo-dataset"
REPLACEMENT_CI_DATASET_NAME: Final[str] = "census-income-dataset"
CENSUS_INCOME_SQL_VIEW_NAME: Final[str] = "census-income-demo-sql-view"
REPLACEMENT_CI_SQLVIEW_NAME: Final[str] = "census-income-sql"

CENSUS_INCOME_YAML_POD_NAME: Final[str] = "census-income-yaml-demo"
CENSUS_INCOME_YAML_DATASET_NAME: Final[str] = "census-income-yaml-demo-dataset"
REPLACEMENT_CI_YAML_DATASET_NAME: Final[str] = "census-income-yaml-dataset"


MNIST_POD_NAME: Final[str] = "mnist-demo"
MNIST_DATASET_NAME: Final[str] = "mnist-demo-dataset"
REPLACEMENT_MNIST_DATASET_NAME: Final[str] = "mnist-dataset"


SEGMENTATION_POD_NAME: Final[str] = "segmentation-data-demo"
SEGMENTATION_DATASET_NAME: Final[str] = "segmentation-data-demo-dataset"
REPLACEMENT_SEG_DATASET_NAME: Final[str] = "segmentation-data-dataset"


PSI_POD_NAME: Final[str] = "psi-demo"
PSI_DATASET_NAME: Final[str] = "psi-demo-dataset"
REPLACEMENT_PSI_DATASET_NAME: Final[str] = "psi-dataset"

# Path details
BITFOUNT_ROOT: Final[Path] = Path(__file__).parent.parent.parent.parent
TUTORIALS_ROOT: Final[Path] = BITFOUNT_ROOT / "tutorials"
TEST_SCHEMAS_PATH: Final[Path] = (
    BITFOUNT_ROOT / "tests" / "integration" / "resources" / "schemas"
)


@fixture
def username() -> str:
    """Name of user hosting pod."""
    return "test_username"


@fixture(scope="module")
def pod_suffix() -> str:
    """Generate a unique suffix for all pods in this test run."""
    return str(int(time.time()))  # unix timestamp


@pytest.fixture(scope="module")
def monkeypatch_module_scope() -> Generator[MonkeyPatch, None, None]:
    """Module-scoped monkeypatch."""
    mpatch = MonkeyPatch()
    yield mpatch
    mpatch.undo()


@fixture(autouse=True, scope="module")
def set_bitfount_environment(
    bitfount_env: str, monkeypatch_module_scope: MonkeyPatch
) -> None:
    """Monkeypatches Bitfount environment for tutorial tests.

    Guarantees that the envvar will be restored to the original value when
    tests finish.
    """
    monkeypatch_module_scope.setenv(ENVIRONMENT_ENVVAR, bitfount_env)


@fixture(scope="module")
def bitfount_env() -> str:
    """Determines the Bitfount environment to run the tests against.

    Defaults to staging if not explicitly set.
    """
    env = os.getenv(ENVIRONMENT_ENVVAR, _STAGING_ENVIRONMENT)
    logging.info(f'Using the "{env}" environment for these tutorial tests.')
    return env


@fixture(scope="module")
def authentication_user(bitfount_env: str) -> str:
    """Returns the username to use for authentication."""
    if bitfount_env == _STAGING_ENVIRONMENT:
        user = STAGING_USERNAME
    elif bitfount_env == _PRODUCTION_ENVIRONMENT:
        user = PRODUCTION_USERNAME
    else:
        raise ValueError(
            f"No authentication user defined"
            f' for Bitfount environment "{bitfount_env}"'
        )

    logging.info(f'Authentication user "{user}" will be used for these tests.')
    return user


@fixture(scope="module")
def authentication_password() -> str:
    """Returns the password for logging in as the target user.

    This will be supplied as the BF_USER_PASSWORD environment variable.
    """
    if not (pswd := os.getenv(PASSWORD_ENVVAR)):
        raise ValueError("No user password provided, unable to proceed.")
    else:
        return pswd


@fixture(scope="module")
def token_dir(tmp_path_factory: TempPathFactory) -> Path:
    """Temporary directory for tokens."""
    return tmp_path_factory.mktemp(".bitfount", numbered=False) / "bitfount_tokens"


@fixture(scope="function")
def patched_authentication_code(
    authentication_password: str, authentication_user: str, token_dir: Path
) -> str:
    """Returns code that patches bitfount session and OIDC authentication.

    This enables them to be run in a headless environment and still perform
    the OAuth logins required.
    """
    return get_patched_authentication_code_nb(
        authentication_user, authentication_password, token_dir
    )


@fixture(scope="module")
def census_income_pod_name(pod_suffix: str) -> str:
    """Name of the census income pod."""
    pod_name = f"{CENSUS_INCOME_POD_NAME}-{pod_suffix}"
    logger.info(f"Census income pod name: {pod_name}")
    return pod_name


@fixture(scope="module")
def census_income_dataset_name(pod_suffix: str) -> str:
    """Name of the census income dataset."""
    dataset_name = f"{REPLACEMENT_CI_DATASET_NAME}-{pod_suffix}"
    logger.info(f"Census income sql view pod name: {dataset_name}")
    return dataset_name


@fixture(scope="module")
def census_income_sql_view_name(pod_suffix: str) -> str:
    """Name of the census income dataset."""
    dataset_name = f"{REPLACEMENT_CI_SQLVIEW_NAME}-{pod_suffix}"
    logger.info(f"Census income sql view dataset name: {dataset_name}")
    return dataset_name


@fixture(scope="module")
def census_income_yaml_pod_name(pod_suffix: str) -> str:
    """Name of the census income pod."""
    pod_name = f"{CENSUS_INCOME_YAML_POD_NAME}-{pod_suffix}"
    logger.info(f"Census income yaml pod name: {pod_name}")
    return pod_name


@fixture(scope="module")
def census_income_yaml_dataset_name(pod_suffix: str) -> str:
    """Name of the census income dataset."""
    dataset_name = f"{REPLACEMENT_CI_YAML_DATASET_NAME}-{pod_suffix}"
    logger.info(f"Census income yaml dataset name: {dataset_name}")
    return dataset_name


def _replace_in_notebook_source_code(
    query: str, replacement: str, notebook: NotebookNode
) -> NotebookNode:
    """Replaces all occurrences of `query` with `replacement` in `notebook` source code.

    Args:
        query: code to replace
        replacement: replacement code
        notebook: notebook to have code replaced

    Returns:
        The same notebook with updated source code.
    """
    loggable_query = query.replace("\n", "\\n")
    loggable_replacement = replacement.replace("\n", "\\n")
    logger.info(f'Replacing "{loggable_query}" with "{loggable_replacement}" ')

    changes_made = False
    for i, cell in enumerate(notebook["cells"]):
        orig_source_code: str = cell["source"]
        if cell["cell_type"] == "code" and query in orig_source_code:
            # Mark if changes have been made so we know that things have been
            # applied correctly; every replace should cause at least one change.
            # We know it will be applied because of the `query in` check above.
            changes_made = True
            new_source_code = orig_source_code.replace(query, replacement)
            notebook["cells"][i]["source"] = new_source_code

    if not changes_made:
        raise AssertionError(
            f'No code was replaced when trying to replace "{loggable_query}" '
            f'with "{loggable_replacement}"'
        )
    return notebook


@fixture(scope="module")
def extra_imports() -> str:
    """Extra imports needed for testing."""
    return (
        "from bitfount.federated.keys_setup import _get_pod_keys\n"
        "from pathlib import Path\n"
        "from typing import Tuple, Any\n"
        "import unittest"
    )


@fixture(scope="module")
def change_dir_code() -> str:
    """Changes the directory of the jupyter notebook execution to `tutorials`."""
    return ""


@fixture(scope="module")
def log_queue_manager() -> Generator[LogQueueManager, None, None]:
    """Hosts and starts a LogQueueManager instance for logging messages."""
    with LogQueueManager(
        address=("", _LOG_QUEUE_PORT), authkey=_LOG_QUEUE_AUTH_KEY
    ) as manager:
        logger.info("LogQueueManager started")
        yield manager


@fixture
def keystore_path(tmp_path_factory: TempPathFactory) -> Path:
    """Temporary file for key storage."""
    return tmp_path_factory.mktemp("key_store") / "known_workers.yml"


@fixture(scope="module")
def mnist_pod_name(pod_suffix: str) -> str:
    """Name of the MNIST pod."""
    mnist_pod_name = f"{MNIST_POD_NAME}-{pod_suffix}"
    logger.info(f"MNIST pod name: {mnist_pod_name}")
    return mnist_pod_name


@fixture(scope="module")
def mnist_dataset_name(pod_suffix: str) -> str:
    """Name of the MNIST dataset."""
    mnist_dataset_name = f"{REPLACEMENT_MNIST_DATASET_NAME}-{pod_suffix}"
    logger.info(f"MNIST dataset name: {mnist_dataset_name}")
    return mnist_dataset_name


@fixture(scope="module")
def seg_pod_name(pod_suffix: str) -> str:
    """Name of the Segmentation pod."""
    seg_pod_name = f"{SEGMENTATION_POD_NAME}-{pod_suffix}"
    logger.info(f"Segmentation pod name: {seg_pod_name}")
    return seg_pod_name


@fixture(scope="module")
def seg_dataset_name(pod_suffix: str) -> str:
    """Name of the Segmentation dataset."""
    seg_dataset_name = f"{REPLACEMENT_SEG_DATASET_NAME}-{pod_suffix}"
    logger.info(f"Segmentation dataset name: {seg_dataset_name}")
    return seg_dataset_name


@fixture(scope="module")
def psi_pod_name(pod_suffix: str) -> str:
    """Name of the Segmentation pod."""
    psi_pod_name = f"{PSI_POD_NAME}-{pod_suffix}"
    logger.info(f"PSI pod name: {psi_pod_name}")
    return psi_pod_name


@fixture(scope="module")
def psi_dataset_name(pod_suffix: str) -> str:
    """Name of the PSI dataset."""
    psi_dataset_name = f"{REPLACEMENT_PSI_DATASET_NAME}-{pod_suffix}"
    logger.info(f"PSI dataset name: {psi_dataset_name}")
    return psi_dataset_name


def _fix_lru_caches() -> None:
    # The torch.backends.mps.is_available() function is wrapped in an LRU cache
    # which doesn't play nice with multiprocessing (in these tests). We remove the
    # caching functionality here so that the pod process and modeller process don't
    # interfere with each other.
    logger.warning("Patching LRU cache of torch.backends.mps.is_available if needed")
    logger.warning(f"MPS available = {MPS_AVAILABLE}")

    # We create literal functions here (rather than just one returning
    # MPS_AVAILABLE) so that torch doesn't need access to the variable from
    # this module
    if MPS_AVAILABLE:

        def _patched_is_available() -> bool:
            return True

    else:

        def _patched_is_available() -> bool:
            return False

    try:
        torch.backends.mps.is_available = _patched_is_available  # type: ignore[assignment] # Reason: monkeypatching # noqa: B950
    except AttributeError:
        pass


def start_census_income_pod(
    authentication_password: str,
    census_income_pod_name: str,
    census_income_dataset_name: str,
    authentication_user: str,
    extra_imports: str,
    token_dir: Path,
    keystore_path: Path,
    census_income_yaml_dataset_name: Optional[str] = None,
) -> None:
    """Tutorial 1 pod - tested in multiple tests."""
    # Change the notebook from markdown and replace pod name
    ntbk = jupytext.read(f"{TUTORIALS[1]}.md")
    # Exclude the prerequisite pip install
    ntbk = _replace_in_notebook_source_code("!pip install bitfount", "", ntbk)
    # Dataset name needs to be replaced before pod name is
    ntbk = _replace_in_notebook_source_code(
        CENSUS_INCOME_DATASET_NAME, census_income_dataset_name, ntbk
    )
    ntbk = _replace_in_notebook_source_code(
        CENSUS_INCOME_POD_NAME, census_income_pod_name, ntbk
    )

    if census_income_yaml_dataset_name is not None:
        ntbk = _replace_in_notebook_source_code(
            CENSUS_INCOME_YAML_DATASET_NAME, census_income_yaml_dataset_name, ntbk
        )

    ntbk = _replace_in_notebook_source_code(
        "pod = Pod(",
        f'{extra_imports}\npod_keys=_get_pod_keys( Path("{str(token_dir)}")/"pods" / "{census_income_pod_name}")\npod = Pod(pod_keys=pod_keys,username="{authentication_user}",',  # noqa: B950
        ntbk,
    )

    ntbk = _replace_in_notebook_source_code(
        "import nest_asyncio",
        f"""from pathlib import Path\nimport bitfount.hub.helper\nbitfount.hub.helper.BITFOUNT_KEY_STORE = Path("{str(keystore_path)}")\nimport nest_asyncio""",  # noqa: B950
        ntbk,
    )
    with open(f"{TUTORIALS[1]}.ipynb", mode="w", encoding="utf-8") as f:
        nbformat.write(ntbk, f)
    session_patcher, oidc_patcher = _patch_authentication_code(
        authentication_user, authentication_password, str(token_dir)
    )
    session_patcher.start()
    oidc_patcher.start()

    # Due to uses of lru_cache, we need to ensure that this pod has unique access
    # to imported libraries
    _fix_lru_caches()

    # Execute the notebook
    try:
        importlib.import_module(f"ipynb.fs.full.{TUTORIALS[1]}")
    except BaseException as e:
        logging.critical(f"Error in census-income-pod: {e}")
        logging.exception(e)
        raise


@tutorial_test
@tutorial_2_test
def test_tutorial_2(
    authentication_password: str,
    authentication_user: str,
    census_income_pod_name: str,
    census_income_dataset_name: str,
    extra_imports: str,
    keystore_path: Path,
    token_dir: Path,
) -> None:
    """Test for Tutorial 2 - querying_and_training_a_model.md."""
    # Set up pod
    pod_process = multiprocessing.Process(
        target=start_census_income_pod,
        name="Pod_Runner",
        args=(
            authentication_password,
            census_income_pod_name,
            census_income_dataset_name,
            authentication_user,
            extra_imports,
            token_dir,
            keystore_path,
        ),
    )
    pod_process.start()
    time.sleep(40)  # give the pods time to spin up
    assert pod_process.is_alive()

    # change the markdown notebooks to ipynb and replace relevant fields
    ntbk = jupytext.read(f"{TUTORIALS[2]}.md")
    # Exclude the prerequisite pip install
    ntbk = _replace_in_notebook_source_code("!pip install bitfount", "", ntbk)
    ntbk = _replace_in_notebook_source_code(
        CENSUS_INCOME_DATASET_NAME, census_income_dataset_name, ntbk
    )
    ntbk = _replace_in_notebook_source_code(
        "import nest_asyncio",
        f"""from pathlib import Path\nimport bitfount.hub.helper\nbitfount.hub.helper.BITFOUNT_KEY_STORE = Path("{str(keystore_path)}")\nimport nest_asyncio""",  # noqa: B950
        ntbk,
    )
    ntbk = _replace_in_notebook_source_code(
        "schema = get_pod_schema(pod_identifier)",
        "from bitfount import BitfountSchema\nschema = BitfountSchema."
        f"load_from_file('{str(TEST_SCHEMAS_PATH)}/census_income_schema.yaml')\n"  # noqa: B950
        f"schema.tables[0].name = '{census_income_dataset_name}'",
        ntbk,
    )
    with open(f"{TUTORIALS[2]}.ipynb", mode="w", encoding="utf-8") as f:
        nbformat.write(ntbk, f)

    # Patch OIDC challenge
    session_patcher, oidc_patcher = _patch_authentication_code(
        authentication_user, authentication_password, str(token_dir)
    )
    session_patcher.start()
    oidc_patcher.start()
    # Execute the notebook
    notebook = importlib.import_module(f"ipynb.fs.full.{TUTORIALS[2]}")
    # Check the notebook variables.
    assert (
        "occupation"
        in notebook.query_result[
            f"{authentication_user}/{census_income_dataset_name}"
        ].keys()
    )
    assert isinstance(notebook.schema, BitfountSchema)
    assert notebook.results is not None
    assert notebook.results[0]["AUC"] > 0.6
    assert notebook.protocol_results is not None
    assert notebook.protocol_results[0]["AUC"] > 0.6
    # terminate processes
    session_patcher.stop()
    oidc_patcher.stop()
    pod_process.terminate()
    os.remove(f"{TUTORIALS[2]}.ipynb")
    os.remove(f"{TUTORIALS[1]}.ipynb")


def start_yaml_census_income(
    authentication_password: str,
    census_income_yaml_pod_name: str,
    census_income_yaml_dataset_name: str,
    authentication_user: str,
    token_dir: Path,
    keystore_path: Path,
    census_income_dataset_name: str,
) -> None:
    """Tutorial 3, tested in the tutorial 4 test."""
    # Try changing working directory if not already changed
    ntbk = jupytext.read(f"{TUTORIALS[3]}.md")
    # Exclude the prerequisite pip install
    ntbk = _replace_in_notebook_source_code("!pip install bitfount", "", ntbk)
    # Dataset name needs to be replaced before pod name
    ntbk = _replace_in_notebook_source_code(
        CENSUS_INCOME_YAML_DATASET_NAME, census_income_yaml_dataset_name, ntbk
    )
    ntbk = _replace_in_notebook_source_code(
        f"name: {CENSUS_INCOME_YAML_POD_NAME}",
        f"username: {authentication_user}\nname: {CENSUS_INCOME_YAML_POD_NAME}",  # noqa: B950
        ntbk,
    )
    ntbk = _replace_in_notebook_source_code(
        CENSUS_INCOME_YAML_POD_NAME, census_income_yaml_pod_name, ntbk
    )
    ntbk = _replace_in_notebook_source_code(
        CENSUS_INCOME_DATASET_NAME, census_income_dataset_name, ntbk
    )

    ntbk = _replace_in_notebook_source_code(
        "import nest_asyncio",
        f"""from pathlib import Path\nimport bitfount.hub.helper\nbitfount.hub.helper.BITFOUNT_KEY_STORE = Path("{str(keystore_path)}")\nimport nest_asyncio""",  # noqa: B950
        ntbk,
    )
    with open(f"{TUTORIALS[3]}.ipynb", mode="w", encoding="utf-8") as f:
        nbformat.write(ntbk, f)
    session_patcher, oidc_patcher = _patch_authentication_code(
        authentication_user, authentication_password, str(token_dir)
    )
    session_patcher.start()
    oidc_patcher.start()

    # Due to uses of lru_cache, we need to ensure that this pod has unique access
    # to imported libraries
    _fix_lru_caches()

    importlib.import_module(f"ipynb.fs.full.{TUTORIALS[3]}")


@tutorial_test
@tutorial_4_test
def test_tutorial_4(
    authentication_password: str,
    authentication_user: str,
    census_income_pod_name: str,
    census_income_dataset_name: str,
    census_income_yaml_pod_name: str,
    census_income_yaml_dataset_name: str,
    extra_imports: str,
    keystore_path: Path,
    token_dir: Path,
) -> None:
    """Test for Tutorial 4 - training_a_model_on_two_pods.md."""
    # Set up the census-income pod
    pod_process = multiprocessing.Process(
        target=start_census_income_pod,
        name="Pod_Runner",
        args=(
            authentication_password,
            census_income_pod_name,
            census_income_dataset_name,
            authentication_user,
            extra_imports,
            token_dir,
            keystore_path,
            census_income_yaml_dataset_name,
        ),
    )
    pod_process.start()
    # Set up census-income-yaml pod
    yaml_pod_process = multiprocessing.Process(
        target=start_yaml_census_income,
        name="YAML_Pod_Runner",
        args=(
            authentication_password,
            census_income_yaml_pod_name,
            census_income_yaml_dataset_name,
            authentication_user,
            token_dir,
            keystore_path,
            census_income_dataset_name,
        ),
    )
    yaml_pod_process.start()
    time.sleep(40)  # give the pods time to spin up
    assert pod_process.is_alive()
    assert yaml_pod_process.is_alive()

    # change the markdown notebooks to ipynb and replace relevant fields
    ntbk = jupytext.read(f"{TUTORIALS[4]}.md")
    # Exclude the prerequisite pip install
    ntbk = _replace_in_notebook_source_code("!pip install bitfount", "", ntbk)
    ntbk = _replace_in_notebook_source_code(
        CENSUS_INCOME_DATASET_NAME, census_income_dataset_name, ntbk
    )
    ntbk = _replace_in_notebook_source_code(
        CENSUS_INCOME_YAML_DATASET_NAME, census_income_yaml_dataset_name, ntbk
    )
    ntbk = _replace_in_notebook_source_code(
        "import nest_asyncio",
        f"""from pathlib import Path\nimport bitfount.hub.helper\nbitfount.hub.helper.BITFOUNT_KEY_STORE = Path("{str(keystore_path)}")\nimport nest_asyncio""",  # noqa: B950
        ntbk,
    )
    ntbk = _replace_in_notebook_source_code(
        "schema = combine_pod_schemas([first_pod_identifier, second_pod_identifier])",  # noqa: B950
        f"schema = BitfountSchema.load_from_file('{str(TEST_SCHEMAS_PATH)}/census_income_schema.yaml')\n"  # noqa: B950
        "import copy;schema.tables.append(copy.deepcopy(schema.tables[0]))\n"  # noqa: B950
        f"schema.tables[0].name = '{census_income_dataset_name}';schema.tables[1].name = '{census_income_yaml_dataset_name}'",  # noqa: B950
        ntbk,
    )
    with open(f"{TUTORIALS[4]}.ipynb", mode="w", encoding="utf-8") as f:
        nbformat.write(ntbk, f)

    # Patch OIDC challenge
    session_patcher, oidc_patcher = _patch_authentication_code(
        authentication_user, authentication_password, str(token_dir)
    )
    session_patcher.start()
    oidc_patcher.start()
    # Execute the notebook
    notebook = importlib.import_module(  # noqa: B950 # this will be used when updating the tests
        f"ipynb.fs.full.{TUTORIALS[4]}"
    )
    assert isinstance(notebook.schema, BitfountSchema)
    assert notebook.results is not None
    assert len(notebook.results) == 2
    assert notebook.results[0]["AUC"] > 0.6
    assert notebook.results[1]["AUC"] > 0.6
    # terminate processes
    session_patcher.stop()
    oidc_patcher.stop()
    pod_process.terminate()
    yaml_pod_process.terminate()
    # terminate processes
    os.remove(f"{TUTORIALS[3]}.ipynb")
    os.remove(f"{TUTORIALS[1]}.ipynb")
    os.remove(f"{TUTORIALS[4]}.ipynb")


def start_mnist_pod(
    authentication_password: str,
    mnist_pod_name: str,
    mnist_dataset_name: str,
    authentication_user: str,
    extra_imports: str,
    token_dir: Path,
) -> None:
    """Tutorial 5 - tested in the test for tutorial 6."""
    ntbk = jupytext.read(f"{TUTORIALS[5]}.md")
    # Exclude the prerequisite pip install
    ntbk = _replace_in_notebook_source_code("!pip install bitfount", "", ntbk)
    # Dataset name needs to be replaced before pod name is.
    old_dataset_name = MNIST_DATASET_NAME
    replacement_dataset_name = mnist_dataset_name
    ntbk = _replace_in_notebook_source_code(
        old_dataset_name, replacement_dataset_name, ntbk
    )
    old_pod_name = MNIST_POD_NAME
    replacement_pod_name = mnist_pod_name
    ntbk = _replace_in_notebook_source_code(old_pod_name, replacement_pod_name, ntbk)
    ntbk = _replace_in_notebook_source_code(
        "pod = Pod(",
        f'{extra_imports}\npod_keys=_get_pod_keys( Path("{str(token_dir)}")/"pods" / "{replacement_dataset_name}")\npod = Pod(pod_keys=pod_keys,',  # noqa: B950
        ntbk,
    )
    ntbk = _replace_in_notebook_source_code(
        "%%writefile extract.py",
        "",
        ntbk,
    )
    ntbk = _replace_in_notebook_source_code(
        "%run extract.py",
        "",
        ntbk,
    )
    ntbk = _replace_in_notebook_source_code(
        "import nest_asyncio",
        f"""from pathlib import Path\nimport bitfount.hub.helper\nimport subprocess\nbitfount.hub.helper.BITFOUNT_KEY_STORE = Path("{str(keystore_path)}")\nimport nest_asyncio""",  # noqa: B950
        ntbk,
    )
    ntbk = _replace_in_notebook_source_code(
        f'name="{mnist_pod_name}",',
        f'username="{authentication_user}",\nname="{mnist_pod_name}",',
        ntbk,
    )
    with open(f"{TUTORIALS[5]}.ipynb", mode="w", encoding="utf-8") as f:
        nbformat.write(ntbk, f)
    session_patcher, oidc_patcher = _patch_authentication_code(
        authentication_user, authentication_password, str(token_dir)
    )
    session_patcher.start()
    oidc_patcher.start()

    # Due to uses of lru_cache, we need to ensure that this pod has unique access
    # to imported libraries
    _fix_lru_caches()

    importlib.import_module(f"ipynb.fs.full.{TUTORIALS[5]}")


@tutorial_test
@tutorial_6_test
def test_tutorial_6(
    authentication_password: str,
    authentication_user: str,
    extra_imports: str,
    keystore_path: Path,
    mnist_dataset_name: str,
    mnist_pod_name: str,
    token_dir: Path,
) -> None:
    """Test for tutorial 6 - running_an_image_data_pod.md."""
    # Set up MNIST pod
    pod_process = multiprocessing.Process(
        target=start_mnist_pod,
        name="MNIST_Pod_Runner",
        args=(
            authentication_password,
            mnist_pod_name,
            mnist_dataset_name,
            authentication_user,
            extra_imports,
            token_dir,
        ),
    )
    pod_process.start()
    time.sleep(40)  # give the pods time to spin up
    assert pod_process.is_alive()

    # Get the notebook
    ntbk = jupytext.read(f"{TUTORIALS[6]}.md")
    # Exclude the prerequisite pip install
    ntbk = _replace_in_notebook_source_code("!pip install bitfount", "", ntbk)
    # change the markdown notebooks to ipynb and replace relevant fields
    ntbk = _replace_in_notebook_source_code(
        MNIST_DATASET_NAME, mnist_dataset_name, ntbk
    )
    ntbk = _replace_in_notebook_source_code(
        "import nest_asyncio",
        f"""from pathlib import Path\nimport bitfount.hub.helper\nbitfount.hub.helper.BITFOUNT_KEY_STORE = Path("{str(keystore_path)}")\nimport nest_asyncio""",  # noqa: B950
        ntbk,
    )
    ntbk = _replace_in_notebook_source_code(
        "schema = get_pod_schema(pod_identifier)",
        "from bitfount import BitfountSchema\nschema = BitfountSchema."
        f"load_from_file('{str(TEST_SCHEMAS_PATH)}/mnist_schema.yaml')\n"
        f"schema.tables[0].name = '{mnist_dataset_name}'",
        ntbk,
    )
    with open(f"{TUTORIALS[6]}.ipynb", mode="w", encoding="utf-8") as f:
        nbformat.write(ntbk, f)

    # Patch OIDC challenge
    session_patcher, oidc_patcher = _patch_authentication_code(
        authentication_user, authentication_password, str(token_dir)
    )
    session_patcher.start()
    oidc_patcher.start()

    # Execute the notebook
    notebook = importlib.import_module(  # noqa: B950 # this will be used when updating the tests
        f"ipynb.fs.full.{TUTORIALS[6]}"
    )
    assert isinstance(notebook.schema, BitfountSchema)
    assert notebook.results is not None
    assert len(notebook.results) == 1
    assert notebook.results[0]["AUC"] > 0.4
    # terminate processes
    session_patcher.stop()
    oidc_patcher.stop()
    pod_process.terminate()
    os.remove(f"{TUTORIALS[6]}.ipynb")
    os.remove(f"{TUTORIALS[5]}.ipynb")
    os.remove("mnist_labels.csv")
    os.remove("mnist_images.zip")
    shutil.rmtree("mnist_images")


@tutorial_test
@tutorial_7_test
def test_tutorial_7(
    authentication_password: str,
    authentication_user: str,
    census_income_pod_name: str,
    census_income_dataset_name: str,
    extra_imports: str,
    keystore_path: Path,
    token_dir: Path,
) -> None:
    """Test for tutorial 7 - training_a_custom_model.md."""
    # change the markdown notebooks to ipynb and replace relevant fields
    ntbk = jupytext.read(f"{TUTORIALS[7]}.md")
    # Exclude the prerequisite pip install
    ntbk = _replace_in_notebook_source_code("!pip install bitfount", "", ntbk)
    old_dataset_name = CENSUS_INCOME_DATASET_NAME
    replacement_dataset_name = census_income_dataset_name
    ntbk = _replace_in_notebook_source_code(
        old_dataset_name, replacement_dataset_name, ntbk
    )
    ntbk = _replace_in_notebook_source_code(
        "import nest_asyncio",
        f"""from pathlib import Path\nimport bitfount.hub.helper\nbitfount.hub.helper.BITFOUNT_KEY_STORE = Path("{str(keystore_path)}")\nfrom MyCustomModel import MyCustomModel\nimport nest_asyncio""",  # noqa: B950
        ntbk,
    )
    ntbk = _replace_in_notebook_source_code(
        "schema = get_pod_schema(pod_identifier)",
        "from bitfount import BitfountSchema\nschema = BitfountSchema."
        f"load_from_file('{str(TEST_SCHEMAS_PATH)}/census_income_schema.yaml')\n"  # noqa: B950
        f"schema.tables[0].name = '{census_income_dataset_name}'",
        ntbk,
    )
    # Get the custom model from the notebook and save it separately
    for cell in ntbk.cells:
        if cell.cell_type == "code" and "class MyCustomModel" in cell.source:
            with open("MyCustomModel.py", mode="w", encoding="utf-8") as f:
                imports = """import torch\nfrom torch import nn as nn\nfrom torch.nn import functional as F\nfrom torchmetrics.functional import accuracy\nfrom bitfount import PyTorchBitfountModel, PyTorchClassifierMixIn\n"""  # noqa: B950
                model = imports + cell.source

                f.write(model)
            cell.source = ""
    with open(f"{TUTORIALS[7]}.ipynb", mode="w", encoding="utf-8") as f:
        nbformat.write(ntbk, f)
    # set up pod
    pod_process = multiprocessing.Process(
        target=start_census_income_pod,
        name="Pod_Runner",
        args=(
            authentication_password,
            census_income_pod_name,
            census_income_dataset_name,
            authentication_user,
            extra_imports,
            token_dir,
            keystore_path,
        ),
    )
    pod_process.start()
    time.sleep(40)  # give the pods time to spin up
    assert pod_process.is_alive()
    # Patch OIDC challenge
    session_patcher, oidc_patcher = _patch_authentication_code(
        authentication_user, authentication_password, str(token_dir)
    )
    session_patcher.start()
    oidc_patcher.start()
    # Execute the notebook
    notebook = importlib.import_module(  # noqa: B950 # this will be used when updating the tests
        f"ipynb.fs.full.{TUTORIALS[7]}"
    )
    assert isinstance(notebook.schema, BitfountSchema)
    assert notebook.local_results is not None
    assert float(notebook.local_results["val_acc"]) > 0.6
    assert notebook.results is not None
    assert len(notebook.results) == 2
    assert float(notebook.results[0]["val_acc"]) > 0.6
    assert float(notebook.results[1]["val_acc"]) > 0.6
    assert notebook.protocol_results is not None
    pod_name = authentication_user + "/" + replacement_dataset_name
    assert pod_name in notebook.protocol_results
    assert float(notebook.protocol_results[pod_name]["AUC"]) > 0.6
    # terminate processes
    session_patcher.stop()
    oidc_patcher.stop()
    pod_process.terminate()
    # cleanup
    os.remove(f"{TUTORIALS[1]}.ipynb")
    os.remove(f"{TUTORIALS[7]}.ipynb")
    os.remove("MyCustomModel.py")


@tutorial_test
@tutorial_8_test
def test_tutorial_8(
    authentication_password: str,
    authentication_user: str,
    census_income_pod_name: str,
    census_income_dataset_name: str,
    extra_imports: str,
    keystore_path: Path,
    token_dir: Path,
) -> None:
    """Tests tutorial 8 - using_pretrained_models.md."""
    # set up pod
    pod_process = multiprocessing.Process(
        target=start_census_income_pod,
        name="Pod_Runner",
        args=(
            authentication_password,
            census_income_pod_name,
            census_income_dataset_name,
            authentication_user,
            extra_imports,
            token_dir,
            keystore_path,
        ),
    )
    pod_process.start()
    time.sleep(40)  # give the pods time to spin up
    assert pod_process.is_alive()

    # Set up the notebook from `Running a pod` tutorial as it is used here
    # change the markdown notebooks to ipynb and replace relevant fields
    ntbk = jupytext.read(f"{TUTORIALS[2]}.md")
    # Exclude the prerequisite pip install
    ntbk = _replace_in_notebook_source_code("!pip install bitfount", "", ntbk)
    old_dataset_name = CENSUS_INCOME_DATASET_NAME
    replacement_dataset_name = census_income_dataset_name
    ntbk = _replace_in_notebook_source_code(
        old_dataset_name, replacement_dataset_name, ntbk
    )
    ntbk = _replace_in_notebook_source_code(
        "import nest_asyncio",
        f"""from pathlib import Path\nimport bitfount.hub.helper\nbitfount.hub.helper.BITFOUNT_KEY_STORE = Path("{str(keystore_path)}")\nimport nest_asyncio""",  # noqa: B950
        ntbk,
    )
    ntbk = _replace_in_notebook_source_code(
        "schema = get_pod_schema(pod_identifier)",
        "from bitfount import BitfountSchema\nschema = BitfountSchema."
        f"load_from_file('{str(TEST_SCHEMAS_PATH)}/census_income_schema.yaml')\n"  # noqa: B950
        f"schema.tables[0].name = '{census_income_dataset_name}'",
        ntbk,
    )
    # We only need the model fitting and serialization from Running a pod` tutorial.
    for cell in ntbk.cells:
        if (
            cell.cell_type == "code"
            and ("query" in cell.source or "protocol" in cell.source)
            and "import" not in cell.source
        ):
            cell.source = ""
    with open(f"{TUTORIALS[2]}.ipynb", mode="w", encoding="utf-8") as f:
        nbformat.write(ntbk, f)

    # change the markdown notebooks to ipynb and replace relevant fields
    ntbk = jupytext.read(f"{TUTORIALS[8]}.md")
    # Exclude the prerequisite pip install
    ntbk = _replace_in_notebook_source_code("!pip install bitfount", "", ntbk)
    ntbk = _replace_in_notebook_source_code(
        old_dataset_name, replacement_dataset_name, ntbk
    )
    ntbk = _replace_in_notebook_source_code(
        "import nest_asyncio",
        f"""from pathlib import Path\nimport bitfount.hub.helper\nbitfount.hub.helper.BITFOUNT_KEY_STORE = Path("{str(keystore_path)}")\nimport nest_asyncio""",  # noqa: B950
        ntbk,
    )
    ntbk = _replace_in_notebook_source_code(
        "schema = get_pod_schema(pod_identifier)",
        "from bitfount import BitfountSchema\nschema = BitfountSchema."
        f"load_from_file('{str(TEST_SCHEMAS_PATH)}/census_income_schema.yaml')\n"  # noqa: B950
        f"schema.tables[0].name = '{census_income_dataset_name}'",
        ntbk,
    )
    with open(f"{TUTORIALS[8]}.ipynb", mode="w", encoding="utf-8") as f:
        nbformat.write(ntbk, f)

    # Patch OIDC challenge
    session_patcher, oidc_patcher = _patch_authentication_code(
        authentication_user, authentication_password, str(token_dir)
    )
    session_patcher.start()
    oidc_patcher.start()

    # Execute the notebooks
    # First, Tutorial 2
    importlib.import_module(f"ipynb.fs.full.{TUTORIALS[2]}")
    # Now, Tutorial 8
    notebook = importlib.import_module(  # noqa: B950 # this will be used when updating the tests
        f"ipynb.fs.full.{TUTORIALS[8]}"
    )
    assert isinstance(notebook.schema, BitfountSchema)
    pod_name = authentication_user + "/" + replacement_dataset_name
    assert notebook.results is not None
    assert pod_name in notebook.results
    assert len(notebook.results) == 1
    assert notebook.results[pod_name]["AUC"] > 0.6
    assert notebook.protocol_results is not None
    assert pod_name in notebook.protocol_results
    assert notebook.protocol_results[pod_name]["AUC"] > 0.6
    # terminate processes
    session_patcher.stop()
    oidc_patcher.stop()
    pod_process.terminate()
    # cleanup
    os.remove(f"{TUTORIALS[1]}.ipynb")
    os.remove(f"{TUTORIALS[2]}.ipynb")
    os.remove(f"{TUTORIALS[8]}.ipynb")
    os.remove("training_a_model.pt")


@tutorial_test
@tutorial_9_test
def test_tutorial_9(
    authentication_password: str,
    authentication_user: str,
    census_income_pod_name: str,
    census_income_dataset_name: str,
    extra_imports: str,
    keystore_path: Path,
    token_dir: Path,
) -> None:
    """Test for Tutorial 9 - privacy_preserving_techniques.md."""
    # set up pod
    pod_process = multiprocessing.Process(
        target=start_census_income_pod,
        name="Pod_Runner",
        args=(
            authentication_password,
            census_income_pod_name,
            census_income_dataset_name,
            authentication_user,
            extra_imports,
            token_dir,
            keystore_path,
        ),
    )
    pod_process.start()
    time.sleep(40)  # give the pods time to spin up
    assert pod_process.is_alive()

    # change the markdown notebooks to ipynb and replace relevant fields
    ntbk = jupytext.read(f"{TUTORIALS[9]}.md")
    # Exclude the prerequisite pip install
    ntbk = _replace_in_notebook_source_code("!pip install bitfount", "", ntbk)
    old_dataset_name = CENSUS_INCOME_DATASET_NAME
    replacement_dataset_name = census_income_dataset_name
    ntbk = _replace_in_notebook_source_code(
        old_dataset_name, replacement_dataset_name, ntbk
    )
    ntbk = _replace_in_notebook_source_code(
        "import nest_asyncio",
        f"""from pathlib import Path\nimport bitfount.hub.helper\nbitfount.hub.helper.BITFOUNT_KEY_STORE = Path("{str(keystore_path)}")\nimport nest_asyncio""",  # noqa: B950
        ntbk,
    )
    ntbk = _replace_in_notebook_source_code(
        "schema = get_pod_schema(pod_identifier)",
        "from bitfount import BitfountSchema\nschema = BitfountSchema."
        f"load_from_file('{str(TEST_SCHEMAS_PATH)}/census_income_schema.yaml')\n"  # noqa: B950
        f"schema.tables[0].name = '{census_income_dataset_name}'",
        ntbk,
    )
    with open(f"{TUTORIALS[9]}.ipynb", mode="w", encoding="utf-8") as f:
        nbformat.write(ntbk, f)

    # Patch OIDC challenge
    session_patcher, oidc_patcher = _patch_authentication_code(
        authentication_user, authentication_password, str(token_dir)
    )
    session_patcher.start()
    oidc_patcher.start()

    # Execute the notebook
    notebook = importlib.import_module(  # noqa: B950 # this will be used when updating the tests
        f"ipynb.fs.full.{TUTORIALS[9]}"
    )
    assert isinstance(notebook.schema, BitfountSchema)
    pod_name = authentication_user + "/" + replacement_dataset_name
    assert notebook.query_result is not None
    assert pod_name in notebook.query_result
    assert "occupation" in notebook.query_result[pod_name]
    assert notebook.results is not None
    assert len(notebook.results) == 1
    assert "epsilon" in notebook.results[0]
    assert notebook.results[0]["AUC"] > 0.4
    # terminate processes
    session_patcher.stop()
    oidc_patcher.stop()
    pod_process.terminate()
    os.remove(f"{TUTORIALS[9]}.ipynb")
    os.remove(f"{TUTORIALS[1]}.ipynb")


#
def start_segmentation_pod(
    authentication_password: str,
    seg_pod_name: str,
    seg_dataset_name: str,
    authentication_user: str,
    extra_imports: str,
    token_dir: Path,
    keystore_path: Path,
) -> None:
    """Pod from Tutorial 10 - tested in the test for tutorial 11."""
    ntbk = jupytext.read(f"{TUTORIALS[10]}.md")
    # Exclude the prerequisite pip install
    ntbk = _replace_in_notebook_source_code("!pip install bitfount", "", ntbk)
    # Dataset name needs to be replaced before pod name is.
    old_dataset_name = SEGMENTATION_DATASET_NAME
    replacement_dataset_name = seg_dataset_name
    ntbk = _replace_in_notebook_source_code(
        old_dataset_name, replacement_dataset_name, ntbk
    )
    old_pod_name = SEGMENTATION_POD_NAME
    replacement_pod_name = seg_pod_name
    ntbk = _replace_in_notebook_source_code(old_pod_name, replacement_pod_name, ntbk)
    ntbk = _replace_in_notebook_source_code(
        "pod = Pod(",
        f'{extra_imports}\npod_keys=_get_pod_keys( Path("{str(token_dir)}")/"pods" / "{replacement_pod_name}")\npod = Pod(pod_keys=pod_keys,',  # noqa: B950,
        ntbk,
    )

    ntbk = _replace_in_notebook_source_code(
        f'name="{seg_pod_name}",',
        f'username="{authentication_user}",\nname="{seg_pod_name}",',
        ntbk,
    )
    ntbk = _replace_in_notebook_source_code(
        "import nest_asyncio",
        f"""from pathlib import Path\nimport bitfount.hub.helper\nbitfount.hub.helper.BITFOUNT_KEY_STORE = Path("{str(keystore_path)}")\nimport nest_asyncio""",  # noqa: B950,
        ntbk,
    )
    with open(f"{TUTORIALS[10]}.ipynb", mode="w", encoding="utf-8") as f:
        nbformat.write(ntbk, f)
    session_patcher, oidc_patcher = _patch_authentication_code(
        authentication_user, authentication_password, str(token_dir)
    )
    session_patcher.start()
    oidc_patcher.start()
    importlib.import_module(f"ipynb.fs.full.{TUTORIALS[10]}")


@tutorial_test
@tutorial_11_test
def test_tutorial_11(
    authentication_password: str,
    authentication_user: str,
    extra_imports: str,
    keystore_path: Path,
    seg_dataset_name: str,
    seg_pod_name: str,
    token_dir: Path,
) -> None:
    """Test for tutorial 11- training_a_custom_segmentation_model.md."""
    # set up pod
    pod_process = multiprocessing.Process(
        target=start_segmentation_pod,
        name="Segmentation_Pod_Runner",
        args=(
            authentication_password,
            seg_pod_name,
            seg_dataset_name,
            authentication_user,
            extra_imports,
            token_dir,
            keystore_path,
        ),
    )
    pod_process.start()
    time.sleep(30)  # give the pods time to spin up
    assert pod_process.is_alive()

    # change the markdown notebooks to ipynb and replace relevant fields
    ntbk = jupytext.read(f"{TUTORIALS[11]}.md")
    # Exclude the prerequisite pip install
    ntbk = _replace_in_notebook_source_code("!pip install bitfount", "", ntbk)
    ntbk = _replace_in_notebook_source_code(
        SEGMENTATION_DATASET_NAME, seg_dataset_name, ntbk
    )
    ntbk = _replace_in_notebook_source_code(
        "import nest_asyncio",
        f"""from pathlib import Path\nimport bitfount.hub.helper\nbitfount.hub.helper.BITFOUNT_KEY_STORE = Path("{str(keystore_path)}")\nfrom MyCustomSegmentationModel import MyCustomSegmentationModel\nimport nest_asyncio""",  # noqa: B950
        ntbk,
    )
    ntbk = _replace_in_notebook_source_code(
        "schema = get_pod_schema(pod_identifier)",
        "from bitfount import BitfountSchema\nschema = BitfountSchema."
        f"load_from_file('{str(TEST_SCHEMAS_PATH)}/data-schema-segmentation-data-demo.yaml')\n"  # noqa: B950
        f"schema.tables[0].name = '{seg_dataset_name}'",
        ntbk,
    )
    for cell in ntbk.cells:
        if (
            cell.cell_type == "code"
            and "class MyCustomSegmentationModel" in cell.source
        ):
            with open("MyCustomSegmentationModel.py", mode="w", encoding="utf-8") as f:
                imports = """import torch\nfrom torch import nn as nn\nfrom torch.nn import functional as F\nfrom bitfount import SoftDiceLoss, SEGMENTATION_METRICS, PyTorchBitfountModel, PyTorchClassifierMixIn\n"""  # noqa: B950
                model = imports + cell.source

                f.write(model)
            cell.source = ""
    with open(f"{TUTORIALS[11]}.ipynb", mode="w", encoding="utf-8") as f:
        nbformat.write(ntbk, f)

    # Patch OIDC challenge
    session_patcher, oidc_patcher = _patch_authentication_code(
        authentication_user, authentication_password, str(token_dir)
    )
    session_patcher.start()
    oidc_patcher.start()

    # Execute the notebook
    notebook = importlib.import_module(  # noqa: B950 # this will be used when updating the tests
        f"ipynb.fs.full.{TUTORIALS[11]}"
    )
    assert notebook.MyCustomSegmentationModel is not None
    assert isinstance(notebook.schema, BitfountSchema)
    assert notebook.results is not None
    # terminate processes
    session_patcher.stop()
    oidc_patcher.stop()
    pod_process.terminate()
    os.remove(f"{TUTORIALS[10]}.ipynb")
    os.remove(f"{TUTORIALS[11]}.ipynb")


def start_psi_pod(
    authentication_password: str,
    psi_pod_name: str,
    psi_dataset_name: str,
    authentication_user: str,
    extra_imports: str,
    token_dir: Path,
    keystore_path: Path,
) -> None:
    """Pod from Tutorial 12 - tested in the test for tutorial 13."""
    ntbk = jupytext.read(f"{TUTORIALS[12]}.md")
    # Exclude the prerequisite pip install
    ntbk = _replace_in_notebook_source_code("!pip install bitfount", "", ntbk)
    # Dataset name needs to be replaced before pod name is.
    old_dataset_name = PSI_DATASET_NAME
    replacement_dataset_name = psi_dataset_name
    ntbk = _replace_in_notebook_source_code(
        old_dataset_name, replacement_dataset_name, ntbk
    )
    old_pod_name = PSI_POD_NAME
    replacement_pod_name = psi_pod_name
    ntbk = _replace_in_notebook_source_code(old_pod_name, replacement_pod_name, ntbk)
    ntbk = _replace_in_notebook_source_code(
        "pod = Pod(",
        f'{extra_imports}\npod_keys=_get_pod_keys( Path("{str(token_dir)}")/"pods" / "{replacement_dataset_name}")\npod = Pod(pod_keys=pod_keys,',  # noqa: B950,
        ntbk,
    )

    ntbk = _replace_in_notebook_source_code(
        "datasources=[",
        f'username="{authentication_user}",\ndatasources=[',
        ntbk,
    )
    ntbk = _replace_in_notebook_source_code(
        "import nest_asyncio",
        f"""from pathlib import Path\nimport bitfount.hub.helper\nbitfount.hub.helper.BITFOUNT_KEY_STORE = Path("{str(keystore_path)}")\nimport nest_asyncio""",  # noqa: B950,
        ntbk,
    )
    with open(f"{TUTORIALS[12]}.ipynb", mode="w", encoding="utf-8") as f:
        nbformat.write(ntbk, f)
    session_patcher, oidc_patcher = _patch_authentication_code(
        authentication_user, authentication_password, str(token_dir)
    )
    session_patcher.start()
    oidc_patcher.start()
    importlib.import_module(f"ipynb.fs.full.{TUTORIALS[12]}")


@tutorial_test
@tutorial_13_test
def test_tutorial_13(
    authentication_password: str,
    authentication_user: str,
    extra_imports: str,
    keystore_path: Path,
    psi_pod_name: str,
    psi_dataset_name: str,
    token_dir: Path,
) -> None:
    """Test for tutorial 13- private-set-intersection-2.md."""
    # set up pod
    pod_process = multiprocessing.Process(
        target=start_psi_pod,
        name="Pod_Runner",
        args=(
            authentication_password,
            psi_pod_name,
            psi_dataset_name,
            authentication_user,
            extra_imports,
            token_dir,
            keystore_path,
        ),
    )
    pod_process.start()
    time.sleep(40)  # give the pods time to spin up
    assert pod_process.is_alive()
    # change the markdown notebooks to ipynb and replace relevant fields
    ntbk = jupytext.read(f"{TUTORIALS[13]}.md")
    # Exclude the prerequisite pip install
    ntbk = _replace_in_notebook_source_code("!pip install bitfount", "", ntbk)
    ntbk = _replace_in_notebook_source_code(PSI_DATASET_NAME, psi_dataset_name, ntbk)

    ntbk = _replace_in_notebook_source_code(
        "import nest_asyncio",
        f"""from pathlib import Path\nimport bitfount.hub.helper\nbitfount.hub.helper.BITFOUNT_KEY_STORE = Path("{str(keystore_path)}")\nimport nest_asyncio""",  # noqa: B950
        ntbk,
    )

    with open(f"{TUTORIALS[13]}.ipynb", mode="w", encoding="utf-8") as f:
        nbformat.write(ntbk, f)

    # Patch OIDC challenge
    session_patcher, oidc_patcher = _patch_authentication_code(
        authentication_user, authentication_password, str(token_dir)
    )
    session_patcher.start()
    oidc_patcher.start()
    # Execute the notebook
    notebook = importlib.import_module(f"ipynb.fs.full.{TUTORIALS[13]}")
    # Check the notebook variables.
    assert notebook.intersection_indices is not None
    assert len(notebook.intersection_indices) == 3
    # terminate processes
    session_patcher.stop()
    oidc_patcher.stop()
    pod_process.terminate()
    os.remove(f"{TUTORIALS[12]}.ipynb")
    os.remove(f"{TUTORIALS[13]}.ipynb")


def start_census_income_sql_views_pod(
    authentication_password: str,
    census_income_pod_name: str,
    census_income_dataset_name: str,
    census_income_sql_view_name: str,
    authentication_user: str,
    extra_imports: str,
    token_dir: Path,
    keystore_path: Path,
) -> None:
    """Tutorial 14 pod - tested in tutorial 15."""
    # Change the notebook from markdown and replace pod name
    ntbk = jupytext.read(f"{TUTORIALS[14]}.md")
    # Exclude the prerequisite pip install
    ntbk = _replace_in_notebook_source_code("!pip install bitfount", "", ntbk)
    # Dataset names needs to be replaced before pod name is.
    ntbk = _replace_in_notebook_source_code(
        CENSUS_INCOME_DATASET_NAME, census_income_dataset_name, ntbk
    )
    ntbk = _replace_in_notebook_source_code(
        CENSUS_INCOME_SQL_VIEW_NAME, census_income_sql_view_name, ntbk
    )
    ntbk = _replace_in_notebook_source_code(
        CENSUS_INCOME_POD_NAME, census_income_pod_name, ntbk
    )

    ntbk = _replace_in_notebook_source_code(
        "pod = Pod(",
        f'{extra_imports}\npod_keys=_get_pod_keys( Path("{str(token_dir)}")/"pods" / "{census_income_pod_name}")\npod = Pod(pod_keys=pod_keys,username="{authentication_user}",',  # noqa: B950
        ntbk,
    )

    ntbk = _replace_in_notebook_source_code(
        "import nest_asyncio",
        f"""from pathlib import Path\nimport bitfount.hub.helper\nbitfount.hub.helper.BITFOUNT_KEY_STORE = Path("{str(keystore_path)}")\nimport nest_asyncio""",  # noqa: B950
        ntbk,
    )
    with open(f"{TUTORIALS[14]}.ipynb", mode="w", encoding="utf-8") as f:
        nbformat.write(ntbk, f)
    session_patcher, oidc_patcher = _patch_authentication_code(
        authentication_user, authentication_password, str(token_dir)
    )
    session_patcher.start()
    oidc_patcher.start()

    # Due to uses of lru_cache, we need to ensure that this pod has unique access
    # to imported libraries
    _fix_lru_caches()

    # Execute the notebook
    try:
        importlib.import_module(f"ipynb.fs.full.{TUTORIALS[14]}")
    except BaseException as e:
        logging.critical(f"Error in census-income-pod: {e}")
        logging.exception(e)


@tutorial_test
@tutorial_15_test
def test_census_income_sql_views(
    authentication_password: str,
    census_income_pod_name: str,
    census_income_dataset_name: str,
    census_income_sql_view_name: str,
    authentication_user: str,
    extra_imports: str,
    token_dir: Path,
    keystore_path: Path,
) -> None:
    """Test for Tutorial 15 - querying_a_sql_view_pod.md."""
    # Set up pod
    pod_process = multiprocessing.Process(
        target=start_census_income_sql_views_pod,
        name="Pod_Runner",
        args=(
            authentication_password,
            census_income_pod_name,
            census_income_dataset_name,
            census_income_sql_view_name,
            authentication_user,
            extra_imports,
            token_dir,
            keystore_path,
        ),
    )
    pod_process.start()
    time.sleep(40)  # give the pods time to spin up
    assert pod_process.is_alive()

    # change the markdown notebooks to ipynb and replace relevant fields
    ntbk = jupytext.read(f"{TUTORIALS[15]}.md")
    # Exclude the prerequisite pip install
    ntbk = _replace_in_notebook_source_code("!pip install bitfount", "", ntbk)
    ntbk = _replace_in_notebook_source_code(
        CENSUS_INCOME_DATASET_NAME, census_income_dataset_name, ntbk
    )
    ntbk = _replace_in_notebook_source_code(
        CENSUS_INCOME_SQL_VIEW_NAME, census_income_sql_view_name, ntbk
    )

    with open(f"{TUTORIALS[15]}.ipynb", mode="w", encoding="utf-8") as f:
        nbformat.write(ntbk, f)

    # Patch OIDC challenge
    session_patcher, oidc_patcher = _patch_authentication_code(
        authentication_user, authentication_password, str(token_dir)
    )
    session_patcher.start()
    oidc_patcher.start()

    # Execute the notebook
    notebook = importlib.import_module(f"ipynb.fs.full.{TUTORIALS[15]}")
    # Check the notebook variables.
    assert (
        "occupation"
        in notebook.query_result[
            f"{authentication_user}/{census_income_dataset_name}"
        ].keys()
    )
    assert (
        "age"
        in notebook.view_query_result[
            f"{authentication_user}/{census_income_sql_view_name}"
        ].keys()
    )
    assert isinstance(notebook.query_result, dict)
    # terminate processes
    session_patcher.stop()
    oidc_patcher.stop()
    pod_process.terminate()
    os.remove(f"{TUTORIALS[14]}.ipynb")
    os.remove(f"{TUTORIALS[15]}.ipynb")

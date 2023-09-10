from os.path import join, dirname
from types import ModuleType
from pytest import fixture

from mypy import api

from budosystems.xtra import mypy_plugin


def test_subproject_import():
    assert isinstance(mypy_plugin, ModuleType)


def test_run_budosystems_models():
    args = [
        '-p', 'budosystems.models',
        '--config-file', join(dirname(__file__), 'budosystems-core-mypy.ini'),
        '--show-traceback'
    ]

    result = api.run(args)

    if result[0]:
        print('\nType checking report:\n')
        print(result[0])  # stdout

    if result[1]:
        print('\nError report:\n')
        print(result[1])  # stderr

    print('\nExit status:', result[2])
    assert 0 <= result[2] < 2, "mypy did not terminate normally."

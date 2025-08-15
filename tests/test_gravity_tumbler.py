import types
import pathlib
import numpy as np
import re


def load_tumble():
    path = pathlib.Path(__file__).resolve().parent.parent / "weekly" / "gravitiy-tumbler.py"
    source = path.read_text()
    # collect import lines
    imports = []
    for line in source.splitlines():
        if line.startswith("import") or line.startswith("from"):
            imports.append(line)
    match = re.search(r"def tumble\(tower: np.ndarray\):.*?return new_tower", source, re.S)
    code = "\n".join(imports) + "\n" + match.group(0)
    module = types.ModuleType("gravity_tumbler")
    exec(code, module.__dict__)
    return module.tumble


def test_tumble_single_rotation():
    tumble = load_tumble()
    tower = np.array([
        list("..."),
        list(".#."),
        list("#.#"),
    ])
    result = tumble(tower)
    expected = np.array([
        list("..."),
        list("..#"),
        list(".##"),
    ])
    np.testing.assert_array_equal(result, expected)


def test_tumble_full_and_empty_columns_twice():
    tumble = load_tumble()
    tower = np.array([
        list("#.#"),
        list("#.#"),
        list("#.#"),
    ])
    after_first = tumble(tower)
    after_second = tumble(after_first)
    expected = np.array([
        list(".##"),
        list(".##"),
        list(".##"),
    ])
    np.testing.assert_array_equal(after_second, expected)

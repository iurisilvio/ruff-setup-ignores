import json
from pathlib import Path
from subprocess import PIPE, Popen

# Python built-in tomllib is read only, so I need tomlkit dependency.
import tomlkit
from ruff.__main__ import find_ruff_bin


class RuffError(Exception):
    pass


def call_ruff():
    ruff = find_ruff_bin()
    # Use custom per-file-ignores to not use the generated one.
    command = f"{ruff} . --quiet --format=json --per-file-ignores='_:F401'"
    child = Popen(command, shell=True, stdout=PIPE, stderr=PIPE)
    stdout, stderr = child.communicate()
    if stderr:
        raise RuffError(stderr)

    return json.loads(stdout)


def data_cleanup(violations):
    cwd = Path().absolute()
    per_file_violations = {}
    for violation in violations:
        # violation example
        # {
        #     "code": "E722",
        #     "message": "Do not use bare `except`",
        #     "fix": null,
        #     "location": {
        #         "row": 233,
        #         "column": 9
        #     },
        #     "end_location": {
        #         "row": 233,
        #         "column": 15
        #     },
        #     "filename": "/home/ubuntu/code/myapp/foo.py",
        #     "noqa_row": 233
        # }

        relative_filename = Path(violation["filename"]).relative_to(cwd)
        file_violations = per_file_violations.setdefault(str(relative_filename), set())
        file_violations.add(violation["code"])

    # Sort files and codes to make it deterministic.
    return {
        filename: list(sorted(codes))
        for filename, codes in sorted(per_file_violations.items())
    }


def update_toml(toml_file, data):
    toml_path = Path(toml_file)
    basename = toml_path.name
    toml_data = tomlkit.loads(toml_path.read_text())

    if basename == "pyproject.toml":
        toml_data.setdefault("tool", {})
        ruff_section = toml_data["tool"].setdefault("ruff", {})

    elif basename in {"ruff.toml", ".ruff.toml"}:
        try:
            ruff_section = toml_data["tool"]["ruff"]
        except KeyError:
            ruff_section = toml_data

    current = ruff_section.get("per-file-ignores", {})
    if current != data:
        ruff_section["per-file-ignores"] = data
        with open(toml_file, "w") as f:
            tomlkit.dump(toml_data, f)


def main(toml_file):
    data = call_ruff()
    clean_data = data_cleanup(data)
    update_toml(toml_file, clean_data)

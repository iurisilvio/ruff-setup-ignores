import sys
import ruff_setup_ignores


if __name__ == "__main__":
    try:
        toml_file = sys.argv[1]
    except IndexError:
        toml_file = "pyproject.toml"

    ruff_setup_ignores.main(toml_file)

SHELL := bash
.PHONY: docs
MINIMUM_PYTHON_VERSION := 3.8

# Create all hatch environments + install maya-zen-tools in mayapy
install:
	{ hatch --version || pipx install --upgrade hatch || python3 -m pip install --upgrade hatch ; } && \
	PATH="$$(hatch run python scripts/which_mayapy.py -d 2023):$$PATH" && \
	mayapy -m pip install pip --upgrade && \
	mayapy -m pip install mypy coverage pytest dependence -e . --upgrade --upgrade-strategy eager && \
	mayapy -m maya_zen_tools.install && \
	PATH="$$(hatch run python scripts/which_mayapy.py -d 2024):$$PATH" && \
	mayapy -m pip install pip --upgrade && \
	mayapy -m pip install mypy coverage pytest dependence -e . --upgrade --upgrade-strategy eager && \
	mayapy -m maya_zen_tools.install && \
	PATH="$$(hatch run python scripts/which_mayapy.py -d 2025):$$PATH" && \
	mayapy -m pip install pip --upgrade && \
	mayapy -m pip install mypy coverage pytest dependence -e . --upgrade --upgrade-strategy eager && \
	mayapy -m maya_zen_tools.install && \
	PATH="$$(hatch run python scripts/which_mayapy.py -d 2026):$$PATH" && \
	mayapy -m pip install pip --upgrade && \
	mayapy -m pip install mypy coverage pytest dependence -e . --upgrade --upgrade-strategy eager && \
	mayapy -m maya_zen_tools.install && \
	hatch env create default && \
	hatch env create docs && \
	hatch env create hatch-static-analysis && \
	hatch run python scripts/install_addin.py && \
	echo "Installation complete"

# Re-create all environments, from scratch (no reference to pinned
# requirements)
reinstall:
	{ hatch --version || pipx install --upgrade hatch || python3 -m pip install --upgrade hatch ; } && \
	hatch env prune && \
	make && \
	make requirements

# Zip the Autodesk App Store add-in package
addin:
	cd ApplicationAddins && \
	rm ZenTools.zip && \
	zip -x **/.* -X -r ZenTools.zip ZenTools && \
	hatch run python scripts/install_addin.py

distribute:
	hatch build && hatch publish && rm -rf dist

# Upgrade all requirements in all hatch environments, and in mayapy
upgrade:
	PATH="$$(hatch run python scripts/which_mayapy.py -d 2023):$$PATH" && \
	mayapy -m dependence upgrade\
	 . dependence && \
	PATH="$$(hatch run python scripts/which_mayapy.py -d 2024):$$PATH" && \
	mayapy -m dependence upgrade\
	 . dependence && \
	PATH="$$(hatch run python scripts/which_mayapy.py -d 2025):$$PATH" && \
	mayapy -m dependence upgrade\
	 . dependence && \
	PATH="$$(hatch run python scripts/which_mayapy.py -d 2026):$$PATH" && \
	mayapy -m dependence upgrade\
	 . dependence && \
	hatch run dependence upgrade\
	 --include-pointer /tool/hatch/envs/default\
	 --include-pointer /project\
	 pyproject.toml && \
	hatch run docs:dependence upgrade\
	 --include-pointer /tool/hatch/envs/docs\
	 pyproject.toml && \
	hatch run hatch-static-analysis:dependence upgrade\
	 --include-pointer /tool/hatch/envs/hatch-static-analysis\
	 pyproject.toml

# This will update pinned requirements to align with the
# package versions installed in each environment, and will align the project
# dependency versions with those installed in the default environment
requirements:
	PATH="$$(hatch run python scripts/which_mayapy.py -d 2023):$$PATH" && \
	mayapy -m dependence update\
	 --include-pointer /project\
	 pyproject.toml && \
	PATH="$$(hatch run python scripts/which_mayapy.py -d 2024):$$PATH" && \
	mayapy -m dependence update\
	 --include-pointer /project\
	 pyproject.toml && \
	PATH="$$(hatch run python scripts/which_mayapy.py -d 2025):$$PATH" && \
	mayapy -m dependence update\
	 --include-pointer /project\
	 pyproject.toml && \
	PATH="$$(hatch run python scripts/which_mayapy.py -d 2026):$$PATH" && \
	mayapy -m dependence update\
	 --include-pointer /project\
	 pyproject.toml && \
	hatch run dependence update\
	 --include-pointer /tool/hatch/envs/default\
	 pyproject.toml && \
	hatch run hatch-static-analysis:dependence update pyproject.toml --include-pointer /tool/hatch/envs/hatch-static-analysis && \
	hatch run docs:dependence update pyproject.toml --include-pointer /tool/hatch/envs/docs

# Test & check linting/formatting (for local use only)
test:
	{ hatch --version || pipx install --upgrade hatch || python3 -m pip install --upgrade hatch ; } && \
	PATH="$$(hatch run python scripts/which_mayapy.py -d 2023):$$PATH" && \
	mayapy -m pytest -s -vv -p no:faulthandler && \
	PATH="$$(hatch run python scripts/which_mayapy.py -d 2024):$$PATH" && \
	mayapy -m pytest -s -vv -p no:faulthandler && \
	PATH="$$(hatch run python scripts/which_mayapy.py -d 2025):$$PATH" && \
	mayapy -m pytest -s -vv -p no:faulthandler && \
	PATH="$$(hatch run python scripts/which_mayapy.py -d 2026):$$PATH" && \
	mayapy -m pytest -s -vv -p no:faulthandler && \
	hatch fmt --check && \
	hatch run mypy

format:
	hatch fmt --formatter && \
	hatch fmt --linter && \
	hatch run mypy && \
	echo "Format Successful!"

docs:
	hatch run docs:mkdocs build && \
	hatch run docs:mkdocs serve

# Cleanup untracked files
clean:
	git add . && git clean -f -e .zen -e .vscode -e .idea -x .

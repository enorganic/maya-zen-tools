SHELL := bash
.PHONY: docs
MINIMUM_PYTHON_VERSION := 3.8

# Create all hatch environments + install maya-zen-tools in mayapy
install:
	{ hatch --version || pipx install --upgrade hatch || python3 -m pip install --upgrade hatch ; } && \
	mayapy -m pip install pip --upgrade && \
	mayapy -m pip install dependence -e . --upgrade --upgrade-strategy eager && \
	hatch env create default && \
	hatch env create docs && \
	hatch env create hatch-test && \
	hatch env create hatch-static-analysis && \
	echo "Installation complete"

# Re-create all environments, from scratch (no reference to pinned
# requirements)
reinstall:
	{ hatch --version || pipx install --upgrade hatch || python3 -m pip install --upgrade hatch ; } && \
	hatch env prune && \
	make && \
	make requirements

distribute:
	hatch build && hatch publish && rm -rf dist

# Upgrade all requirements in all hatch environments, and in mayapy
upgrade:
	mayapy -m dependence freeze\
	 -nv '*'\
	 . dependence > .requirements.txt && \
	mayapy -m pip install --upgrade --upgrade-strategy eager\
	 -r .requirements.txt && \
	hatch run dependence freeze\
	 -nv '*'\
	 --include-pointer /tool/hatch/envs/default\
	 --include-pointer /project\
	 pyproject.toml >> .requirements.txt && \
	hatch run pip install --upgrade --upgrade-strategy eager\
	 -r .requirements.txt && \
	hatch run docs:dependence freeze\
	 -nv '*'\
	 --include-pointer /tool/hatch/envs/docs\
	 --include-pointer /project\
	 pyproject.toml > .requirements.txt && \
	hatch run docs:pip install --upgrade --upgrade-strategy eager\
	 -r .requirements.txt && \
	hatch run hatch-static-analysis:dependence freeze\
	 -nv '*'\
	 --include-pointer /tool/hatch/envs/docs\
	 --include-pointer /project\
	 pyproject.toml > .requirements.txt && \
	hatch run hatch-static-analysis:pip install --upgrade --upgrade-strategy eager\
	 -r .requirements.txt && \
	hatch run hatch-test.py$(MINIMUM_PYTHON_VERSION):dependence freeze\
	 -nv '*'\
	 --include-pointer /tool/hatch/envs/hatch-test\
	 --include-pointer /project\
	 pyproject.toml > .requirements.txt && \
	hatch run hatch-test.py$(MINIMUM_PYTHON_VERSION):pip install --upgrade --upgrade-strategy eager\
	 -r .requirements.txt && \
	 rm .requirements.txt && \
	make requirements

# This will update pinned requirements to align with the
# package versions installed in each environment, and will align the project
# dependency versions with those installed in the default environment
requirements:
	mayapy -m dependence update\
	 --include-pointer /project\
	 pyproject.toml && \
	hatch run dependence update\
	 --include-pointer /tool/hatch/envs/default\
	 pyproject.toml && \
	hatch run hatch-static-analysis:dependence update pyproject.toml --include-pointer /tool/hatch/envs/hatch-static-analysis && \
	hatch run docs:dependence update pyproject.toml --include-pointer /tool/hatch/envs/docs && \
	hatch run hatch-test.py$(MINIMUM_PYTHON_VERSION):dependence update pyproject.toml --include-pointer /tool/hatch/envs/hatch-test

# Test & check linting/formatting (for local use only)
test:
	{ hatch --version || pipx install --upgrade hatch || python3 -m pip install --upgrade hatch ; } && \\
	hatch fmt --check && hatch run mypy && hatch test && mayapy -

format:
	hatch fmt && \
	hatch run mypy && \
	echo "Format Successful!"

docs:
	hatch run docs:mkdocs build && \
	hatch run docs:mkdocs serve

# Cleanup untracked files
clean:
	git add . && git clean -f -e .zen -e .vscode -e .idea -x .

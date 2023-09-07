template = '''from taskr import runners, utils
from importlib.metadata import version

# Taskr config settings

## The default task to run, when typing just 'taskr'
DEFAULT = "all"

## If you want people to only use taskr in a VENV, set this to True. If not, set to
## false or delete it
VENV_REQUIRED = True

# If you want an environment variable file to be loaded before every task
# Files needs to be in the form of var_name=value
ENVS = ".env"

#Builds a wheel
def build() -> bool:
    return runners.run(["python -m build --wheel -n;", "echo 'Artifact:'; ls dist/"])


# Remove build artifacts, cache, etc.
def clean() -> bool:
    retValue = utils.cleanBuilds()

    if retValue:
        retValue = utils.cleanCompiles()

    return retValue


# Run tests
def test() -> bool:
    return runners.run("python -m pytest tests/ -vv")


# Run black
def fmt() -> bool:
    return runners.run("python -m black .")


# Sort imports
def sort() -> bool:
    return runners.run("python -m isort --atomic .")


# Run formatter
def fmt() -> bool:
    return runners.run("python -m black .")


# Checks types
def types() -> bool:
    return runners.run("python -m mypy src/*.py ")


def lint() -> bool:
    return runners.run("ruff  src/* --fix")


# Runs all static analysis tools
def all() -> bool:
    return runners.run_conditional(fmt, lint, types)


# Runs a server based on a passed in variable
def run_server(env: str = "dev") -> bool:
    ENVS = {"ENV": env}
    return runners.run("python server.py", ENVS)


# Bump setup.py version
def bump(version: str = "") -> bool:
    return utils.bumpVersion(version)


# Some non python tasks

# Squash the branch
def squish() -> None:
    runners.run("git rebase -i `git merge-base HEAD master`")


# Tag the branch
def tag(ver: str = "") -> bool:
    if ver == "":
        ver = version("package-name")

    return runners.run([f"git tag v{ver};", "git push --tags"])

'''

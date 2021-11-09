
# Install Dependencies
if you have already setup your sytem to use python, pyenv, poetry, and virtualenv then you can skip to [here](#create-virtual-environment-with-pyenv) and create your virtualenv

## Install pyenv and pyenv-virtualenv

### Prerequisites

```bash
sudo apt-get update
sudo apt-get upgrade
lsb_release -a
```

### pyenv install

references:

* [pyenv](https://github.com/pyenv/pyenv)
* [pyenv installer](https://github.com/pyenv/pyenv-installer)
* [common probs](https://github.com/pyenv/pyenv/wiki/Common-build-problems)
* [basic github checkout](https://github.com/pyenv/pyenv#basic-github-checkout)

```bash
sudo apt-get install -y make build-essential libssl-dev zlib1g-dev libbz2-dev \
libreadline-dev libsqlite3-dev wget curl llvm libncurses5-dev libncursesw5-dev \
xz-utils tk-dev libffi-dev liblzma-dev python-openssl git

# Following from https://github.com/pyenv/pyenv#basic-github-checkout
cd ~
git clone https://github.com/pyenv/pyenv.git ~/.pyenv
echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bashrc
echo 'export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bashrc
echo -e 'if command -v pyenv 1>/dev/null 2>&1; then\n  eval "$(pyenv init -)"\nfi' >> ~/.bashrc
exec "$SHELL"   # may need to restart your shell by logging out and back in
```

```bash
pyenv install 3.7.4  # install desired version
pyenv global 3.7.4   # set pyenv globally
python --version     # validate
```

### virtualenv install
[pyenv-virtualenv](https://github.com/pyenv/pyenv-virtualenv)
```bash
cd ~
git clone https://github.com/pyenv/pyenv-virtualenv.git ~/.pyenv/plugins/pyenv-virtualenv
echo 'eval "$(pyenv virtualenv-init -)"' >> ~/.bashrc
exec "$SHELL"   # may need to restart your shell by logging out and back in
```
restart your terminal

## Install poetry (for dependency resolution)

See https://poetry.eustace.io/docs/#installation

If you want the preview version of poetry:

```bash
cd ~
mkdir -p ~/tmp ; cd ~/tmp
wget https://raw.githubusercontent.com/sdispater/poetry/master/get-poetry.py
python get-poetry.py --preview
```

Ensure that poetry is on your path

```bash
echo 'export PATH="$HOME/.poetry/bin:$PATH"' >> ~/.bashrc
exec "$SHELL"   # may need to restart your shell by logging out and back in
poetry --version
```

## Download Source Code

```bash
cd ~
git clone <clone URL>
```

# Create Virtual Environment with pyenv

The `.python-version` file can be consulted to create your virtual env.

```bash
cd ~/wms-stream-processor
venv_name=`cat .python-version`
echo $venv_name
py_version=`echo ${venv_name##*-}`
echo $py_version
pyenv virtualenv $py_version $venv_name
```

# Install project Dependencies

install dependencies from the pyproject.toml and lock file:

```bash
poetry install
```

## Add a dependency

```bash
poetry add <some_python_package>
```

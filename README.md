# Overview

A full stack micro-service using Ember, Falcon, and Mongo

## Project setup

### backend

The Python Falcon backend uses [`pyenv`](https://github.com/pyenv/pyenv) to manage language version and project dependencies.

#### Install `pyenv` and `pyenv-virtualenv`

Install `pyenv` and `pyenv-virtualenv` with Homebrew:

```
$ brew install pyenv
$ brew install pyenv-virtualenv
```

Connect `pyenv` to your shell environment. I use [Oh My Zsh](https://github.com/robbyrussell/oh-my-zsh) so I add these lines near the end of `~/.zshrc`:

```
export PYENV_ROOT="$HOME/.pyenv"
export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init -)"
eval "$(pyenv virtualenv-init -)"
```

Restart your shell.

Complete install instructions: [`pyenv`](https://github.com/pyenv/pyenv#installation), [`pyenv-virtualenv`](https://github.com/pyenv/pyenv-virtualenv#installation)

## Install the virtual environment

First, ensure our mac is up to date. We need various xcode command line tools, like `zlib`. XCode is frequently updated, so if you already have these installed, you may have to acknowledge the license agreement for the latest version.

```
$ xcode-select --install
```

Install the python version:

```
$ pyenv install 3.6.2
```

Create the virtualenv

```
$ pyenv virtualenv 3.6.2 ember-falcon-mongo-3.6.2
```

**NOTE**: you may have to restart your shell to pick up changes here as well.

Verify everything works:

```
~/code/makara ᐅ cd ember-falcon-mongo
(ember-falcon-mongo-3.6.2) ~/code/makara/ember-falcon-mongo (master ✘)✹✭ ᐅ
(ember-falcon-mongo-3.6.2) ~/code/makara/ember-falcon-mongo (master ✘)✹✭ ᐅ python --version
Python 3.6.2
```

When you enter the project directory, you should see the virturalenv show as the first item in your command prompt and `python --version` should show `3.6.2`.


### datastore

### frontend

#!/usr/bin/env bash
set -o errexit

curl -LsSf https://astral.sh/uv/install.sh | sh
source $HOME/.local/bin/env

make setup

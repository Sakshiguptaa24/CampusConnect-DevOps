#!/usr/bin/env bash
set -e
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )/.." && pwd )"

echo "Setting up CampusConnect..."
cd "$DIR/backend"
pip install -r requirements.txt

cd "$DIR/frontend"
npm install

echo "Setup Complete!"

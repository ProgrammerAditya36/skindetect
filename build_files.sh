#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

# Print each command before executing it (for debugging purposes)
set -x

# Ensure we're in the project root directory
cd "$(dirname "$0")"

# Set up and activate the virtual environment (if it's not already done)
if [ ! -d "venv" ]; then
  python3 -m venv venv
fi

source venv/bin/activate

# Upgrade pip to the latest version
pip install --upgrade pip

# Install the required dependencies
pip install -r requirements.txt

# Run database migrations (if necessary)
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput


# Any other build steps (e.g., compressing assets)

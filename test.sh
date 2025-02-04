#!/bin/bash
# Run all codex tests
set -euxo pipefail
poetry run pytest
# pytest-cov leaves .coverage.$HOST.$PID.$RAND files around while coverage itself doesn't
poetry run coverage erase || true
bash -c "cd frontend && npm run test:unit"

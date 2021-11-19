#!/bin/bash
# Lint checks
set -euxo pipefail
if [ "${1:-}" = "-f" ]; then
    # Fix before check
    ./fix-lint.sh
fi
poetry run flake8 .
poetry run isort --check-only .
poetry run black --check .
poetry run pyright
poetry run vulture .
bash -c "cd frontend && npx eslint --ext .js,.vue '**'"
prettier --check .
# hadolint Dockerfile*
shellcheck -x ./*.sh ./**/*.sh
shfmt -d -i 4 ./*.sh ./**/*.sh

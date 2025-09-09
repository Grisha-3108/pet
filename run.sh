#!/bin/ash

export PROMETHEUS_MULTIPROC_DIR=$PWD/metrics

if [ -d "$PROMETHEUS_MULTIPROC_DIR" ]; then
rm -R "$PROMETHEUS_MULTIPROC_DIR"
fi
mkdir "$PROMETHEUS_MULTIPROC_DIR"

python -m alembic upgrade head
python main.py
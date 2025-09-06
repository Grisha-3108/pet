#!/bin/bash

export PROMETHEUS_MULTIPROC_DIR=$DIRSTACK/metrics

if [ -d "$PROMETHEUS_MULTIPROC_DIR" ]; then
rm -R "$PROMETHEUS_MULTIPROC_DIR"
fi
mkdir "$PROMETHEUS_MULTIPROC_DIR"

uv run main.py
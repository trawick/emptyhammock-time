#!/bin/sh

if ! python -m unittest discover; then
    exit 1
fi

if ! flake8 .; then
    exit 1
fi

if ! pylint e_time; then
    echo "Ignoring pylint errors"
fi

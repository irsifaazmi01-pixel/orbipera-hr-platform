#!/usr/bin/env sh
cd "$(dirname "$0")" || exit 1
printf 'ORBIPERA: buka http://127.0.0.1:8765 di browser.\n'
python3 server.py

@echo off
cd /d "%~dp0"
start "" pythonw rule_editor_gui.py examples/simple-index-rules.example.csv

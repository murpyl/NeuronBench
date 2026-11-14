#!/bin/bash
# Grader. Runs after the agent finishes; /tests is not present while the agent works.
mkdir -p /logs/verifier
python3 /tests/grade.py

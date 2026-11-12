# Lab 01 — prompts for your AI lab partner

Paste these into any coding agent along with this folder's files.

## 1. Find the breaking point
Here is a lab (docker-compose.yml, writer.py, auditor.py). Add a RATE
environment variable to writer.py that caps total writes per second.
Then write a script that runs `make exp1` at 500, 1k, 2k, 5k and 10k
writes/s and prints loss % for each. At what rate does loss first exceed 1%?

## 2. Vary the experiment
Propose three changes to this lab that would change the result, such as
more writers, microsecond timestamps, or a different key distribution.
For each, predict the outcome and explain why BEFORE I run it.

## 3. Read my results
Here is my auditor output: <paste>. Explain it using ties, in-flight
reordering and clock skew. Point out anything those three causes
do not explain.

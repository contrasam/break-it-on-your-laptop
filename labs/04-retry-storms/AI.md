# Lab 04: prompts for your AI lab partner

Paste these into any coding agent along with this folder's files.

## 1. Find the breaking point
Here is a lab (docker-compose.yml, retry.py, dep.py, api.py, loadgen.py, auditor.py).
Write a script that runs `make exp2` with SLOW_FOR set to 0.5, 1, 2 and 5 seconds and
prints, for each, whether the system recovered. What is the shortest slowdown that
starts a storm that never ends on my machine? Then do the same for RATE at 50, 75 and 100.

## 2. Vary the experiment
Propose three changes to this lab that would change the result, such as a longer client
timeout, retrying at only one layer, a different BUDGET, or making dep drop requests whose
X-Give-Up-At has passed. For each, predict calls per request and recovery time and explain
why BEFORE I run it.

## 3. Read my results
Here is my auditor output: <paste>. Using the per-second timeline, explain when the dependency
was the bottleneck and when the retries were. Point to the rows where wasted work starts,
and explain why the queue keeps growing after the dependency is fast again.

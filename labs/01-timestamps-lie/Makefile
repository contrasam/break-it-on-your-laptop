# Lab 01: Timestamps lie at 10k req/s
MODE   ?= lww
SKEW_C ?= 0
export MODE SKEW_C

run:
	@docker compose down -v --remove-orphans >/dev/null 2>&1 || true
	@docker compose up -d --build --quiet-pull redis writer-a writer-b writer-c
	@echo "writers running for $${DURATION:-20}s (mode=$(MODE), writer C skew=$(SKEW_C)ms)..."
	@docker compose wait writer-a writer-b writer-c >/dev/null
	@docker compose --profile audit run --rm auditor
	@docker compose down -v >/dev/null 2>&1

exp1:            ## perfect clocks, last-write-wins
	@$(MAKE) --no-print-directory run MODE=lww SKEW_C=0
exp2:            ## writer C's clock is 5 ms behind
	@$(MAKE) --no-print-directory run MODE=lww SKEW_C=-5
fix:             ## same skew, versioned compare-and-set
	@$(MAKE) --no-print-directory run MODE=cas SKEW_C=-5

.PHONY: run exp1 exp2 fix

# Lab 04: Retry storms
RETRY    ?= naive
SLOW_FOR ?= 5
export RETRY SLOW_FOR

run:
	@docker compose down -v --remove-orphans >/dev/null 2>&1 || true
	@docker compose up -d --build --quiet-pull dep api1 api2 nginx
	@echo "load running for $${DURATION:-30}s (retry=$(RETRY), dependency slow for $(SLOW_FOR)s)..."
	@docker compose run --rm loadgen
	@docker compose --profile audit run --rm auditor
	@docker compose down -v >/dev/null 2>&1

exp1:            ## healthy dependency, naive retries
	@$(MAKE) --no-print-directory run RETRY=naive SLOW_FOR=0
exp2:            ## dependency slow for 5 s, naive retries
	@$(MAKE) --no-print-directory run RETRY=naive
exp3:            ## same slowdown, exponential backoff with jitter
	@$(MAKE) --no-print-directory run RETRY=backoff
fix:             ## same slowdown, backoff + jitter + retry budget
	@$(MAKE) --no-print-directory run RETRY=budget

.PHONY: run exp1 exp2 exp3 fix

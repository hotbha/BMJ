# Conventional Commits for BMJ

This project follows [Conventional Commits](https://www.conventionalcommits.org/).

## Format

<type>(<scope>): <description>

## Types

feat, fix, docs, style, refactor, perf, test, chore, ci

## Scopes

auth, catalog, cart, checkout, subscription, order, webhook, notif, delivery, cache, infra, docs, test, refactor

## Examples

feat(auth): add Phone OTP signup with 10-min expiry
fix(cart): prevent mixed-mode items returning wrong error code
docs(readme): update installation steps

## Breaking Changes

Add ! after type/scope and BREAKING CHANGE: in footer.

## Body

Imperative mood, explain what/why, wrap at 72 chars.

## References

Closes: #N, Fixes: #N, Refs: #N

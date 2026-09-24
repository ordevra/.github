# Contributing

> Purpose: how work reaches `main` in every Ordevra repository. A repository's own `AGENTS.md` or `CONTRIBUTING.md` adds to these rules and wins where they differ.

## Workflow

1. **Fetch, then branch from the current `main`.** Use a short descriptive name,
   such as `docs/onboarding-fix`. AI collaborators use their own prefix:
   `claude/<topic>` for Claude sessions, `codex/<topic>` for Codex sessions.
2. **Commit the specific paths you changed.** Never `git add -A` or
   `git commit -a`: more than one person or AI session may be working in the same
   tree, and a blanket commit sweeps their half-finished work into yours.
3. **Write commit subjects as `<area>: <what changed>`**, for example
   `docs: fix broken setup link`. Say *why* in the body when the reason is not
   obvious from the diff.
4. **Open a pull request** and fill in the template: purpose, validation, the
   secrets and client-data check, rollback and any decision needed.
5. **Merge after required checks pass and review conversations are resolved.**
   Pull requests are squash-merged, so the pull request title becomes the commit
   on `main`; give it the same `<area>: <what changed>` form.

Do not push directly to `main`.

## What never goes in a repository

Secrets, credentials, tokens, private keys, live environment files, client data
and personal data. Commit only sanitized examples such as `.env.example`. If you
find any of these already committed, stop and report it privately (see
[SECURITY.md](SECURITY.md)) rather than quietly deleting it; removing a file does
not remove it from history.

## Issues

Blank issues are disabled. Use the bug report, task or decision form. A decision
issue records a choice that needs owner sign-off: the options, a recommendation
and a deadline.

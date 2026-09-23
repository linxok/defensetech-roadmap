# Contributing

Thanks for improving the course. Two rules matter more than anything else:

1. **Concrete over generic.** Versions, parameters, numbers, exact error
   messages. No filler paragraphs.
2. **No duplicated text.** Shared material lives in `docs/`; modules link
   to it. `scripts/check_duplicates.py` fails otherwise.

Read `CONTENT_STANDARD.md` first — it defines module statuses, required
files and the quality bar.

## Repository layout

- `NN-topic/` — 18 modules; each must contain README, lab, checks/,
  solution/ and the auxiliary files listed in `CONTENT_STANDARD.md`.
- `capstone/` — the end-to-end system; modules add components to it.
- `docs/` — shared docs (workflow, FAQ, templates, setup, glossary).
- `scripts/` — structure, duplicate, lab-check runners.
- `tests/` — pytest suite (structure, examples, contracts, lab checks).

## Quality gates

Run before opening a PR:

```bash
make lint     # markdownlint-cli2
make test     # structure + duplicates + pytest
make check    # every module's checks/ against solution/
make build    # mkdocs build --strict (needs requirements-docs.txt)
```

CI runs the same gates plus `docker compose build` for the capstone and a
nightly ArduPilot SITL smoke test.

## Adding a lab check

1. Create `NN-topic/checks/check_lab.py` with a `--target` argument
   (default: the module's `solution/`).
2. It must exit non-zero on an empty/stub target and zero on the
   reference solution. Offline only: no SITL, Docker or network.
3. Add the reference implementation under `NN-topic/solution/`.
4. `tests/test_lab_checks.py` will pick it up automatically.

## Updating a module README

Keep the structure from `CONTENT_STANDARD.md`: status line, theory map,
control questions, expected artifact, capstone link, mistakes, primary
sources. 5+ primary sources and 3+ verifiable questions are mandatory.

## Commit style

Short imperative subject, body explains what was verified and how.
Do not commit secrets, `.env` files (except `capstone/.env`), or generated
artifacts (`site/`, `.mkdocs-build/`).

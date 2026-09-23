# DefenseTech Roadmap

Open-source, hands-on course that takes a senior software engineer to a
**Drone / Autopilot Software** role in DefenseTech: MAVLink, ArduPilot/PX4,
ROS2, C++/Python, telemetry backends and a real capstone.

Course content and module READMEs are written in Ukrainian; file names,
code identifiers, commands and site navigation are English.

## Choose one track

| Track | Deep modules | Focus |
|---|---|---|
| **Drone / Autopilot Software** (recommended) | 05–09 | MAVLink, ArduPilot, PX4, ROS2, C++ |
| Onboard CV / AI | 12–13 (+09) | OpenCV, YOLO, edge inference |
| Backend / Platform (GCS, fleet) | 10–11, 14–15 | FastAPI, queues, Kubernetes |

Everything else is studied at outline level. Spreading across tracks is
the main reason people never finish; pick one.

## Quick start

```bash
git clone https://github.com/linxok/defensetech-roadmap.git
cd defensetech-roadmap
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt
python scripts/verify_structure.py
python scripts/run_lab_checks.py
```

Then read `QUICKSTART.md` and start with `00-introduction/`.

## Module status

Every module declares its status (see `CONTENT_STANDARD.md`):
`stub` — skeleton, `outline` — usable overview, `complete` — self-sufficient.

| Module | Status | Automatic lab check |
|---|---|---|
| 00 Introduction | outline | yes |
| 01 DefenseTech Fundamentals | outline | yes |
| 02 Linux for Robotics | outline | yes |
| 03 Networking | outline | yes |
| 04 Python | complete | yes |
| 05 Modern C++ | complete | yes |
| 06 MAVLink | complete | yes |
| 07 ArduPilot | complete | yes |
| 08 PX4 | complete | yes |
| 09 ROS2 | complete | yes |
| 10 Backend Systems | outline | yes |
| 11 Distributed Systems | outline | yes |
| 12 Computer Vision | outline | yes |
| 13 AI | outline | yes |
| 14 Ground Control | outline | yes |
| 15 DevOps | outline | yes |
| 16 Portfolio Projects | outline | yes |
| 17 Interview | outline | yes |

## Capstone

`capstone/` is the end-to-end system every module feeds into:
MAVLink gateway → FastAPI backend → RabbitMQ → worker → PostgreSQL;
the GCS UI gets live frames over WebSocket from the backend.

```bash
cd capstone && docker compose up --build   # sim mode, no autopilot needed
COMPOSE_PROFILES=sitl docker compose up    # real ArduPilot SITL in Docker
```

See `capstone/README.md` for the architecture, API contract, metrics and
the map from modules to components.

## Repository layout

```text
├── 00-introduction … 17-interview   # 18 modules, each with lab/checks/solution
├── capstone/                        # end-to-end telemetry system
├── demos/                           # focused demos (CV, AI, logs)
├── docs/                            # setup, tools, glossary, workflow, FAQ
├── notes/                           # hardware buying guide, field notes
├── scripts/                         # structure, duplicate, reference and lab checks
├── tests/                           # pytest: structure, examples, contracts
└── .github/workflows/ci.yml         # lint, checks, pytest, mkdocs, SITL
```

## Quality gates

```bash
make lint              # markdownlint-cli2
make test              # structure + duplicates(--all) + references + pytest
make check             # every module's checks/ against its solution/
make build             # mkdocs build --strict
```

The CI runs the same gates, plus a nightly ArduPilot SITL smoke test.
No text or code block may be duplicated between modules —
`scripts/check_duplicates.py --all` enforces this, and shared material
lives in `docs/`. `scripts/check_references.py` fails on references to
files that do not exist.

## Hardware

Start with SITL only. A real kit makes sense after 2–3 weeks of successful
simulator work — see `notes/beginner-drone-kits.md` for a phased path
with prices.

## Contributing

Read `CONTENT_STANDARD.md` and `CONTRIBUTING.md`. Every lab must ship a
`checks/` script that fails on a stub and passes on the reference
`solution/`.

## License

MIT — see `LICENSE`.

# profile-readme

GitHub profile README (`rayho30`) — generates animated terminal-themed SVG panels.

## Pipelines

- **Daily (auto)**: GitHub Actions cron `0 5 * * *` — `pull_contributions.py` → `render_graph.py` → commit `graph.svg` + `assets/contributions.json`. No auth needed (scrapes public GitHub HTML).
- **Art (one-time, manual)**: `clean_photo.py <photo>` → `render_portrait.py` + `render_panel.py` → `portrait.svg` + `sysinfo.svg`. These are committed once and rarely change.

## Commands

```bash
pip install -r tools/requirements-daily.txt   # httpx + lxml (daily cron)
pip install -r tools/requirements-art.txt     # Pillow, numpy, opencv-python-headless, optional rembg

python tools/pull_contributions.py            # fetches → assets/contributions.json
python tools/render_graph.py                  # assets/contributions.json → graph.svg
python tools/clean_photo.py <path>            # preps photo → assets/photo-ready.png
python tools/render_portrait.py               # assets/photo-ready.png → portrait.svg
PREVIEW=1 python tools/render_panel.py        # sysinfo.svg (PREVIEW=1 disables animations)
```

## Key facts

- **No tests, linters, or formatters** configured.
- Only files tracked by the auto-commit action: `assets/contributions.json graph.svg`.
- Daily pipeline is self-healing: if `pull_contributions.py` fails, it keeps the previous `contributions.json`.
- `render_panel.py` uses `PREVIEW=1` env var for a static (non-animated) SVG.
- `rembg` optional — without it, `clean_photo.py` skips background removal with a warning.

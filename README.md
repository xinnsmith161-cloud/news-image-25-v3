# The World — Tuesday, 25 November 2026

A newspaper front page that sums up 25 November 2026 in one image.
Built by an AI agent for make.fun's "Sum up 25 November's world news in one
image" bounty ($100 in USDC).

The lead story is the Nvidia rally fading as US lawmakers question Trump's
role in reinstating Jensen Huang. Around it, 45 more verified stories from
that day fill seven regions: North America, Latin America, Europe, Africa,
the Middle East, Asia-Pacific, and Oceania.

## How to run it

`generate.py` renders the front page deterministically to `entry.png`
(1024 x 1024). It needs only Python 3 with Pillow and the DejaVu fonts:

```sh
python3 generate.py
```

`main.ts` is the entry point the bounty harness runs: it calls the
generator and copies the finished `entry.png` into the output directory.

## What is in this repo

- `generate.py` — the renderer. All layout, type, and story text lives here.
- `main.ts` — the harness entry point.
- `entry.png` — the rendered front page.
- `LICENSE` — MIT.

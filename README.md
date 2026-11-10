# Isha — reel editing workspace

Shared workspace for Isha's Instagram Reels: the house style, the editing pipeline, the brand kit and the per-reel project scripts.

## Start here
- **`ISHA_REEL_SYSTEM.md`**: the rulebook for formats, captions, titles, grade, audio, export and QA.
- **`REFERENCE_LIBRARY.md`**: what each reference reel does, with measurements (the evidence behind the rules).
- **`pipeline/README.md`**: how to run `pipeline/isha.py` (probe, sheet, render, transcribe, qa).
- **`projects/bhai_dooj/REEL_SPEC.md`**: the reel the client loved. Its look (fonts, colours, captions, ending, music) is the default for new reels; picture in `brand/06_client_approved_look.png`.

## Layout
```
brand/         visual boards (type, palette, captions, titles, grades) + safe-zone overlay
fonts/         static TTFs used by the captions (OFL licences in fonts/licenses/)
luts/          grade looks as .cube
templates/     starting edit.json for formats A–E (E = client-approved look)
sfx_library/   sound effects used in the reels
pipeline/      isha.py and helper scripts
projects/<reel>/   per-reel scripts (make.py etc.)
inbox/<reel>/      raw clips go here (NOT in git)
models/            whisper model goes here (NOT in git)
```

## What is not in git (and why)
Raw footage, renders and big models are too large for GitHub, so `.gitignore` leaves them out:
- `inbox/`: raw clips from Isha. Get them from the shared Drive folder and drop them in `inbox/<reel>/`.
- `projects/*/build/` and `projects/*/out/`: intermediates and finished reels. Rebuild them with the pipeline, or grab the finals from Drive.
- `models/ggml-small.bin`: the whisper.cpp model (465 MB). Download it into `models/`:
  `curl -L -o models/ggml-small.bin https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-small.bin`
- Any `.mp4` / `.mov` file.

## Raw clips that ARE in git (Git LFS)
Some reels' raw clips are shared here through Git LFS, so collaborators can pull them directly:
- `inbox/lakshadweep_part2/`: Lakshadweep part 2 (13 clips)

Install LFS once before cloning: `git lfs install`. To share another reel's clips, add
`!inbox/<reel>/` and `!inbox/<reel>/*` to the end of `.gitignore`. Videos in `inbox/` are tracked by LFS automatically.

## Setup
Needs Python 3 with `numpy` and `Pillow`, plus an ffmpeg/ffprobe build that includes libass and whisper.
```bash
git clone <this repo>
cd isha
pip install numpy pillow
# add the whisper model (above) and raw clips, then follow pipeline/README.md
```

## Working together
- Work on a branch per reel or change (`git checkout -b safari-v6`), then open a pull request.
- If you change a style in `pipeline/isha.py`, run `python pipeline/brandkit.py` so the boards in `brand/` stay in sync.
- Don't commit video files. If a reel needs new footage, put it on Drive and say where in the PR.

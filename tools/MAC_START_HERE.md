# Start the Blender opening on your Mac

For the newest **Messi / Mbappe / Ronaldo superhero sequence**, use [the crossover packet](../episodes/002-ronaldo-hate-psychology/mac/superhero-crossover/README.md). It recreates the four-shot reference as a revised eight-second sequence with a side-profile pointing shot.

For the latest **floating Messi cartoon opening**, follow [the new packet instructions](../episodes/002-ronaldo-hate-psychology/mac/messi-floating/README.md). That clip is 12 seconds and opens directly in a clean camera view. The guide below applies to the earlier three-set 30-second opening.

Repository: https://github.com/issa402/YoutubeBlen.git

The Mac runs Git and Blender. The commands below go in **Terminal**, not Blender's Python console. They generate the scene from code; you do not need to copy or paste the Python script into Blender. Use the employer-approved Blender/Git installation and transfer location.

## 1. Download once

This example keeps the project in your Movies folder. In Terminal:

```bash
mkdir -p "$HOME/Movies"
cd "$HOME/Movies"
git clone https://github.com/issa402/YoutubeBlen.git
cd YoutubeBlen/episodes/002-ronaldo-hate-psychology/mac/opening-hd
```

Use a normal clone. No recursive submodule download is needed. The project contains the imported reference files directly. If Git asks for authentication, use your normal GitHub sign-in.

The initial source/text payload is approximately **1 MB before Git compression**, including the imported reference project. The standalone HD Blender packet is about **30 KB**. Git metadata adds overhead. Later pulls download changed objects rather than the whole folder. Models, Python environments, downloaded tools, credentials, audio and rendered video are ignored and are not included.

## 2. Generate the editable scene

Blender should be installed at `/Applications/Blender.app`. The script was exercised with Blender **4.5.13 LTS on Windows**; actual Mac execution still needs its first local check.

```bash
bash run.sh build
open opening-hd.blend
```

The first command launches Blender in the background and builds the objects, lighting, three cameras and animation keyframes. The second opens the resulting file in the Blender app. In Blender, move your pointer over the timeline and press **Space** to play or pause. Drag the timeline playhead to inspect a frame. The sequence runs from frame 1 to 720 at 24 fps: **30 seconds**. Viewport playback may run slower than real time; the rendered video still uses the specified frame rate.

If `open` does not choose Blender, launch Blender and use **File → Open**, then select `opening-hd.blend` inside this folder.

## 3. Check nine rendered frames

Back in Terminal, in the same `opening-hd` directory:

```bash
bash run.sh preview
open previews
```

This renders nine 1920×1080 PNG images covering the beginning, middle and end of each shot. Inspect them before the longer render. Existing preview files are preserved; repeat a changed preview in a fresh copy of this packet.

## 4. Render the whole opening

```bash
bash run.sh render
```

Keep Terminal open until it reports completion. This writes `frames/frame_0001.png` through `frames/frame_0720.png`. Based on the Windows samples, expect roughly **1.5–2 GB of generated images**; the exact total and render time depend on the machine/settings. This is disk space used after rendering, not the size of your Git pull.

The images are silent. Windows adds the prepared narration, captions and final MP4. The Python code is included in `studio/finish.py`, and its CLI is `studio finish-opening`; the [finishing guide](HD_FINISHING.md) gives exact commands. This packet creates the opening, not all nine chapters of the episode.

To continue an interrupted render without changing scripts or settings:

```bash
bash run.sh resume
```

Resume checks saved frame integrity and a source fingerprint. If it finds an incomplete frame/ledger mismatch, keep the files and send the log for diagnosis; do not delete random frames to bypass the check.

## 5. Pull future improvements

Finish or stop a running render first. In Terminal:

```bash
cd "$HOME/Movies/YoutubeBlen"
git pull --ff-only
cd episodes/002-ronaldo-hate-psychology/mac/opening-hd
```

If you have already rendered an older version, preserve that version's folder/output and run changed scene code in a fresh packet copy. Updated code cannot safely resume frames rendered from a different source fingerprint. Render outputs stay local and cannot be overwritten by Git because they are ignored.

## If Blender fails

The launcher prints the path of its uniquely named `render-*.log`. Return that file, `motion-report.json` if present, your Blender version, and a preview image through the permitted transfer method. An error exit stops the launcher; it does not report success after a Python exception.

If Blender is installed elsewhere, set its executable path before the command:

```bash
BLENDER_BIN="/approved/path/Blender.app/Contents/MacOS/Blender" bash run.sh build
```

No AI accounts, neural models, Python packages or MCP setup are required on the Mac for this scene.

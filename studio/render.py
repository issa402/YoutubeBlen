"""Create a dependency-free, portable Blender render handoff."""
import json
import shutil
from pathlib import Path


def create_package(output_dir: Path, seconds: int = 8) -> dict:
    """Create a fresh self-contained package; never overwrite a previous render."""
    if type(seconds) is not int or not 1 <= seconds <= 120:
        raise ValueError('seconds must be an integer between 1 and 120')
    source = Path(__file__).resolve().parents[1] / 'blender' / 'studio_scene.py'
    if not source.is_file():
        raise FileNotFoundError(f'Missing scene source: {source}')
    destination = Path(output_dir).expanduser().resolve()
    manifest = {
        'schema_version': 1, 'scene': 'trophy_media_machine', 'seed': 42,
        'fps': 24, 'frame_start': 1, 'frame_end': seconds * 24,
        'resolution': [1920, 1080], 'output': 'frames',
        'preview_resolution': [640, 360],
        'editorial_label': 'OPINION',
        'description': 'Original visual metaphor: abstract red and cyan football competitors, trophy and media screens; no real likeness or match reconstruction.',
    }
    destination.mkdir(parents=True, exist_ok=False)
    shutil.copyfile(source, destination / 'studio_scene.py')
    (destination / 'manifest.json').write_text(
        json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
    (destination / 'README.md').write_text('''# Trophy / media machine

Original stylized football visual metaphor, not a match reconstruction.
This folder contains all scene inputs. No downloaded assets or Python packages.
Run only where your employer permits Blender and these repository files.
Requires Blender 4.2 or newer. Copy this whole folder to an approved Mac location.
Open Terminal in that folder. The commands deliberately use relative paths.

```sh
# Build the scene and save scene.blend without rendering.
/Applications/Blender.app/Contents/MacOS/Blender --background --python studio_scene.py -- --manifest manifest.json
# Render three inexpensive frames for visual review.
/Applications/Blender.app/Contents/MacOS/Blender --background --python studio_scene.py -- --manifest manifest.json --preview
# After checking previews, render the full PNG sequence.
/Applications/Blender.app/Contents/MacOS/Blender --background --python studio_scene.py -- --manifest manifest.json --render
```

On Windows substitute your Blender executable for the application path above.
Outputs: scene.blend, validation.json, previews/*.png, frames/*.png.
Eevee uses the available device; there are no assumed Metal or CUDA settings.
Preview checks are required before choosing an expensive final render.
validation.json distinguishes scene validation from a completed render.
Return only approved outputs using your approved transfer method.
''', encoding='utf-8')
    return {'package': str(destination), 'manifest': str(destination / 'manifest.json'),
            'frames': manifest['frame_end'], 'status': 'ready_for_blender'}

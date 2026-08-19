# Profile asset provenance

The profile hero is a deterministic composition around the operator-selected
`duo_square_00003_` character ensemble: the girl and her cute, cat-like spirit
forms are Ghost. Final typography, prompt-square geometry, static scanlines,
RGB border, and layout are rendered by
`tools/generate_canticle_profile_assets.py`; diffusion is not used for text or
identity geometry.

| Asset | Source and status |
|---|---|
| `ghost-duo-square-00003.png` | Operator-selected Ghost ensemble; AnimagineXL 3.1; seed `20260820`; square batch slot 3; generated locally on 2026-08-18 |
| `ghost-duo-square-00003-dance.mp4` | Normalized 560×560, 12 fps, 120-frame motion source derived from the operator-supplied animation of the exact approved square; audio and attached cover art removed |
| `ghost-cameo.png` | Deterministic display-size render of the selected Ghost source |
| `canticle-logo.svg` | Official Canticle RGB prompt-square lockup from the Canticle-AI-Research organization profile |
| `link-{research,canticle,x,kofi,patreon,coffee}.svg` | Deterministic GitHub-safe link buttons with the selected cute cat-like Ghost spirit motif |
| `cyber-divider.svg` | Editable static isometric concept for the deterministic spectral cube relay |
| `cyber-divider.png` | Static reduced-motion poster rendered from the same projected-cube geometry as the loop |
| `cyber-divider.gif` | Baked GitHub-safe loop of six shaded RGB cubes growing, tumbling off-axis, and emitting their own color glows above a quiet carrier line |
| `canticle-profile-hero.png` | Static reduced-motion poster generated from the approved mascot source |
| `canticle-profile-hero.gif` | Nine-second GitHub hero using the supplied articulated Ghost animation inside an invariant right-side window; no synthetic translation, rotation, scaling, bobbing, or whole-image motion |

The Ghost source used AnimagineXL 3.1 at 1024×1024 with `dpmpp_2m`, the
`karras` scheduler, 28 steps, CFG 6.5, and seed `20260820`. The full positive
and negative prompts are preserved in the machine-readable provenance file.

The original and normalized motion-source hashes, loop construction, hero
hashes, and animation parameters are recorded in
`canticle-profile-hero.provenance.json` after generation. This revised motion
composition is approved for the BlackhatShiftey GitHub profile; it is not a
canonical Ghost-repo identity asset or company-library replacement.

The divider animation is deterministic geometry rendered by
`tools/generate_cyber_divider.py`; it does not use diffusion or external
assets. Its loop settings and output hash are recorded in
`cyber-divider.provenance.json`. The static PNG is selected when the viewer
requests reduced motion; the SVG preserves an editable static concept. RGB
motion belongs to the individually colored cubes; the terminal carrier stays
static and neutral.

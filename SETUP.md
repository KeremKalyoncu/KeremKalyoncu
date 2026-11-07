# KEREM / AERO — V5 installation

## What changed
- 100% visual profile: **no Markdown headings, tables, badges or paragraphs between scenes**.
- 11 full-width authored image panels, with compact explanatory text **inside** the images.
- Public GitHub projects are individually clickable; VollSign links to its official website.
- Liquid Internet and private work are excluded from project showcase.
- The linked projects and company are not presented as realtime telemetry or invented live demos.
- Every image includes meaningful alternative text for accessibility.

## Installation without disturbing existing README
1. Extract this ZIP.
2. Clone `KeremKalyoncu/KeremKalyoncu` using GitHub Desktop.
3. Create a new branch: `feat/aero-v5`.
4. Replace `README.md` with this package's `README.md`.
5. Copy ALL files in this package's `assets/` into your repo's `assets/` (do not delete existing assets).
6. Commit and push the branch.
7. Preview at `https://github.com/KeremKalyoncu/KeremKalyoncu/blob/feat/aero-v5/README.md`.
8. Review links, mobile readability, and content, then open a PR to `main` if happy.

## Technical notes
- GitHub profile README does not allow scripting/layout CSS like a regular website. Each wide image is a single clickable surface, not draggable desktop windows.
- These JPG assets render consistently within GitHub's sanitization limitations.
- Some UI drawings (charts, map view, QR code) are **illustrative art**, not actual product screenshots nor live data; do not portray them as such.
- Images need the exact relative path under `assets/`.
- The scripts and legacy Actions from your old profile are **not** modified; once the new README is published the old issue-ops hooks may need disabling because the new README intentionally omits their target sections. Existing scripts can remain until you decide to clean up.
- If you want actual live widgets or interactive windows, implement them in your own website; this README is a visual gallery constrained by GitHub's renderer.

## Customization
Run `python build_aero.py` (requires Pillow) to regenerate the images. The `sources/` folder contains the visual backgrounds used by the build script. Regenerate by running the script from any directory. For another look, replace these image files with your own scene artwork. No fonts are redistributed.

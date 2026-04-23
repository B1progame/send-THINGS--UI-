# CrocDrop v1.1.0 - In-App Updater + Stability Fixes

## Highlights
- Added an in-app updater in **Settings** (`Update App` button).
- App now checks GitHub releases, compares versions, and downloads updates directly.
- Added a dedicated update popup with a live download progress bar.
- Update flow now closes CrocDrop, applies the downloaded update package, and restarts automatically (no installer rerun required).
- Fixed startup warning: `QFont::setPointSize: Point size <= 0 (-1)`.

## What Changed
- New app update service for release check, download, and restart flow.
- Added app version metadata used by updater checks.
- Wired updater into application context and Settings UI.
- Added threaded update worker so UI remains responsive during downloads.
- Added safer fallback font initialization to prevent invalid font-size warnings at startup.

## User Impact
- Updating CrocDrop is now one click from Settings.
- Cleaner startup output with the font warning resolved.
- Better reliability for future version upgrades.

## Notes
- Update ZIP assets should be attached to GitHub releases for updater compatibility.
- If CrocDrop is installed in a protected directory, update apply may require elevated permissions.

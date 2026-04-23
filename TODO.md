# TODO

- Clarify friend detection: currently a "friend" is only a remembered alias from transfer code/session history, not verified identity.
- Add clearer friend trust flow: let user mark entries as "Trusted Friend" manually and show trust badge in Devices page.
- Add identity warning text in Devices page: "Code-based alias only, not cryptographic proof of person."
- Update UI (again).
- Add auto update support (check GitHub releases, notify user, and in-app update flow).

## UI/UX Improvements

- Add full theme switcher: `Light`, `Dark`, and `System`.
- Auto-apply theme on OS change when `System` is selected.
- Improve light theme contrast (especially muted text, borders, and cards).
- Improve dark theme readability (less glow, better neutral grays, clearer input states).
- Add accent presets with preview chips and a custom color picker.
- Add a compact density mode for smaller spacing in lists/tables.
- Add accessible font scaling (Small / Medium / Large).

## Quality of Life

- Add first-run onboarding tooltip flow for Send/Receive.
- Add transfer speed + ETA in active transfers.
- Add optional sound notification on transfer complete/fail.
- Add “Open logs folder” button in Logs page.
- Add “Copy diagnostics” one-click button for support.

## Stability & Security

- Add update channel selector (Stable / Beta).
- Add release signature/hash verification step for app self-updates.
- Add rollback support if update apply fails.
- Add safer shutdown handling during active transfers.

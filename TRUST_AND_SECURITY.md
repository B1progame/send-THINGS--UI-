# TRUST_AND_SECURITY

## Source of Truth and Binary Trust

CrocDrop only treats the official repository as authoritative:
- Repository: `https://github.com/schollz/croc`
- Latest release metadata: `https://api.github.com/repos/schollz/croc/releases/latest`
- Allowed download prefix: `https://github.com/schollz/croc/releases/download/`

CrocDrop refuses non-official release URLs for binary download.

## Verification Steps Implemented

1. Fetch latest release JSON from official GitHub API endpoint.
2. Validate release page URL is under official `github.com/schollz/croc/releases/...`.
3. Select OS/arch-matching asset.
4. Download only if asset URL matches official release prefix.
5. Compute local SHA-256 of downloaded archive.
6. If checksums asset is present and parseable, compare expected hash for the selected archive.
7. Persist installed binary path/version/source for diagnostics.

## What This Does Not Claim

- Does **not** claim files or binaries are "virus-free".
- Does **not** claim security guarantees beyond those provided by croc protocol/implementation.
- Does **not** claim immutable output format from croc CLI logs.

## Runtime Safety Posture

- No automatic firewall modifications.
- No permanent background daemon/service installation.
- Subprocesses are user-triggered and managed by app lifecycle.
- Canceled/failed transfers remain marked non-successful.
- Diagnostics expose exact binary path/version/source for user auditability.

## Relay Model

V1 focuses on stock/public croc relay behavior.
Architecture keeps relay settings abstracted so self-hosted relay can be added/used later via Settings without replacing transfer engine.

## Local Self-Test Safety

Self-test uses local temporary directories and hash-compare verification.
It is intended for transfer workflow validation, not for cryptographic certification.

# Codex Skills Mirror

This repository mirrors the local Codex skills currently installed under `~/.codex/skills`.

## Layout

- `skills/`: skill directories, kept in the same shape as the local Codex skills folder
- `scripts/sync-to-codex-home.ps1`: sync tracked skills from this repository into `~/.codex/skills`
- `skills-manifest.md`: inventory of the mirrored skills

## Sync on a new machine

1. Clone this repository.
2. Run `powershell -ExecutionPolicy Bypass -File .\\scripts\\sync-to-codex-home.ps1`.
3. Restart Codex.

The sync script only overwrites the skill directories tracked by this repository. It does not remove unrelated skills that may already exist on the target machine.

# Changelog

All notable version changes to plugins in this repository.

## [mosaic-buddy@3.2.0] - 2026-04-23
- Fix telemetry hook: strip /mosaic-buddy instead of old /beacon prefix
- Fix telemetry hook: add all command aliases to skip list (prevents double-counting)
- Fix telemetry hook: case-insensitive subcommand matching
- Fix telemetry hook: remove curl background race condition
- Clean up unused timestamp variable


## [mosaic-admin@3.1.0] - 2026-04-22
- Aligned version with mosaic-buddy (jumped from 1.0.0 to 3.1.0)

## [mosaic-buddy@3.1.0] - 2026-04-22
- Bumped from 3.0.2 to 3.1.0 (minor)


## [mosaic-buddy@3.0.2] - 2026-04-22
- Bumped from 3.0.1 to 3.0.2 (patch)


## [mosaic-buddy@3.0.1] - 2026-04-22
- Renamed from beacon to mosaic-buddy, rewrote README, fixed instant interactive menu

## [mosaic-buddy@3.0.0] - 2026-04-22
- Renamed plugin from beacon to mosaic-buddy

## [mosaic-buddy@2.3.0] - 2026-04-21
- Redesigned /mosaic-buddy 10x to use parallel Sonnet subagents + Opus synthesis

## [mosaic-buddy@2.2.0] - 2026-04-21
- Split coaching into /mosaic-buddy 5x (fast) and /mosaic-buddy 10x (deep)

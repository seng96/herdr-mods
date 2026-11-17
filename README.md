# herdr-mods

Mods for the [Herdr app](https://herdr.dev), one folder each (`<name>/mods/<name>/` plus
`RECIPE.md` and `preview.png`), the layout herdr.dev/mods expects.

| Mod | What it is |
|---|---|
| [`over9k-usage`](over9k-usage/) | Claude, Codex and Gemini (Antigravity CLI) usage limits in one strip at the bottom of the window. A Windows-friendly fork of [herunan/herdr-over9k](https://github.com/herunan/herdr-over9k/tree/main/over9k-usage): needs only Python, no `sh`/`jq`. |

## Install a mod

Copy `over9k-usage/mods/over9k-usage/` into `~/.config/herdr-app/mods/` (Windows:
`%USERPROFILE%\.config\herdr-app\mods\`), then follow that mod's RECIPE.md.

## License

MIT. `over9k-usage` is derived from Over9k (MIT, © the Over9k authors); see [LICENSE](LICENSE).

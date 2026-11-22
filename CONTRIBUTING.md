# Contributing

Plugin content belongs in the product repositories (`plugin/` directory); open changes there. This repository only lists releases.

- Move a pin: `python3 scripts/bump-ref.py <plugin> <tag>`, then `python3 scripts/validate.py`.
- Add a plugin: add an entry to every file in `scripts/marketplace.py` `FORMATS` (same name, repository, path and ref), then validate.
- Tests: `python3 -m unittest discover -s tests`.
- Commits: conventional commits, one logical change each. Hooks: `poly hooks install`.

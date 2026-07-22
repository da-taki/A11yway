# Development

Use small changes and focused tests. Keep runtime artifacts out of commits.

## Useful commands

```bash
python -m compileall a11yway scripts
pytest
python -m pytest tests/test_web_demo.py tests/test_render_docker_smoke.py
python -m pytest tests/test_wcag_coverage.py
python -m a11yway.main --wcag-coverage-markdown docs/WCAG22_COVERAGE.md
docker build -t a11yway-render-smoke .
docker run --rm a11yway-render-smoke python scripts/render_docker_smoke.py
```

## Project map

- `a11yway/`: package code.
- `a11yway/core/`: analyzers, report builders, registries, and helpers.
- `a11yway/templates/web_demo/`: Flask templates.
- `a11yway/static/web_demo/`: web UI CSS.
- `a11yway/workflow_packs/`: bundled workflow definitions.
- `tests/`: unit and integration tests.
- `scripts/`: release and deployment smoke scripts.

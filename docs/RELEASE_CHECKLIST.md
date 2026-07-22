# Release Checklist

Before a release:

1. Run the full test suite.
2. Regenerate `docs/WCAG22_COVERAGE.md` from the JSON registry.
3. Build the package artifacts.
4. Run the wheel smoke script.
5. Build the Render Docker image.
6. Run `scripts/render_docker_smoke.py` inside that image.
7. Check that generated reports, screenshots, outreach files, and local audit output are not staged.
8. Confirm README and package metadata still describe the same public behavior.

Do not publish a release from a dirty tree.

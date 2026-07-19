.PHONY: validate roadmap roadmap-status issues test quality methods bundle verify-bundle bootstrap-dry-run

validate:
	uv run riopa validate --root .
	uv run riopa roadmap validate --root .

roadmap:
	uv run riopa roadmap validate --root .

roadmap-status:
	uv run riopa roadmap status --root . --output ROADMAP_STATUS.md

issues:
	uv run riopa roadmap generate-issues --root .

# Unit and integration tests.
test:
	uv run pytest

quality:
	uv run ruff check .
	uv run ruff format --check .
	uv run riopa validate --root .
	uv run riopa roadmap validate --root .
	uv run pytest --cov=riopa_provenance --cov-branch --cov-report=term-missing --cov-fail-under=90

methods:
	uv run riopa methods --manifest examples/minimal/snapshot-manifest.json --output examples/minimal/METHODS.md

bundle:
	uv run riopa research-object --manifest examples/minimal/snapshot-manifest.json --output-dir dist/example-research-object

verify-bundle: bundle
	cd dist/example-research-object && sha256sum --check checksums.sha256

bootstrap-dry-run:
	bash scripts/bootstrap_github.sh \
		--owner edithatogo \
		--repo riopa-infrastructure \
		--visibility public \
		--create-project \
		--create-issues \
		--cross-repo \
		--mirror-umbrella

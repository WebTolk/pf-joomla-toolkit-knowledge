# Joomla Toolkit for ProcessForge

Version **1.0.1** · Package `joomla.toolkit.documentation` · Resource `joomla-toolkit`

A portable knowledge package with Joomla architecture rules, extension structures and Joomla 6 REST API notes. This first release preserves the existing toolkit; substantive updates will follow in separate releases. The copied documentation includes historical development-flow references from its original baseline.

## Download and updates

Download `joomla.toolkit.documentation-1.0.1.zip` from [GitHub Releases](https://github.com/WebTolk/pf-joomla-toolkit-knowledge/releases). Use the package ZIP asset for PF installation; GitHub source-code archives contain repository tooling and are not installation assets.

The stable update server is hosted entirely in GitHub Releases:

- Manifest: `https://github.com/WebTolk/pf-joomla-toolkit-knowledge/releases/latest/download/joomla-toolkit.json`
- Changelog: `https://github.com/WebTolk/pf-joomla-toolkit-knowledge/releases/latest/download/CHANGELOG.md`

Both URLs are included in `package.yaml` inside the ZIP. Each manifest version points to a tag-specific ZIP and includes its SHA-256. The `latest` URL advances with each stable GitHub release; prereleases must not replace the stable release. Installation remains an explicit operator action.

## Installation

Unpack the package ZIP into a receiving workplace's chosen package directory and register its `package.yaml` through that workplace's package roots and knowledge-package registry. Keep the IDs above. The resource path is package-relative and needs no private documentation root. Run the native `knowledge-package-doctor` and refresh the package's resource index after registration.

For an existing original 1.0.0 installation, the package has no update URL yet. Add the `update_sites` block from `updates/bootstrap-package-site.yaml` to its installed `package.yaml`, preserving its version, resources and other metadata. This one-time metadata registration lets PF discover the first external release. A global bootstrap-source entry alone does not create an installed-entity candidate in the verified PF version. After installation, the package's own `update_sites` keeps discovery working.

```text
python <pf-cli> update entity-sources rebuild --workplace <workplace>
python <pf-cli> update candidates refresh --workplace <workplace>
python <pf-cli> update candidates list --workplace <workplace>
python <pf-cli> update stage --workplace <workplace> --candidate <candidate-id>
python <pf-cli> update verify --workplace <workplace> --candidate <candidate-id>
python <pf-cli> update apply --workplace <workplace> --candidate <candidate-id> --confirm
```

The receiving workplace owns the install path. Back up existing installations before applying an update. GitHub Releases and SHA-256 protect artifact identity; release assets must never be replaced under an already published version.

## Development and release

```text
python -m pip install -r requirements.txt
python tools/check.py
python tools/release.py
python tools/test_native_updater.py --pf-root <installed-pf-root>
```

Run native updater tests against the installed PF Core before release; pass `--remote` after publishing to test the public release URLs. Test workplaces are isolated beneath `.pf/tmp/initial-release/`; shared source packages are not installed or replaced by these tests.

For a new release: update `VERSION`, `package.yaml`, resource version/index and `CHANGELOG.md`; run checks, build the ZIP, commit and push, tag the exact commit, and upload the generated ZIP, `joomla-toolkit.json`, `SHA256SUMS` and `CHANGELOG.md` to a stable GitHub release. The build preserves older manifest versions and refuses to rewrite a published version with different bytes. Publish the next release under a new version.

The project is initialized locally with PF process `knowledge-package-update`, simple coordination and project-local knowledge-maintainer specialization. Private PF state and host configuration are excluded from Git and release assets. See [provenance and licensing](NOTICE.md).

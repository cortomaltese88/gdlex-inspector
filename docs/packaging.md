# Debian packaging

GD LEX Inspector can be built as a local Debian package without root access
and without downloading dependencies:

```bash
./scripts/build_deb.sh
sudo apt install ./dist/*.deb
```

The version in the package filename and control metadata is read from
`pyproject.toml`. The package installs:

- Python sources under `/usr/lib/gdlex-inspector/`;
- the `gdlex-inspector` launcher under `/usr/bin/`;
- the desktop entry under `/usr/share/applications/`;
- the SVG icon under `/usr/share/icons/hicolor/scalable/apps/`;
- the README and license under `/usr/share/doc/gdlex-inspector/`.

The Debian package depends on `python3` and `python3-pyside6`. This dependency
keeps both the CLI and the bundled GUI usable after installation.

## Future APT distribution

The current workflow only creates a local `.deb` and a CI artifact. A future
APT publishing step will need a repository layout, signed metadata, retention
rules, and an explicit release process. Signing keys and publishing tokens must
remain outside this repository and be supplied by the publication environment.

No APT repository, package signing, tag, or release is created by the current
build script or CI workflow.

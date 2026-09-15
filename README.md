# homebrew-tap
Official Homebrew tap for the Specz CLI

```sh
brew install specz-ai/homebrew-tap/specz
```

## Releases

Maintainers stage a CLI-only prerelease containing `specz_cli-X.Y.Z.tar.gz` and
`specz.rb`, then trigger **Build and publish Specz CLI** with that version.
The workflow builds and tests source installations on Apple Silicon and Intel,
uploads candidate bottles, and verifies bottle installs on fresh runners.
Only successful verification updates the stable formula and latest release.

Native jobs use standard GitHub-hosted runners in this public repository and
only public CLI assets. No private-repository checkout or external credentials
are required. Tests and builds have read-only permissions; only publishing jobs
can update releases or the formula.

To retry an incomplete candidate, rerun the failed workflow jobs or dispatch
`release.yml` with the same version. Stable releases cannot be overwritten and
promotion refuses to downgrade the formula.

Validate workflow contracts locally with:

```sh
python3 -m unittest discover -s tests -v
ruby -c Formula/specz.rb
```

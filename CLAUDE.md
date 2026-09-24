<!-- //// Neoffice — added file (no upstream equivalent on version-3): branch/remote
     //// conventions of this fork and the commit-the-build pipeline. Upstream develop
     //// ships a CLAUDE.md of its own (a symlink to AGENTS.md); if the fork ever
     //// follows develop again, keep this file and import theirs with @AGENTS.md.
     //// (Rewritten in English at the 2026-09-24 merge; it was in French.) -->

# Neoffice fork conventions

## Branches and remotes

- **Production branch:** `version-15` on `origin` (bvisible/insights). The fleet pulls it.
- **Upstream (read only):** `upstream` → https://github.com/frappe/insights.git,
  branch **`version-3`** (the release line; `version-3-hotfix` feeds it).
- Always push to `origin`, never to `upstream`.
- Sync: `git fetch upstream && git merge upstream/version-3` on a
  `merge/upstream-version-3-<date>` branch, test on osiris, then fast-forward `version-15`.
- `NEOFFICE_FORK_MARKERS.md` lists every `////` marker and what to do with it at the next
  merge. Every change to upstream code carries a `//// Neoffice — <why>` marker.

### Why version-3 and not develop (decided 2026-09-24)

Our fleet runs Frappe **v15** (fork `bvisible/frappe`, branch `version-15`). Upstream's
`develop` now targets Frappe **develop**: its CI tests it there, and its frontend links
`@framework/ui` to `../../frappe/ui` and imports pieces that exist only in Frappe develop
(`telemetry`, `components/TrialBanner`). It cannot be built against our frappe. `version-3`
is the line upstream releases for v15 and v16; it carries the same security fixes and the
same features that matter here (prebuilt module dashboards and their nudge). Until
2026-09-24 this fork followed `develop`; both lines share our old base `2a44ecbb`.

## Build pipeline (commit-the-build)

Never run `yarn build` or `bench build --app insights` on a Neoffice server: the instances
have 2–4 GB of RAM and the vite build is OOM-killed. The SPA build only runs on GitHub
Actions (`bench build --app insights` still bundles `insights/public/js/*.bundle.js`, the
desk-side nudge, which is small).

1. Change a source file under `frontend/`, commit, `git push origin version-15`. Do not build.
2. `.github/workflows/build-frontend.yml` sees the push, runs `yarn build` on ubuntu-latest
   (Node 20) and commits the artifacts back as `[skip-build] frontend artifacts for <SHA>`
   (author `github-actions[bot]`).
3. On the instances the update pipeline pulls both commits. When `bench build --app insights`
   runs, the root `package.json` finds the artifacts already present and skips vite.

### Paths

- Frontend source: `frontend/` (the v3 app in `frontend/src2/`, the legacy v2 app in
  `frontend/src/`)
- Vite artifacts (committed): `insights/public/frontend/`
- SPA HTML entries (committed): `insights/www/insights.html` and `insights/www/insights_v2.html`,
  committed together: both are rewritten by every build.
- Root build script: `cd frontend && yarn build` → `copy-html-entry` + `copy-html-entry2`.

### Forcing a local rebuild (on a workstation, never on a server)

```bash
FORCE_REBUILD=1 yarn build
```

### Further reading

- Canonical pattern: `bvisible/neoffice-devops:main` → `docs/COMMIT-BUILD-PATTERN.md`
- Obsidian: `NORA/04-savoir-faire/drive-frontend-build-pattern`

# Neoffice fork markers

Every change this fork makes to code we did not write carries a `//// Neoffice`
comment saying **why** (see `CLAUDE.md`, rule "mark every change to code that is
not ours"). At the next upstream merge, `grep -rn "////"` must give the complete
map of our divergence.

This file is the other half of that map: it records the **base** the markers are
measured against, and every divergence that **cannot carry a comment** — JSON,
PO/POT, images, lock files, generated build artifacts, and hunks whose syntax
has no room for a comment.

---

## insights

Fork `bvisible/insights`, branch **`version-15`** · upstream `frappe/insights`
(default branch `develop`; release branches `version-3`, `version-3-hotfix`;
legacy `main`).

### The base — and the proof

```
BASE = 2a44ecbb321298faed024708d29936f120f7357e
     = "Merge pull request #790 from mterceno/fix-delete-workbooks-with-folders"
       upstream/develop, 2026-02-09
```

**No upstream branch tip and no upstream tag is contained in our `version-15`**
(`git merge-base --is-ancestor <tip> origin/version-15` fails for every ref under
`refs/remotes/upstream/`). So the base is the plain merge-base, not a swallowed
upstream tip — unlike `webshop` (which contained upstream's tip) or `wiki`
(whose base was the tip of `upstream/version-3`). The merge-base is the *same*
commit for `develop`, `version-3` and `version-3-hotfix`; `main` is a stale 2024
lineage and is not the parent.

Distance from BASE, measured 2026-09-04:

| branch | ahead of BASE |
|---|---|
| `origin/version-15` (ours) | **43** |
| `upstream/develop` | 1041 |
| `upstream/version-3` | 1105 |
| `upstream/version-3-hotfix` | 1076 |

**Attribution.** `git rev-list origin/version-15 ^BASE ^upstream/develop
^upstream/version-3 ^upstream/version-3-hotfix ^upstream/main` returns exactly
**43** commits — the same 43 as `^BASE` alone, i.e. nothing of upstream's leaks
into the range. Authors: Jérémy Christillin 34, our build bot
(`github-actions[bot]`, the commit-the-build and i18n pushes) 9. **Zero**
`(cherry picked from commit …)` lines: this fork carries no backport, so no
marker in the tree says "drop at the merge".

`git blame` (without `-w`) on every unmarked hunk pointed at one of those 43
commits, except the two removal-only hunks of `frontend/components.d.ts`
(a regenerated file — see below).

### What cannot carry a comment

| path | why it is here | what to do at the merge |
|---|---|---|
| `package.json` | JSON, no comment syntax. `"build"` was rewritten to skip `yarn build` when `insights/public/frontend/assets` already exists (`FORCE_REBUILD=1` overrides), and `"build:force"` added. Upstream builds unconditionally; our 2 GB instances OOM, so the fleet pulls the committed artifact instead. | keep ours, re-apply upstream's other script changes by hand |
| `frontend/package.json` | JSON, no comment syntax. `NODE_OPTIONS=--max-old-space-size=4096` prefixed to `"build"` (the default heap is not enough for this SPA), and `"build:force"` added as the twin of the root script. | keep the `NODE_OPTIONS` prefix on whatever upstream's build line becomes |
| `insights/locale/fr.po`, `insights/locale/main.pot` | added files, gettext catalogues — no comment carries meaning to a merge. 502 French strings (commit `323fcc12`). Upstream ships no `fr` catalogue. | keep ours; regenerate the POT, `bench update-po-files`, never hand-merge |
| `insights/public/frontend/**` (216 files) | **committed build output** (vite). Upstream gitignores it. Never mark it, never hand-edit it: it is rewritten wholesale by `yarn build` and by the `build-frontend.yml` bot. | take upstream's source, rebuild, let the bot commit the artifact |
| `insights/www/insights.html`, `insights/www/insights_v2.html` | **generated** by `yarn copy-html-entry[2]` from the vite output. They *do* carry a marker, and that is deliberate: vite copies HTML comments verbatim, so the marker now lives in the sources `frontend/index.html` / `frontend/index_v2.html` and is re-emitted into these two files at every build. Do not hand-edit. | rebuild; the marker comes back on its own |
| `frontend/components.d.ts` | **generated** by `unplugin-vue-components`. Our only divergence is two stale entries (`Autocomplete`, `Popover`) that our regeneration dropped because upstream had already deleted the `.vue` files. Not an intention. | take upstream's file; the plugin rewrites it anyway |
| `.github/workflows/*.yml` (4 added) | ours entirely, no upstream equivalent: `build-frontend.yml` (commit-the-build bot), `tests.yml` + `upstream-preview.yml` (fleet CI, tracker #138), `fork-markers.yml` (this discipline). The marker tool skips `.github/` by design. | keep ours, take upstream's workflows alongside |

No DocType JSON diverges (`git diff --name-only BASE HEAD -- '*.json'` returns
only the two `package.json`), so **nothing here needs to become a Custom Field**.

### Hunks a comment cannot reach

Vue single-file components forbid a comment **inside a multi-line opening tag**,
between attributes. Where an i18n change lands on an attribute line, the marker
sits on the line above the element's **opening tag** instead — still inside the
tool's 3-line lookback, but the marker documents the element, not the attribute:

- `frontend/src2/settings/DataStoreSettings.vue` — `<SettingItem>` ×3, `<Button>` ×1
- `frontend/src2/settings/GeneralSettings.vue` — `<SettingItem>` ×4, `<Button>` ×1
- `frontend/src2/settings/PermissionsSettings.vue` — `<SettingItem>` ×3, `<Button>` ×2
- `frontend/src2/dashboard/Dashboard.vue` — `<Button>` ×1
- `frontend/src2/dashboard/DashboardList.vue` — `<FormControl>` ×1

Same shape inside object literals passed as props (`{ label: __('…') }` in a
`:items` / `dropdownOptions` array): the marker sits above the literal's opening
brace or above the array, never between two keys.

### Whitespace-only divergence

None. Every hunk changes content; no file diverges by indentation or line
endings alone.

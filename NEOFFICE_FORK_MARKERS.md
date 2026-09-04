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
| `insights/locale/fr.po`, `insights/locale/main.pot` | added files, gettext catalogues — no comment carries meaning to a merge. Commit `323fcc12` translated 502 strings; the file now holds **678 entries, 678 translated (100%, polib, no fuzzy)**. Upstream has *since* started shipping its own `locale/` (20+ languages, `fr.po` included) — but upstream's French is **186 translated of 686, 500 untranslated**. | **keep ours**, merge only upstream's *new* msgids into it (`bench generate-pot-file` + `bench update-po-files`). Taking upstream's `fr.po` would drop ~492 finished translations. Never hand-merge a PO. |
| `insights/public/frontend/**` (216 files) | **committed build output** (vite). Upstream gitignores it. Never mark it, never hand-edit it: it is rewritten wholesale by `yarn build` and by the `build-frontend.yml` bot. | take upstream's source, rebuild, let the bot commit the artifact |
| `insights/www/insights.html`, `insights/www/insights_v2.html` | **generated** by `yarn copy-html-entry[2]` from the vite output. They *do* carry a marker, and that is deliberate: vite copies HTML comments verbatim, so the marker now lives in the sources `frontend/index.html` / `frontend/index_v2.html` and is re-emitted into these two files at every build. Do not hand-edit. | rebuild; the marker comes back on its own |
| `frontend/components.d.ts` | **generated** by `unplugin-vue-components`. Our only divergence is two stale entries (`Autocomplete`, `Popover`) that our regeneration dropped because upstream had already deleted the `.vue` files. Not an intention. | take upstream's file; the plugin rewrites it anyway |
| `.github/workflows/*.yml` (4 added) | ours entirely, no upstream equivalent: `build-frontend.yml` (commit-the-build bot), `tests.yml` + `upstream-preview.yml` (fleet CI, tracker #138), `fork-markers.yml` (this discipline). The marker tool skips `.github/` by design. | keep ours, take upstream's workflows alongside |
| `insights/insights/doctype/insights_data_source_v3/insights_data_source_v3.json` | JSON, no comment syntax. Security pass of 2026-09-04 (tracker #231): `connection_string` (was `Text`) and `bigquery_service_account_key` (was `JSON`) became **`Password` at `permlevel: 1`**, and a permission row `{permlevel 1, read, write, Insights Admin}` was appended. Both fields held a database DSN and a service-account private key **in clear**, readable by any `Insights User` through `frappe.client.get_list`. `modified` bumped so instances re-import the doctype. `http_headers` (DuckDB: the headers sent to fetch a remote file, an Authorization among them) and `api_custom_headers` (REST API) were moved to `permlevel: 1` in the same pass — upstream classes them as credentials too — and stay JSON fields. | **upstream/develop already carries the identical `permlevel: 1` on all four fields and the identical permission row** — take theirs, then re-apply the two `fieldtype: Password` values on top. Upstream deliberately keeps the values in clear and relies on the permlevel alone (`insights/tests/test_data_source_credentials.py`: "`Password` fields already mask themselves. These four do not, so they carry a permlevel instead."); we hold both, so the value survives neither a table dump nor a Version record. |
| `insights/insights/doctype/insights_data_source/insights_data_source.json` | JSON, no comment syntax. Same pass: v2's `connection_string` (was `Small Text`) became **`Password` at `permlevel: 1`** with a `{permlevel 1, read, write, System Manager}` row — v2 grants read AND write on this doctype to every `Insights User`, so the DSN travelled with the record. `modified` bumped. | keep ours; upstream has not touched this legacy doctype |

**Two DocType JSON now diverge** (2026-09-04, security pass — see the two rows
above). They do not need to become Custom Fields: both changes are a fieldtype and
a permlevel on fields that already exist, and one of the two is a change upstream
has itself made since. The migration that goes with them —
`insights.insights.doctype.insights_data_source_v3.patches.encrypt_data_source_secrets`
— moves the values already stored in clear into `__Auth` and repairs the permission
level on instances whose permissions are customised (a DocType carrying any
`Custom DocPerm` row ignores its shipped `DocPerm` rows entirely, so the permlevel
row would never have reached them). Nothing else here needs to become a Custom Field.

### Hunks a comment cannot reach

A Vue SFC forbids a comment **inside a multi-line opening tag**, between two
attributes. Where an i18n change lands on such an attribute line, the marker is
placed on the line above the element's **opening tag** — close enough to stay
inside the tool's 3-line lookback in every case but one:

- **`frontend/src2/settings/PermissionsSettings.vue`** — `:label="__('New Team')"`
  sits **3 lines deep** inside its own `<Button …>` opening tag (after `v-if`
  and `class`), so no reachable line can carry a comment. The marker is on the
  `<Button>` element itself and says so; `fork_markers.py check` reports this one
  hunk as unmarked **by design**. It is the only one.

Two more shapes needed a comment style other than the obvious one, and both are
worth knowing before touching them again:

- **inside a JS expression passed as an attribute value** (`:options="[ … ]"` in
  `dashboard/Dashboard.vue`): a `/* //// … */` block comment inside the array is
  valid JS and compiles, where an HTML comment could not go.
- **inside a `v-for` destructuring** (`charts/components/NumberChart.vue`): same
  trick, but the comment **must be one line and must not contain a standalone
  " in " or " of "** — Vue splits the `v-for` value on the first one it finds
  (`forAliasRE`), and a multi-line comment containing "…attributes of a…" broke
  the template compiler outright. Found the hard way.

### Whitespace-only divergence

None. Every hunk changes content; no file diverges by indentation or line
endings alone.

### Where the markers are

Written 2026-09-04 from `47098758` (`origin/version-15`), five comment-only
commits, **180 marker lines across 24 files**. `fork_markers.py check --base
2a44ecbb --head <tip>` goes from **81 unmarked hunks to 1** — that one being the
`:label` of `PermissionsSettings.vue` described above.

| commit | area | what it covers |
|---|---|---|
| `chore(fork): mark build & CI plumbing` | build | `.gitignore`, `vite.config.js`, `components.d.ts`, `CLAUDE.md`, the two `index*.html` sources and their two `www/` artifacts, this manifest |
| `chore(fork): mark the NumberChart label and the disabled upstream patches` | behaviour | `patches.txt`, `charts/components/NumberChart.vue` |
| `chore(fork): mark the NeoCockpit chrome` | chrome | `App.vue` + the two added `NeoCockpit*.vue` |
| `chore(fork): mark the clay design system and the dark mode` | design | `src/index.css`, `src2/index.css`, `charts/colors.ts`, `charts/helpers.ts` |
| `chore(fork): mark the French i18n wrapping` | i18n | 4 `settings/*.vue`, 3 `dashboard/*.vue` |

`frontend/src2/main.ts` already carried a `//// neoffice` marker (lower-case)
from commit `19cca75b`; it was left as it stands — the tool matches on `////`,
and rewriting the line would have made this pass non-comment-only.

### Merge forecast — `upstream/develop`, measured 2026-09-04

Upstream is **1041 commits** ahead of BASE and touches **952 files**; we touch
247 (216 of them the committed build output). **22 files are touched on both
sides** — that is the whole conflict surface:

| file | upstream commits since BASE | what to expect |
|---|---|---|
| `frontend/src/index.css` | 2, **then deleted** | ⚠️ upstream removes the whole legacy `frontend/src/` app (**370 files**) and `frontend/index_v2.html` with it. Our clay token override lives *only* here — see the defect note below; it must be re-homed in `src2/index.css`, not resurrected in a deleted tree. |
| `frontend/components.d.ts` | 2, **then deleted** | conflict disappears; take the deletion |
| `frontend/src2/charts/helpers.ts` | 17 | the heaviest. Our 14 markers are all inside `getXAxis` / `getYAxis` / `getTooltip` / `getLegend` / funnel / map. Re-apply `chartTheme()` on top of upstream's rewritten option builders. |
| `insights/patches.txt` | 16 | append-only on both sides; keep our two commented lines **and** upstream's new entries. A patch listed without its module kills `bench migrate` fleet-wide — check every new entry has its `.py`. |
| `frontend/package.json` | 13 | keep the `NODE_OPTIONS` prefix on whatever the build line becomes |
| `frontend/src2/dashboard/DashboardList.vue` | 13 | 10 i18n markers; re-wrap any string upstream added |
| `insights/locale/*` | 11 / 18 | see the locale row above — keep ours |
| `.gitignore`, `frontend/vite.config.js` | 7 each | keep the un-ignore block and the memory caps |
| `frontend/src2/charts/components/NumberChart.vue` | 6 | the `label` override is 3 small hunks; re-apply |
| `frontend/src2/main.ts`, `App.vue`, `settings/PermissionsSettings.vue`, `dashboard/DashboardCard.vue` | 5–6 each | routine |
| `CLAUDE.md` | 1 | upstream added its own; keep both contents |
| the rest | 1–4 | routine |

**Two DocType JSON diverge** since the 2026-09-04 security pass (see above);
neither has to be re-expressed as a Custom Field at the merge.

Files that exist only on our side (no conflict possible, but they must be
carried forward): the 4 `.github/workflows/*.yml`, the 2 `NeoCockpit*.vue`, the
2 `insights/www/*.html` artifacts, and `insights/public/frontend/**`.

### The 2026-09-04 security pass, and what upstream already fixed

Six defects were fixed on this fork on 2026-09-04 (tracker #231). Measured the
same day against `upstream/develop` (1041 commits ahead of our BASE), **three of
them are already fixed upstream, differently** — those markers say so and must be
resolved by *taking upstream's version*, not by keeping ours:

| ours | upstream/develop | at the merge |
|---|---|---|
| `insights/api/__init__.py` — `_load_doc_for_method()` anchors the document on the stored row | `check_stored_document()` — checks the permission on the stored row before building the payload document | **take upstream's**; ours only predates it. Upstream still does not call `check_if_latest()`, which ours does — keep that half if it still matters |
| `insights/api/data_sources.py` — the three table endpoints call `InsightsTablev3.get_ibis_table()` | `get_permitted_ibis_table()`, same intent | **take upstream's** |
| `insights_query_v3.export()` — `frappe.has_permission()` per linked query | `check_referenced_query_access()`, plus a guard for a dependency that no longer exists | **take upstream's** |
| `insights/permissions.py` — `docs is None` guard in `has_doc_permission()` | **not fixed** (identical code) | keep ours, and it is in the upstream PR |
| `ibis_utils.get_sql_tables_to_restrict()` — CTE shadowing | **not fixed**: `query_utils.extract_sql_table_refs()` still drops every table whose name matches a CTE alias | keep ours, re-express on top of upstream's `_get_sql_table_bindings()`; it is in the upstream PR |
| `connectors/postgresql.py` — quote the DSN credentials only | **not fixed** (`quote_plus` over the whole DSN) | keep ours; it is in the upstream PR |
| the two DocType JSON — `Password` fieldtype + migration | **permlevel only**, values still in clear | keep the fieldtype half; it is in the upstream PR |

The upstream PR is prepared on `bvisible/insights`, branch
`upstream/security-hardening-2026-09`, cut from `upstream/develop` and carrying no
`////` marker. Every marker of this pass names it as its removal condition.

### One defect that changes the merge

`frontend/src/index.css` is the **legacy v2 app's** stylesheet, imported only by
`frontend/src/main.js`. The clay accent override (commit `b99326f9`) was put
there, so it is compiled into `index_v2-*.css` and loaded only by
`insights/www/insights_v2.html` — **not** by `insights/www/insights.html`, the
page users actually open, which loads `index-*.css`. The main SPA therefore
still shows frappe-ui blue for links, focus rings and accent surfaces. Upstream
deletes that whole tree at the merge, which would silently delete the override
with it. **Re-home the token block in `frontend/src2/index.css`** rather than
carrying it into a deleted file. (The clay *chart* palette is unaffected: it
lives in `src2/charts/colors.ts` and is compiled into the shared chunk.)

## Auto-marked (fork-markers workflow)

The fork-markers bot wrote this entry while the file was empty — 7e711e98 had
truncated it (see the commit that restored it). It says the same thing as the
`insights_data_source_v3.json` row of the table above; kept because a marker the
bot wrote is a marker somebody may go looking for.

- `insights/insights/doctype/insights_data_source_v3/insights_data_source_v3.json` — added `"permlevel": 1` to the `http_headers` and `api_custom_headers` fields — both carry credentials (DuckDB fetch `Authorization` header, REST API custom headers) on a doctype readable by every Insights User, so they are locked down like `connection_string`, matching upstream's classification of all four fields as credentials (7e711e98 "fix(security): the two header fields are credentials too")

# Living-history publication

The current reading edition is `index.html`; `history.html` lists every published edition. `versions.json` records the current and eventual final edition plus manuscript SHA-256 hashes.

## Publishing a revision

1. Preserve existing `versions/vNNN/` directories unchanged.
2. Create the next numbered directory with the complete Markdown and rendered HTML, its date and edition label.
3. Append its record and change summary to `versions.json`, update `current_version`, and verify its manuscript hash.
4. Update the current reading page and public edition record. Commit and deploy these paths together.
5. Only on the authors’ explicit designation, set `final_version` to the selected preserved edition and exhibit it prominently on both public pages. Keep all earlier editions.

The private Google Doc is a working copy. Published snapshots remain the record of what readers saw at each edition. Do not publish private source documents or unpublished personal records.

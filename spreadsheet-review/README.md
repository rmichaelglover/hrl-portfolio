# Spreadsheet Review — pilot 0.1

A browser-based, read-only second look at `.xlsx` workbooks. Open the page, choose a workbook, review flags, mark decisions, and download a text or JSON report. No accounts, installation, or Python needed for everyday use.

## Current checks

- Saved Excel error cells.
- Formula text containing a broken `#REF!` reference outside a double-quoted literal.
- A differing relative formula pattern surrounded by four agreeing formulas: two above and two below in the same column.
- A numeric literal inside that same local formula sequence.

Pattern findings are questions, not diagnoses. Intentional fixed-price overrides, subtotals, and other business exceptions can be valid. Negative amounts and duplicate names are not treated as errors. No automatic repairs are made.

## Data handling

Workbook bytes are read into browser memory and passed to a local worker. There is no workbook upload or analysis server, no analytics, and no persistent browser storage. Vendored scripts are served from the same site. The sample button fetches only the public fictional sample. Selecting a real workbook does not send its bytes or filename to the website.

The app cannot write back to the chosen input file. Reports are downloaded only when requested and include flagged cell values, formulas, and review decisions. Closing a workbook clears app-held results and decisions; browser memory reclamation is managed by the browser. Reloading loses decisions. This pilot is not a secure-erasure facility.

## Limits

- `.xlsx` only; no encrypted workbooks or old `.xls` files.
- 12 MB compressed file, 60 MB declared uncompressed ZIP contents, 3,000 ZIP entries, 150,000 populated cells, 30-second processing timeout. ZIP64 containers are excluded.
- Formula calculations are not evaluated or refreshed. Saved error values may reflect an earlier Excel calculation.
- Charts, pivot tables, macros, Power Query, external data connections, linked workbook contents, and business rules are not audited.
- Structured-table and array expressions are excluded from formula-pattern comparisons; their broken-reference and saved-error checks still run. Names and complex Excel reference syntax do not receive a full semantic analysis.
- Hidden sheets are included and labeled. Merged candidate cells are skipped. Local pattern checks require populated immediate neighbors and can miss clustered mistakes, whole-column errors, boundary errors, and errors in short blocks.
- The view shows at most 200 matching findings at once; filters narrow the list, and exports include all findings.

Zero flags is not a certificate of correctness. No real-company accuracy estimate has been established. The earlier synthetic research benchmark is separate from these first product checks; GMM/HRL ranking and automatic repair are not shipped in this pilot.

## Try it

Use “Try the fictional lighting quote.” It contains four expected review locations: D6 (unexpected addition), D11 (intentional fixed amount), D16 (broken reference), and C18 (saved Excel error). B19 is a legitimate negative return and D22 a subtotal; neither should be flagged in this sample. No real customers, company records, or prices are used.

## Feedback for the first pilot

Use one recurring spreadsheet task. Record which flags were useful, intentional, confusing, or missed, whether the explanations made sense, and whether the review saved time. Agree on business-specific rules only after learning what the columns mean. The unidentified reporting/business application is not integrated; its .xlsx exports can be tried within the same limits.

## Development

Serve this directory over HTTP; browser workers need a suitable web origin. From the repository root:

```sh
python3 -m http.server 8786 --bind 127.0.0.1
node spreadsheet-review/test-engine.cjs
```

Open `http://127.0.0.1:8786/spreadsheet-review/` in a modern browser. Test coverage includes reference normalization, legitimate exceptions, saved errors, hidden sheets, non-mutation, known XLSX findings, and invalid containers. Browser checks additionally exercise the worker, file selection, decisions, filters, exports, clearing and invalid files.

`make_sample.py` regenerates the fictional workbook with openpyxl. SheetJS 0.20.3 is vendored under Apache-2.0; see vendor/NOTICE.md and vendor/LICENSE.sheetjs. Other original application files retain the portfolio's existing licensing terms.

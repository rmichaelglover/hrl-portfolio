# UI and sharing review

A light presentation pass, not an exhaustive test of every simulation.

- Added static Open Graph and large-image card metadata to 105 HTML pages.
  Each has a page-specific card; existing artwork is used when available,
  with a branded geometric illustration as fallback. Shared Woodland story
  pages receive metadata through their Jekyll layout.
- The musical hyperobject shares a single-camera, colored-octave preview.
  The interactive stereo view remains available and remains its default.
- Updated homepage scope to include independent sound, geometry, and CA labs;
  pointed its featured launch to the sound field; removed conflicting
  "newest" labels and an unqualified forecasting comparison claim.
- Added a portfolio return link to Conceptual Resolution.
- Scanned internal HTML navigation links, accounting for Markdown pages that
  Jekyll publishes as HTML. No unresolved local targets remained in that scan.
- Checked metadata uniqueness and image availability/dimensions; inspected
  the main sound, portfolio, and CA cards. Existing simulation tests still pass.

Facebook renders the static card, not live canvas animation or audio. Its own
cache and placement can affect when a refreshed image appears or how it crops.
No posts or messages were sent to Facebook.

Maintenance:

    python3 tools/build_social.py
    python3 tools/render_social.py
    python3 tools/check_social.py

The renderer needs Chrome and Python websocket-client. Run after regenerating
site pages. Musical source templates retain their metadata across build.py.

References: https://ogp.me/ (static metadata fields).

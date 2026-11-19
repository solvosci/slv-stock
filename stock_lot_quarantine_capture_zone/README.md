# Shellfish Toxin Zone Control

Requires `mollusk_purification` (see its own README). This module adds
a SECOND, independent quarantine reason: administrative closure of
capture zones due to marine biotoxins, as published by INTECMAR
(Xunta de Galicia).

## Installation

1. Install `mollusk_purification` first (see its README).
2. Copy `toxin_zone_control` into your addons path.
3. Install the Python dependencies used by the INTECMAR PDF parser:
   `pip install pdfplumber requests --break-system-packages`
   (the module installs without them, but the scheduled sync will log
   an error until they are present).
4. Restart Odoo, update the apps list, install "Shellfish Toxin Zone
   Control".

## Configuration

1. **Build your zone hierarchy**: Inventory > Configuration >
   Locations. Create children under "Vendors" for each Ría > Zone >
   Capture Zone > Polygon you source from. On each, check **Is Harvest
   Zone**. If you plan to use the automated sync, also fill in
   **INTECMAR Zone Code** with the official code used in their
   bulletins.
2. **Enter the administrative status history**: Inventory >
   Capture Zone Status (menu), or directly from each zone location's
   "Administrative Status History" tab. At minimum, create one record
   per zone with `state = open`, `date_from` = whenever you started
   tracking it, `date_to` empty.
3. On each product: check **Subject to Capture Zone Control**.
4. At reception, on "Detailed Operations", use the **From** column
   (now editable, restricted to capture zones) to declare the exact
   polygon of origin per line.

## ✅ Parser calibrado (2026-08-09) — estado de la investigación

Contrariamente a lo que sugería mi primera comprobación, el PDF de
INTECMAR PDF **does contain extractable text** (the initial failure
was on my extraction tool's side, not the PDF itself). This was
confirmed by copying real text from a sample table.

**Important finding:** the roman numeral columns (ZONE and the
SUB-ZONE prefix) get corrupted **non-deterministically** during text
extraction (the same "III" comes out as "П", "ПI" or "IПП" in
different rows of the same report — typical of a subsetted font
without a correct CMap for those glyphs). Because of this, the parser
**does not use those columns to identify the zone** — it uses the
**(Ria, Polygon)** pair instead, both of which extract cleanly across
every row of the tested sample.

The regex (`ROW_RE` in `intecmar_sync.py`) was validated against 13
real lines extracted from a sample of the report (Arousa and
Ares-Betanzos rías), including edge cases: hyphenated names, polygons
containing a comma, and a polygon whose own name ends in a token that
could be confused with the PSP/Lipophilic/ASP columns — **13/13
correct**.

**What's left before enabling the cron in production:**

1. Configure `intecmar_ria` and `intecmar_polygon` on each
   `stock.location` marked as a zone (they must match EXACTLY,
   character for character, what INTECMAR publishes — use the
   polygon name, not the roman-numeral code).
2. Manually run `action_dry_run_preview()` (e.g. from Settings >
   Technical > Server Actions, or from the Odoo shell:
   `env['shellfish.intecmar.sync'].action_dry_run_preview()`) against
   the real server — my development environment has no network access
   to `intecmar.gal`, so this part has to be tested on your side.
   Check the logs: it will tell you which changes would be applied
   and which (ria, polygon) pairs did not match any location.
3. Only after a clean dry-run, activate the cron `Shellfish: sync
   INTECMAR toxin zone bulletins`.
4. Reports 1402/1403/1404 (epifaunal/infaunal/scallop) presumably use
   the same row format, but only 1401 (raft) has been validated —
   run the dry-run against those too before trusting them if you use
   them.



## How it works

1. **Reception**: for a controlled product, the receiving line
   declares its zone of origin (`location_id`). On validation, the
   module looks up that zone's administrative state **on the
   reception date** (not "today" — this matters if you enter data
   late) via `intecmar.capture.zone.status.get_state_on_date()`.
   - `open` → lot marked "Not Applicable / Exempt" for this reason.
   - `closed` / `restricted` / `pending` → lot marked **Blocked**,
     physically segregated to the warehouse's quarantine location
     (shared with the purification module), and a `toxin_block_reason`
     is recorded referencing the exact bulletin record.
2. **Combined with purification**: a lot only physically leaves
   quarantine once BOTH `purification_state` and `toxin_block_state`
   are cleared (`is_ready_for_sale = True`). Whichever mechanism
   clears last triggers the actual stock transfer.
3. **Manipulation guard**: while `toxin_block_state = 'blocked'`, any
   attempt to confirm a stock move or post a manufacturing order
   involving that lot raises a `UserError` — not just a sales block.
4. **Release**: always manual, from **Inventory > Toxin Block -
   Pending Review**, via the "Release" button on each lot — by design,
   there is no automatic release for this reason.

## Testing without the real INTECMAR connector

You don't need the scraper working to test the core blocking logic:

1. Create a capture zone location (e.g. "Vendors / Ría de Arousa /
   Polígono X"), check "Is Capture Zone".
2. Add a `intecmar.capture.zone.status` record for it:
   `state = closed`, `date_from` = today, `date_to` empty.
3. Mark a test product "Subject to Capture Zone Control".
4. Create a receipt, select that zone in the "From" column of the
   line, validate.
5. Check **Inventory > Toxin Block - Pending Review**: the lot should
   appear. Try moving/selling it — it should be rejected.
6. Click **Release**, confirm. The lot should now show as released
   and (if purification is also clear) physically move back to stock.

## License

LGPL-3

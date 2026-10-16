Blocks lots captured from a capture zone/product-type whose INTECMAR
administrative status is currently closed, tracking each lot's capture
origin(s) - capture zone, product type and date - against
`stock_intecmar_capture_zone`'s status history.

A blocked lot is physically moved to the same quarantine area used by
`stock_lot_quarantine`'s purification hold, and stays there until
manually released and reviewed: unlike a purification hold, a capture
zone closure is never lifted automatically just because time has
passed.

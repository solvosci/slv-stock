Blocks lots captured from a capture zone/product-type whose INTECMAR
administrative status is currently closed, tracking each lot's capture
origin(s) - capture zone, product type and date - against
`stock_intecmar_capture_zone`'s status history.

A blocked lot is physically moved to the same quarantine area used by
`stock_lot_quarantine`'s purification hold, and stays there until its
capture zone/type is reopened for its capture date - reflected
automatically whenever the status history changes - or a manager
releases it by hand. Unlike a purification hold, it is never lifted
automatically just because time has passed.

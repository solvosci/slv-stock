Syncs the Intecmar's microbiological sanitary classification
(A/B/C) per capture zone and product type, bridged to
`stock_intecmar_capture_zone`'s own capture zones via INTECMAR's
biotoxin zone codes.

Not historized: each sync reflects the current classification only.
The same classification code can cover the same capture zone for more
than one product type, and the same (capture zone, product type) pair
can appear under more than one code with a different result.

1.  Capture Zones and product types populate automatically from the
    INTECMAR sync; only create one by hand for a capture zone/type not yet
    published there.
2.  Go to *Inventory \> Configuration \> Toxin Control \> INTECMAR
    State Mapping* to review which states block extraction. A state
    the sync has just registered defaults to blocking; uncheck
    *Blocks Extraction* on the ones that do not.
3.  Go to *Inventory \> Configuration \> Toxin Control \> Capture Zone
    Status* to see the full history, or open a capture zone's own form for
    just its periods. A period can also be entered manually (e.g. an
    administrative resolution not yet reflected by the sync) by
    picking or creating a state on the fly.
4.  A scheduled action runs the sync against INTECMAR hourly.

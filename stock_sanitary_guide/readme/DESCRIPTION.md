Looks up an official sanitary guide (Documento de orixe) issued by
Pesca de Galicia's webservice and attaches it to a receipt line,
filling in the capture zone and biological zone straight from the
guide's own data.

When a guide reports a capture or biological zone that has no real
INTECMAR status tracking behind it, this addon creates it and
resolves its state directly from the guide instead of leaving it
undetermined. INTECMAR's own data always takes precedence where it
already exists; this only fills genuine gaps.

A daily sync also pre-populates capture and biological zones from the
Xunta's own zone catalog, covering zones INTECMAR's feed does not
carry. If a guide is later corrected and a lot's own zone no longer
matches it, that lot is flagged for review instead of being rewritten
automatically.

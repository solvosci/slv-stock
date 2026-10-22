1.  Go to *Settings \> Inventory \> Sanitary Guide (Pesca de
    Galicia)* and set the webservice URL together with both sets of
    credentials: the HTTP Basic Auth pair required by the gateway,
    and the user sent inside the request body itself, identifying
    who is querying the document.
2.  On a receipt subject to zone control, open *Operations \> Detailed
    Operations* on the line and use the *Guía* button to look up a
    guide by its number. Confirming it fills in *Capture Zone* and
    *Biological Zone* on the line from the guide's own data.
3.  Go to *Inventory \> Products \> Sanitary Guides \> Guides* to see
    every guide looked up so far. *Query API* refetches a guide's
    data; *View PDF* downloads the official document on demand
    without storing it.
4.  A guide's *Lots* and *To Review* buttons open the lots linked to
    it; *To Review* only lists the ones whose own zone no longer
    matches the guide's current data.
5.  A scheduled action syncs the Xunta's zone catalog daily, creating
    any capture or biological zone it lists that INTECMAR's own sync
    does not yet cover.

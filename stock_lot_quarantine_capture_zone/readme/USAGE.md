1.  On each product subject to toxin control: *Inventory \> Products
    \> Products*, set its *INTECMAR Product Types*.
2.  When receiving such a product, pick the *Capture Zone* on the
    receipt line before validating. A line received without one is
    not toxin-controlled, and a note is posted on the picking instead.
3.  Go to *Inventory \> Products \> Toxin Control \> Toxin Block -
    Pending Review* to see every lot currently blocked.
4.  A lot is released on its own once its capture zone/type is open
    again for its capture date, reflected the moment that period is
    recorded in `stock_intecmar_capture_zone`. A Purification manager
    can also release it directly from that same list with the
    *Release* button, regardless of what the zone data says.
5.  A lot's own form shows its capture origins and their current
    INTECMAR status on the *Toxin Zone Control* page.

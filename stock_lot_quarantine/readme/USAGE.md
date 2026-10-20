1.  Go to *Inventory \> Configuration \> Warehouses*, open the
    warehouse, and set *Quarantine Location (Purification)* to an
    internal location excluded from its delivery routes and removal
    strategy.
2.  On each product needing a hold period: *Inventory \> Products \>
    Products*, check *Purifiable*, set *Purification Hours*, and make
    sure it is tracked *By Lots*.
3.  Go to *Inventory \> Configuration \> Operation Types* and check
    *Allows Blocked Lots (Purification)* on any operation type whose
    real final destination (the last step of a multi-step route, or
    the only step of a single-step one) should be able to receive a
    blocked lot anyway, such as Manufacturing. Leave it unchecked on
    Delivery Orders and anything else that should never carry one.
4.  Validate a receipt as usual, checking or leaving unchecked
    *Received Already Purified?* on each line.
5.  Go to *Inventory \> Purification Tracking* to see the state and
    time remaining of every lot.
6.  A scheduled action releases a lot automatically once its hours
    have elapsed.

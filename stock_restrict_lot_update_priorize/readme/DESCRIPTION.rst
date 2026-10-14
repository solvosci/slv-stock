This addon is based on ``stock_restrict_lot_update``, which enables forcing lot
reservation.

That automatic reservation only applies for available quantities, not reserved
yet. With this addon, stealing reservation from other moves that previously
reserved our restricted lot is possible in some situations:

* The currently reserved move has no set the same restricted lot.
* There's enough quantity to be stolen.

Moves that have lost their reservations are re-assigned.

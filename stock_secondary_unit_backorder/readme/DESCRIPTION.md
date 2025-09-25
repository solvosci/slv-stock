This is a temporary addon that is needed meanwhile base 'stock_secondary_unit' addon is not fixed.

Originally, when creating a partial delivery, the '_compute_secondary_uom_qty' function should be executed, recalculating the secondary quantity, but it does not.
With this temporary solution, every time the partial delivery is created, the function is forced to be executed for all the lines on the delivery note.

1. First, add the products (marked as ADR or not) to the delivery order.
2. The fields package_qty and package_weight are computed, but can also be manually modified at the stock.move, stock.picking, and stock.picking.batch levels, as long as the record is not in 'Draft', 'Done', or 'Cancelled' state.
3. Printing the consignment note is only allowed if the chosen delivery method has an associated carrier (res.partner).

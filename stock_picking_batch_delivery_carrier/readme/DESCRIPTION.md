This module introduces a mandatory delivery method (carrier_id) field on stock.picking.batch.
It ensures that only pickings with the same delivery method can be grouped in a batch,
and blocks the addition of pickings without an assigned carrier.

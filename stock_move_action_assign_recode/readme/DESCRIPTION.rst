This addon modifies the official Odoo stock.move ``_action_assign`` method 
in order to allow associating all the generated stock of the origin movements 
to the destination, even if it exceeds.

The current source matches (without modifications) to https://github.com/odoo/odoo/commit/7d9264c56ac725c8d19aebad55d5668df2a8c814 . 
If it's used in a later version of Odoo, use this SHA-1 to get differences add
update this implementation, if required.

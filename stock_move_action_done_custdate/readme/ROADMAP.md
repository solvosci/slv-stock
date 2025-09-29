This code could be substituted for a more agressive but maybe more secure one,
replacing current ``_action_done`` methods for ``stock.move`` and
``stock.move.line`` models with a code copy, changing 
``fields.Datetime.now()`` for the desired date.
 
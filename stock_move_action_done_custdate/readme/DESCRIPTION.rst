Enables passing a custom date for a stock move when move is marked as done.

In order to use it, when ``_action_done`` for stock.move is called, a 
``stock_move_custom_date`` variable should exist in ``context``. In that case,
current date for ``stock.move`` and ``stock.move.line`` records will be used.

PLEASE USE IT WITH CAUTION. No checks are passed, no verifications are made.

The current filter is applied with "sm.date <= '{date} 00:00:00'", which evaluates the lots existence up to
the start of the day in UTC. This results in a 1-day offset when interpreted in local time (CEST).

To mitigate this, we opted to increment the date by a whole day, so we query up to
the "start of the next day", which is effectively equivalent to querying "the end of the given day" in CEST.

This is a partial solution: it doesn't properly account for time zones (UTC vs CEST).
We should calculate 00:00:00 CEST of the next day and convert it to UTC before applying it to the filter.

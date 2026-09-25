Tracks a purification/hold period per lot for purifiable products.

Each real storage bin gets a matching quarantine bin, created
automatically the first time it is needed. A blocked lot is physically
moved there and stays until its purification time elapses. Which
operation types (deliveries, internal transfers, manufacturing...) are
allowed to move a blocked lot out of quarantine is configurable per
operation type, not fixed by the addon itself; by default none are,
other than its own automated transfers, so a lot cannot be sold while
blocked as long as that is left unconfigured.

Creates a brand new valuation method by warehouse and date history.

Features summary:

* A history average price can be maintained for a certain category
  by product, warehouse and date. Every date is treated as a closed
  valuation block. In this records a stock summary and its correspondent
  valuation at date is provided, replacing Stock Valuation Layer usage
  for stock-at-date determination.
* As per-warehouse valuation is provided, internal transfers between
  warehouse generate valuations.
* Custom date operations are supported, so a general avarage prices
  and valuations recalculation is provided when a past stock operation is
  marked as done.
* Prices base are purchase incomings and internal transfer inputs.

This addon can be inherited in order to support other processes such
as MRP processes.

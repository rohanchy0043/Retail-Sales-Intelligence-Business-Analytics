# Data Quality Report

## Dataset status
- Source rows: **9,994**
- Cleaned rows: **9,994**
- Rows removed or unavailable for required analysis: **0**

## Cleaning actions
- Trimmed and standardized text fields.
- Converted date and numeric fields; invalid required values were excluded.
- Removed exact duplicate rows.
- Excluded negative sales and non-positive quantities.
- Ship dates earlier than order dates were set to missing rather than deleted.
- Added Year, Month, Quarter, Delivery Days, and Profit Margin fields.

## Impact
- Duplicate rows removed: 0
- Negative-sales rows removed: 0
- Non-positive-quantity rows removed: 0
- Ship-before-order dates corrected to missing: 0

No source records are silently deleted: every exclusion category is documented above.
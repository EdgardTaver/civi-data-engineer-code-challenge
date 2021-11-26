# Assumptions

* A `username` is **unique**.
* If a _User_ has `NULL` latitude or `NULL` longitude, it is considered an invalid entity and it will not be added to _DWH_.
* The position of a _User_ may be **updated** at any time. Therefore, if we attempt to insert a user into _DWH_, but the username already exists, then its position must be updated.

## Regions

* A deleted (soft-deleted) region is **not** considered a valid region.
* The deletion of regions from the **DWH** depends on the soft-deletion process to always work.
# Generate random integer partitions

This is a python wrapper for the rust crate `random-partition` for generating integers partitions with a given number of parts.

# Example

```python
import random_partition_py as rpp

# generates a single partition of 20 into 5 parts
print(rpp.random_partitions(20, 5))

# generates multiple partitions 
print(rpp.random_partitions(20, 5, 3))

# same thing but with an additional seed (note that the seed is kw-only)
print(rpp.random_partitions_seeded(20, 5, 3, seed=0))
```

# Description

Generate approximately uniformly distributed random integer partitions of a given size.

# Algorithm

The algorithm is essentially the algorithm described here https://stackoverflow.com/questions/10287021/an-algorithm-for-randomly-generating-integer-partitions-of-a-particular-length with some core functions rewritten as dynamic programs to make the whole thing more efficient.

# Building

Note that due to an external dependency on a bigint library implemented in C some system setup is required. In particular the M4 macro processor has to be installed (may look like `sudo apt-get install m4`).
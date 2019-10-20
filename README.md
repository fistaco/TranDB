# TranDB

TranDB is a library that makes it easy to make checkers and tests based on transactional logs and
databases. 

The main benefit of TranDB is the concept of *flows*. Given a database where one of the columns
is time, TranDB allows you to define a *flow* as a series of transactions that follow one
another in time given certain criteria.

For example, say you are given this database for CPU core transactions. Say want to see all
`WRs` to any address *A*, and then the next subsequent `RD` to the same address *A*:

| Time | Command | Address  |
| ---- | ------- | -------- |
| 0    | WR      | 0xc0ffee |
| 10   | RD      | 0xc0ffee |
| 20   | NOP     | 0x000000 |
| 30   | WR      | 0x00beef |
| 40   | NOP     | 0x000000 |
| 50   | RD      | 0x00beef |

Given a TranDB object `my_db` with a loaded database, the query above is simply:
```Python
event1 = my_db["Command == WR && Address == @a"] # @a is a match for any address
event2 = my_db["Command == RD && Address == @"]
flow = my_db.flow(event1, event2)
```
The `flow` variable now is a 2D list in Python containing the following:

| Time | Command | Address  |
| ---- | ------- | -------- |
| 0    | WR      | 0xc0ffee |
| 10   | RD      | 0xc0ffee |
| 30   | WR      | 0x00beef |
| 50   | RD      | 0x00beef |

### Prerequisites

Python 3.6+

## Running the tests

Currently calling `TranDB.py` as main will run all unit tests.

## Contributing

Please contribute to this project with the following criteria for your pull requests:
* PEP8 Compilant
* All developed code is unit-tested, ideally done with test-driven development

Please submit issues if you have an enhancement request or if you encounter bugs.

## Authors

* [Sean McLoughlin](https://github.com/SeanMcLoughlin)

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

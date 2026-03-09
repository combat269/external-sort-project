# External K-Way Merge Sort Engine 💾

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![Algorithms](https://img.shields.io/badge/Algorithms-External_Sorting-success?style=for-the-badge)
![Systems](https://img.shields.io/badge/Systems-File_I/O-blue?style=for-the-badge)

## Overview

This project implements a **multi-pass external merge sort engine** designed to sort datasets that **do not fit in main memory**.

External sorting is a fundamental technique used in **database systems**, **storage engines**, and **large-scale data processing**, where files must be sorted under strict memory constraints while keeping disk I/O efficient.

The implementation uses **page-based I/O** to simulate realistic buffer management and performs sorting in two stages:

1. **Run generation** — create sorted chunks that fit into memory
2. **Multi-pass K-way merge** — repeatedly merge sorted runs until one final sorted file remains

The system works with **fixed-size binary records** and sorts them using the **4-byte `product_id` key** stored at the beginning of each record.

---

## Table of Contents

- [How the Algorithm Works](#how-the-algorithm-works)
- [Key Features](#key-features)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [Usage](#usage)
- [Example Workflow](#example-workflow)
- [Configuration](#configuration)
- [Performance Notes](#performance-notes)
- [Concepts Covered](#concepts-covered)

---

## How the Algorithm Works

The external sort runs in two main phases.

### Phase 1 — Run Generation

The input file is read in chunks bounded by the available buffer size.

For each chunk:

- Records are loaded into memory
- Sorted in RAM
- Optionally deduplicated
- Written back to disk as an intermediate **run file**

Each run file is therefore a sorted subset of the original input.

### Phase 2 — Multi-Pass K-Way Merge

After generating all runs, the algorithm merges them using a **K-way merge** strategy.

If the buffer has **B pages**:

- **B - 1 pages** are used for input runs
- **1 page** is used as the output buffer

The algorithm repeatedly merges groups of runs until only one final sorted output file remains.

A **heap-based priority queue** is used to always select the next smallest (or largest) record among the active runs.

---

## Key Features

### Page-Based Disk I/O

The implementation works with **fixed-size pages**, mimicking buffer pool behavior in database systems.

### Heap-Based K-Way Merge

A **priority queue (`heapq`)** is used to efficiently merge multiple sorted runs at the same time.

### Configurable Sorting Order

Supports both **ascending** and **descending** sorting modes.

### Duplicate Elimination

A `unique=True` option removes duplicate records during:

- Run generation
- Merge phase

### Fixed-Size Binary Record Processing

The sorter is designed for binary files containing fixed-size records, making it suitable for systems-style workloads.

### Multi-Pass External Sorting

Handles datasets larger than RAM by repeatedly merging intermediate runs across multiple passes.

---

## Project Structure

```
external-merge-sort/
├── sort_engine.py       # Core sorting engine (run generation + K-way merge)
├── record.py            # Binary record parsing and comparison logic
├── buffer.py            # Page buffer management
├── generate_data.py     # Utility to generate test input files
├── main.py              # Entry point and CLI
├── tests/
│   ├── test_sort.py     # Unit tests for sort correctness
│   └── test_merge.py    # Unit tests for merge logic
└── README.md
```

---

## Getting Started

### Prerequisites

- Python 3.8+
- No external dependencies — uses only the standard library

### Installation

```bash
git clone https://github.com/your-username/external-merge-sort.git
cd external-merge-sort
```

### Generate Test Data

```bash
python generate_data.py --records 100000 --output input.bin
```

---

## Usage

### Basic Sort

```bash
python main.py --input input.bin --output sorted.bin
```

### With Custom Buffer Size

```bash
python main.py --input input.bin --output sorted.bin --buffer-pages 8
```

### Descending Order

```bash
python main.py --input input.bin --output sorted.bin --order desc
```

### With Duplicate Elimination

```bash
python main.py --input input.bin --output sorted.bin --unique
```

### Programmatic Usage

```python
from sort_engine import ExternalSortEngine

engine = ExternalSortEngine(
    page_size=4096,       # bytes per page
    buffer_pages=8,       # number of buffer pages available
    record_size=128,      # bytes per record
    key_offset=0,         # byte offset of sort key within record
    key_size=4,           # sort key is a 4-byte integer
    ascending=True,
    unique=False
)

engine.sort(input_path="input.bin", output_path="sorted.bin")
```

---

## Example Workflow

```text
Unsorted Input File
        ↓
Read chunk into memory  (bounded by buffer size)
        ↓
Sort records in RAM
        ↓
(Optional) Deduplicate
        ↓
Write sorted run to disk
        ↓
Repeat for all chunks
        ↓
K-Way Merge: merge B-1 runs at a time using a min-heap
        ↓
Repeat merge passes until one run remains
        ↓
Final Sorted Output File
```

### Concrete Example

Given a buffer of **4 pages** and an input that produces **12 runs**:

| Pass           | Runs In                 | Runs Out            |
| -------------- | ----------------------- | ------------------- |
| Run Generation | raw input               | 12 sorted runs      |
| Pass 1         | 12 runs (3 groups of 4) | 3 merged runs       |
| Pass 2         | 3 runs                  | 1 final sorted file |

---

## Configuration

| Parameter      | Description                                | Default |
| -------------- | ------------------------------------------ | ------- |
| `page_size`    | Size of one I/O page in bytes              | `4096`  |
| `buffer_pages` | Number of pages held in memory             | `8`     |
| `record_size`  | Size of one record in bytes                | `128`   |
| `key_offset`   | Byte offset of the sort key in each record | `0`     |
| `key_size`     | Size of the sort key in bytes              | `4`     |
| `ascending`    | Sort order (`True` = ascending)            | `True`  |
| `unique`       | Remove duplicate keys                      | `False` |

---

## Performance Notes

- **I/O cost** is approximately **2N × (number of passes)**, where N is the total number of pages
- **Number of passes** = ⌈log<sub>B−1</sub>(N/B)⌉ + 1
- Using a **larger buffer** (more pages) reduces the number of merge passes required
- The **heap-based merge** ensures O(log K) record selection at each step, where K is the number of active runs

---

## Concepts Covered

This project demonstrates and applies the following systems and algorithms concepts:

- External memory algorithms
- Buffer pool management
- Binary file I/O in Python (`struct`, `io`)
- Heap-based priority queues (`heapq`)
- Multi-pass merge strategies
- Fixed-size record formats
- Disk I/O cost analysis

---

## License

This project is licensed under the [MIT License](LICENSE).

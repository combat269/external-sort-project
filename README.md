# External Merge Sort Engine 💾

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![Systems](https://img.shields.io/badge/Systems_Programming-Backend-blue?style=for-the-badge)
![Database](https://img.shields.io/badge/Database_Internals-Algorithms-success?style=for-the-badge)

## 📌 Overview
[cite_start]This project implements a complete multi-pass external sorting algorithm designed to handle massive datasets that exceed available RAM constraints[cite: 9, 16]. [cite_start]Modeled after internal relational database sorting engines, it reads fixed-size binary records (32 bytes), chunks them into memory-bound pages, and utilizes an optimal K-Way merge to produce a fully sorted output file[cite: 15, 36, 70].

## ⚙️ Core Architecture

[cite_start]The sorting process is strictly page-based to simulate realistic database I/O buffer pool management[cite: 18, 39]. The engine executes in two main phases:

### 1. Run Generation (Phase 0)
* [cite_start]Reads the massive unsorted binary file in chunks bounded by a configurable `buffer_pages` and `page_size`[cite: 39, 43].
* [cite_start]Sorts records in-memory based on a 4-byte `product_id` key[cite: 13, 17, 62].
* [cite_start]Writes the intermediate sorted chunks to disk as individual "run" files[cite: 36].

### 2. Multi-Pass K-Way Merge
* [cite_start]Utilizes a Min/Max Heap (Priority Queue) to intelligently stream and merge `k` sorted runs simultaneously[cite: 70].
* [cite_start]Allocates $B-1$ buffer pages for streaming input runs and 1 page for the output buffer[cite: 72].
* [cite_start]Recursively performs merge passes until a single, fully sorted master file remains[cite: 91, 115].

## 🛡️ Key Features & Constraints Handled

* **Strict Page Boundary Alignment:** Safely handles unaligned memory operations. [cite_start]If a 32-byte record does not perfectly fit in the remaining space of a page, the engine respects the boundary by padding the rest of the page and starting the record on the next one[cite: 22, 23]. 
* [cite_start]**Ascending & Descending Sorts:** Configurable sorting order depending on query requirements[cite: 26].
* [cite_start]**Duplicate Elimination:** Includes a `unique` flag that, when enabled, filters out duplicate records during both the initial run generation and the final merge phases to conserve disk space and ensure data integrity[cite: 28, 29, 111].

## 📂 Project Structure

```text
external-sort-project/
├── src/
│   └── external_sort.py        # Core sorting logic and buffer management
├── tests/
│   └── tester.py               # Comprehensive edge-case test suite
├── .gitignore
└── README.md
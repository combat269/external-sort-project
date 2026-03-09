# External Sort

A disk-based **external merge sort** implementation in Python. Designed to sort binary record files that are too large to fit in memory, using a configurable buffer pool and a k-way merge strategy.

---

## Project Structure

```
EXTERNAL-SORT/
├── src/
│   └── external_sort.py      # Core sorting logic
├── tests/
│   └── tester.py             # Automated test suite
├── temp_files/               # Temporary run files (auto-generated, gitignored)
├── .gitattributes
├── .gitignore
└── README.md
```

---

## How It Works

The sort runs in two phases:

### Phase 1 — Run Generation (`generate_runs`)

Reads the input file in chunks that fit within the buffer pool, sorts each chunk in memory, optionally removes duplicates, and writes the sorted chunk as a **run file** to `temp_files/`.

### Phase 2 — K-Way Merge (`merge_runs` / `external_sort`)

Repeatedly merges groups of up to `B-1` run files (where `B` is the number of buffer pages) using a min-heap, until a single sorted output file remains. The final merge writes directly to the output file.

---

## Record Format

Records are **fixed-size binary structs**. The first 4 bytes hold a `uint32` product ID used as the sort key:

```
[ product_id (4 bytes) | padding (28 bytes) ] = 32 bytes total
```

---

## API

```python
from src.external_sort import external_sort

stats = external_sort(
    input_filename="input.bin",
    output_filename="output.bin",
    buffer_pages=5,
    page_size=1024,
    record_size=32,
    ascending=True,   # False for descending
    unique=False       # True to deduplicate by product_id
)

# stats = { "num_runs": int, "num_passes": int, "output_file": str }
```

| Parameter         | Type   | Description                             |
| ----------------- | ------ | --------------------------------------- |
| `input_filename`  | `str`  | Path to the input binary file           |
| `output_filename` | `str`  | Path for the sorted output file         |
| `buffer_pages`    | `int`  | Number of pages in the buffer pool      |
| `page_size`       | `int`  | Size of one page in bytes               |
| `record_size`     | `int`  | Size of one record in bytes             |
| `ascending`       | `bool` | Sort direction (default: `True`)        |
| `unique`          | `bool` | Remove duplicate IDs (default: `False`) |

---

## Running the Tests

```bash
python tests/tester.py
```

The test suite in `tests/tester.py` auto-generates random binary input files, runs the sorter, and validates the output against Python's built-in `sorted()` as ground truth.

### Test Cases

| Test                    | Records | Buffer Pages | Page Size | Mode                 |
| ----------------------- | ------- | ------------ | --------- | -------------------- |
| `Basic_Ascending`       | 100     | 3            | 256 B     | Ascending            |
| `Basic_Descending`      | 100     | 3            | 256 B     | Descending           |
| `Duplicate_Removal`     | 200     | 4            | 256 B     | Unique + Ascending   |
| `Large_Volume_Data`     | 5,000   | 5            | 1,024 B   | Multi-pass merge     |
| `Stress_Page_Alignment` | 200     | 5            | 100 B     | Unaligned boundaries |

Each test prints a `✅ PASSED` or `❌ FAILED` result. On failure, up to 3 mismatched index samples are shown to aid debugging. Input and output files are cleaned up automatically after each test.

---

## Notes

- `temp_files/` is created automatically during sorting and can be safely deleted after a run.
- Records with a `product_id` of `0` are treated as **padding** and skipped during reads.
- The k-way merge uses `B-1` input buffers, where `B = buffer_pages`, leaving one buffer for output.

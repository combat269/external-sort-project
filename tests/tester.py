import os
import sys
import struct
import random
import shutil

# dynamically add the project root to the system path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from src.external_sort import external_sort

# --- CONFIGURATION ---
RECORD_SIZE = 32
TEMP_DIR = "temp_files"

def create_random_input(filename, num_records):
    """Generates a binary file with random 32-byte records."""
    ids = [random.randint(1, 5000) for _ in range(num_records)]
    with open(filename, 'wb') as f:
        for product_id in ids:
            record = struct.pack('I', product_id) + (b'\x00' * 28)
            f.write(record)
    return ids

def read_output_ids(filename):
    """Reads the output file and extracts the product_ids."""
    extracted_ids = []
    empty_record = b'\x00' * RECORD_SIZE
    if not os.path.exists(filename): return None

    with open(filename, 'rb') as f:
        while True:
            chunk = f.read(RECORD_SIZE)
            if not chunk or len(chunk) < RECORD_SIZE: break
            if chunk == empty_record: continue
            extracted_ids.append(struct.unpack('I', chunk[:4])[0])
            
    return extracted_ids

def run_complex_test(test_name, num_records, buffer_pages, page_size, unique=False, ascending=True):
    print(f"\n[{test_name.upper()}] | Records: {num_records} | Buffer: {buffer_pages} | Page Size: {page_size}")
    
    input_file = os.path.join(project_root, f"test_{test_name}_in.bin")
    output_file = os.path.join(project_root, f"test_{test_name}_out.bin")

    # generate and calculate expected truth
    raw_ids = create_random_input(input_file, num_records)
    expected_ids = sorted(list(set(raw_ids)) if unique else raw_ids, reverse=not ascending)
    
    try:
        external_sort(
            input_filename=input_file,
            output_filename=output_file,
            buffer_pages=buffer_pages,
            page_size=page_size,
            record_size=RECORD_SIZE,
            ascending=ascending,
            unique=unique
        )
    except Exception as e:
        print(f"  ❌ CRASH: Exception thrown -> {e}")
        return

    student_ids = read_output_ids(output_file)
    
    if student_ids is None:
        print("  ❌ FAILED: No output file generated.")
        return

    if student_ids == expected_ids:
        print(f"  ✅ PASSED: Array perfectly matched expected output.")
    else:
        print(f"  ❌ FAILED: Expected {len(expected_ids)} records, got {len(student_ids)}.")
        
        # show a sample of the mismatch to help debugging
        limit = min(len(student_ids), len(expected_ids), 3)
        for i in range(limit):
            if student_ids[i] != expected_ids[i]:
                print(f"     -> Index {i}: Expected [{expected_ids[i]}], Got [{student_ids[i]}]")

    if os.path.exists(input_file): os.remove(input_file)
    if os.path.exists(output_file): os.remove(output_file)

if __name__ == "__main__":
    print("🚀 Running Advanced External Sort Test Suite...\n")
    
    temp_path = os.path.join(project_root, TEMP_DIR)
    if not os.path.exists(temp_path): os.makedirs(temp_path)

    # 1. the basics
    run_complex_test("Basic_Ascending", 100, 3, 256, unique=False, ascending=True)
    run_complex_test("Basic_Descending", 100, 3, 256, unique=False, ascending=False)

    # 2. duplicate handling
    run_complex_test("Duplicate_Removal", 200, 4, 256, unique=True, ascending=True)

    # 3. volume stress test (forces multiple K-Way merge passes)
    run_complex_test("Large_Volume_Data", 5000, 5, 1024, unique=False, ascending=True)

    # 4. the trap: unaligned page boundaries (100 is not divisible by 32)
    run_complex_test("Stress_Page_Alignment", 200, 5, 100, unique=False, ascending=True)

    print("\n🏁 Test Suite Finished.")
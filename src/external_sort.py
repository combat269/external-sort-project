import os
import struct
import heapq
import shutil
from typing import List

def get_pid(data):
    #  pulling the 4-byte ID 
    return struct.unpack('I', data[:4])[0]


# -----------------RUN GENERATION
def generate_runs(input_file: str,
                  pool_pages: int,
                  pg_size: int,
                  item_size: int,
                  out_folder: str,
                  is_asc: bool = True,
                  is_unique: bool = False) -> List[str]:
    
    #output directory
    if not os.path.exists(out_folder):
        os.makedirs(out_folder)

    run_files = []
    r_count = 0
    
    # calculating howw  many records we can fit in our buffer pool 
    buffer_limit = pool_pages * pg_size
    items_per_run = buffer_limit // item_size
    read_amount = items_per_run * item_size

    with open(input_file, 'rb') as f_in:
        while True:
            #read as many data as possible to buffer
            raw = f_in.read(read_amount)
            if not raw:
                break
            
            # converting raw bytes into a list of records
            records = [raw[i * item_size : (i + 1) * item_size] for i in range(len(raw) // item_size)]
            
            if not records:
                break

            # sort the internal buffer
            records.sort(key=get_pid, reverse=not is_asc)

            # removing duplicates if unique flag is on
            if is_unique:
                temp = []
                if records:
                    temp.append(records[0])
                    for i in range(1, len(records)):
                        if get_pid(records[i]) != get_pid(records[i-1]):
                            temp.append(records[i])
                records = temp

            # write sorted run into disk
            path = os.path.join(out_folder, f"run_{r_count}.bin")
            with open(path, 'wb') as f_out:
                written = 0
                for r in records:
                    f_out.write(r)
                    written += len(r)
                
                # pad the file with null bytes to reach fully buffer size
                padding = buffer_limit - written
                if padding > 0:
                    f_out.write(b'\x00' * padding)
            
            run_files.append(path)
            r_count += 1

    return run_files


#------------reading runs rec by rec
class RunStreamer:
    # class to read from run files one record at a time
    def __init__(self, path, p_size, i_size):
        self.f = open(path, 'rb')
        self.p_size = p_size
        self.i_size = i_size
        self.data_buf = b"" 
        self.eof = False

    def next_item(self):
        while True:
            # loading more data from disk if buffer is low
            while len(self.data_buf) < self.i_size:
                if self.eof:
                    return None
                chunk = self.f.read(self.p_size)
                if not chunk:
                    self.eof = True
                    break
                self.data_buf += chunk
            
            if len(self.data_buf) < self.i_size:
                return None

            rec = self.data_buf[:self.i_size]
            self.data_buf = self.data_buf[self.i_size:]
            
            #skipping padding records
            if get_pid(rec) != 0:
                return rec
            
            if self.eof or not self.data_buf:
                return None

    def close(self):
        self.f.close()

def merge_runs(files: List[str],
               output_path: str,
               pool_pages: int,
               pg_size: int,
               item_size: int,
               is_asc: bool = True,
               is_unique: bool = False) -> None:

    heap = [] 
    streams = []
    
    # filling the heap with the first  record from  each run
    for i, path in enumerate(files):
        stream = RunStreamer(path, pg_size, item_size)
        item = stream.next_item()
        if item:
            val = get_pid(item)
            key = val if is_asc else -val
            heapq.heappush(heap, (key, i, item))
        streams.append(stream)

    out_cache = []
    prev_val = None 

    with open(output_path, 'wb') as f_out:
        while heap:
            #pop smollest record
            _, idx, rec = heapq.heappop(heap)
            curr_val = get_pid(rec)
            
            # duplicate check during merge
            if is_unique and prev_val is not None and curr_val == prev_val:
                pass 
            else:
                out_cache.append(rec)
                prev_val = curr_val
                
                # flush to disk when page is full
                if len(out_cache) * item_size >= pg_size:
                    for r in out_cache: f_out.write(r)
                    out_cache = []

            # grabbing next from the same run
            next_val = streams[idx].next_item()
            if next_val:
                v = get_pid(next_val)
                k = v if is_asc else -v
                heapq.heappush(heap, (k, idx, next_val))

        if out_cache:
            for r in out_cache: f_out.write(r)

    for s in streams:
        s.close()

def external_sort(input_filename: str,
                  output_filename: str,
                  buffer_pages: int,
                  page_size: int,
                  record_size: int,
                  ascending: bool = True,
                  unique: bool = False) -> dict:
    
    temp_path = "temp_files"
    if not os.path.exists(temp_path):
        os.makedirs(temp_path)
    
    # run the generator of runs
    runs = generate_runs(input_filename, buffer_pages, page_size, record_size, temp_path, ascending, unique)
    
    total_runs = len(runs)
    pass_count = 1
    current_runs = runs
    
    # b-1 pages
    k_merge = max(2, buffer_pages - 1)

    while len(current_runs) > 1:
        next_gen = []
        for i in range(0, len(current_runs), k_merge):
            batch = current_runs[i : i + k_merge]
            
            # last pass writes to the final output file
            if len(current_runs) <= k_merge:
                dest = output_filename
            else:
                # name pattern: out_pass_X_run_Y.bin
                dest = os.path.join(temp_path, f"out_pass_{pass_count}_run_{len(next_gen)}.bin")
            
            merge_runs(batch, dest, buffer_pages, page_size, record_size, ascending, unique)
            
            if dest != output_filename:
                next_gen.append(dest)
        
        current_runs = next_gen
        pass_count += 1

    #copy the only run
    if total_runs == 1:
        shutil.copy(runs[0], output_filename)

    # --> reeturn stats
    return {
        "num_runs": total_runs,
        "num_passes": pass_count,
        "output_file": output_filename
    }
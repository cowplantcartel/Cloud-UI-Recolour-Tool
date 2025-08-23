# The majority of this code was written by p182 (https://github.com/p182) for use in this project
# Thank you so much p182 - I could not have done this without you!!

import re
import struct # for structured writing
import io # to create BytesIO stream
import time # Unix timestamp for DBPF creation and modification date
import os # for os.path.getsize in debug output
import subprocess # for calling the external Refpack compressor
import sys # for platform (OS) check, etc.

# --- DBPF Constants ---
DBPF_SIGNATURE = b'DBPF'
DBPF_MAJOR_VERSION = 0x00000002
DBPF_MINOR_VERSION = 0x00000000
DBPF_USER_MAJOR_VERSION = 0x00000001
DBPF_USER_MINOR_VERSION = 0x00000001
DBPF_UNKNOWN_0x14_FIELD = 0x00000000

DBPF_INDEX_MAJOR_VERSION = 0x00000001
DBPF_INDEX_MINOR_VERSION = 0x00000003 # Typically 3 for DBPF 2.0

RESOURCE_ALIGNMENT = 16 # 16 byte alignment for reading access (filesystem, computing) optimization, not neccesarry, can be disabled for slightly smalller filesize

# --- Helper Functions ---

def _pad_data(data: bytes, alignment: int) -> bytes:
    """Pads data with null bytes to meet specified alignment."""
    padding_needed = (alignment - (len(data) % alignment)) % alignment
    return data + b'\x00' * padding_needed

def _bytes_to_human_readable(num_bytes: int) -> str:
    """Converts a byte count to a human-readable format (KB, MB, GB)."""
    if num_bytes < 1024:
        return f"{num_bytes} B"
    elif num_bytes < 1024 * 1024:
        return f"{num_bytes / 1024.0:.2f} KB"
    elif num_bytes < 1024 * 1024 * 1024:
        return f"{num_bytes / (1024.0 * 1024.0):.2f} MB"
    else:
        return f"{num_bytes / (1024.0 * 1024.0 * 1024.0):.2f} GB"

# --- Refpack Compression Function ---
def compress_refpack(data: bytes) -> bytes:
    """
    Compresses data using an external Rust-based Refpack utility via stdin/stdout.
    Dynamically determines the compressor's executable name based on OS and searches for it.
    """
    compressor_name = "refpack_pipe"
    if sys.platform == "win32": # Check if running on Windows
        compressor_name += ".exe"

    # Possible paths to check for the compressor
    script_dir = os.path.dirname(os.path.abspath(__file__)) # Directory of the current Python script
    
    # Priority 1: In the same directory as the script
    compressor_path = os.path.join(script_dir, compressor_name)
    
    if not os.path.exists(compressor_path):
        # Priority 2: In a 'bin' subfolder relative to the script
        compressor_path = os.path.join(script_dir, "bin", compressor_name)
        
        if not os.path.exists(compressor_path):
            # Fallback: Check if it's in the current working directory (where the user runs the script)
            # This is less reliable for distribution, but useful for quick testing
            compressor_path = os.path.join(os.getcwd(), compressor_name)
            
            if not os.path.exists(compressor_path):
                raise FileNotFoundError(
                    f"Refpack compressor '{compressor_name}' not found. "
                    f"Please place it in '{script_dir}', '{os.path.join(script_dir, 'bin')}', "
                    f"or the current working directory '{os.getcwd()}'."
                )

    startupinfo = None
    creationflags = 0
    if sys.platform == "win32":
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        creationflags = subprocess.CREATE_NO_WINDOW

    proc = subprocess.Popen(
        [compressor_path], # Use the dynamically found path
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        startupinfo=startupinfo,
        creationflags=creationflags
    )
    out, err = proc.communicate(input=data)
    if proc.returncode != 0:
        raise RuntimeError(f"Refpack compression failed (exit code {proc.returncode}):\n{err.decode()}")
    return out

# --- Main DBPF Writer Function ---

def create_dbpf_package(output_path: str, resources: list):
    """
    Creates a DBPF package from a list of provided resources,
    with optional Refpack compression.

    Args:
        output_path (str): The file path where the DBPF package will be saved.
        resources (list): A list of dictionaries, each representing a resource:
            {
                "type_id": uint32,    # The resource Type ID
                "group_id": uint32,   # The resource Group ID
                "instance_id": uint64,# The resource Instance ID
                "data": bytes         # The raw binary data of the resource
                "name": str           # (Optional) Name for logging purposes
            }
    """
    print(f"--- Starting DBPF package creation: {output_path} ---")

    all_data_blocks_buffer = io.BytesIO() # Buffer to collect all resource data
    index_entries_to_write = []           # List to store information for index entries
    current_physical_data_offset = 96     # Data offset starts after the DBPF header (96 bytes)

    # 1. Process each resource: handle as uncompressed, pad, collect data and index info
    for i, res in enumerate(resources):
        type_id = res["type_id"]
        group_id = res["group_id"]
        instance_id = res["instance_id"]
        raw_data = res["data"]
        resource_name = res.get('name', f'Resource {i+1} (Type:0x{type_id:X}, Group:0x{group_id:X}, Instance:0x{instance_id:X})')

        original_data_len = len(raw_data) # This will always be the MemSize
        data_to_process = raw_data         # This will be the data written to disk (could be compressed or original)
        disk_size = original_data_len      # Default to original size on disk
        is_compressed_flag = 0x0000        # Default to uncompressed

        # Compression logic
        if not raw_data:
            print(f"  Warning: {resource_name} has empty data. Skipping compression and writing 0-byte resource.")
            data_to_process = b'' # Ensure empty bytes if data is truly empty
            disk_size = 0
            original_data_len = 0 # MemSize should be 0 for empty data
        else:
            try:
                compressed_data = compress_refpack(raw_data)
                # Check if compressed data is actually smaller
                if len(compressed_data) < original_data_len:
                    data_to_process = compressed_data
                    disk_size = len(compressed_data)
                    is_compressed_flag = 0xFFFF # Mark as compressed
                    #print(f"  Info: {resource_name} compressed from {original_data_len} B to {len(compressed_data)} B.")
                #else:
                    #print(f"  Info: {resource_name} compressed size ({len(compressed_data)} B) is not smaller than original ({original_data_len} B). Using uncompressed data.")
                    # Defaults (data_to_process=raw_data, disk_size=original_data_len, is_compressed_flag=0x0000) are already set
            except (FileNotFoundError, RuntimeError) as e:
                print(f"  Warning: Refpack compression failed for {resource_name}: {e}. Using uncompressed data.")
                # Defaults are already set

        # Pad resource data to the required alignment
        padded_data = _pad_data(data_to_process, RESOURCE_ALIGNMENT)
        
        # Write the padded resource data to the main data buffer
        all_data_blocks_buffer.write(padded_data)

        # Store information needed for the index entry
        index_entries_to_write.append({
            "type_id": type_id,
            "group_id": group_id,
            "instance_id": instance_id,
            "chunk_offset": current_physical_data_offset,
            "disk_size": disk_size,             # Actual size on disk (compressed or uncompressed)
            "mem_size": original_data_len,      # Original uncompressed size
            "is_compressed_flag": is_compressed_flag,
            "unknown_word": 0x0000 # 0x0000 as per usual DBPF observation
        })

        current_physical_data_offset += len(padded_data)

    total_padded_data_bytes = all_data_blocks_buffer.tell() # Total size of all resource data (including padding)
    print(f"\nTotal resource data size (including padding): {_bytes_to_human_readable(total_padded_data_bytes)}")

    # 2. Dynamic Index Header (indextype_main) Calculation
    index_offset = current_physical_data_offset # Index offset is right after all resources data section
    index_entry_count = len(index_entries_to_write) # Index (usually 1 per resource) count in collection

    calculated_index_header_size = 4 # Initial size for indextype_main itself
    calculated_single_entry_base_size = 32 # Default entry size if all TGI parts are in it

    dynamic_index_type_main = 0x00000000

    common_type_id = 0
    common_group_id = 0
    common_instance_high = 0

    if index_entry_count > 0:
        first_entry = index_entries_to_write[0]
        common_type_id = first_entry["type_id"]
        common_group_id = first_entry["group_id"]
        common_instance_high = (first_entry["instance_id"] >> 32) & 0xFFFFFFFF

        all_types_same = True
        for entry in index_entries_to_write:
            if entry["type_id"] != common_type_id:
                all_types_same = False
                break
        
        all_groups_same = True
        for entry in index_entries_to_write:
            if entry["group_id"] != common_group_id:
                all_groups_same = False
                break

        all_instance_high_same = True
        for entry in index_entries_to_write:
            if ((entry["instance_id"] >> 32) & 0xFFFFFFFF) != common_instance_high:
                all_instance_high_same = False
                break

        if all_types_same:
            dynamic_index_type_main |= 0x01 # Set 1 to bitmask
            calculated_index_header_size += 4 # We promoting common entry type into header, so header size higher to store it
            calculated_single_entry_base_size -= 4 # We promoting common entry type into header, so each entry size smaller, because we don't need to store it separately
        if all_groups_same:
            dynamic_index_type_main |= 0x02 # Set 2 to bitmask
            calculated_index_header_size += 4 # We promoting common entry group into header, so header size higher to store it
            calculated_single_entry_base_size -= 4 # We promoting common entry group into header, so each entry size smaller, because we don't need to store it separately
        if all_instance_high_same:
            dynamic_index_type_main |= 0x04 # Set 4 to bitmask
            calculated_index_header_size += 4 # We promoting common higher part of instance ID into header, so header size higher to store it
            calculated_single_entry_base_size -= 4 # We promoting common higher part of instance ID into header, so each entry size smaller, because we don't need to store it separately
        
        print(f"  DEBUG: Dynamic IndexTypeMain: 0x{dynamic_index_type_main:X}")
        if (dynamic_index_type_main & 0x01) != 0:
            print(f"  DEBUG:   Common TypeId: 0x{common_type_id:X}")
        if (dynamic_index_type_main & 0x02) != 0:
            print(f"  DEBUG:   Common GroupId: 0x{common_group_id:X}")
        if (dynamic_index_type_main & 0x04) != 0:
            print(f"  DEBUG:   Common Instance High: 0x{common_instance_high:X}")
    else:
        # No entries, use default flags and sizes
        dynamic_index_type_main = 0x00000000
        calculated_index_header_size = 4
        calculated_single_entry_base_size = 32

    index_size = calculated_index_header_size + (index_entry_count * calculated_single_entry_base_size)
    print(f"  Calculated Index Size: {index_size} bytes")
    print(f"  Number of Index Entries: {index_entry_count}")
    print(f"  Index Offset: {index_offset} bytes")

    # 3. Build DBPF Header (96 bytes total)
    dbpf_header_buffer = io.BytesIO()
    current_unix_time = int(time.time())

    # Pack DBPF header fields (little-endian)
    dbpf_header_buffer.write(DBPF_SIGNATURE)
    dbpf_header_buffer.write(struct.pack('<I', DBPF_MAJOR_VERSION))
    dbpf_header_buffer.write(struct.pack('<I', DBPF_MINOR_VERSION))
    dbpf_header_buffer.write(struct.pack('<I', DBPF_USER_MAJOR_VERSION))
    dbpf_header_buffer.write(struct.pack('<I', DBPF_USER_MINOR_VERSION))
    dbpf_header_buffer.write(struct.pack('<I', DBPF_UNKNOWN_0x14_FIELD))
    dbpf_header_buffer.write(struct.pack('<I', current_unix_time)) # Date Created
    dbpf_header_buffer.write(struct.pack('<I', current_unix_time)) # Date Modified
    dbpf_header_buffer.write(struct.pack('<I', DBPF_INDEX_MAJOR_VERSION))
    dbpf_header_buffer.write(struct.pack('<I', index_entry_count))
    dbpf_header_buffer.write(struct.pack('<I', 0x00000000)) # Old Index Offset
    dbpf_header_buffer.write(struct.pack('<I', index_size)) # Index Size
    dbpf_header_buffer.write(struct.pack('<I', 0x00000000)) # Hole Entry Count
    dbpf_header_buffer.write(struct.pack('<I', 0x00000000)) # Hole Offset
    dbpf_header_buffer.write(struct.pack('<I', 0x00000000)) # Hole Size
    dbpf_header_buffer.write(struct.pack('<I', DBPF_INDEX_MINOR_VERSION))
    dbpf_header_buffer.write(struct.pack('<I', index_offset)) # Actual DBPF 2.0 Index Offset
    dbpf_header_buffer.write(struct.pack('<I', 0x00000000)) # Unknown 2.0 field
    dbpf_header_buffer.write(b'\x00' * 24) # Reserved (3 x ulong = 24 bytes)

    # 4. Build Index Data
    index_data_buffer = io.BytesIO()

    # Write Index Header (indextype_main and common TGI parts)
    index_data_buffer.write(struct.pack('<I', dynamic_index_type_main))
    if (dynamic_index_type_main & 0x01) != 0:
        index_data_buffer.write(struct.pack('<I', common_type_id)) # Promoting common type to header
    if (dynamic_index_type_main & 0x02) != 0:
        index_data_buffer.write(struct.pack('<I', common_group_id)) # Promoting common group to header
    if (dynamic_index_type_main & 0x04) != 0:
        index_data_buffer.write(struct.pack('<I', common_instance_high))# Promoting common higher part of instance ID to header

    # Write individual Index Entries
    for entry in index_entries_to_write:
        # DiskSize is OR-ed with 0x80000000 as per DBPF spec (indicates valid disk size)
        final_disk_size = entry["disk_size"] | 0x80000000 

        # InstanceID (uint64) is split into High and Low DWords for writing
        instance_high = (entry["instance_id"] >> 32) & 0xFFFFFFFF
        instance_low = entry["instance_id"] & 0xFFFFFFFF

        entry_args_for_pack = []

        if (dynamic_index_type_main & 0x01) == 0: # TypeID is NOT common
            entry_args_for_pack.append(entry["type_id"])
        if (dynamic_index_type_main & 0x02) == 0: # GroupID is NOT common
            entry_args_for_pack.append(entry["group_id"])
        if (dynamic_index_type_main & 0x04) == 0: # Instance High is NOT common
            entry_args_for_pack.append(instance_high)
        
        # Instance Low is always written
        entry_args_for_pack.append(instance_low)

        # Remaining fields are always written
        entry_args_for_pack.extend([
            entry["chunk_offset"],
            final_disk_size,
            entry["mem_size"],
            entry["is_compressed_flag"],
            entry["unknown_word"]
        ])
        
        # Determine the struct format string based on what TGI parts were included
        current_entry_format = '<'
        if (dynamic_index_type_main & 0x01) == 0: current_entry_format += 'I' # TypeID
        if (dynamic_index_type_main & 0x02) == 0: current_entry_format += 'I' # GroupID
        if (dynamic_index_type_main & 0x04) == 0: current_entry_format += 'I' # Instance High
        current_entry_format += 'I' # Instance Low (always present)
        current_entry_format += 'IIIHH' # ChunkOffset, DiskSize, MemSize, IsCompressedFlag, UnknownWord
        
        #print(f"  DEBUG - Entry {entry['instance_id']:X}: Format='{current_entry_format}', Args Count={len(entry_args_for_pack)}")
        index_data_buffer.write(struct.pack(current_entry_format, *entry_args_for_pack))

    # 5. Write to file
    with open(output_path, 'wb') as f:
        f.write(dbpf_header_buffer.getvalue()) # Write header
        f.write(all_data_blocks_buffer.getvalue()) # Write resource data
        f.write(index_data_buffer.getvalue()) # Write index

    print(f"\nDBPF package '{output_path}' successfully created.")
    print(f"File size on disk: {_bytes_to_human_readable(os.path.getsize(output_path))}")

# Load contents to import into the package
def read_resources(folder_path):
    pattern = re.compile(r"S3_([0-9A-Fa-f]{8})_([0-9A-Fa-f]{8})_([0-9A-Fa-f]{16})")
    resources = []

    for root, _, files in os.walk(folder_path):
        for filename in files:
            match = pattern.search(filename)
            if match:
                type_id_str, group_id_str, instance_id_str = match.groups()
                file_path = os.path.join(root, filename)
                
                with open(file_path, "rb") as f:
                    file_data = f.read()

                resource = {
                    "type_id": int(type_id_str, 16),
                    "group_id": int(group_id_str, 16),
                    "instance_id": int(instance_id_str, 16),
                    "data": file_data
                }

                resources.append(resource)

    return resources

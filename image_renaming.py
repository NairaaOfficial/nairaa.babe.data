import os
import re
from collections import defaultdict

IMAGE_FOLDER = "images_renamed"
TEMP_EXT = ".tmp"
pattern = re.compile(r"^\d+_\d+\.(png|jpg|jpeg|webp)$", re.IGNORECASE)

# Step 1: Collect and group all valid files regardless of day number
valid_files = [f for f in os.listdir(IMAGE_FOLDER) if pattern.match(f)]
valid_files.sort()  # optional: sort alphabetically before reassigning

# Step 2: Split into batches per day (e.g. every N images = 1 day)
# Let's group by real day logic: scan day numbers from filename
day_group = defaultdict(list)

for f in valid_files:
    match = re.match(r"(\d+)_\d+\.(\w+)", f)
    if match:
        original_day = int(match.group(1))
        day_group[original_day].append(f)

# Step 3: Sort by original_day, but assign new day numbers starting from 1
sorted_original_days = sorted(day_group.keys())

temp_renames = {}
new_day_counter = 1

for original_day in sorted_original_days:
    files = sorted(day_group[original_day])
    for idx, old_name in enumerate(files, start=1):
        ext = os.path.splitext(old_name)[1].lower()
        tmp_name = f"{new_day_counter}_{idx}{ext}{TEMP_EXT}"
        old_path = os.path.join(IMAGE_FOLDER, old_name)
        tmp_path = os.path.join(IMAGE_FOLDER, tmp_name)
        os.rename(old_path, tmp_path)
        temp_renames[tmp_path] = os.path.join(IMAGE_FOLDER, f"{new_day_counter}_{idx}{ext}")
    new_day_counter += 1

# Step 4: Final rename from temporary to actual filename
for tmp_path, final_path in temp_renames.items():
    os.rename(tmp_path, final_path)
    print(f"✅ Renamed to: {os.path.basename(final_path)}")

print("\n🎉 All files renamed with fresh day and index numbers!")

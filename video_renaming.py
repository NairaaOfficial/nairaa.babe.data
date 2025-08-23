import os

def rename_videos_sequentially(folder_path):
    """
    Renames all files in the given folder to Video_1.mp4, Video_2.mp4, etc.
    Args:
        folder_path (str): Path to the folder containing the video files
    """
    if not os.path.exists(folder_path):
        print(f"Error: Folder '{folder_path}' does not exist.")
        return

    files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
    files.sort()  # Sort for consistent ordering

    for idx, filename in enumerate(files, start=1):
        new_filename = f"Video_{idx}.mp4"
        old_path = os.path.join(folder_path, filename)
        new_path = os.path.join(folder_path, new_filename)

        # Skip if already named correctly
        if filename == new_filename:
            continue

        # If the new filename already exists, skip to avoid overwrite
        if os.path.exists(new_path):
            print(f"Warning: '{new_filename}' already exists. Skipping '{filename}'.")
            continue

        try:
            os.rename(old_path, new_path)
            print(f"Renamed: '{filename}' → '{new_filename}'")
        except Exception as e:
            print(f"Error renaming '{filename}': {e}")

    print("\nRenaming complete.")

def main():
    folder_path = "C:/Users/Rohan Arora/Documents/Data_Sharing_AR/SHARE_FINAL_OUTPUT/SET_1/VIDEOS"
    rename_videos_sequentially(folder_path)

if __name__ == "__main__":
    main()

import os
import json
import re

# --- Configuration ---
# Set the base directory containing your image category folders
IMAGES_BASE_DIR = 'images' # Replace with the actual path to your images folder
# Set the desired output path for the JSON manifest file
MANIFEST_OUTPUT_PATH = 'image-manifest.json' # Output file in the same directory as the script
# Set the base path you want to use for image URLs in the manifest (can be empty if not needed)
# If you are serving these images via a web server, this might be '/images' or similar.
# If you just need the relative paths from IMAGES_BASE_DIR, set it to ''
WEB_BASE_PATH = 'images'
# --- End Configuration ---

IMAGE_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.avif']

gallery_data = []

# Function to create a display name from a folder name
def create_display_name(name):
    # Replace underscores/hyphens with spaces and capitalize words
    s = re.sub(r'[_-]', ' ', name)
    return s.title() # Capitalizes the first letter of each word

print(f"Scanning for categories in: {os.path.abspath(IMAGES_BASE_DIR)}")

try:
    # Ensure the base directory exists
    if not os.path.isdir(IMAGES_BASE_DIR):
        raise FileNotFoundError(f"Image base directory not found: {IMAGES_BASE_DIR}")

    # Find categories (subdirectories)
    categories = [d for d in os.listdir(IMAGES_BASE_DIR)
                  if os.path.isdir(os.path.join(IMAGES_BASE_DIR, d))]

    print(f"Found categories: {', '.join(categories)}")

    for category_name in categories:
        category_dir_path = os.path.join(IMAGES_BASE_DIR, category_name)
        category_images_paths = []
        try:
            # List files in the category directory
            files_in_category = os.listdir(category_dir_path)

            # Filter for valid image extensions and sort them CASE-INSENSITIVELY <<< CHANGE HERE
            image_files = sorted([
                f for f in files_in_category
                if os.path.isfile(os.path.join(category_dir_path, f)) and \
                   os.path.splitext(f)[1].lower() in IMAGE_EXTENSIONS
            ], key=str.lower) # <--- Added key=str.lower for case-insensitive sort

            # Create web-accessible paths (or relative paths if WEB_BASE_PATH is empty)
            if WEB_BASE_PATH:
                 # Use forward slashes for web paths, even on Windows
                 category_images_paths = [f"/{WEB_BASE_PATH}/{category_name}/{file}".replace("\\", "/") for file in image_files]
            else:
                 # Store relative paths from the category folder if no web path needed
                 category_images_paths = [os.path.join(category_name, file) for file in image_files]


        except OSError as read_err:
            print(f"Error reading images in category {category_name}: {read_err}")
            continue # Skip to the next category

        if category_images_paths:
            # Determine cover image (first one alphabetically after sorting)
            cover_image = category_images_paths[0]

            # Create a display name for the category
            category_display_name = create_display_name(category_name)

            gallery_data.append({
                'categoryName': category_name, # Folder name
                'categoryDisplayName': category_display_name, # Formatted name
                'coverImage': cover_image,
                'images': category_images_paths,
            })
            print(f" -> Category '{category_name}' added with {len(category_images_paths)} images. Cover: {cover_image}")
        else:
            print(f" -> Category '{category_name}' has no valid images, skipping.")

    # Write the JSON manifest file
    try:
        with open(MANIFEST_OUTPUT_PATH, 'w', encoding='utf-8') as f:
            json.dump(gallery_data, f, indent=2, ensure_ascii=False) # Pretty print JSON
        print(f"\nSuccessfully generated manifest at: {os.path.abspath(MANIFEST_OUTPUT_PATH)}")
    except IOError as write_err:
        print(f"\nError writing manifest file: {write_err}")

except FileNotFoundError as e:
    print(f"Error: {e}")
except Exception as error:
    print(f"An unexpected error occurred: {error}")

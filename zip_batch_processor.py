import subprocess
import os
import threading

# Function to extract a single file using 7z and check its actual output location
def extract_file(zip_path, file):
    try:
        # Extracting file to the current directory
        result = subprocess.run(['7z', 'e', zip_path, file, '-o./extracted'], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        extracted_file_path = f"./extracted/{file}"
        
        if os.path.isfile(extracted_file_path):
            print(f"[Success] Extracted: {extracted_file_path}")
            return extracted_file_path
        else:
            print(f"[Error] Extracted, but file not found in expected path: {extracted_file_path}")
            return None
    except subprocess.CalledProcessError as e:
        print(f"[Error] Failed to extract {file}: {e}")
        return None

# Function to commit and push a single file
def git_commit_and_push(file):
    try:
        # Check if the file exists after extraction
        if os.path.isfile(file):
            # Commit and push the extracted file
            subprocess.run(["git", "add", file], check=True)
            subprocess.run(["git", "commit", "-m", f"Add extracted file: {file}"], check=True)
            subprocess.run(["git", "push"], check=True)

            # Clean up the file after push
            os.remove(file)
            print(f"[Success] Pushed and deleted: {file}")
        else:
            print(f"[Error] File not found after extraction: {file}")
    except subprocess.CalledProcessError as e:
        print(f"[Error] Git operation failed for {file}: {e}")
    except Exception as e:
        print(f"[Error] Failed to delete {file}: {e}")

# Process each batch by extracting files and pushing them to the repository
def process_batch(zip_path, batch):
    threads = []
    for file in batch:
        t = threading.Thread(target=process_file, args=(zip_path, file))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

# Function to handle the processing of a single file: extract, push, and clean up
def process_file(zip_path, file):
    extracted_file = extract_file(zip_path, file)
    if extracted_file:
        git_commit_and_push(extracted_file)

# Main function to process files in batches
def main():
    zip_path = 'zbbig2.zip'  # Path to the ZIP file
    batch_size = 5  # Set the desired batch size

    # Create a directory for extracted files if not exists
    if not os.path.exists('./extracted'):
        os.makedirs('./extracted')

    # Read the list of files to be processed from file_list.txt
    with open('file_list.txt', 'r') as f:
        files = f.read().splitlines()

    # Split files into batches and process each batch
    for i in range(0, len(files), batch_size):
        batch = files[i:i + batch_size]
        process_batch(zip_path, batch)

if __name__ == "__main__":
    main()

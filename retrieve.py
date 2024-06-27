import time
import argparse
import os
from openai import OpenAI

def check_batch_status(client, batch_id):
    return client.batches.retrieve(batch_id)

def retrieve_results(client, output_file_id, index, output_prefix, output_dir):
    content = client.files.content(output_file_id).content
    os.makedirs(output_dir, exist_ok=True)
    with open(f"{output_dir}/{output_prefix}{index}.jsonl", "wb") as f:
        f.write(content)

def wait_for_batch_completion(client, batch_id):
    while True:
        batch_status = check_batch_status(client, batch_id)
        status = batch_status.status
        if status in ['completed', 'failed', 'expired']:
            return batch_status
        time.sleep(60)  # Wait for 60 seconds before checking again

def main(args):
    client = OpenAI(api_key=args.api_key)

    # Get all batch ID files in the specified directory
    batch_files = [f for f in os.listdir(args.batch_dir) if f.startswith(args.batch_prefix) and f.endswith('.txt')]
    if not batch_files:
        print("No batch ID files found in the specified directory.")
        return
    for batch_file in batch_files:
        with open(os.path.join(args.batch_dir, batch_file), 'r', encoding='utf-8') as f:
            batch_id = f.read().strip()
        
        # Extract index from the filename
        index = batch_file.replace(args.batch_prefix, '').replace('.txt', '')
        
        # Wait for the batch to complete
        batch_status = wait_for_batch_completion(client, batch_id)

        # Retrieve the results if completed
        if batch_status.status == 'completed':
            output_file_id = batch_status.output_file_id
            retrieve_results(client, output_file_id, index, args.output_prefix, args.output_dir)
            print(f"Batch {index} processing completed and results retrieved.")
        else:
            print(f"Batch {index} processing did not complete successfully. Status: {batch_status.status}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Retrieve GPT4O batch API results")
    parser.add_argument("--api_key", type=str, help="OpenAI API Key", default="sk-proj-")
    parser.add_argument("--batch_dir", type=str, required=True, help="Directory containing batch files")
    parser.add_argument("--batch_prefix", type=str, default="0527-batch", help="Prefix for batch ID files")
    parser.add_argument("--output_prefix", type=str, default="prev-batch_output_", help="Prefix for output files")
    parser.add_argument("--output_dir", type=str, default="output", help="Directory to save output files")
    args = parser.parse_args()
    main(args)

import os
import argparse
from openai import OpenAI
from glob import glob

def upload_file(client, file_path):
    return client.files.create(
        file=open(file_path, "rb"),
        purpose="batch"
    )

def create_batch(client, batch_input_file_id):
    return client.batches.create(
        input_file_id=batch_input_file_id,
        endpoint="/v1/chat/completions",
        completion_window="24h",
        metadata={
            "description": "image description job"
        }
    )

def main(args):
    client = OpenAI(api_key=args.api_key)

    # Get all JSONL files in the specified directory
    jsonl_files = glob(os.path.join(args.input_dir, f"{args.prefix}*.jsonl"))
    
    for i, file_path in enumerate(jsonl_files):
        batch_input_file = upload_file(client, file_path)
        batch_input_file_id = batch_input_file.id
        batch = create_batch(client, batch_input_file_id)
        print(f"Batch created for file {file_path}:")
        print(batch)

        # Save the batch_id to a file
        output_file = os.path.join(args.output_dir, f"{args.output_prefix}{i}.txt")
        with open(output_file, "w", encoding='utf-8') as f:
            f.write(batch.id)
        print(f"Batch ID saved to {output_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Upload files and create batches for GPT4O API")
    parser.add_argument("--api_key", type=str, help="OpenAI API Key", default="sk-proj-")
    parser.add_argument("--input_dir", type=str, required=True, help="Directory containing input JSONL files")
    parser.add_argument("--output_dir", type=str, required=True, help="Directory to save batch IDs")
    parser.add_argument("--prefix", type=str, default="request052701-", help="Prefix for input JSONL files")
    parser.add_argument("--output_prefix", type=str, default="0527-batch", help="Prefix for output batch ID files")
    args = parser.parse_args()
    main(args)

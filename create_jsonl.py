import json
import os
import base64
import argparse
from typing import List, Dict
from glob import glob

def create_jsonl_file(requests, file_path):
    """
    Create a JSONL file with the given requests.
    :param requests: List of requests.
    :param file_path: Path to the JSONL file.
    """
    
    with open(file_path, 'w', encoding='utf-8') as f:
        for request in requests:
            json.dump(request, f)
            f.write('\n')

def encode_image(image_path):
    """
    Utility function to encode an image to base64.
    :param image_path: Path to the image file.
    """
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')
    
def read_text_file(text_file_path: str) -> str:
    """
    Read the text file and return the content.
    :param text_file_path: Path to the text file.
    
    :return: Content of the text file.
    
    # Note: This function is not used in the current implementation, use if you need some text content.
    """
    with open(text_file_path, "r", encoding='utf-8') as text_file:
        return text_file.read()
    
def prepare_requests(image_files):
    """
    Prepare requests for image description task.
    :param image_files: List of image file paths.
    """
    requests_list = []
    unique_ids = []
    for image_path in image_files:
        alttext_if_exist = ""
        base64_image = encode_image(image_path)
        basename = os.path.basename(image_path)
        unique_ids.append(f"request-{basename}")
        request = {
            "custom_id": f"request-{basename}",
            "method": "POST",
            "url": "/v1/chat/completions",
            "body": {
                "model": "gpt-4o",
                "messages": [
                    {
                        "role": "system",
                        "content": "You are an AI assistant that helps people find information. You will be asked to caption the images for academic classification task. Describe the image in sentences with detailed manner. Omit the redundant articles, pronouns, and try to say in shortest words, with organized structure. If there is no person, describe the image with objects positions and its features. Otherwise, describe the persons, actions and objects with cinematic effects, especially its shot, angle, and actions, gender, age, and special features for each person. Include the colors, appearances, features."
                    },
                {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": f"Describe the image in sentences with detailed manner. {alttext_if_exist}"
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                "max_tokens": 600
            }
        }
        requests_list.append(request)
    return requests_list, unique_ids

def main(args):
    image_directory = args.image_directory
    all_files = glob(os.path.join(image_directory, "**"), recursive=True)
    print(f"Total images: {len(all_files)}")
    exts = ["jpg", "jpeg", "png", "gif", "webp"]
    all_files = [f for f in all_files if os.path.isfile(f)]
    print(f"Total files: {len(all_files)}")
    all_images = [f for f in all_files if f.split(".")[-1].lower() in exts]
    
    splits = [all_images[i:i + args.per_jsonl] for i in range(0, len(all_images), args.per_jsonl)]
    print(f"Total jsonl files: {len(splits)}")
    unique_ids = set()
    for i, image_files in enumerate(splits):
        requests_prepared, uniques = prepare_requests(image_files)
        if any(u in unique_ids for u in uniques):
            print(f"Duplicate unique ids found in batch {i}")
        unique_ids.update(uniques)
        jsonl_file_path = f"{args.prefix}batch_requests_{i}.jsonl"
        create_jsonl_file(requests_prepared, jsonl_file_path)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create JSONL files for GPT4O batch API")
    parser.add_argument("--image_directory", type=str, required=True, help="Directory containing images")
    parser.add_argument("--per_jsonl", type=int, default=120, help="Number of images per JSONL file")
    parser.add_argument("--prefix", type=str, default="request052701-", help="Prefix for output JSONL files")
    args = parser.parse_args()
    main(args)

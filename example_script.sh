API_KEY="sk-proj-"  # Replace with your actual API key
DATASET="/"
# create jsonl files
python create_jsonl.py --image_directory $DATASET --prefix request0702 --output_directory $DATASET
# upload to batch api
python upload_api.py --api_key $API_KEY --input_directory $DATASET --prefix request0702 --output_prefix response0702 --output_directory $DATASET
# retrieve the files (this is blocking operation, do not run in background)
python retrieve.py --api_key $API_KEY --batch_directory $DATASET --batch_prefix response0702 --output_directory $DATASET --output_prefix response_retrieved0702
# match move, this will create .txt files in corresponding file.
# You may see warning message when some results were not successful
python match_move.py --result_directory $DATASET --prefix response_retrieved0702 --find_directory $DATASET

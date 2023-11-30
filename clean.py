# Description: Removes all but location data from a world json file. This is useful for creating a new world map.

import json
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--input-file-name', required=True)


class cleanJson:
    def __init__(self, input_file_path, output_file_path):
        self.input_file_path = input_file_path
        self.output_file_path = output_file_path

    def remove_keys(self, data, keys_to_remove):
        if isinstance(data, dict):
            return {k: self.remove_keys(v, keys_to_remove) for k, v in data.items() if k not in keys_to_remove}
        elif isinstance(data, list):
            return [self.remove_keys(item, keys_to_remove) for item in data]
        else:
            return data

    def process_json_file(self):
        with open(self.input_file_path, 'r') as file:
            data = json.load(file)

        keys_to_remove = ['rooms', 'npcs', 'items', 'containers']
        cleaned_data = self.remove_keys(data, keys_to_remove)

        with open(self.output_file_path, 'w') as file:
            json.dump(cleaned_data, file, indent=4)

        print(f"Cleaned data saved successfully as {self.output_file_path}.")
        print(f"Original data length: {len(data)}")
        print(f"Cleaned data length: {len(cleaned_data)}")

if __name__ == '__main__':
    input_file_path = f'data/worlds/{parser.parse_args().input_file_name}.json'
    output_file_path = f'data/worlds/{parser.parse_args().input_file_name}_cleaned.json'
    cleaner = cleanJson(input_file_path, output_file_path)
    cleaner.process_json_file()
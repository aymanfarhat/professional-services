"""
Copyright 2021 Google LLC

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    https://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""
import re
import argparse
from io import StringIO
from google.cloud import storage


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
            '--file1',
            required=True,
            help='Path for the first file')
    parser.add_argument(
            '--file2', 
            required=True, 
            help='Path for the second file')

    args = parser.parse_args()
    file1_path = parse_gcs_path(args.file1)
    file2_path = parse_gcs_path(args.file2)

    dataflow_output = load_kv_txt(extract_gcs_file(*file1_path))
    flink_output = load_kv_txt(extract_gcs_file(*file2_path))

    # Perform symmetric difference on both sets i.e.
    # return a new set with elements in either the set or other but not both
    diff = set(dataflow_output.items()) ^ set(flink_output.items())
    print(diff)


def extract_gcs_file(bucket_name, path):
    """Download and extract a GCS bucket file into a UTF-8 string"""
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(path)

    return blob.download_as_string().decode('utf-8')


def load_kv_txt(txt):
    """Loads a kv text file represented as string into a dict"""
    a_dictionary = {}
    for line in txt.split('\n'):
        if(len(line) > 0):
            key, value = line.split(':')
            a_dictionary[key] = value.rstrip().strip()

    return a_dictionary


def parse_gcs_path(path):
    p = re.compile(r'^gs:\/\/(.+?)\/(.+)')
    result = p.match(path)
    if result:
        return result.groups()
    else:
        raise Exception('Invalid GCS bucket path format')

if __name__ == "__main__":
    main()

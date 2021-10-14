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
import argparse
import logging
import re
import apache_beam as beam
from apache_beam.io import ReadFromText
from apache_beam.io import WriteToText
from apache_beam.options.pipeline_options import PipelineOptions
from apache_beam.options.pipeline_options import SetupOptions


def main(argv=None, save_main_session=True):
  """Main entry point; defines and runs the wordcount pipeline."""

  parser = argparse.ArgumentParser()

  parser.add_argument(
    '--input',
    required=True,
    help='The file path for the input text to process.')

  parser.add_argument(
    '--output', 
    required=True, 
    help='The path prefix for output files.')

  parser.add_argument(
    '--shards', 
    required=False, 
    type=int,
    help='Number of shards for output')

  args, beam_args = parser.parse_known_args()

  beam_options = PipelineOptions(beam_args)

  with beam.Pipeline(options=beam_options) as p:
    lines = p | ReadFromText(args.input)
    counts = (
        lines
        | 'Split' >> (
            beam.FlatMap(
                lambda x: re.findall(r'[A-Za-z\']+', x)).with_output_types(str))
        | 'PairWithOne' >> beam.Map(lambda x: (x, 1))
        | 'GroupAndSum' >> beam.CombinePerKey(sum))

    def format_result(word_count):
      (word, count) = word_count
      return '%s: %s' % (word, count)

    output = counts | 'Format' >> beam.Map(format_result)

    output | WriteToText(file_path_prefix=args.output, num_shards=args.shards)


if __name__ == '__main__':
  logging.getLogger().setLevel(logging.INFO)
  main()

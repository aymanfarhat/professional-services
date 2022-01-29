# Copyright 2022 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
"""
from postgres import Database
import utils

def extract_db_dump(username, password, host, port, database, dump_file_name):
  connection = f'postgresql://{username}:{password}@{host}:{port}/{database}'
  command = [
      'pg_dump',
      '--clean',
      f'{connection}',
      '-f',
      f'/tmp/{dump_file_name}'
  ]
  utils.sh(command)
  return f'/tmp/{dump_file_name}'

def build_sequence_file(
  username, password, host, port, database, sequence_file_name):
  db = Database(host, database, username, password, port)

  table_sequences = db.execute_query("""
      SELECT
          tbls.table_name as tbl,
          cols.column_name as col,
          PG_GET_SERIAL_SEQUENCE(tbls.table_name, cols.column_name) as serial_seq
      FROM information_schema.tables tbls
      JOIN information_schema.columns as cols
      ON cols.table_name = tbls.table_name
      WHERE
      tbls.table_schema NOT IN ('information_schema', 'pg_datalog') AND
      tbls.table_type = 'BASE TABLE' AND
      PG_GET_SERIAL_SEQUENCE(tbls.table_name, cols.column_name) IS NOT NULL;
      """)

  sequence_sql = ''
  for seq in table_sequences:
    table_name, column_name, seq_name = seq
    max_val_query = f"""SELECT MAX({column_name}) FROM {table_name}"""
    max_val_result = db.execute_query(max_val_query)
    max_val = max_val_result[0][0]
    if max_val is not None:
      sequence_sql += f"SELECT setval('{seq_name}', {(max_val + 1)});\n"

  output_write_path = f'/tmp/{sequence_file_name}'
  with open(output_write_path, 'w', encoding='utf-8') as sequence_output:
    sequence_output.write(sequence_sql)

  return output_write_path

def import_db(username, password, host, port, database, gcs_sql_file_path):
  utils.sh([
    'gsutil',
    'cp',
    gcs_sql_file_path,
    '/tmp/'
  ])

  split_path = gcs_sql_file_path.split('/')

  return utils.sh([
    'psql',
    '-d',
    f'postgresql://{username}:{password}@{host}:{port}/{database}',
    '-f',
    f'/tmp/{split_path[-1]}'
  ])

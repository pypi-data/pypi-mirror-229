from liveramp_automation.helpers.bigquery import BigQueryConnector

project_id = "liveramp-eng-qa-reliability"
dataset_id = "quality_team_test"
table_name = "test"
connector = BigQueryConnector(project_id, dataset_id)
sql_query = f"SELECT * FROM `{project_id}.{dataset_id}.{table_name}` where id >= 1;"
output_csv_path = "tests/test_helpers/test.csv"
bucket_name = "quality_team_test"
source_blob_name = "test.csv"


def test_connect():
    result = connector.connect()
    assert result == 0


def test_query():
    result = connector.query(sql_query)
    if result:
        for row in result:
            print(row)
    assert result


def test_query_rows():
    result = connector.query_rows(sql_query)
    assert result


def test_query_export():
    result = connector.query_export(sql_query, output_csv_path)
    assert result == 0


def test_dataset_tables():
    result = connector.dataset_tables()
    assert result


def test_insert_from_bucket():
    result = connector.insert_from_bucket(bucket_name, source_blob_name, table_name)
    assert result

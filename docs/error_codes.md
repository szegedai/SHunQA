# Error Codes to handle and to give

## PipelineFailError

- `out_of_domain`: when a query is out of domain
- `reader_failed`: when the reader pipeline was not passed correctly
- `bad_index`: when the provided index doesn't exist
- `cant_connect_to_elastic`: when a connection couldn't be estabilished with Elastic
- `elastic_connection_timeout`: when a connection timeout occurs while waiting for the Elastic response
- `context_aggregation_failed`: when the returned text was not passed correctly

## CheckFailError

- `missing_query`: when query is missing from data
- `missing_key_reader`: when query or context is missing from data
- `missing_query_or_official_contexts`: when query or the official_contexts missing
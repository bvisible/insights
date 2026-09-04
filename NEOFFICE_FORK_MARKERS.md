# Neoffice fork markers

## Auto-marked (fork-markers workflow)
- `insights/insights/doctype/insights_data_source_v3/insights_data_source_v3.json` — added `"permlevel": 1` to the `http_headers` and `api_custom_headers` fields — both carry credentials (DuckDB fetch `Authorization` header, REST API custom headers) on a doctype readable by every Insights User, so they are locked down like `connection_string`, matching upstream's classification of all four fields as credentials (7e711e98 "fix(security): the two header fields are credentials too")

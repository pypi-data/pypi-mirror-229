import re

from typing import NamedTuple, Dict, List


class TableInfo(NamedTuple):
    unique_keys: List
    date_time_col: str


def __create_cast_col_sql(column_name, cast_type):
    result = f"CAST({column_name} as {cast_type})"
    return result


def replace_table_names(sql, replacement, table_info_dict, cast_col_map={}):
    from_pattern = r"(?i)\bFROM\s+([^\s()]+)"
    join_pattern = r"(?i)\bJOIN\s+([^\s()]+)"
    for parse_name, pattern in zip(["FROM", 'JOIN'], [from_pattern, join_pattern]):
        for i in re.finditer(pattern, sql):
            group = i.group()
            table_name = group.split(" ")[-1]
            only_table_name = table_name.split(".")[-1]
            table_info = table_info_dict[only_table_name]
            unique_keys = table_info.unique_keys
            unique_keys = [__create_cast_col_sql(uk, cast_col_map[uk]) if uk in cast_col_map else uk
                           for uk in unique_keys]
            sql = re.sub(pattern,
                         r"{0} ({1})".format(parse_name,
                                             replacement.format(unique_keys=",".join(unique_keys),
                                                                date_time_col=table_info.date_time_col,
                                                                table=table_name)), sql)
    return sql


def generate_sql_for_bq(sql, table_info: Dict[str, TableInfo], cast_col_map={}):
    format_sql = """
    SELECT * FROM (
          SELECT
              *,
              ROW_NUMBER()
                  OVER (PARTITION BY {unique_keys} order by {date_time_col} desc)
                  as row_number
          FROM {table}
        )
        WHERE row_number = 1
    """
    result_sql = replace_table_names(sql, format_sql, table_info, cast_col_map)
    return result_sql

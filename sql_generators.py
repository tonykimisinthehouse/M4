def select_query_raw_time_series(table_name, time_column_name, value_column_name,
                                 from_time, to_time, additional_conditions_dict=None):
    """
    :param table_name: relational table name time series data is stored
    :param time_column_name: column used for time attribute / x-scale in the visualization plot
    :param value_column_name: column used for value attribute / y-scale in the visualization plot
    :param from_time: time value that is equivalent to the data type stored in the time column only for now
    :param to_time: time value that is equivalent to the data type stored in the time column only for now
    :param additional_conditions_dict: a dict with dict's keys = column names and dict's values = specific value
    :return:
    """
    if additional_conditions_dict is None:
        additional_conditions_dict = {}
    sqls_select = f"SELECT {time_column_name}, {value_column_name}"
    sqls_from = f"FROM {table_name}"
    sqls_where = f"WHERE {time_column_name} >= {from_time} and {time_column_name} <= {to_time}"
    for condition_column_name in additional_conditions_dict.keys():
        sqls_where += f"AND {condition_column_name} = {additional_conditions_dict[condition_column_name]}"

    result_query = " ".join([sqls_select, sqls_from, sqls_where])
    return result_query


def sql_compute_time_interval(time_column_name, from_time, to_time, num_intervals):
    return f"round({num_intervals}*({time_column_name} - {from_time})/({to_time}-{from_time}))"


def sql_minmax_aggregation(table_name, time_column_name, value_column_name,
                           from_time, to_time,
                           chart_width):
    result_query = f"""SELECT {time_column_name}, {value_column_name} FROM {table_name} JOIN
    (SELECT {sql_compute_time_interval(time_column_name, from_time, to_time, chart_width)} as k,
    min({value_column_name}) as v_min, max({value_column_name}) as v_max
    FROM {table_name} GROUP BY k) as QA
    ON k = {sql_compute_time_interval(time_column_name, from_time, to_time, chart_width)}
    AND ({value_column_name} = v_min OR {value_column_name} = v_max)"""
    return result_query


def sql_m4_aggregation(table_name, time_column_name, value_column_name,
                           from_time, to_time,
                           chart_width):
    result_query = f"""SELECT {time_column_name}, {value_column_name} FROM {table_name} JOIN
    (SELECT {sql_compute_time_interval(time_column_name, from_time, to_time, chart_width)} as k,
    min({value_column_name}) as v_min, max({value_column_name}) as v_max,
    min({time_column_name}) as t_min, max({time_column_name}) as t_max
    FROM {table_name} GROUP BY k) as QA
    ON k = {sql_compute_time_interval(time_column_name, from_time, to_time, chart_width)}
    AND ({value_column_name} = v_min OR {value_column_name} = v_max
    OR {time_column_name} = t_min OR {time_column_name} = t_max
    )"""
    return result_query


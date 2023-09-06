from typing import Union, Any, Tuple


def assert_where_clause_have_all_parameters(
    where_column_name: Union[str, None], where_operator: Union[str, None], where_value: Union[int, str, list, None]
) -> Tuple[Any, str]:
    """
    :param where_column_name: (Union[str, None]) Either or not to use a column name in the 'where' clause.
    :param where_operator: (Union[str, None]) Either or not to use an SQL operator (ex. >, <=, ==, in, between).
    :param where_value: (Union[int, str, list, None]) value(s) to be used in the 'where' clause.

    :return: (tuple[Any, str]) If where clause has all the needed parameters.
    """
    return (where_column_name is None and where_operator is None and where_value is None) or (
        where_column_name is not None and where_operator is not None and where_value is not None
    ), "Using a where requires 3 parameters 'where_value' and 'where_operator' and 'where_column_name'"


def assert_is_aggregate_function_with_where_clause(
    agg_fct: Union[str, None], where_param: Union[str, None]
) -> Tuple[bool, str]:
    """
    :param agg_fct: (Union[str, None]) Either or not to use an aggregate SQL functions (ex. max, min, avg, etc.).
    :param where_param: (Union[str, None]) Either or not to there is a where parameter.
    :return: (tuple[Any, str]) If aggregate function and where clause are not used or one of them is used at a time.
    """
    return (
        (agg_fct is None and where_param is None)
        or (agg_fct is None and where_param is not None)
        or (agg_fct is not None and where_param is None),
        "Wrong order of evaluation. Cannot use 'where' with aggregate function (unless using ''where'' clause "
        "combined with an other 'select' with a 'betwween' or an 'in' for example)",
    )

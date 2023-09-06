import unittest

from sql_repository.utils import assert_where_clause_have_all_parameters, assert_is_aggregate_function_with_where_clause


class UtilsTests(unittest.TestCase):
    def setUp(self):
        self.expected_result_exception_is_where_clause_all_param = (
            "Using a where requires 3 parameters 'where_value' and 'where_operator' and 'where_column_name'"
        )
        self.expected_result_exception_is_agg_with_where_clause = (
            "Wrong order of evaluation. Cannot use 'where' with aggregate function (unless using ''where'' clause "
            "combined with an other 'select' with a 'betwween' or an 'in' for example)"
        )

    def test_givenNoParameters_whenIsWhereClauseHaveAllParameters_thenReturnTrue(self):
        # Given
        a_col_name = None
        a_operator = None
        a_value = None

        # When
        result = assert_where_clause_have_all_parameters(a_col_name, a_operator, a_value)

        # Then
        expected_result = (True, self.expected_result_exception_is_where_clause_all_param)
        self.assertEqual(result, expected_result)

    def test_givenAllParameters_whenIsWhereClauseHaveAllParameters_thenReturnTrue(self):
        # Given
        a_col_name = "tab1"
        a_operator = "in"
        a_value = ["value"]

        # When
        result = assert_where_clause_have_all_parameters(a_col_name, a_operator, a_value)

        # Then
        expected_result = (True, self.expected_result_exception_is_where_clause_all_param)
        self.assertEqual(result, expected_result)

    def test_givenSomeParameters_whenIsWhereClauseHaveAllParameters_thenReturnFalse(self):
        # Given
        a_col_name = "col"
        a_operator = None
        a_value = ["value"]

        # When
        result = assert_where_clause_have_all_parameters(a_col_name, a_operator, a_value)

        # Then
        expected_result = (False, self.expected_result_exception_is_where_clause_all_param)
        self.assertEqual(result, expected_result)

    def test_givenNoAggregateFunctionAndNoWhereClauseParameter_whenIsAggFunctionWithWhere_thenReturnTrue(self):
        # Given
        a_agg_fct = None
        where_param = None

        # When
        result = assert_is_aggregate_function_with_where_clause(a_agg_fct, where_param)

        # Then
        expected_result = (True, self.expected_result_exception_is_agg_with_where_clause)
        self.assertEqual(result, expected_result)

    def test_givenNoAggregateFunctionAndWhereClauseParameter_whenIsAggFunctionWithWhere_thenReturnTrue(self):
        # Given
        a_agg_fct = None
        where_param = "in"

        # When
        result = assert_is_aggregate_function_with_where_clause(a_agg_fct, where_param)

        # Then
        expected_result = (True, self.expected_result_exception_is_agg_with_where_clause)
        self.assertEqual(result, expected_result)

    def test_givenAggregateFunctionAndNoWhereClauseParameter_whenIsAggFunctionWithWhere_thenReturnTrue(self):
        # Given
        a_agg_fct = "max"
        where_param = None

        # When
        result = assert_is_aggregate_function_with_where_clause(a_agg_fct, where_param)

        # Then
        expected_result = (True, self.expected_result_exception_is_agg_with_where_clause)
        self.assertEqual(result, expected_result)

    def test_givenAggregateFunctionAndWhereClauseParameter_whenIsAggFunctionWithWhere_thenReturnTrue(self):
        # Given
        a_agg_fct = "max"
        where_param = "in"

        # When
        result = assert_is_aggregate_function_with_where_clause(a_agg_fct, where_param)

        # Then
        expected_result = (False, self.expected_result_exception_is_agg_with_where_clause)
        self.assertEqual(result, expected_result)

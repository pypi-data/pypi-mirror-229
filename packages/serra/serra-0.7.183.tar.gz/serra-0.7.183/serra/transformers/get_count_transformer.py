from pyspark.sql import functions as F

from serra.transformers.transformer import Transformer

class GetCountTransformer(Transformer):
    """
    A transformer to get the count of occurrences of a column in the DataFrame.

    :param config: A dictionary containing the configuration for the transformer.
                   It should have the following keys:
                   - 'group_by_columns': A list of column names to group the DataFrame by.
                   - 'count_column': The name of the column for which the count is to be calculated.
    """

    def __init__(self, config):
        self.config = config
        self.group_by_columns = config.get("group_by_columns")
        self.count_column = config.get("count_column")

    def transform(self, df):
        """
        Calculate the count of occurrences of the specified column in the DataFrame.

        :param df: The input DataFrame to be transformed.
        :return: A new DataFrame with the count of occurrences of the specified column
                 for each group defined by the 'group_by' column(s).
        """

        return df.groupBy(*self.group_by_columns).agg(F.count(self.count_column))
    
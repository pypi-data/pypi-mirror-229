from pyspark.sql import functions as F

from serra.transformers.transformer import Transformer

class FilterTransformer(Transformer):
    """
    A transformer to filter the DataFrame based on a specified condition.

    :param config: A dictionary containing the configuration for the transformer.
                   It should have the following keys:
                   - 'condition': A list of values to filter the DataFrame by.
                   - 'column': The name of the column to apply the filter on.
    """

    def __init__(self, config):
        self.config = config
        self.filter_values = config.get("filter_values")
        self.filter_column = config.get("filter_column")
        self.is_expression = config.get('is_expression')

    def transform(self, df):
        """
        Filter the DataFrame based on the specified condition.

        :param df: The input DataFrame to be transformed.
        :return: A new DataFrame with rows filtered based on the specified condition.
        """
        if self.is_expression:
            return df.filter(F.expr(self.filter_values))

        return df.filter(df[self.filter_column].isin(self.filter_values))
    
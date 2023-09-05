from serra.transformers.transformer import Transformer
from pyspark.sql.functions import lit,max,min
from pyspark.sql import Window

class GetMaxOrMinTransformer(Transformer):
    """
    Test transformer to add a column to the dataframe with the maximum or minimum value from another column.

    :param config: A dictionary containing the configuration for the transformer.
                   It should have the following key:
                   - 'col_dict' (dict): A dictionary specifying the column to be transformed and the operation to be performed.
                                       The dictionary format should be {'input_column': 'aggregation_type'}.
                                       The output_column will contain the result of the aggregation operation.
    """

    def __init__(self, config):
        self.config = config
        self.columns_and_operations = self.config.get('columns_and_operations')
        self.new_column_names = self.config.get('new_column_names')
        self.group_by_columns = self.config.get("group_by_columns")

    def transform(self, df):
        """
        Add a column with the maximum or minimum value to the DataFrame.

        :param df: The input DataFrame.
        :return: A new DataFrame with an additional column containing the maximum or minimum value.
        """
        window_spec = Window.partitionBy(self.group_by_columns)

        i = 0
        for input_col_name, agg_type in self.columns_and_operations.items():
            if agg_type == 'max':
                result_col = max(input_col_name).over(window_spec)
            elif agg_type == 'min':
                result_col = min(input_col_name).over(window_spec)
            
            df = df.withColumn(self.new_column_names[i], result_col)
            i+=1
        
        return df


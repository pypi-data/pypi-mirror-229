import pandas as pd
import pyspark
from IPython.display import display, HTML

from spark_dataframe_tools.functions.generator import show_pd_df
from spark_dataframe_tools.functions.generator import show_size_df
from spark_dataframe_tools.functions.generator import show_spark_df
from spark_dataframe_tools.utils import BASE_DIR
from spark_dataframe_tools.utils import utils_color

pyspark.sql.dataframe.DataFrame.show2 = show_spark_df
pyspark.sql.dataframe.DataFrame.size = show_size_df
pd.DataFrame.show2 = show_pd_df

style_df = """
<style>
.output_subarea.output_text.output_stream.output_stdout > pre {
   width:max-content;
}
.p-Widget.jp-RenderedText.jp-OutputArea-output > pre {
   width:max-content;
}"""
display(HTML(style_df))

dataframe_all = ["show_pd_df", "show_spark_df", "apply_dataframe"]

__all__ = dataframe_all

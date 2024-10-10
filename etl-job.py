import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job

args = getResolvedOptions(sys.argv, ['JOB_NAME'])
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

# Reading from Glue catalog
datasource0 = glueContext.create_dynamic_frame.from_catalog(database = "demotesting", table_name = "rawcsvstorage", transformation_ctx = "datasource0")

# Writing to S3 in Parquet format
datasink4 = glueContext.write_dynamic_frame.from_options(
    frame = datasource0,
    connection_type = "s3",
    connection_options = {"path": "s3://serverless-glue-lambda-project/transformedparquetstorage/"},
    format = "parquet",
    transformation_ctx = "datasink4"
)

job.commit()
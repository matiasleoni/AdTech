import boto3
import pandas as pd


### COMPLETE THE FOLLOWING CODES:
s3=boto3.client("s3", aws_access_key_id='', aws_secret_access_key='')
bucket_name="bucketdatacruda2"
s3_object="ads_views"

obj=s3.get_object(Bucket=bucket_name, Key=s3_object)
df=pd.read_csv(obj['Body'])


print(df.head())

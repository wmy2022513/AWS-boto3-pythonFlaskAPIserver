
1.python/boto3 script is in the hardware folder
2.software folder is for web development and software.zip is for s3 bucket

execute:

run hardware/server.py
it will create ec2 instance and route 53 record as well as nginx with gunicorn run on the dns-record,
it may take up to couple minutes waiting for the internet register the dns
import boto3
import time

key_path = '<your_key.pem>'
sec_gr = '<your_security_group>'
ami_id = '<your_ami_id>'
region = 'eu-west-1'
tag_name = {"Key": "Name", "Value": "<your_instance_name>"}

client = boto3.client('ec2', region_name=region)

# Define the Userdata script that you want to use.
userdata_script = '''#!/bin/bash
# Update the instance packages
sudo apt -y update
sudo apt-get -y install 

# Install Python
sudo apt install -y python3
sudo apt install -y python3-pip

# Install unzip
sudo apt install unzip

# Install Flask and gunicorn using pip3
sudo apt install -y python3-flask
sudo pip3 install gunicorn

# Install Nginx
sudo apt update
sudo apt install -y nginx

mkdir CA
cd CA
# Download the file using wget
sudo wget https://s3.eu-west-1.amazonaws.com/18.cctstudents.com/software.zip
# Extract the file
sudo unzip software.zip

# Configure Nginx
sudo tee /etc/nginx/nginx.conf > /dev/null <<EOT
user root;
worker_processes auto;
error_log /var/log/nginx/error.log;
pid /run/nginx.pid;

events {
    worker_connections 1024;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    log_format  main  '\$remote_addr - \$remote_user [\$time_local] "\$request" '
                      '\$status \$body_bytes_sent "\$http_referer" '
                      '"\$http_user_agent" "\$http_x_forwarded_for"';

    access_log  /var/log/nginx/access.log  main;

    sendfile on;
    keepalive_timeout 65;

    server {
        listen 80;
        server_name <your_dns_name>;

        location / {
            proxy_pass http://127.0.0.1:5000;
            proxy_set_header Host \$host;
            proxy_set_header X-Real-IP \$remote_addr;
        }
    }
}
EOT

# Create a systemd service for the Flask application
sudo tee /etc/systemd/system/flaskapp.service > /dev/null <<EOT
[Unit]
Description=Flask App
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/CA/software
Environment="PATH=/usr/local/bin"
ExecStart=/usr/local/bin/gunicorn --bind 0.0.0.0:5000 app:app
Restart=always

[Install]
WantedBy=multi-user.target
EOT

# Reload the systemd daemon
sudo systemctl daemon-reload
# Start Nginx
sudo systemctl start nginx
# Enable and start the Flask service
sudo systemctl enable flaskapp
sudo systemctl start flaskapp
#need to restart nginx, otherwise keep giving nginx default page
sudo systemctl restart nginx'''

# Launch a new EC2 instance and pass the Userdata script as a parameter.
response = client.run_instances(
    BlockDeviceMappings=[
        {
            'DeviceName': '/dev/sda1',
            'Ebs': {
                'DeleteOnTermination': True,
                'VolumeSize': 8,
                'VolumeType': 'gp2'
            },
        },
    ],
    ImageId= ami_id,
    InstanceType='t3.micro',
    MaxCount=1,
    MinCount=1,
    KeyName=key_path.split('/')[-1].split('.')[0],
    UserData=userdata_script,
    Monitoring={
        'Enabled': False
    },
    SecurityGroupIds=[
        sec_gr,
    ],
    TagSpecifications=[{'ResourceType': 'instance',
                        'Tags': [tag_name]}]
)

instance_id = response['Instances'][0]['InstanceId']

print(instance_id)

# Wait for instance to start running
while True:
    response = client.describe_instances(InstanceIds=[instance_id])
    instance_state = response['Reservations'][0]['Instances'][0]['State']['Name']

    if instance_state == 'running':
        break

    time.sleep(5)  # Wait for 5 seconds before checking again

# Get instance public IP address
ip_address = response['Reservations'][0]['Instances'][0]['PublicIpAddress']

# Create Route 53 DNS record
route53 = boto3.client('route53')
zone_id = '<your_zone_id>'
dns_name = '<your_dns_name>'

response = route53.change_resource_record_sets(
    HostedZoneId=zone_id,
    ChangeBatch={
        'Changes': [
            {
                'Action': 'UPSERT',
                'ResourceRecordSet': {
                    'Name': dns_name,
                    'Type': 'A',
                    'TTL': 300,
                    'ResourceRecords': [
                        {
                            'Value': ip_address
                        },
                    ],
                }
            },
        ]
    }
)

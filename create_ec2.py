import boto3
import os
import sys
import yaml
import pprint
import time
from botocore.exceptions import ClientError

script_name=os.path.basename(__file__)

if len(sys.argv) < 2:
    print ("usage: {0} <function> [arguments]".format(script_name))
    sys.exit(1)

region = os.environ.get('EC2REGION')

if region is None:
    print ("Please add a region or set the EC2REGION environment variable.")
    sys.exit(1)

print ("> working on region: {0}".format(region))

Access_Id = os.environ.get('AWS_ACCESS_ID')

if region is None:
    print ("Please add a region or set the AWS_ACCESS_ID environment variable.")
    sys.exit(1)

Secret_Key = os.environ.get('AWS_SECRET_KEY')

if region is None:
    print ("Please add a region or set the AWS_SECRET_KEY environment variable.")
    sys.exit(1)

ec2 = boto3.client('ec2')
outfile = open('ec2-keypair.pem','w')
key_pair = ec2.create_key_pair(KeyName='ec2-keypair')
KeyPairOut = str(key_pair['KeyMaterial'])
print ("Generating Key Pair in current direcotry")
outfile.write(KeyPairOut)
outfile.close()
os.system('chmod 400 ec2-keypair.pem')
key='ec2-keypair'

def create():
    if len(sys.argv) < 3:
        print("usage: {0} create <path/to/description.yaml>")
        sys.exit(1)

    try:
        with open(sys.argv[2], 'r') as f:
            y = yaml.load(f,Loader=yaml.FullLoader)
    except IOError:
        print ("{0} not found.".format(sys.argv[2]))
        sys.exit(1)
    blockdevmap = [
        {
            'DeviceName': y['server']['volumes'][0]['device'],
            'Ebs': { 
                'VolumeSize' : y['server']['volumes'][0]['size_gb']
            }
        },
        {
            'DeviceName': y['server']['volumes'][1]['device'],
             'Ebs': { 
                 'VolumeSize' : y['server']['volumes'][1]['size_gb']
            }
        }
    ]
    myCode = """
        #!/bin/bash
        sudo su - 
        useradd user1
        useradd user2
        mkfs.xfs /dev/xvdf
        mkdir /data
        mount /dev/xvdf /data
        mkdir /test
        mkdir /data/test
        chmod 777 /test
        chmod 777 /data/test
        sudo su - user1
        """
    print("creating instance ")
    conn = ec2.run_instances(InstanceType=y['server']['instance_type'],
                              MaxCount=y['server']['min_count'], 
                              MinCount=y['server']['max_count'], 
                              KeyName=key,
                              ImageId=y['server']['ami_type'],
                              BlockDeviceMappings=blockdevmap,UserData=myCode)
    time.sleep(60)
    print("Instance Created")

if __name__ == '__main__':
    getattr(sys.modules[__name__], sys.argv[1])()

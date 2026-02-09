import boto3
import time


ec2 = boto3.resource('ec2', region_name='us-west-1') 
client = boto3.client('ec2', region_name='us-west-1')

def manage_ec2():
   
    print("Launching instances...")
    instances = ec2.create_instances(
        ImageId='ami-0290e60ec230db1e4', 
        MinCount=2,
        MaxCount=2,
        InstanceType='t3.micro'
    )
    
    time.sleep(30)
   
    instance_ids = [instance.id for instance in instances]
    print(f"Created instances: {instance_ids}")

    
    print(f"Stopping instance {instance_ids[0]}...")
    client.stop_instances(InstanceIds=[instance_ids[0]])

    # Give AWS a moment to update statuses
    print("Fetching updated details...\n")
    time.sleep(5) 

    # 3. Fetch and display details of all instances
    print(f"{'Instance Id':<20} {'Type':<15} {'IP Address':<15} {'Status'}")
    print("-" * 65)
    
    all_instances = ec2.instances.all()
    for inst in all_instances:
        
        ip = inst.public_ip_address if inst.public_ip_address else "N/A"
        print(f"{inst.id:<20} {inst.instance_type:<15} {ip:<15} {inst.state['Name']}")

if __name__ == "__main__":
    manage_ec2()
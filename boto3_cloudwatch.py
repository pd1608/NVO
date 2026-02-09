import boto3
from datetime import datetime, timedelta, timezone


session = boto3.Session()
cloudwatch = session.client('cloudwatch')
ec2 = session.client('ec2')

def get_running_instance():
    """Fetches the first running instance ID found in the account."""
    instances = ec2.describe_instances(
        Filters=[{
            'Name': 'instance-state-name', 
            'Values': ['running'] 
        }]
    )
    for reservation in instances['Reservations']:
        for instance in reservation['Instances']:
            return instance['InstanceId']
    return None

def get_metric(instance_id, metric_name):
    """Fetches the average value for a specific metric over the last 30 minutes."""
   
    end_time = datetime.now(timezone.utc) 
    start_time = end_time - timedelta(minutes=30)
    
    response = cloudwatch.get_metric_statistics(
        Namespace='AWS/EC2',
        MetricName=metric_name,
        Dimensions=[{'Name': 'InstanceId', 'Value': instance_id}],
        StartTime=start_time,
        EndTime=end_time,
        Period=1800,
        Statistics=['Average']
    )
    
    datapoints = response.get('Datapoints', [])
    if not datapoints:
        return "No Data"
    
    value = datapoints[0]['Average']
    return f"{value:.2f}"


instance_id = get_running_instance()

if instance_id:
    print(f"Instance ID: {instance_id}")
    print(f"Status Check: {get_metric(instance_id, 'StatusCheckFailed')}")
    print(f"CPU Utilization: {get_metric(instance_id, 'CPUUtilization')}%")
    print(f"Network In: {get_metric(instance_id, 'NetworkIn')} Bytes")
    print(f"Network Out: {get_metric(instance_id, 'NetworkOut')} Bytes")
else:
    print("No running instances found.")
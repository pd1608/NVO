import boto3
import time

# --- CONFIGURATION ---
REGION = 'us-west-1'
MONITORED_IDS = ['i-0472ac4ae47003425', 'i-0b0cd1b28b0ef3873'] 
SNS_TOPIC_ARN = 'arn:aws:sns:us-west-1:778830035283:CPU_alert'
AMI_ID = 'ami-0290e60ec230db1e4' 
INSTANCE_TYPE = 't3.micro'
CPU_THRESHOLD = 0.1            # Threshold in percentage
# ---------------------

ec2 = boto3.client('ec2', region_name=REGION)
cloudwatch = boto3.client('cloudwatch', region_name=REGION)
sns = boto3.client('sns', region_name=REGION)

def get_cpu_usage(instance_id):
    """Fetches CPU utilization from CloudWatch."""
    res = cloudwatch.get_metric_statistics(
        Namespace='AWS/EC2',
        MetricName='CPUUtilization',
        Dimensions=[{'Name': 'InstanceId', 'Value': instance_id}],
        StartTime=time.time() - 600,
        EndTime=time.time(),
        Period=300,
        Statistics=['Average']
    )
    return res['Datapoints'][0]['Average'] if res['Datapoints'] else 0.0

def replace_instance(old_id, usage):
    """Alerts, terminates the existing instance, and launches a new one."""
    print(f"⚠️ High CPU ({usage}%) on {old_id}. Terminating and replacing...")
    
    # Send Notification
    sns.publish(
        TopicArn=SNS_TOPIC_ARN,
        Subject="Existing EC2 Replaced",
        Message=f"Existing instance {old_id} was terminated due to {usage}% CPU usage."
    )
    
    # Terminate Old
    ec2.terminate_instances(InstanceIds=[old_id])
    
    # Spin up NEW (No KeyName used)
    new_launch = ec2.run_instances(
        ImageId=AMI_ID,
        MinCount=1,
        MaxCount=1,
        InstanceType=INSTANCE_TYPE
    )
    new_id = new_launch['Instances'][0]['InstanceId']
    print(f"✅ Replacement Instance ID: {new_id}")
    return new_id

def main():
    print(f"Starting monitor for existing instances: {MONITORED_IDS}")
    
  
    current_targets = list(MONITORED_IDS)

    try:
        while True:
            # Checking every 30 seconds
            time.sleep(30)
            for i, instance_id in enumerate(current_targets):
                usage = get_cpu_usage(instance_id)
                print(f"[{time.strftime('%H:%M:%S')}] {instance_id}: {usage}%")
                
                if usage > CPU_THRESHOLD:
                    new_id = replace_instance(instance_id, usage)
                    # Update our target list to monitor the new instance now
                    current_targets[i] = new_id
    except KeyboardInterrupt:
        print("\nMonitoring stopped.")

if __name__ == "__main__":
    main()
# aws_ec2
aws manage ec2

Determine the instance state using its DNS name (need at least 2 
verifications: TCP and HTTP).
Create an AMI of the stopped EC2 instance and add a descriptive tag 
based on the EC2 name along with the current date.
Terminate stopped EC2 after AMI creation.
Clean up AMIs older than 7 days.
Print all instances in fine-grained output, INCLUDING terminated one, 
with highlighting their current state.

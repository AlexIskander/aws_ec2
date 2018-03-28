#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import re
import urllib2
import datetime
import boto3
from botocore.exceptions import ClientError
from socket import socket, gethostbyname, AF_INET, SOCK_STREAM, gaierror


listId = ['i-id1',
          'i-id2',
          'i-id3']

listUrl = ['http://a.devoups.tk',
           'http://b.devoups.tk',
           'http://c.devoups.tk']


ec2 = boto3.client('ec2')
now = datetime.datetime.now()


class Color():
    """ We make color inference, for beauty. """
    CYAN = '\033[36m'
    PURPLE = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDCOLOR = '\033[0m'



def createTag(tag, image_id):
    ec2 = boto3.resource("ec2")
    image = ec2.Image(image_id)
    tag = image.create_tags(Tags=[{'Key': 'Name', 'Value': tag}])
    print(tag)


def createImage(id, tag):
    today = now.strftime("%Y-%m-%d-%H:%M")
    image = ec2.create_image(Description=today, InstanceId=id, Name=tag)
    createTag(tag + today, image['ImageId'])


def terminatedInstance(ids):
    response = ec2.terminate_instances(InstanceIds=ids)
    print(response)


def cheakStatusInstances():
    response = ec2.describe_instances(Filters=[{'Name': 'key-name', 'Values': ['key_name']}])

    ids = []

    for instance in response['Reservations']:
        if instance['Instances'][0]['State']['Name'] == "stopped":
            id = instance['Instances'][0]['InstanceId']
            response_tag = ec2.describe_tags(Filters=[{'Name': 'resource-id', 'Values': [id]}])
            tag = response_tag['Tags'][0]['Value']
            createImage(id, tag)
            ids.append(id)
    return ids


def cheakPort():
  port = 80
  for target in targets:
    try:
        targetIP = gethostbyname(re.sub(r"http[s]?://", "", target))
    except gaierror as error:
        print("%s %s in domain %s %s" % (Color.RED, error, target, Color.ENDCOLOR))
    else:
        s = socket(AF_INET, SOCK_STREAM)
        result = s.connect_ex((targetIP, port)) 
        if not (result) :
            print 'Port %d is open on %s' % (port, target)
        s.close()



def determineInstance():
    
    for url in listUrl:
        try:
            request = urllib2.urlopen(url, timeout=1)
        except urllib2.HTTPError as error:
            print(error)
            print("%s url %s available but site not working good, maybe you don't have index file %s" % (Color.YELLOW, url, Color.ENDCOLOR))
        except urllib2.URLError as error:
            print(error)
        else:
            print('%s  avilable' % url)


def instanceStatus():
    ec2 = boto3.resource("ec2")
    instances = ec2.instances.filter()
    for instance in instances:
        if instance.state == "stoped":
            print('%s %s %s %s %s' % (Color.RED, instance.id, instance.instance_type, instance.state, Color.ENDCOLOR))
        else:
           print('%s %s %s %s %s' % (Color.GREEN, instance.id, instance.instance_type, instance.state, Color.ENDCOLOR))



def deregisterImage(image_id):
    if image_id:
        for id in image_id:
            response = ec2.deregister_image(ImageId=id)
            print(response)


def describeIimages():
    response = ec2.describe_images(Owners=['owner'])
    image_id = []
    for image in response['Images']:
        createDate = image['CreationDate'].split('T')[0]
        if createDate < '{:%Y-%m-}{}'.format(now, now.day - 7):
            image_id.append(image['ImageId'])
    return image_id


if __name__ == "__main__":
    cheakPort()
    determineInstance()
    ids =  cheakStatusInstances()
    terminatedInstance(ids)
    image_id = describeIimages()
    deregisterImage(image_id)
    instanceStatus()

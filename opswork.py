#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function

import re
import urllib2
import datetime
from socket import socket, gethostbyname, AF_INET, SOCK_STREAM, gaierror
import boto3


LIST_ID = ['i-id1',
           'i-id2',
           'i-id3']

LIST_URL = ['http://a.devoups.tk',
            'http://b.devoups.tk',
            'http://c.devoups.tk']


EC2 = boto3.client('EC2')
NOW = datetime.datetime.now()


class Color():
    """ We make color inference, for beauty. """
    CYAN = '\033[36m'
    PURPLE = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDCOLOR = '\033[0m'



def create_tag(tag, image_id):
    """ Create tag"""
    EC2 = boto3.resource("EC2")
    image = EC2.Image(image_id)
    tag = image.create_tags(Tags=[{'Key': 'Name', 'Value': tag}])
    print(tag)


def create_image(id, tag):
    """Create image"""
    today = NOW.strftime("%Y-%m-%d-%H:%M")
    image = EC2.create_image(Description=today, InstanceId=id, Name=tag)
    create_tag(tag + today, image['ImageId'])


def terminated_instance(ids):
    """ Create instance """
    response = EC2.terminate_instances(InstanceIds=ids)
    print(response)


def cheak_status_instances():
    """Check  status instances if stopped run function create_image"""
    response = EC2.describe_instances(Filters=[{'Name': 'key-name', 'Values': ['key_name']}])

    ids = []

    for instance in response['Reservations']:
        if instance['Instances'][0]['State']['Name'] == "stopped":
            id = instance['Instances'][0]['InstanceId']
            response_tag = EC2.describe_tags(Filters=[{'Name': 'resource-id', 'Values': [id]}])
            tag = response_tag['Tags'][0]['Value']
            create_image(id, tag)
            ids.append(id)
    return ids


def cheak_port(targets):
    """Check port for availability"""
    port = 80
    for target in targets:
        try:
            target_ip = gethostbyname(re.sub(r"http[s]?://", "", target))
        except gaierror as error:
            print("%s %s in domain %s %s" % (Color.RED, error, target, Color.ENDCOLOR))
        else:
            s = socket(AF_INET, SOCK_STREAM)
            result = s.connect_ex((target_ip, port)) 
            if not (result):
                print( 'Port %d is open on %s' % (port, target))
            s.close()



def determine_instance():
    """Check url for availability """
    for url in LIST_URL:
        try:
            request = urllib2.urlopen(url, timeout=1)
        except urllib2.HTTPError as error:
            print(error)
            print("%s url %s available but site not working good, maybe you don't have index file %s" % (Color.YELLOW, url, Color.ENDCOLOR))
        except urllib2.URLError as error:
            print(error)
        else:
            print('%s  avilable' % url)


def instance_status():
    """ Check status instances """
    EC2 = boto3.resource("EC2")
    instances = EC2.instances.filter()
    for instance in instances:
        if instance.state == "stoped":
            print('%s %s %s %s %s' % (Color.RED, instance.id, instance.instance_type, instance.state, Color.ENDCOLOR))
        else:
           print('%s %s %s %s %s' % (Color.GREEN, instance.id, instance.instance_type, instance.state, Color.ENDCOLOR))



def deregister_image(image_id):
    """ clear images"""
    if image_id:
        for id in image_id:
            response = EC2.deregister_image(ImageId=id)
            print(response)


def describe_iimages():
    """find images older then 7 days"""
    response = EC2.describe_images(Owners=['owner'])
    image_id = []
    for image in response['Images']:
        create_date = image['CreationDate'].split('T')[0]
        if create_date < '{:%Y-%m-}{}'.format(NOW, NOW.day - 7):
            image_id.append(image['ImageId'])
    return image_id


if __name__ == "__main__":
    cheak_port(LIST_URL)
    determine_instance()
    ids = cheak_status_instances()
    terminated_instance(ids)
    image_id = describe_iimages()
    deregister_image(image_id)
    instanceStatus()

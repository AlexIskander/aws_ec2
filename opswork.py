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


class Color(object):
    """ делаем цветной вывод, для красоты. """

    def __init__(self, msg, color):
        self._msg = msg
        self._color = color

    colors = {
        "cyan": '\033[36m',
        "purple": '\033[95m',
        "blue": '\033[94m',
        "green": '\033[92m',
        "yellow": '\033[93m',
        "red": '\033[91m',
        "endcolor": '\033[0m'
    }

    def msg(self):
        """msg"""
        return self._msg

    def color(self):
        """color"""
        return self.colors[self._color]

    def __repr__(self):
        return "%s %s %s" % (
            self.color(), self.msg(), self.colors["endcolor"])


def create_tag(tag, image_id):
    """ Create tag"""
    EC2 = boto3.resource("EC2")
    image = EC2.Image(image_id)
    tag = image.create_tags(Tags=[{'Key': 'Name', 'Value': tag}])
    print(tag)


def create_image(instance_id, tag):
    """Create image"""
    today = NOW.strftime("%Y-%m-%d-%H:%M")
    image = EC2.create_image(Description=today, InstanceId=instance_id, Name=tag)
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
            instance_id = instance['Instances'][0]['InstanceId']
            response_tag = EC2.describe_tags(Filters=[{'Name': 'resource-id',
                                                       'Values': [instance_id]}])
            tag = response_tag['Tags'][0]['Value']
            create_image(instance_id, tag)
            ids.append(instance_id)
    return ids


def cheak_port(targets):
    """Check port for availability"""
    port = 80
    for target in targets:
        try:
            target_ip = gethostbyname(re.sub(r"http[s]?://", "", target))
        except gaierror as err:
            msg = "{0} in domain {1}".format(err, target)
            print(Color(msg, "red"))
        else:
            s = socket(AF_INET, SOCK_STREAM)
            result = s.connect_ex((target_ip, port))
            if not result:
                print("Port {0} is open on {1}".format(port, target))
            s.close()


def determine_instance():
    """Check url for availability """
    for url in LIST_URL:
        try:
            request = urllib2.urlopen(url, timeout=1)
        except urllib2.HTTPError as err:
            print(err)
            msg = "url {0} available but site not working good, maybe you don't have index file"
            print(Color(msg.format(url), "yellow"))
        except urllib2.URLError as error:
            print(Color(error, "red"))
        else:

            print(Color("{0} avilable".format(url), "green"))

def instance_status():
    """ Check status instances """
    EC2 = boto3.resource("EC2")
    instances = EC2.instances.filter()
    for instance in instances:
        msg = "{0} {1} {2}".format(instance.id, instance.instance_type, instance.state)
        if instance.state == "stoped":
            print(Color(msg, "red"))
        else:
           print(Color(msg, "green"))


def deregister_image(image_id):
    """ clear images"""
    if image_id:
        for img_id in image_id:
            response = EC2.deregister_image(ImageId=img_id)
            print(response)


def describe_images():
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
    IDS = cheak_status_instances()
    terminated_instance(IDS)
    IMAGE_ID = describe_images()
    deregister_image(IMAGE_ID)
    instance_status()

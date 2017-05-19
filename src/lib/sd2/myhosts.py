#!/usr/bin/env python
#############################################################################
# Copyright (c) 2017 SiteWare Corp. All right reserved
#############################################################################
import sys

initialized = False
config_dct = {}
imagesdict = {}
containersdict = {}
hostsdict = {}
hosts = None

def init(a_config_dct = None):
    global config_dct, containersdict,hostsdict, imagesdict, initialized, hosts
    from . import config
    if a_config_dct is None:
        config_dct = config.read_config()
    else:
        config_dct = a_config_dct

    for image in config_dct.get('images', []):
        imagesdict[image['name']] = image

    hosts = config_dct.get('hosts', [])
    hostsdict = {x['name']: x for x in hosts}

    for host in hosts:
        try:
            base = host['base']
        except KeyError:
            sys.stderr.write(
                "ERROR: base address for {} was not found.\n".format(
                    host['name']))
            sys.exit(1)
        host['local-ip'] = "172.172.{}.100".format(base)
        containers = []
        host_name = host['name']
        for cont, imagename in enumerate(host.get('containers', [])):
            cont = {
                'ip': "172.172.{}.{}".format(base, 101 + cont),
                'image': imagesdict[imagename] if isinstance(imagename,
                                                             basestring) else
                imagesdict[imagename['imagename']],
                'image_name': imagename if isinstance(imagename,
                                                      basestring) else
                imagename['imagename'],
                'name': "{}-{}".format(host_name, (
                cont if isinstance(imagename, basestring) else imagename[
                    'name'])),
            }
            containers.append(cont)
            containersdict[cont['name']] = cont
        host['containers'] = containers
    initialized = True


def get_container_extra_flags(containerName):
    if not initialized:
        init()
    cont = containersdict[containerName]
    return cont['image'].get('extra_flags', '')

def get_container_command(containerName):
    if not initialized:
        init()
    cont = containersdict[containerName]
    return cont['image'].get('command', '')

def get_container_docker_image(containerName):
    if not initialized:
        init()
    cont = containersdict[containerName]
    return cont['image']['docker_name']

def get_container_ports(containerName):
    if not initialized:
        init()
    cont = containersdict[containerName]
    return cont['image'].get('ports', [])

def get_container_ip(containerName):
    if not initialized:
        init()
    cont = containersdict[containerName]
    return cont['ip']

def get_container_names(hostname):
    if not initialized:
        init()
    host = hostsdict[hostname]
    return [x['name'] for x in host['containers']]

def get_hosts():
    if not initialized:
        init()
    return hosts
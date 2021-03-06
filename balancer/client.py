# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2010-2011 OpenStack, LLC
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

"""
Client classes for callers of a Glance system
"""

import errno
import httplib
import json
import logging
import os
import socket
import sys

import balancer.api.v1
from balancer.common import client as base_client
from balancer.common import exception
from balancer.common import utils

logger = logging.getLogger(__name__)
SUPPORTED_PARAMS = balancer.api.v1.SUPPORTED_PARAMS
SUPPORTED_FILTERS = balancer.api.v1.SUPPORTED_FILTERS


class V1Client(base_client.BaseClient):

    """Main client class for accessing Balancer resources"""

    DEFAULT_PORT = 8181
    DEFAULT_DOC_ROOT = ""

    def get_loadbalancers(self, **kwargs):
        res = self.do_request("GET", "loadbalancers")
        data = json.loads(res.read())['loadbalancers']
        return data

    def get_algorithms(self, **kwargs):
        algorithms = ["RoundRobin", "LeastConnections", "LeastLoaded",
"LeastBandwidth"]
        return algorithms

    def get_probe_types(self, **kwargs):
        probes = ["CONNECT", "HTTP", "HTTPS", "ICMP"]
        return probes

    def get_loadbalancer_details(self, lb_id):
        res = self.do_request("GET", "loadbalancers/%s/detail" % lb_id)
        data = json.loads(res.read())
        return data

    def get_loadbalancer(self, lb_id):
        res = self.do_request("GET", "loadbalancers/%s" % lb_id)
        data = json.loads(res.read())['loadbalancer']
        return data

    def create_lb(self, body):
        post_body = json.dumps(body)
        data = self.do_request("POST", "loadbalancers", post_body,
                              {'content-type': 'application/json'})
        return data

    def get_nodes_for_lb(self, lb_id):
        res = self.do_request("GET", "loadbalancers/%s/nodes" % lb_id)
        data = json.loads(res.read())['nodes']
        return data

    def get_balancers_with_vm(self, vm_id):
        res = self.do_request("GET", "loadbalancers/find_for_VM/%s" % vm_id)
        data = json.loads(res.read())['loadbalancers']
        return data

    def activate_node(self, node_id, lb_id):
        res = self.do_request("PUT",
                "/loadbalancers/%s/nodes/%s/inservice" % (lb_id, node_id))
        return res

    def suspend_node(self, node_id, lb_id):
        res = self.do_request("PUT",
                "/loadbalancers/%s/nodes/%s/outofservice" % (lb_id, node_id))
        return res

    def activate_vmnode_in_lbs(self, vmnode_id, lb_id_list):
        for lb_id in lb_id_list:
            nodes = self.get_nodes_for_lb(lb_id)

            for node in nodes:
                if node['vm_id'] == vmnode_id:
                    self.activate_node(node['id'], lb_id)

    def suspend_vmnode_in_lbs(self, vmnode_id, lb_id_list):
        for lb_id in lb_id_list:
            nodes = self.get_nodes_for_lb(lb_id)

            for node in nodes:
                if node['vm_id'] == vmnode_id:
                    self.suspend_node(node['id'], lb_id)

    def activate_vmnode(self, vmnode_id):
        return balancerclient(request).activate_node(node_id)

    def suspend_vmnode(self, vmnode_id):
        return balancerclient(request).suspend_node(node_id)

    def remove_vmnode_from_lbs(self, vmnode_id, lb_id_list):
        return balancerclient(request).remove_node_from_lbs(node_id,
                                                            lb_id_list)

    def get_devices(self):
        res = self.do_request("GET", "devices")
        data = json.loads(res.read())['devices']
        return data

    def add_vmnode_to_lb(self, node, lb_id):
        body = json.dumps(node)
        res = self.do_request("PUT", "loadbalancers/%s/nodes" % lb_id, body,
                            {'content-type': 'application/json'})
        return res

    def delete_lb(self, lb_id):
        res = self.do_request("DELETE", "loadbalancers/%s" % lb_id)
        return res

    def get_sticky_list(self):
        list = ["http-cookie", "ip-netmask", "http-header"]
        return list

    def add_probe_to_lb(self, probe, lb_id):
        body = json.dumps(probe)
        res = self.do_request("PUT",
                            "loadbalancers/%s/healthMonitoring" % lb_id, body,
                            {'content-type': 'application/json'})
        return True

    def add_sticky_to_lb(self, sticky, lb_id):
        body = json.dumps(sticky)
        res = self.do_request("PUT",
                        "loadbalancers/%s/sessionPersistence" % lb_id, body,
                        {'content-type': 'application/json'})
        return True

    def add_image(self, image_meta=None, image_data=None, features=None):
        """
        Tells Glance about an image's metadata as well
        as optionally the image_data itself

        :param image_meta: Optional Mapping of information about the
                           image
        :param image_data: Optional string of raw image data
                           or file-like object that can be
                           used to read the image data
        :param features:   Optional map of features

        :retval The newly-stored image's metadata.
        """
        headers = utils.image_meta_to_http_headers(image_meta or {})

        if image_data:
            body = image_data
            headers['content-type'] = 'application/octet-stream'
            image_size = self._get_image_size(image_data)
            if image_size:
                headers['x-image-meta-size'] = image_size
                headers['content-length'] = image_size
        else:
            body = None

        utils.add_features_to_http_headers(features, headers)

        res = self.do_request("POST", "/images", body, headers)
        data = json.loads(res.read())
        return data['image']

    def update_image(self, image_id, image_meta=None, image_data=None,
                     features=None):
        """
        Updates Glance's information about an image

        :param image_id:   Required image ID
        :param image_meta: Optional Mapping of information about the
                           image
        :param image_data: Optional string of raw image data
                           or file-like object that can be
                           used to read the image data
        :param features:   Optional map of features
        """
        if image_meta is None:
            image_meta = {}

        headers = utils.image_meta_to_http_headers(image_meta)

        if image_data:
            body = image_data
            headers['content-type'] = 'application/octet-stream'
            image_size = self._get_image_size(image_data)
            if image_size:
                headers['x-image-meta-size'] = image_size
                headers['content-length'] = image_size
        else:
            body = None

        utils.add_features_to_http_headers(features, headers)

        res = self.do_request("PUT", "/images/%s" % image_id, body, headers)
        data = json.loads(res.read())
        return data['image']

    def delete_image(self, image_id):
        """
        Deletes Glance's information about an image
        """
        self.do_request("DELETE", "/images/%s" % image_id)
        return True

    def get_cached_images(self, **kwargs):
        """
        Returns a list of images stored in the image cache.
        """
        res = self.do_request("GET", "/cached_images")
        data = json.loads(res.read())['cached_images']
        return data

    def get_queued_images(self, **kwargs):
        """
        Returns a list of images queued for caching
        """
        res = self.do_request("GET", "/queued_images")
        data = json.loads(res.read())['queued_images']
        return data

    def delete_cached_image(self, image_id):
        """
        Delete a specified image from the cache
        """
        self.do_request("DELETE", "/cached_images/%s" % image_id)
        return True

    def delete_all_cached_images(self):
        """
        Delete all cached images
        """
        res = self.do_request("DELETE", "/cached_images")
        data = json.loads(res.read())
        num_deleted = data['num_deleted']
        return num_deleted

    def queue_image_for_caching(self, image_id):
        """
        Queue an image for prefetching into cache
        """
        self.do_request("PUT", "/queued_images/%s" % image_id)
        return True

    def delete_queued_image(self, image_id):
        """
        Delete a specified image from the cache queue
        """
        self.do_request("DELETE", "/queued_images/%s" % image_id)
        return True

    def delete_all_queued_images(self):
        """
        Delete all queued images
        """
        res = self.do_request("DELETE", "/queued_images")
        data = json.loads(res.read())
        num_deleted = data['num_deleted']
        return num_deleted

    def get_image_members(self, image_id):
        """Returns a mapping of image memberships from Registry"""
        res = self.do_request("GET", "/images/%s/members" % image_id)
        data = json.loads(res.read())['members']
        return data

    def get_member_images(self, member_id):
        """Returns a mapping of image memberships from Registry"""
        res = self.do_request("GET", "/shared-images/%s" % member_id)
        data = json.loads(res.read())['shared_images']
        return data

    def _validate_assocs(self, assocs):
        """
        Validates membership associations and returns an appropriate
        list of associations to send to the server.
        """
        validated = []
        for assoc in assocs:
            assoc_data = dict(member_id=assoc['member_id'])
            if 'can_share' in assoc:
                assoc_data['can_share'] = bool(assoc['can_share'])
            validated.append(assoc_data)
        return validated

    def replace_members(self, image_id, *assocs):
        """
        Replaces the membership associations for a given image_id.
        Each subsequent argument is a dictionary mapping containing a
        'member_id' that should have access to the image_id.  A
        'can_share' boolean can also be specified to allow the member
        to further share the image.  An example invocation allowing
        'rackspace' to access image 1 and 'google' to access image 1
        with permission to share::

            c = glance.client.Client(...)
            c.update_members(1, {'member_id': 'rackspace'},
                             {'member_id': 'google', 'can_share': True})
        """
        # Understand the associations
        body = json.dumps(self._validate_assocs(assocs))
        self.do_request("PUT", "/images/%s/members" % image_id, body,
                        {'content-type': 'application/json'})
        return True

    def add_member(self, image_id, member_id, can_share=None):
        """
        Adds a membership association between image_id and member_id.
        If can_share is not specified and the association already
        exists, no change is made; if the association does not already
        exist, one is created with can_share defaulting to False.
        When can_share is specified, the association is created if it
        doesn't already exist, and the can_share attribute is set
        accordingly.  Example invocations allowing 'rackspace' to
        access image 1 and 'google' to access image 1 with permission
        to share::

            c = glance.client.Client(...)
            c.add_member(1, 'rackspace')
            c.add_member(1, 'google', True)
        """
        body = None
        headers = {}
        # Generate the body if appropriate
        if can_share is not None:
            body = json.dumps(dict(member=dict(can_share=bool(can_share))))
            headers['content-type'] = 'application/json'

        self.do_request("PUT", "/images/%s/members/%s" %
                        (image_id, member_id), body, headers)
        return True

    def delete_member(self, image_id, member_id):
        """
        Deletes the membership assocation.  If the
        association does not exist, no action is taken; otherwise, the
        indicated association is deleted.  An example invocation
        removing the accesses of 'rackspace' to image 1 and 'google'
        to image 2::

            c = glance.client.Client(...)
            c.delete_member(1, 'rackspace')
            c.delete_member(2, 'google')
        """
        self.do_request("DELETE", "/images/%s/members/%s" %
                        (image_id, member_id))
        return True


class ProgressIteratorWrapper(object):

    def __init__(self, wrapped, transfer_info):
        self.wrapped = wrapped
        self.transfer_info = transfer_info
        self.prev_len = 0L

    def __iter__(self):
        for chunk in self.wrapped:
            if self.prev_len:
                self.transfer_info['so_far'] += self.prev_len
            self.prev_len = len(chunk)
            yield chunk
            # report final chunk
        self.transfer_info['so_far'] += self.prev_len


class ProgressClient(V1Client):

    """
    Specialized class that adds progress bar output/interaction into the
    TTY of the calling client
    """
    def image_iterator(self, connection, headers, body):
        wrapped = super(ProgressClient, self).image_iterator(connection,
                                                                headers,
                                                                body)
        try:
            # spawn the animation thread if the connection is good
            connection.connect()
            return ProgressIteratorWrapper(wrapped,
                                        self.start_animation(headers))
        except (httplib.HTTPResponse, socket.error):
            # the connection is out, just "pass"
            # and let the "glance add" fail with [Errno 111] Connection refused
            pass

    def start_animation(self, headers):
        transfer_info = {
            'so_far': 0L,
            'size': headers.get('x-image-meta-size', 0L)
        }
        pg = animation.UploadProgressStatus(transfer_info)
        if transfer_info['size'] == 0L:
            sys.stdout.write("The progressbar doesn't show-up because "
                            "the headers[x-meta-size] is zero or missing\n")
        sys.stdout.write("Uploading image '%s'\n" %
                        headers.get('x-image-meta-name', ''))
        pg.start()
        return transfer_info

Client = V1Client


def get_client(host, port=None, username=None,
               password=None, tenant=None,
               auth_url=None, auth_strategy=None,
               auth_token=None, region=None,
               is_silent_upload=True, insecure=False):
    """
    Returns a new client Glance client object based on common kwargs.
    If an option isn't specified falls back to common environment variable
    defaults.
    """

    if auth_url or os.getenv('OS_AUTH_URL'):
        force_strategy = 'keystone'
    else:
        force_strategy = None

    creds = dict(username=username or
                         os.getenv('OS_AUTH_USER', os.getenv('OS_USERNAME')),
                 password=password or
                         os.getenv('OS_AUTH_KEY', os.getenv('OS_PASSWORD')),
                 tenant=tenant or
                         os.getenv('OS_AUTH_TENANT',
                                 os.getenv('OS_TENANT_NAME')),
                 auth_url=auth_url or os.getenv('OS_AUTH_URL'),
                 strategy=force_strategy or auth_strategy or
                          os.getenv('OS_AUTH_STRATEGY', 'noauth'),
                 region=region or os.getenv('OS_REGION_NAME'),
    )

    if creds['strategy'] == 'keystone' and not creds['auth_url']:
        msg = ("--os_auth_url option or OS_AUTH_URL environment variable "
               "required when keystone authentication strategy is enabled\n")
        raise exception.ClientConfigurationError(msg)

    use_ssl = (creds['auth_url'] is not None and
        creds['auth_url'].find('https') != -1)

    client = (ProgressClient if not is_silent_upload else Client)

    return client(host=host,
                port=port,
                use_ssl=use_ssl,
                auth_tok=auth_token or
                os.getenv('OS_TOKEN'),
                creds=creds,
                insecure=insecure)

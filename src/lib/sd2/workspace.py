#!/usr/bin/env python
#############################################################################
# Copyright (c) 2017 SiteWare Corp. All right reserved
#############################################################################

from . import myhosts

class Workspace(object):
    def __init__(self, node):
        self._node = node

    def get_targets(self):
        hosts = self._node.get('targets', [])
        rr = [x for x in hosts if myhosts.is_enabled(x['name'])]
        rr.extend([x for x in hosts if myhosts.exists_container(x['name'])])
        for host in hosts:
            assert 'name' in host
        return rr

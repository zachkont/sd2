#!/usr/bin/env python
#############################################################################
# Copyright (c) 2017 SiteWare Corp. All right reserved
#############################################################################
import logging
import subprocess
import fcntl
import os
import sys

ON_POSIX = 'posix' in sys.builtin_module_names

from .util import convert_rsync_to_regex
from .util import kill_subprocess_process
from .workspace import Workspace
from .connections import Connections

g_args = None
g_workspaces = None

def workspace_instance_sync(wi):
    for host in Workspace(wi).get_targets():
        if g_args.hosts and not host['name'] in g_args.hosts:
            continue
        host['needsync'] = 1

def workspace_instance_has_path(wi, apath):
    import re
    full_path = os.path.join(wi['source_root'], wi.get('source', ''))
    if not full_path.endswith(os.path.sep):
        full_path += os.path.sep
    if apath.startswith(full_path):
        logging.debug("%s might belong to %s", apath, wi['name'])
        for paths in wi.get('paths'):
            if paths.get('include'):
                found = False
                for ipath in paths.get('include'):
                    logging.debug("CNS:INCL:%s (%s) %s", ipath, apath, full_path)
                    ripath = convert_rsync_to_regex(ipath)
                    if (re.match(r'^' + wi['source_root'].rstrip('/') + ripath + r'$', apath)):
                        logging.debug("FOUND:INCL:%s (%s)", ipath, apath)
                        found = True
                        break
                if not found:
                    return False
                if found:
                    return True
            if paths.get('exclude'):
                for epath in paths.get('exclude'):
                    logging.debug("CNS:EXCL:%s (%s)", epath, apath)
                    repath = convert_rsync_to_regex(epath)
                    if (re.match(r'^' + wi['source_root'].rstrip('/') + repath + r'$', apath)):
                            logging.debug("EXCL %s from %s", apath, wi['name'])
                            return False
        return True
    return False

def deal_with_changed_file(wi, fpath):
    if workspace_instance_has_path(wi, fpath):
        logging.debug("FOUND: wsi %s has path %s", wi['name'], fpath)
        if os.path.isfile(fpath):
            for target in Workspace(wi).get_targets():
                if g_args.hosts and not target['name'] in g_args.hosts:
                    continue
                cmd = "scp -p {} {}:{}".format(
                    fpath,
                    target['name'],
                    fpath.replace(os.environ.get('HOME'), '~'))
                if g_args.dryrun:
                    cmd = 'echo ' + cmd
                logging.info(cmd)
                subprocess.Popen(cmd, shell=True)
        else:
            workspace_instance_sync(wi)


# fswatch includes everything in --include if exists. Then checks --exclude
# Order does not matter
# http://emcrisostomo.github.io/fswatch/doc/1.4.3/pdf/fswatch.pdf
class FSWatcher(Connections):
    def __init__(self, args, workspaces):
        global g_args, g_workspaces
        g_args = args
        g_workspaces = workspaces
        logging.debug("FSW:EE")
        host = g_args.hosts
        assert host == '' or isinstance(host, list)
        for wi in g_workspaces:
            cmd = ['fswatch',
                   '--latency', '0.1',
                   '--recursive',
                   # "--exclude='.*\.pyc$'",
                   # "--exclude='.*\.swp$'",
                   # "--exclude='.*\.swpx$'",
                   # "--exclude='\.idea/.*'",
                   # "--exclude='\.git/.*'"
                   ]
            paths_to_watch = []
            if not host or set(host).intersection(
                    [x['name'] for x in Workspace(wi).get_targets()]):
                for paths in wi.get('paths'):
                    if paths.get('include'):
                        for path in paths.get('include'):
                            cmd.append(
                                "--include='{}'".format(convert_rsync_to_regex(path)))
                    elif paths.get('exclude'):
                        for path in paths.get('exclude'):
                            cmd.append(
                                "--exclude='{}'".format(convert_rsync_to_regex(path)))

                paths_to_watch.append(
                    os.path.join(wi['source_root'], wi.get('source', '')))
            for pp in paths_to_watch:
                if not pp.endswith(os.path.sep):
                    pp += '/'
                cmd.append(pp)
            strcmd = " ".join(cmd)
            logging.info("%s %s", wi['name'], strcmd)
            wi['fswatchproc'] = subprocess.Popen(
                strcmd,
                shell=True,
                bufsize=1,  # line buffered
                stdout=subprocess.PIPE,
                # stderr=subprocess.PIPE,
                close_fds=ON_POSIX
            )
            fl = fcntl.fcntl(wi['fswatchproc'].stdout, fcntl.F_GETFL)
            fcntl.fcntl(wi['fswatchproc'].stdout, fcntl.F_SETFL,
                        fl | os.O_NONBLOCK)
        logging.debug("FSW:LL")

    def poll(self):
        for ws in g_workspaces:
            proc = ws['fswatchproc']
            try:
                line = proc.stdout.readline().strip()
            except IOError:
                continue
            logging.debug('CONS %s %s', ws['name'], line)
            deal_with_changed_file(ws, line)

    def shutdown(self):
        for wi in g_workspaces:
            proc = wi['fswatchproc']
            kill_subprocess_process(proc, "FSWATH {}".format(wi['name']))
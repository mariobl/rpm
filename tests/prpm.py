#!/usr/bin/python3

import rpm
import argparse

class transCb:
    fds = {}

    def __call__(self, what, amount, total, key, data):
        if what == rpm.RPMCALLBACK_INST_OPEN_FILE:
            f = open(key, 'rb')
            self.fds[key] = f
            return f.fileno()
        elif what == rpm.RPMCALLBACK_INST_CLOSE_FILE:
            del self.fds[key]

def doprobs(ts):
    for p in ts.problems():
        print(p)

def runts(ts):
    probs = ts.run(transCb(), "")
    if probs:
        doprobs(ts)
        return 1
    return 0

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--install', nargs='+', default=[])
    parser.add_argument('-u', '--upgrade', nargs='+', default=[])
    parser.add_argument('-e', '--erase', nargs='+', default=[])
    parser.add_argument('-r', '--reinstall', nargs='+', default=[])
    parser.add_argument('-R', '--restore', nargs='+', default=[])
    parser.add_argument('--root', default='/', action='store')
    parser.add_argument('-n', '--dry-run', action='store_true')
    parser.add_argument('--nosignature', action='store_true')
    parser.add_argument('--nodeps', action='store_true')
    parser.add_argument('--noorder', action='store_true')
    parser.add_argument('-v', '--verbose', action='store_true')
    args = parser.parse_args()

    ts = rpm.ts(args.root)
    ovflags = ts.setVSFlags(ts.getVSFlags() | rpm.RPMVSF_MASK_NOSIGNATURES)
    for arg in args.install:
        ts.addInstall(arg, arg, 'i')
    for arg in args.upgrade:
        ts.addInstall(arg, arg, 'u')
    for arg in args.reinstall:
        ts.addReinstall(arg, arg)
    for arg in args.restore:
        ts.addRestore(arg, arg)
    for arg in args.erase:
        ts.addErase(arg)
    ts.setVSFlags(ovflags)

    if args.nosignature:
        ts.setVfyLevel(rpm.RPMSIG_DIGEST_TYPE)

    if not args.noorder:
        ts.order()

    if not args.nodeps:
        rc = ts.check()
        if rc:
            doprobs(ts)
            exit(rc)

    oflags = ts.setFlags(rpm.RPMTRANS_FLAG_TEST)
    if args.verbose:
        print("Testing")
    rc = runts(ts)
    ts.setFlags(oflags)

    if rc == 0 and not args.dry_run:
        if args.verbose:
            print("Committing")
        rc = runts(ts)

    exit(rc)

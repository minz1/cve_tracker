#!/usr/bin/python3

import json
import utils
import os

from classes import *
from utils import *

from flask import Flask
from flask_mongoengine import MongoEngine

app = Flask(__name__)
app.config.from_pyfile('app.cfg')
db = MongoEngine(app)

mitrelink='https://cve.mitre.org/cgi-bin/cvename.cgi?name='

# Add / update CVEs
f = open('cves.txt')
while True:
    x = f.readline().rstrip()
    if not x: break
    check = CVE.objects(cve_name=x).first()
    if not check:
        CVE(cve_name=x).save()
        Links(cve_id=CVE.objects.get(cve_name=x)['id'], link=mitrelink+x).save()
    else:
        print("Skipped '" + x + "' because it was already added!")

# Add possible statuses
utils.updateStatusDescriptions()

# Add / update kernels
utils.getKernelTableFromGithub(app)

# Add patch statuses for each kernel
f = open('patches.txt')
while True:
    x = f.readline().rstrip()
    if not x: break
    if x[0] != "#":
        k = x.split('|')[0]
        j = json.loads(x.split('|')[1])
        if "lge-gproj" in k or "lge-mako" in k or "lge-p880" in k:
            k = k.replace("lge-", "lge-kernel-")
        else:
            k = "android_kernel_" + k
        try:
            kernel_id = Kernel.objects.get(repo_name=k).id
            for c in j:
                try:
                    cve_id = CVE.objects.get(cve_name=c).id
                    status_id = Status.objects.get(short_id=j[c]).id
                    Patches.objects(cve=cve_id, kernel=kernel_id).update(status=status_id)
                except:
                    print("Couldn't determine id for " + c)
        except:
            print("Couldn't determine id for " + k)

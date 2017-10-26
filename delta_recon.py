#!/usr/bin/python
"""Warning this code is really bad, and it actually breaks things
it was meant to be a delta based recon system for the JNUC 2017 hack-a-thon which I did not have time to finish
due to there only being a few days during the conference to work on this.

credit - Pat Norton - my coworker who helped me on the project
Munki - borrowed ObjC code examples in Python
Mac Admin Slack #python - helpful people

main author - tlark
co author - Pat

Things I did not have time to do:
1 - build the entire XML to PUT to the JSS
2 - build and deploy a launch daemon to watchpath /Applications
3 - actually test this a lot more
4 - build a way to remove apps too

"""
from Foundation import NSMetadataQuery, NSPredicate, NSRunLoop
from Foundation import NSDate
# did not have time to build the XML so commented out etree
#import xml.etree.ElementTree as et
import plistlib
import time
import urllib2
import os
import sys
import subprocess
import base64



# global vars
# we are going to YOLO this and put credentials in a script!
# warning, do not use this or these methods for anything of value or anywhere near a production environment

JSSUSER = 'LOLYOLO'
JSSPASS = 'LOLYOLO'
JSSURL = 'https://hack.myjss.com/JSSResource'
FILE = '/Library/Application Support/JAMF/com.jamf.appstate.plist'
LAUNCHDEEZ = ''''''
XML = ''''''

def get_apps():
    # credit to the Munki project for borrowing code, thanks Munki!
    apps_dict = {}
    query = NSMetadataQuery.alloc().init()
    query.setPredicate_(NSPredicate.predicateWithFormat_("(kMDItemContentType = 'com.apple.application-bundle')"))
    query.setSearchScopes_(['/Applications'])
    query.startQuery()
    start_time = 0
    max_time = 20
    while query.isGathering() and start_time <= max_time:
        start_time += 0.3
        NSRunLoop.currentRunLoop(
        ).runUntilDate_(NSDate.dateWithTimeIntervalSinceNow_(0.3))
    query.stopQuery()
    # check if the app returns a None value for this query, some apps may have embedded Applescripts
    # that will return a None value and will be set to blank
    for app in query.results():
        name = app.valueForAttribute_('kMDItemDisplayName')
        if name:
            version = app.valueForAttribute_('kMDItemVersion') or ''
            apps_dict[name] = version

    return apps_dict


def write_plist(app_dict):
    '''write application data from a dict to a plist file
    with a date stamp'''
    datestamp = int(time.time())
    data = dict(
        apps = dict(app_dict),
        timestamp = datestamp
    )
    plistlib.writePlist(data, FILE)

def diff_apps(current_state):
    '''diff the current app collection with the last known app state'''
    data = plistlib.readPlist(FILE)
    last_state = data['apps']
    print last_state
    current_apps = current_state
    print current_apps
    if last_state != current_apps:
        print 'diff detected'
        diff = { k : current_apps[k] for k in set(current_apps) - set(last_state) }
        print diff
        write_plist(current_apps)
    else:
        print 'no diff found'
        sys.exit(0)
    return diff


def post_diff(diff):
    '''LOL hacks
    poc to update the device record's applications
    warning - this will overwrite the entire record with the last app'''
    xml = '<computer><software><applications><application><name>%s</name><path>%s</path><version>%s</version></application></applications></software></computer>'
    cmd = ['system_profiler', 'SPHardwareDataType', '-xml']
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output = proc.communicate()[0]
    sys_data = plistlib.readPlistFromString(output)
    serial_number = sys_data[-1]['_items'][0]['serial_number']
    print serial_number
    jss_sub_url = str(JSSURL + '/computers/serialnumber/' + '%s') % serial_number
    print jss_sub_url
    request = urllib2.Request(jss_sub_url)
    request.add_header('Authorization', 'Basic ' + base64.b64encode(JSSUSER + ':' + JSSPASS))
    for k, v in diff.items():
        name = k
        version = v
        path = '/Applications/' + '%s.app' % k
        put = xml % (name, path, version)
        print put
        request.add_header('Content-Type', 'text/xml')
        request.get_method = lambda: 'PUT'
        response = urllib2.urlopen(request, put)



def run():
    '''Run the Jewels!'''
    apps = get_apps()
    if not os.path.isfile(FILE):
        write_plist(apps)
    diff = diff_apps(apps)
    post_diff(diff)

run()

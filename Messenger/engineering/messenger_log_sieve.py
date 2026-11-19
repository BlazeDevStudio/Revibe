#!/usr/bin/env python3
"""Redacted Messenger-only Android logcat error counter.

Designed for manual, authorized KitKat testing. Keeps logcat in memory and
outputs only error categories/counts, never chat contents or token strings.
"""
import argparse
from collections import Counter
import json
import re
import shutil
import subprocess
from pathlib import Path

# Android -v threadtime: MM-DD HH:MM:SS.mmm PID TID P TAG: detail
THREADTIME=re.compile(r'^\d\d-\d\d\s+\d\d:\d\d:\d\d\.\d+\s+(\d+)\s+\d+\s+[VDIWEF]\s+')
APP_PROC=re.compile(r'Process:\s*com\.facebook\.orca(?:\:[\w.]+)?,\s*PID:\s*(\d+)',re.I)
APP_START=re.compile(r'\bStart proc\s+(\d+):com\.facebook\.orca(?:\:[\w.]+)?\b',re.I)
ERR_CLASSES={
  'java_crash':re.compile(r'FATAL EXCEPTION',re.I),
  'android_class_missing':re.compile(r'NoClassDefFoundError|ClassNotFoundException',re.I),
  'android_method_missing':re.compile(r'NoSuchMethodError',re.I),
  'dex_verify_failure':re.compile(r'VerifyError',re.I),
  'native_library_failure':re.compile(r'UnsatisfiedLinkError|dlopen failed',re.I),
  'tls_certificate_failure':re.compile(r'SSLHandshakeException|CertPathValidatorException|CERTIFICATE_VERIFY_FAILED',re.I),
  'network_error':re.compile(r'UnknownHostException|ConnectException|SocketTimeoutException',re.I),
  'security_exception':re.compile(r'SecurityException',re.I),
}


def summarize(raw):
    pids=set(APP_PROC.findall(raw))|set(APP_START.findall(raw))
    counter=Counter()
    matched=0
    for line in raw.splitlines():
        match=THREADTIME.match(line)
        if not match or match.group(1) not in pids:
            continue
        matched+=1
        for label, regex in ERR_CLASSES.items():
            if regex.search(line):
                counter[label]+=1
    return {'scope':'Messenger-identified process IDs only',
        'identified_messenger_pids':len(pids),'app_pid_log_lines_examined':matched,
        'app_pid_error_counts':dict(sorted(counter.items())),
        'result_interpretation':('No Messenger process PID identified: no attribution possible.' if not pids
                else 'Matched categories indicate errors in Messenger process; no login or messaging functionality is established.'),
        'privacy':'No raw log entries, personal messages, IDs, credentials, or tokens emitted.'}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    source=p.add_mutually_exclusive_group(required=True)
    source.add_argument('--adb',action='store_true',help='Read recent logcat via one authorized local ADB device')
    source.add_argument('--log-file',type=Path,help='Locally stored test log; avoid saving real personal logs')
    p.add_argument('--output',type=Path,default=Path('messenger_error_categories.json'))
    a=p.parse_args()
    if a.adb:
        if not shutil.which('adb'):p.error('adb not available')
        devices=subprocess.run(['adb','devices'],capture_output=True,text=True,timeout=12,check=False)
        ids=[x.split()[0] for x in devices.stdout.splitlines() if x.endswith('\tdevice')]
        if len(ids)!=1:p.error('Requires exactly one authorized ADB device')
        p1=subprocess.run(['adb','logcat','-d','-v','threadtime','-t','10000'],capture_output=True,text=True,timeout=45,check=False)
        if p1.returncode:p.error('adb logcat failed')
        raw=p1.stdout
    else:
        raw=a.log_file.read_text(encoding='utf-8',errors='replace')
    s=summarize(raw)
    a.output.write_text(json.dumps(s,indent=2)+'\n',encoding='utf-8')
    print('Saved redacted counters to',a.output)

if __name__=='__main__':main()

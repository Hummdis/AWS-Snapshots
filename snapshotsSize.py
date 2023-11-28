#!/usr/bin/env python3.9

import boto3
import json
import pandas as pd
from pandas import json_normalize

ebs = boto3.client('ebs', region_name='us-east-2')
ec2 = boto3.client('ec2', region_name='us-east-2')

# get sorted list of snapshots
snapshots = ec2.describe_snapshots(OwnerIds=['self'])
df = pd.DataFrame.from_dict(snapshots['Snapshots'])
df.sort_values(by=['OwnerId', "VolumeId", "StartTime", "StorageTier"], inplace = True)

# per volumeid lineage, get for each one changed blocks
i = 0
l = len(df.index)
first = True
# EBS default block size reportd to the OS is a 512-byte block size.
# https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/volume_constraints.html
blockSize = 512

# Prevent unbound vars.
v_prev = ""
sid_prev = ""

for index, row in df.iterrows():
    if i == l:
        break
    if row['StorageTier'] != "standard":
        continue
    date = str(row['StartTime']).split('.',1)[0].split(' ')[0]
    time = str(row['StartTime']).split('.',1)[0].split(' ')[1]
    if first:
        v_prev = row['VolumeId']
        sid_prev = row['SnapshotId']
        # print the results, but size is in bytes.
        print(date + ',' + time + ',' + v_prev + "," + 'snap-00000000000000000' + "," + sid_prev + "," + str(row['VolumeSize'] * 1024 * 1024 * 1024))
        first = False
        i = i + 1
        continue
    v = row['VolumeId']
    sid = row['SnapshotId']
    if v == v_prev:
        # This section from https://github.com/akirsman/Snapshots/issues/2
        changed = 0
        token = None
        while True:
            if token:
                page = ebs.list_changed_blocks(FirstSnapshotId = sid_prev,SecondSnapshotId = sid, NextToken = token, MaxResults = 10000)
            else:
                page = ebs.list_changed_blocks(FirstSnapshotId = sid_prev,SecondSnapshotId = sid, MaxResults = 10000)
            
            changed += len(page['ChangedBlocks'])
            if 'NextToken' not in page:
                break
            token = page['NextToken']
            if token is None:
                break
        print(date + ',' + time + ',' + v + "," + sid_prev + "," + sid + "," + str(changed * blockSize))

    v_prev = v
    sid_prev = sid
    i = i + 1

# AWS Snapshots

This Python script was forked from [akirsman](https://github.com/akirsman/Snapshots "Source"), but since people have reported issues and problems with no reply/response I decided to fork the repository and update it.

## Dependancies

You'll need Python 3.9 and there are some depandancies needed to get this to work:

* Boto3
* Pandas

To install the above, use:

```shell
pip3 install boto3 pandas
```

Once done, you should be able to just run the script as needed.

## AWS Region

As of now, you have to hard-code the region in the script, so make sure you update this section with the actual region you need to use:

```python
...
ebs = boto3.client('ebs', region_name='us-east-2')
ec2 = boto3.client('ec2', region_name='us-east-2')
...
```

## Caveats

This script will grab _all_ snapshots that are not in the "archive" storage tier.  The `list_changed_blocks` API from AWS CLI doesn't support querying changed blocks for snapshots in the "archived" storage tier.

# Output Data

The output size is not a size at all, it's the number of changed blocks.  Per AWS, each snapshot block size is 512 KiB (based on a support ticket filed with them).  Therefore, the number returned from `list_changed_blocks` are the number of 512 KiB blocks that have changed on the snapshot.  To get an actual KiB value, take the number of changed blocks and multiply it by 512.

Once you have this number you can perform the additional math in a spreadsheet since the output will be in CSV format.

# To Do

* Accepts arguments for the region.
* Allow the ability to query specific snapshots.

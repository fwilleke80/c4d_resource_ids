# c4d_resource_ids
A Python script that helps keeping your C4D plugin's resource IDs clean.

## What's is about?
Resource IDs for description-based Cinema 4D plugin UIs need to be unique. In case you have several resoure IDs with the same value, you risk e.g. screwing up the user's animation.

This script helps you keeping resource IDs clean by parsing the .h files where resource IDs are defined, and then doing two things:

1. It lists all IDs that share the same values, potentially causing problems.
2. It suggests IDs that can be safely added to the header file and used. Suggestions are bsaed on "gaps" in the ID range, and on the largest existing ID value in the header file.

The script will never alter any of the header files, it just analyzes.


## Usage
Simply call the script using the Terminal / Shell. It runs on both, Python 2.7 and Python 3.x.

`python c4d_check_resource_ids.py PATH [--minval MINVAL] [--help]`

### Examples
```python c4d_check_resource_ids.py /Applications/MAXON/Cinema \4D \R21/plugins/some_plugin/res/description```
Will process all .h files in the specified folder.

```python c4d_check_resource_ids.py /Applications/MAXON/Cinema \4D \R21/plugins/some_plugin/res/description/xmyshader.h```
Will process the specified header file.

```python c4d_check_resource_ids.py /Applications/MAXON/Cinema \4D \R21/plugins/some_plugin/res/description --minval 10000```
Will process all .h files in the specified folder, but only check ID values equal to or larget than 10000.
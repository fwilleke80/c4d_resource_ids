# c4d\_check\_resource\_ids.py
A Python 3 script that helps keeping your C4D plugin's resource IDs clean.

## What's is about?
Resource IDs for description-based Cinema 4D plugin UIs need to be unique. In case you have several resoure IDs with the same value, you risk e.g. screwing up the user's animation.

This script helps you keeping resource IDs clean by parsing the .h files where resource IDs are defined, and then doing two things:

1. It lists all IDs that share the same values, potentially causing problems.
2. It suggests IDs that can be safely added to the header file and used. Suggestions are bsaed on "gaps" in the ID range, and on the largest existing ID value in the header file.

The script will never alter any of the header files, it just analyzes.


## Usage
Simply call the script using the Terminal / Shell. It runs on both, Python 2.7 and Python 3.x.

`python c4d_check_resource_ids.py [-h] [-u] [-s] [-b] [--minval V] PATH`

### Analysis actions
The script can do several things for you:

`-u, --checkunique`  
Check IDs for uniqueness and report shared ID values.  
If you don't supply any action with the command line arguments, this action will be performed by default.

`-s, --suggest`  
Suggest free IDs that can be safely added to the header.

`-b, --showblocks`  
Show continuous blocks of IDs defined in a header.

### Other options
`-m, --minval`  
Only ID values equal to or larget than this value will be processed. Default is 1000.

### Examples
```python c4d_check_resource_ids.py --checkunique --suggest /Applications/MAXON/Cinema\ 4D\ R21/plugins/some_plugin/res/description```  
Will process all .h files in the specified folder, checking for ID value uniqueness and suggesting possible new ID values

```python c4d_check_resource_ids.py --showblocks /Applications/MAXON/Cinema\ 4D\ R21/plugins/some_plugin/res/description/xmyshader.h```  
Will process the specified header file and show the continuous ID value blocks

```python c4d_check_resource_ids.py /Applications/MAXON/Cinema\ 4D\ R21/plugins/some_plugin/res/description --m 10000```  
Will process all .h files in the specified folder, but only check ID values equal to or larger than 10000.

### Better integration into Bash
You can add a bash function to ~/.bash_profile to make usage easier:

```
# Check resource IDs
check-res-ids() {
        python3 /path/to/script/c4d_check_resource_ids.py "$@"
}
```
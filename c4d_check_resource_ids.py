"""
Title:    C4D Check Resource IDs
Author:   Frank Willeke
Requires: Python 2.7 or Python 3

Description:
    Parse one or multiple .h files from C4D resource folders and check therein
    defined resource IDs:

    - List resource IDs that share the same value (potential source of bugs)

    - Suggest free resource IDs that can safely be used,
      based on gaps in ID range and largest existing ID value
"""

import os
import logging
import argparse
import operator
import itertools


# Script metadata
SCRIPT_TITLE = "C4D Resource ID Checker"
SCRIPT_VERSION = "1.1"
SCRIPT_CREDITS = "2020 by Frank Willeke"

# Script settings
LOGLEVEL = logging.INFO
MIN_SUGGEST_IF_EMPTY = 1000 # Minimum suggested ID value if header does not contain any IDs yet

# Set up logger
logging.basicConfig(format="%(levelname)s: %(message)s", level=LOGLEVEL)
log = logging.getLogger("CheckResourceIDs")


def show_id_blocks(valueNameDict):
    """Show list of all continuous ID blocks in the header
    """
    def find_id_blocks(valueNameDict):
        """Identify continuous blocks of IDs, collect them in a list of blocks
        """
        idValues = sorted(valueNameDict.keys())
        idBlocks = []
        for _, g in itertools.groupby(enumerate(idValues), lambda (i,x):i-x):
            group = map(operator.itemgetter(1), g)
            idBlocks.append(group)
        return idBlocks

    idBlocks = find_id_blocks(valueNameDict)
    log.info("Continuous ID blocks:")
    for block in idBlocks:
        for idIndex, idValue in enumerate(block):
            log.info(("\t" if idIndex > 0 else "") + str(idValue))


def suggest_new_ids(valueNameDict, minVal):
    """Suggest new resource IDs that can safely be added to the header
    """
    def get_suggested_value_list(valueNameDict, minVal):
        """Create list of free ID values that can be suggested
        """
        sortedIdValues = sorted(valueNameDict.keys())

        # First free
        largestValue = 0
        valueGaps = []
        suggestedValues = []

        for idIndex, idValue in enumerate(sortedIdValues):
            largestValue = max(largestValue, idValue)

            # Detect gaps in the Id range
            # if current ID value is larger than previous value + 1
            if idValue > sortedIdValues[idIndex - 1] + 1:
                valueGaps.append(sortedIdValues[idIndex - 1])

        # Suggest values from range gaps
        for gap in valueGaps:
            suggestedValues.append(gap + 1)
        
        # Suggest value after largest value
        suggestedValues.append(max(largestValue + 1, minVal))

        return suggestedValues

    suggestedValues = get_suggested_value_list(valueNameDict, minVal)

    log.info("Suggested free ID values:")
    for suggestionIndex, suggestion in enumerate(suggestedValues):
        if len(valueNameDict) > 0:
            if suggestionIndex == len(suggestedValues) - 1:
                reasonStr = "after largest ID"
            else:
                reasonStr = "based on gap in ID range"
        else:
            reasonStr = "no IDs defined in header"
        log.info("\t" + str(suggestion) + " (" + reasonStr + ")")


def check_unique_resource_ids(valueNameDict):
    """Iterates a list of tuples of (ID_NAME, ID_VALUE)
    """
    nothingFound = True
    for idValue in valueNameDict:
        foundNames = valueNameDict[idValue]
        if len(foundNames) > 1:
            log.info(str(idValue))
            for name in foundNames:
                log.info("\t" + name)
            nothingFound = False
    
    if nothingFound:
        if len(valueNameDict) > 0:
            log.info("All IDs are unique.")
        else:
            log.info("No IDs defined in header.")


def associate_values_to_names(lines):
    """Iterates a list of tuples of (ID_NAME, ID_VALUE)
    """
    valueNameDict = {}

    # Associate names with values
    for line in lines:
        idName, idValue = line
        idValue = int(idValue)
        foundNames = valueNameDict.get(idValue)
        if foundNames == None:
            foundNames = [idName]
        else:
            foundNames.append(idName)
        valueNameDict[idValue] = foundNames
    
    return valueNameDict


def parse_c4d_resource_header(file, minval):
    """Parses a C4D resource header file

    Returns a list of lines. Each line is a tuple of (ID_NAME, ID_VALUE)
    """
    def strip_line(line):
        """Strip newline, tabs, spaces
        """
        return line.strip("\r\n").replace("\t", "").replace(" ", "")

    def filter_line(line):
        """Return False for short, comment, preprocessor, and unwanted line
        """
        return len(line) > 3 and line[0] != "/" and line[0] != "#" and line.find("=") != -1

    def clean_line(line):
        """Clean up line
        """
        # Remove inline comment
        commentPos = line.find("//")
        if commentPos != -1:
            line = line[:commentPos]
            
        # Remove trailing comma
        if line[-1] == ",":
            line = line[:-1]

        return line

    try:
        with open(file, "r") as headerFile:
            # Read lines from file
            lines = headerFile.readlines()

            # Filter unnecessary lines
            lines = [strip_line(line) for line in lines]
            lines = [line for line in lines if filter_line(line)]
            lines = [clean_line(line) for line in lines]

            # Now split lines by "="
            lines = [tuple(line.split("=")) for line in lines]

            # Filter lines by ID minval
            lines = [line for line in lines if (len(line) > 1 and int(line[1]) >= minval)]

            return lines

    except IOError as err:
        log.error(err)
        return []


def main():
    print(SCRIPT_TITLE + " " + SCRIPT_VERSION)
    print(SCRIPT_CREDITS)
    print("")
    # Set up arguments
    parser = argparse.ArgumentParser(description="Checks the Cinema 4D resource ID values defined in one or multiple .h files for uniqueness, and suggests new ID values that could be safely used.", epilog="Happy coding!")
    parser.add_argument("path", metavar="PATH", type=str, help="Path to a header file or a folder with multiple header files to check")
    analysisGroup = parser.add_argument_group("Analysis actions", "These are the main actions that can be performed. If you don't choose any of these, --checkunique will be default.")
    analysisGroup.add_argument("-u", "--checkunique", action="store_true", default=False, help="Check IDs for uniqueness and report shared ID values")
    analysisGroup.add_argument("-s", "--suggest", action="store_true", default=False, help="Suggest free IDs that can be safely added to the header")
    analysisGroup.add_argument("-b", "--showblocks", action="store_true", default=False, help="Show continuous blocks of IDs defined in a header")
    parser.add_argument("--minval", metavar="V", type=int, default=100, help="Minimum ID value. Only IDs >= this value are parsed.")

    # Get arguments
    args = parser.parse_args()
    path = args.path
    minVal = args.minval
    checkUnique = args.checkunique
    suggest = args.suggest
    showBlocks = args.showblocks
    log.debug("Path: " + path)
    log.debug("minVal: " + str(minVal))
    log.debug("checkUnique: " + str(checkUnique))
    log.debug("suggest: " + str(suggest))
    log.debug("showBlocks: " + str(showBlocks))

    # Defaults
    if not checkUnique and not suggest and not showBlocks:
        # If none of the three actions were chosen by the user, just to the uniqueness check
        checkUnique = True

    actionList = ["analyzeHeader"]
    if checkUnique:
        actionList.append("checkUnique")
    if suggest:
        actionList.append("suggestIDs")
    if showBlocks:
        actionList.append("showBlocks")
    log.info("Actions: " + ",".join(actionList))
    print("")

    # Check path
    if not os.path.exists(path):
        log.error("Path '" + path + "' does not exist!")
        return

    if os.path.isdir(path):
        # Iterate files in a directory
        log.info("Iterating '" + path + "'...")
        print("")
        for filename in os.listdir(path):
            if os.path.splitext(filename)[1].lower() == ".h":
                # Process header file
                filename = os.path.join(path, filename)
                log.info("Parsing '" + filename + "'...")
                lines = parse_c4d_resource_header(filename, minVal)
                log.debug(str(len(lines)) + " functional lines found.")
                valueNameDict = associate_values_to_names(lines)
                check_unique_resource_ids(valueNameDict)
                if suggest:
                    suggest_new_ids(valueNameDict, max(minVal, MIN_SUGGEST_IF_EMPTY))
                if showBlocks:
                    show_id_blocks(valueNameDict)
                print("")
    else:
        # Check extension
        if not os.path.splitext(path)[1].lower() == ".h":
            log.error("File '" + path + "' is not a .h file!")
            return

        # Parse single header file
        log.info("Parsing " + path + "...")
        lines = parse_c4d_resource_header(path, minVal)
        log.info(str(len(lines)) + " functional lines found.")
        
        # Process header file
        valueNameDict = associate_values_to_names(lines)
        check_unique_resource_ids(valueNameDict)
        if suggest:
            suggest_new_ids(valueNameDict, max(minVal, MIN_SUGGEST_IF_EMPTY))
        if showBlocks:
            show_id_blocks(valueNameDict)


if __name__ == "__main__":
    main()

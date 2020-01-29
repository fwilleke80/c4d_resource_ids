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

logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.INFO)
log = logging.getLogger("CheckResourceIDs")


def suggest_new_ids(valueNameDict):
    """Suggest new resource IDs that can safely be added to the header
    """
    def get_suggested_value_list(valueNameDict):
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
        suggestedValues.append(largestValue + 1)

        return suggestedValues

    suggestedValues = get_suggested_value_list(valueNameDict)

    log.info("Suggested free ID values:")
    for suggestionIndex, suggestion in enumerate(suggestedValues):
        if suggestionIndex == len(suggestedValues) - 1:
            reasonStr = "after largest ID"
        else:
            reasonStr = "based on gap in ID range"
        log.info("\t" + str(suggestion) + " (" + reasonStr + ")")
    print("")


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
        log.info("All IDs are unique")


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
    # Arguments
    parser = argparse.ArgumentParser(description="Checks the Cinema 4D resource ID values defined in one or multiple .h files for uniqueness, and suggests new ID values that could be safely used.")
    parser.add_argument("path", metavar="PATH", type=str, help="Path to a header file or a folder with multiple header files to check")
    parser.add_argument("--minval", metavar="MINVAL", type=int, default=100, help="Minimum ID value. Only IDs with this value or greater are checked.")
    args = parser.parse_args()

    # Check path
    if not os.path.exists(args.path):
        log.error("Path '" + args.path + "' does not exist!")
        return

    if os.path.isdir(args.path):
        # Iterate files in a directory
        log.info("Iterating '" + args.path + "'...")
        print("")
        for filename in os.listdir(args.path):
            if os.path.splitext(filename)[1].lower() == ".h":
                filename = os.path.join(args.path, filename)
                log.info("Parsing '" + filename + "'...")
                lines = parse_c4d_resource_header(filename, args.minval)
                log.debug(str(len(lines)) + " functional lines found.")
                valueNameDict = associate_values_to_names(lines)
                check_unique_resource_ids(valueNameDict)
                print("")
                suggest_new_ids(valueNameDict)
                print("")
    else:
        # Check extension
        if not os.path.splitext(args.path)[1].lower() == ".h":
            log.error("File '" + args.path + "' is not a .h file!")
            return

        # Parse single header file
        log.info("Parsing " + args.path + "...")
        lines = parse_c4d_resource_header(args.path, args.minval)
        log.info(str(len(lines)) + " functional lines found.")
        
        # Check header file
        valueNameDict = associate_values_to_names(lines)
        check_unique_resource_ids(valueNameDict)
        suggest_new_ids(valueNameDict)


if __name__ == "__main__":
    main()

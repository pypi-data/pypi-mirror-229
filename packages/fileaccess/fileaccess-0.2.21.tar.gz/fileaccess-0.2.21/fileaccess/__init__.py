import os
import traceback


# Fileaccess utility class
# Author: Joe Hacobian
# Date: 09-07-2022
#
# Description:A utility class for safely dealing with files
# Usage:
#
# Read example:
# with Fileaccess("filename.txt", "r") as file:
#   for line in file:
#     print(line)
#
# Write example:
# with Fileaccess("filename.txt", "w") as file:
#   file.write("Hello World")
#
# Append example:
# with Fileaccess("filename.txt", "a") as file:
#   file.write("Hello World")
#
# Creating a file or directory:
# Fileaccess.createFile(assetType="f", targetPath="/path/to/file.txt", fileContents="File contents")
#
# If you are creating a file, you must provide a targetPath and fileContents both strings
# If you are creating a directory, you must provide a targetPath as a string
#
# Note: If you are creating a file, the full non-existent part of the containing directory path
# will be created if it does not exist
# File access mode table:
# --------------------------------------------------------------------------------
# |    Mode   | Meaning                                                          |
# --------------------------------------------------------------------------------
# |    'r'    | open for reading (default)                                       |
# |    'w'    | open for writing, truncating the file first                      |
# |    'x'    | open for exclusive creation, failing if the file already exists  |
# |    'a'    | open for writing, appending to the end of file if it exists      |
# |    'b'    | binary mode                                                      |
# |    't'    | text mode (default)                                              |
# |    '+'    | open for updating (reading and writing)                          |
# --------------------------------------------------------------------------------

class Fileaccess():
    def __init__(self, file_name, mode='r'):
        if os.path.exists(file_name):
            self.file_name = file_name
        else:
            raise Exception(f"Filename parameter must be a valid file path")
        if mode in ['r', 'w', 'a']:
            self.mode = mode
        else:
            raise Exception(f"Passed mode must be commonly one of r = read, w = write, a = append, or one of [r,w,x,a,b,t,+]. Instead found: {mode}")

    def __enter__(self):
        self.file = open(self.file_name, self.mode)
        return self.file

    def __exit__(self, exc_type, exc_value, tb):
        self.file.close()
        if exc_type is not None:
            traceback.print_exception(exc_type, exc_value, tb)
            return False
    @classmethod
    def createFile(cls, assetType="f", targetPath=None, fileContents=None, filePermissions="0644", folderPermissions="0755"):
        fileAsset = None
        directoryAsset = None

        if assetType == "d" and targetPath is None:
            print("You have chosen to create a directory WITHOUT providing a target path.\nPlease provide: createFile(targetPath = '/path/of/desired/asset'")
        elif assetType == "f" and targetPath is None:
            print("You have chosen to create a file WITHOUT providing a target path.\nPlease provide: createFile(targetPath = '/path/of/desired/asset'")
        elif assetType == "f" and targetPath is not None and isinstance(targetPath, str):
            fileAsset = targetPath
        elif assetType == "d" and targetPath is not None and isinstance(targetPath, str):
            directoryAsset = targetPath

        if isinstance(directoryAsset, str):
            # sh.mkdir("-p", directoryAsset)
            os.makedirs(directoryAsset, exist_ok=True)
            # sh.chmod(folderPermissions, directoryAsset)
            os.chmod(directoryAsset, int(folderPermissions, 8))

            if os.path.exists(directoryAsset):
                print(f"Created dir: {directoryAsset}, with 755 permissions")
            else:
                print(f"ERROR encountered in creating dir: {directoryAsset}")
            return

        if isinstance(fileAsset, str):
          os.makedirs(os.path.dirname(fileAsset), exist_ok=True)
          with open(fileAsset, 'wb' if isinstance(fileContents, bytes) else 'wt') as fileHandle:
            fileHandle.write(fileContents)
          os.chmod(fileAsset, int(filePermissions, 8))
          print(f"Created file: {fileAsset}, with {filePermissions} permissions")

# copyifnew
A simple Python copy tool for easy redundant backups

What this program is for:
Copyifnew.py checks your source directory and copies everything that is new or 
was changed to the target directory. Symbolic links are ignored. The program 
can also maintain a set of additional directories to store the previous 
versions of files that were changed or deleted.


How it works:
These are the calling parameters:

-s or --source
Required. Where is the data to backup. The whole directory tree from this 
location is copied. Can also be a file name.

-t or --target
Default: target. Where to put the copy.

-d or --diff
If this is specified, it gives the location for the redundance copies. For 
example, if the diff-directory is /redundance and --numdiff is 9, the program 
creates 9 directories for the safety copies of changed and deleted files:
/redundance/1 ... /redundance/9

-n or --numdiff
Default: 9. The number of redundance directories.

-v or --verb
Verbosity:
0: No Output
1: Error messages
2: 1 + Actions (Updates and new files)
3: 2 + Skipped directories
4: Everything...

-e or --exclude
Directories to exclude from copying. Multiple directories are given in a comma-
separated list: dir1,dir2/new,dir3

Examples:
Simple copy of directory tree:
python3 copyifnew.py -s /home/mydir -t /mnt/backupac/strato/home/mydir

Copy of single file:
python3 copyifnew.py -s /etc/fstab -t /mnt/backupac/strato/etc/fstab

Copy of directory with change redundance:
python3 copyifnew.py -s /mnt/backupac -t /backupac/0 -d /backupac



 

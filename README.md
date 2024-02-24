About
=====

What is Files Sync Link?
------------------------

Files Sync Link is an asynchronous file transfer tool tailored 
for data fetching by SFTP and copying data amongst different directories on the same server.
It consists of two main applications: files fetcher and files copier.

- Files Fetcher is a SFTP file fetcher by use of Asyncio and Asyncssh libraries. 
  It fetches files to "incoming" folder and then copies them to "archive" folder.
- Files Copier gets to "incoming" folder and copies files to provided folders.

There is a possibility to run only one loop or to restart in a given time interval,
check for files and copy them if they are there.
All configuration variables are provided in the configuration file in "etc" directory.
We can limit the number of concurrent tasks by providing "concurrency_limit" attribute to the configuration.

Architecture consists of:
- app
- controllers
- actions


Installation and configuration
------------------------------

In order to successfully install Files Sync Link application you need to proceed next steps:

    $ mkdir files-sync-link
    $ cd files-sync-link

Create conda environment - install right version of python - install package:
    
    $ conda install python==3.11.0
    $ conda create -p ./venv python=3.11.0
    $ conda activate venv
    $ python -m pip install --upgrade pip
    $ python setup.py

Project layout
--------------

Here's the directory structure of the Bics Files Sync Link project::

    ├─ files_sync_link                  # files sync link  module
    │    ├── actions                    # actions directory    
    │    │    ├── copy_fs_file.py       # copy a file
    │    │    ├── delete_fs_file.py     # delete a file
    │    │    ├── describe_file.py      # describe a file
    │    │    ├── disk_free_space.py    # check disk free usage
    │    │    ├── file_space_usage.py   # check file space usage
    │    │    ├── glob_fs_files.py      # list files on the server
    │    │    ├── limit_concurrency.py  # limit the number of tasks
    │    │    └── sftp_execute.py       # execute sftp connector
    │    │
    │    ├── apps                       # main applications
    │    │    ├── app_copy_files.py     # copy files application
    │    │    └── app_fetch_files.py    # fetch files application
    │    │
    │    └── controllers                # application controlles
    │         ├── copy_files.py         # copy files controller
    │         └── fetch_files.py        # fetch files controller
    │
    ├── etc                             # configurations directory
    │    ├── fetcher.yml                # file fetcher configuration
    │    └── copier.yml                 # file copier configuration
    │   
    ├── log                             # logging directory 
    │    ├── all-debug.log              # debug log
    │    └── all-error.log              # error log
    │    ├── all-info.log               # info log
    │    └── all-warning.log            # warning log
    │
    ├── README.md
    ├── requirements.txt
    ├── requirements-dev.txt
    ├── setup.py
    ├── VERSION.txt


Usage
-----

    Fetch files over sftp and copy fetched files to multiple sources

    positional arguments:
      config

    optional arguments:
      --stop-on-loop <NUMBER> -> number of loops to do

Fetch files over SFTP:

    $ python -m files_sync_link.app.app_fetch_files --config etc/fetcher.yml --stop-on-loop 1 -vvv


Copy files to multiple sources:

    $ python -m files_sync_link.app.app_copy_files --config etc/copier.yml --stop-on-loop 1 -vvv
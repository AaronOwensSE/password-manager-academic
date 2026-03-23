# password-manager-academic

An academic project that securely generates and stores passwords for any number of local users and any number of platforms per user.

This project was part of a data and applications security class completed in the fall of 2023. Written in Python.

## Background

Requirements for this project were fairly open-ended (contrary to my generic academic project disclaimer below). Students were directed to conceive of their own projects to explore any of the security concepts being discussed in class. I was initially part of a group that decided to build a password manager in Python using Tkinter for the GUI. However, as participation in the class dwindled, I found myself implementing this project on my own. 100% of this code was written by me. My final submission earned an A.

## Features

The password manager's landing page allows the user to create, access, manage, and delete password-protected profiles. A profile is essentially a local user account with access to a set of encrypted passwords.

After logging in to a profile, the user may create, access, manage, and delete credentials for various platforms. A platform is a program, website, or other application requiring typical username and password credentials. Passwords for platforms can be securely auto-generated using a password randomizer.

Data is persisted locally using SQLite. Profile passwords are salted and hashed using SHA256. Platform credentials are symmetrically encrypted using a Fernet key derived from the profile password and a salt. All salts are generated using a secure random string generator.

A default profile "root" with password "doot" is included for demonstration purposes.

## Setup

From the project root directory:

```
pip install -r requirements.txt
```

## Run

From the project root directory:

```
python password_manager.py
```

## Disclaimer

As an academic exercise, this project's scope is limited to a highly specific set of requirements elicited from assignment documentation and classroom discussions. It is presented as a successful fulfillment of learning objectives and a snapshot of my development over time as a programmer.

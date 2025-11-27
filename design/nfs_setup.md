# NSF Share TrueNAS Setup

[https://www.truenas.com/](https://www.truenas.com/)

## Storage Setup

After installing TrueNAS onto a server that has some drives in it,
you need to create a "pool" (a volume of data you can partition)
and then a "dataset" (Folders that you share).

### 1. Go to Storage > Pools > Add

Go through that wizard to create a pool with your drives.
I recommend having redundancy (RAIDZ1 or RAIDZ2) if you have multiple drives. (This protects against 1 and 2 drive failures, at the cost of 1 & 2 drives worth of space, respectively.)

### 2. After creating the pool, click on the 3 dots next to it and select "Add Dataset"

Name it something like "media" or whatever you want.

Permissions can be really annoying in this system, so I end up splitting out all the different buckets I'll need into their own isolated datasets.

The following is a practical example, my setup looks something like this:

- pool: seastorage-V (RAIDZ1 of 4x 4TB drives)
  - dataset: media
  - dataset: minecraft
  - dataset: zoneminder
  - dataset: deluge
  - dataset: documents

Remember: Every folder you make here will be a separate volume you mount when you want access.
If you want to see all of tyour files from say your personal machine, you'll have to mount each dataset separately.
So don't go too crazy and make a bunch of folders for everything,
else you're gunna have a million volumes in your environment that all need to be mounted every startup.
Also, there's a `127.88 KiB` overhead per dataset, so making a million datasets is also wasteful.

If someone ever fixes or documents the permissions system in the future I'll come back and update this.

## Create a User for NFS Mount

### 1. Find the UID of your User

```bash
id -u {your-username}
```

Should be something like `1001`, take note of this number.

### 2. Create the NFS User with the same UID

Accounts > Users > Add

Full Name: <Whatever you want this is crazy that it's a required field>
Username: {your-username}
Password: <Pick a password. This is just for accessing the user on TrueNAS>
User ID: {the-uid-from-above}
Primary Group: Create New Group (same name as username)

Home directory: Idk, doesn't matter. Have a users folder for everybody.

## Create the Share

Sharing > Unix Shares (NFS) > Add

Select the path of the folder you want accessed from your user.

Advanced Options > Set the "Mapall User" and "Mapall Group" to the user you created above.
Skip the Maproot options.

(NOTE: If this is a sub folder of another NFS share you already have you may get error `Another NFS share already exports this dataset for some network`
Yep, TrueNAS is weird like that. You have to create a new folder at the root of a dataset to share it via NFS.)

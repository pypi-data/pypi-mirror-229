OSS

What is OSS standing for? It's the synonym of Object Storage System.

What is the usage of OSS? OSS is a secure, cost-effective, and high-durability cloud storage service.
It enables you to store large amounts of data in the cloud.
DigiCloud OSS is S3 compatible. You can use it to store any type of object,
which allows for uses like storage for Internet applications, backup and recovery, disaster recovery,
data archives, data lakes for analytics, and hybrid cloud storage.

What is bucket? Buckets are the basic containers that hold your data.
Everything that you store in Cloud Storage must be contained in a bucket.
You can use buckets to organize your data and control access to your data,
but unlike directories and folders, you cannot nest buckets.

> **Attention:** There is a single global namespace shared by all buckets in DigiCloud.
> Your bucket name should be unique globally.

## Examples:

1 **List Locations**

    $ digicloud oss location list


2 **Create a Bucket**

    $ digicloud oss bucket create my-bucket-name
      --access-type private
      --storage-class standard
      --location my-location

3 **List Buckets**

    $ digicloud oss bucket list

4 **Get a Bucket details**

    $ digicloud oss bucket show bucket-name-or-id

5 **Update a Bucket**

Note You can just change access-type of a bucket.

    $ digicloud oss bucket update bucket-name-or-id
      --access-type public 
      --is-referrers-enabled false 
      --is-blank-referrer false 
      --cors-cache-timeout 60 
      --referrers asghar.com akbar.ir 
      --cors-sources http:google.com:80 https://1.1.1.1:500 
      --cors-allowed-methods get post put 
      --cors-allowed-headers header-name x-auth 
      --cors-exposed-headers header-name other-header-name
      --is-cors-enabled true

6 **Delete a Bucket**

    $ digicloud oss bucket delete bucket-name-or-id


7 **Create an Access Key**

    $ digicloud oss access key create my-bucket-name
      --access-type read
      --name devops

8 **List Access Keys**
Note that a bucket can have only on access key at the moment.

    $ digicloud oss access key list my-bucket-name

.. Spawn Eden documentation master file, created by
   sphinx-quickstart on Thu Aug  2 00:39:14 2012.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Spawn Eden's documentation!
======================================

Getting started:
----------------

 - We recommend a virtualenv for using these scripts.

 - Install the dependencies for the scripts - Fabric and Cuisine.
   
   .. code-block:: bash 

   		pip install -r requirements.txt
 
 - Use the following commands to install and configure a standalone Eden instance.
   
   **Install :** 

   .. code-block:: bash 

   		fab -H targetmachine setup_eden_standalone
   
   **Configure :**

   .. code-block:: bash 

		fab -H targetmachine configure_eden_standalone

Getting started with Amazon EC2:
--------------------------------

The following illustrates the procedure to spawn a standalone Sahana Eden instance on EC2.

 - Create a file called **.boto** in your home directory with the following contents with the access key and the secret access key as per your account.

   .. code-block:: none

   		[Credentials]
   		aws_access_key_id = REPLACE_ME_WITH_ACCESS_KEY
   		aws_secret_access_key = REPLACE_ME_WITH_SECRET_ACCESS_KEY

 - Upload your public key to be used with the instances created with EC2.

   .. code-block:: none

   		fab aws_import_key:key_name=awskey,public_key=path_to_your_public_key,ZONE='us-east-1b'

 - Create a security group to be used with the instances spawned with EC2.

   .. code-block:: none

       fab aws_create_security_group:name=default,ZONE='us-east-1b'

 - Create a standalone Sahana Eden instance.

   .. code-block:: none

      fab aws_eden_standalone


Fabfile Documentation
---------------------

.. toctree::
   :maxdepth: 4
.. automodule:: fabfile
    :members:



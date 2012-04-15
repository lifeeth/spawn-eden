# Sahana Eden Deployment Scripts

## Getting started

 - We recommend a virtualenv for using these scripts.

 - Install the dependencies for the scripts - Fabric and Cuisine.
   
   run: `pip install -r requirements.txt`
 
 - Use the following commands to install and configure an Eden instance.
   
   Install: `fab -H targetmachine setup_eden`
   
   Configure: `fab -H targetmachine configure_eden`

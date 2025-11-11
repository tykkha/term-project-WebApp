# Credentials Folder

## The purpose of this folder is to store all credentials needed to log into your server and databases. This is important for many reasons. But the two most important reasons is
    1. Grading , servers and databases will be logged into to check code and functionality of application. Not changes will be unless directed and coordinated with the team.
    2. Help. If a class TA or class CTO needs to help a team with an issue, this folder will help facilitate this giving the TA or CTO all needed info AND instructions for logging into your team's server. 


# Below is a list of items required. Missing items will causes points to be deducted from multiple milestone submissions.

1. Server URL or IP:<br>` ubuntu@ec2-18-220-38-31.us-east-2.compute.amazonaws.com `<br>`http://18.220.38.31/`
2. SSH username: `ubuntu`
3. SSH password or key.  :`team9awskey.pem`
4. Database URL or IP and port used.:`127.0.0.1:33060`
5. Database username: `guides`
6. Database password: `gatorguides`
7. Database name (basically the name that contains all your tables):`GatorGuides`
8. Instructions on how to use the above information.

In order to access the  server via ssh, run the following command inside the credentials folder `ssh -i team9awskey.pem ubuntu@ec2-18-220-38-31.us-east-2.compute.amazonaws.com`

# Most important things to Remember
## These values need to kept update to date throughout the semester. <br>
## <strong>Failure to do so will result it points be deducted from milestone submissions.</strong><br>
## You may store the most of the above in this README.md file. DO NOT Store the SSH key or any keys in this README.md file.

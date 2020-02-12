# exeter-treasure-hunt (ExePlore)
An interactive location based treasure hunting game for the Streatham Campus (University of Exeter)

## Setup
`pip3 install -r app/requirements.txt`
`mysql -u root -p`
`source app/Create_userDB.sql`

## Running Locally
`export ETH_PASSWORD="chosen password for root@localhost user for database"`
`python3 app/wsgi.py`

## Dependencies
* python3
* flask
* MySQL

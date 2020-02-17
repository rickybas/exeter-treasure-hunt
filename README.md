# exeter-treasure-hunt (ExePlore)
An interactive location based treasure hunting game for the Streatham Campus (University of Exeter)

## Setup
Clone repo:

`git clone https://github.com/rickybas/exeter-treasure-hunt.git`

`cd exeter-treasure-hunt`

Install dependencies (make sure [system dependencies](#system-dependencies) are installed before this):

`pip3 install -r app/requirements.txt`

Set up MySQL database, enter password for user root@localhost:

`mysql -u root -p < app/create_user_db.sql`

## Running Locally

`python3 app/wsgi.py`

## System dependencies
* Python 3.7
* MySQL 8

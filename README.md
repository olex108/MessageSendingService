# MessageSendingService

Service for sending messages for recipients emails

## User manual

#### Registration by email address

#### Recipients list 
- You can add, update or delete recipients emails and information

#### Messages
- You can add, update or delete messages for mailing

#### Sending mails
- You can add, update or delete mailing 
Service help create mailings for message for list or recipients for period

#### Statistics
- You have statistics of mailing attempts with information of all attempts with number of sent messages 

#### Commands
- "start_mailing": start send emails for LAUNCHED mailing
- "add_managers": add Managers group for moderation of service

## Installation:

For use program need to clone repos 
```
https://github.com/olex108/MessageSendingService.git
```
install dependencies from `pyproject.toml`

For work create file `.env` with params of django settings.py:

```
SECRET_KEY=your-secret-key
DEBUG=Debug param
```

For work create PostgresDB database and add params to file `.env`

```
NAME=name_of_database
USER=name_of_Postgress_DB_user
PASSWORD=password
HOST=host
PORT=port
```

For correct sending email add params to file `.env`

```
EMAIL_ADDRESS=email_address
APP_EMAIL_PASSWORD=app_email_password
```

For cache data add params to file `.env`:

```
LOCATION=host_of_cache
```

## Testing:

For testing you can use command load_test_data
# Description
This is a simple project to test async-api with rabbitmq.

## How to run
- `make start`

## How to test

- Run the following curl to create a new message
```bash
curl --location '127.0.0.1:10000/ping' \
--header 'Content-Type: application/json' \
--data '{
    "message": "test"
}'
```

```json
{
    "timestamp": "2024-04-29 23:05:55+0000",
    "redirect_uri": "/state/0ea6f343-ea95-489f-9a99-18b099039f57",
    "msg": "Waiting for response message from the server may take some time, grab a coffee and relax",
    "is_async": true
}
```

- Check state of the processed data
```bash
curl --location '127.0.0.1:10000/state/0ea6f343-ea95-489f-9a99-18b099039f57'
```

```json
{
    "timestamp": "2024-04-29 23:06:40+0000",
    "msg": "The request is still in progress",
    "completed": false
}
```

- Run 10 seconds later
```bash
curl --location '127.0.0.1:10000/state/0ea6f343-ea95-489f-9a99-18b099039f57'
```

```json
{
    "timestamp": "2024-04-29 23:06:40+0000",
    "msg": "The request is completed",
    "completed": true
}
```

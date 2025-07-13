# How to create a Luffa bot

- Open [https://robot.luffa.im/login](https://robot.luffa.im/login)
- Scan the QR code using Luffa App to Login
- Click “New Bot” to create a bot
    - <span style="color:red;background-color:black;padding:2px 4px;border-radius:4px;font-weight:bold;">Important</span> After creating it, run the following command or use Postman to send the request first.
            
        ```bash
        curl --location 'https://apibot.luffa.im/robot/receive' \
        --header 'Content-Type: application/json' \
        --data '{
            "secret": "Secret Key"
        }'
        ```
            
    - You can use another account to add this bot as a contact using its UID.
        - Execute the command above to approve the add request.
    - If the bot is added by someone or invited to a group, you must execute the above command.
    - <span style="color:red;background-color:black;padding:2px 4px;border-radius:4px;font-weight:bold;">Important</span>In order to avoid strange bugs, the most reliable way is to set up a cron job (refer to [cron.py](app/cron.py).) to run the above receive method **every second**.
  
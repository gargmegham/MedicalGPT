<div>
<img src="https://github.com/gargmegham/MedicalGPT/assets/95271253/75be92df-41e5-46b2-908d-4fc55df236ca"  width="50" height="50">
<h1>Telegram Bot: Using OpenAI models & SDKs with no daily limits to provide people with general medication prescription.<h1>
</div>

We all love [chat.openai.com](https://chat.openai.com), but... It's TERRIBLY laggy, has daily limits, and is only accessible through an archaic web interface.

![Screenshot 2023-05-22 at 9 38 41 AM](https://github.com/gargmegham/MedicalGPT/assets/95271253/b64294df-e6f9-4e65-9a08-e9d7c8bf5c26)

This repo is MedicalGPT your personal medical advidor who will prescribe OTC medicines for your issues like sinus, chest pain etc. **And it works great.**

## Features
- Low latency replies (it usually takes about 3-5 seconds)
- No request limits
- Message streaming
- Support of [ChatGPT API](https://platform.openai.com/docs/guides/chat/introduction)
- List of allowed Telegram users
- This bot has been created under the guidance of a certified Dr.
- This bot understands when certain sentences indicates certain diseases or concerns, and then it asks follow up questions accordingly.
- It also prescribes users based on thier medical conditions, medications, surgeries, allergies etc. which it asks for during registeration process.
- This also allows you to integrate your cal.com account, which allows you to book appointments for specialized treatment from Dr.
---

## Setup
1. Get your [OpenAI API](https://openai.com/api/) key

2. Get your Telegram bot token from [@BotFather](https://t.me/BotFather)

3. Edit `config/config.example.yml` to set your tokens and run 2 commands below (*if you're advanced user, you can also edit* `config/config.example.env`):
    ```bash
    mv config/config.example.yml config/config.yml
    mv config/config.example.env config/config.env
    ```

4. 🔥 And now **run**:
    ```bash
    docker-compose --env-file config/config.env up --build -d
    ```

# How to run

## Using python

**Create a Virtual Environment**:
```bash
python -m venv venv
```

**Install the FFmpeg library**:
```bash
sudo apt-get install -y ffmpeg
```

**Install the requirements**:

```bash
pip install -r requirements.txt
```

**Create a .env file in the root of the project with these variables defined**:

```
DISCORD_BOT_TOKEN=<>
SPOTIFY_CLIENT_ID=<>
SPOTIFY_CLIENT_SECRET=<>
```

**Run the script**:

```bash
python bot.py
```

## Using docker


**Create a .env file in the root of the project with these variables defined**:

```
DISCORD_BOT_TOKEN=<>
SPOTIFY_CLIENT_ID=<>
SPOTIFY_CLIENT_SECRET=<>
```

**Run the docker compose**:


```bash
docker compose up -d
```

# Creating an .exe file

**Run this in the root of the project**:

```bash
pyinstaller --onefile bot.py
```
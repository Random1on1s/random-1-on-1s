# Random 1 on 1 Bot

## General package structure

```zsh
random1on1/
    api/
        algorithm.py     # Abstract definition of algoirthm requirements
        channels.py      # Abstract channel types
        config.py        # Configuration options for random 1 on 1 bot
        pairings.py      # Object representing the weekly product returned by the bot
        participant.py   # Wrapper for discord members that includes relevant info for matching
        
    discord/
        channels.py      # Concrete setup for individual channels (logging, pairing history, announcements, DMs, etc)
        server.py        # Server specific information
        
    matching/
        ... 
    
    random1on1bot.py     # Client to do all the coordinations
```

## Setup workflow

1. Fork repo to your organization
2. Fill in the discord specific information into environment secrets
3. Setup `.github/workflows/run-pairings.yml` workflow to run based on desired schedule
4. ???
5. Profit!

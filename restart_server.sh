#!/bin/bash

proc_count=$(ps aux | grep '[p]ython3 turkish_delight_bot.py' | wc -l)

if [[ $proc_count -eq 0 ]]; then
    echo "Warning: Server is down!"
    cd /home/ubuntu/turkish-delight-bot
    ./log_run_bot
else
    echo "Server is still running."
fi

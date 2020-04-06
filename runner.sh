NOW=$(date +"%F") &&
python3 dov_bot.py > logs/log_$NOW.log 2> logs/log_err_$NOW.log



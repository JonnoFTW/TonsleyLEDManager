@echo off
set DBNAME=led
set DBHOST=localhost
set DBPASS=ledmanager
set DBUSER=LEDManager

@echo on
start python main.py 172.22.11.2:7890
cd webapp\TonsleyLED\tonsleyled
start pserve production.ini --reload
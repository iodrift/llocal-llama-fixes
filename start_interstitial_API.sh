#!/bin/bash
nohup uvicorn interstitial_API:app --port 3456 > /dev/null 2>&1 &

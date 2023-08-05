#!/bin/bash
nohup uvicorn interstitial_API:app --host 0.0.0.0 --port 3456 > /dev/null 2>&1 &
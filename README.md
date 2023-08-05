# llocal-llama-fixes

Here are just some scripts and hacks to facilitate better self-hosting of large language models. 


# interstitial_API - a relay for pseudo-OpenAI-compatible LLM APIs

interstitial_API is essentially a live streaming relay for API calls to allow two things:
    1. the use of partially-OpenAI-compatible APIs that do not have fully defined endpoints (e.g. they are missing /v1/models), and
    2. inject prompts in between user and assistant messages, to stop the AI from auto-completing user messages or carrying on a conversation with itself.

It is lightweight and designed to be run on the same system where the models are actually run. On my MacBook M1 Max it uses ~1.5% of a single CPU thread under load and never has used more than 0.1% of my 64GB of system memory.

To set it up on your machine, read on. Note tese instructions are generally for Mac but can be adapted to your OS... just ask your model to translate it for you :)


## PREREQUISITES

You should have Python 3.7 or higher installed on your system. Linux users should have it already or else know how to get it, Mac and Windows users can download Python from [the official website](https://www.python.org/downloads/). Mac users can also get it using Homebrew if they prefer:
```bash
    brew install python
```



## STEPS

### 1.     **Install the required packages**

You can install the necessary Python packages using pip, the Python package installer. Run the following command to install the requirements:

```bash
    pip install fastapi uvicorn httpx
```

   MacOS may not recognize pip if you installed Python using Homebrew, in which case substitute in pip3.

### 2.     **(MacOS) Move interstitial_API.py to your home folder.**

On MacOS it's recommended that you move interstitial_API.py to your home folder.

You'll also need to chmod it:

```bash
    chmod +x ~/interstitial_API.py
```

### 3.     **(Test) Run the API server**

You can now run the relay server using Uvicorn with the following command:
    ```bash
    uvicorn interstitial_API:app --port 3456
    ```

*Note: you can add `--host 0.0.0.0` to allow other machines / IPs access, but be careful with this function especially if your router exposes your machine to incoming WAN traffic. Consider using Tailscale or Cloudflare Zero Trust for safe(r) remote access.*

If you rename the file, modify the command but omit the .py for purposes of uvicorn.

You should now be able to access the API at `localhost:3456`, and it will relay to `localhost:6789` (e.g. the port used by LM Studio). 

If you need to use a different port, or an address other than localhost, simply edit the relevant lines in the .py file.

To test the relay, try calling it from your UI of choice (I recommend ChatWizard, slickgpt, chat-with-gpt, or big-agi, personally, but all of these except ChatWizard require some code hacks, a subject of a future addtion to this repo). Or use a free API testing app. Or you simply curl it from the command line, but note streaming won't work:

```bash
curl http://localhost:6789/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{"role": "user", "content": "Why is \"What Is To Be Done?\" by V.I. Lenin still worth reading today?"}],
    "temperature": 0.7,
    "max_tokens": -1
  }'
```

### 4.     **Make it run without a terminal open**

If you don't want to have to keep a terminal open running uvicorn, continue by creating a script (your home folder is a good place for it). TextEdit should work, just make sure it actually uses .sh as the extension and not .sh.txt (you can also create it in terminal with `touch start_app.sh`). This script is in this repo as `start_interstitial_API.sh`.

The contents of the script:

```bash
    #!/bin/bash
    nohup python /path_to_your_script/interstitial_API.py > /dev/null 2>&1 &
 ```

Once you've saved your script in your home folder, chmod it in Terminal:
```bash
    chmod +x start_interstitial_API.sh
```

Now you can run that script once with `./start_interstitial_API.sh` in Terminal, and it should continue running after you close Terminal, until you reboot or otherwise kill it.

***Note: to stop the relay, enter `kill -9 $(ps aux | grep '[i]nterstitial_API:app' | awk '{print $2}')` in the Terminal.

### 5.     **(Optional) Start the relay when you log into your Mac**
   
To further reduce friction, you can have this script run quietly on login ensuring the API is always up unless you manually kill it.
a. Open "System Preferences" and find "Login Items" within "General" (or within "Users & Groups" > your user account on older versions of MacOS).
b. Click on the '+' button to add a new login item.
c. Navigate to `start_interstitial_API.sh` and select it and click "Add".

Now your script should run each time you log into your macOS user account.


## **MODIFICATIONS**

As noted you can simply edit your local `interstitial_API.py` to change the server or port of the destination API, at line 23, and edit the injected system messages before user and assistant messages at lines 54 and 55, accordingly. Check your model's card on HuggingFace to find what prompt syntax it responds to.

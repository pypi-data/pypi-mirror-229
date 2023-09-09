Joker API SDK
===============
JokerSDK is an asynchronous python library to wrap around the JokerAPI.co voice API.

Install JokerSDK
----------------
```bash
pip install JokerSDK
```

Initiation
----------
```python
from JokerAPI import SDK, Number

# Joker Initiatior
JokerInstance: SDK = SDK()

# Set API Key
JokerInstance.api_key = "API_KEY"
```

Asynchronous Outbound Call
-------------------------
```python
import asyncio
from JokerAPI import SDK, Number

# Joker Initiatior
JokerInstance: SDK = SDK()

# Set API Key
JokerInstance.api_key = "API_KEY"

# Run the asynchronous function and dial US('111111111') from US('+111111111')
asyncio.run( JokerInstance.dial(dial_to=Number("+111111111"), dial_from=Number("111111111")) )
```

Class Integration
-----------------
```python
import asyncio, JokerAPI

class JokerClass(JokerAPI.SDK):
    def __init__(self, **kwargs) -> None:
        super().__init__(kwargs)

    def set_key(self, key) -> None:
        self.api_key = key

    def dial(self, *args, **kwargs) -> asyncio.run:
        return asyncio.run(self.dial(args, kwargs))
```

Callback server example
-----------------------
```python
import flask
from typing import Any

app: flask.Flask = flask.Flask(__name__)

@app.route("/your_project/callback", methods=["POST"])
async def callbacks() -> Any[flask.Response, flask.jsonify, str]:
    status: dict[str] = {flask.request.json['callsid']: flask.request.json['status']}

    print(f"The CallSID ({flask.request.json['callsid']}) is {flask.request.json['status'].split('.')[1]}")

    return "Any Response."

app.run("0.0.0.0", port=8080)
# Example output for when callback 'call.ringing' is sent.
#> The CallSID ('e074a38cc9a4e77ec') is ringing
```

# plugin_client

`plugin_client` is a Python package that allows your application to communicate with a server using WebSockets. It's designed to handle incoming function calls from the server and execute them locally.

## Installation

To install the package, you can use pip:

```
pip install plugin_client
```

## How to use

Here's a simplified usage example based on your provided test case:

```python
import time
import plugin_client
import cv2
import numpy as np

async def gray_pic(code: str):
    """
    A Function that converts an image to grayscale.
    Parameters: code: (str, required):the file path of the image
    """
    print(code)
    img = cv2.imread(code)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray_image_path = str(time.time()) + ".jpg"
    cv2.imwrite(gray_image_path, gray)
    return gray_image_path

plugin_client.api_key = "your-api-key" # Replace with your actual API key
plugin_client.functions = [gray_pic]
plugin_client.use_common_plugin = False

plugin_client.start()
```

## Important Parameters in the Source Code

- `api_key`: This is used to identify your client to the server. It needs to be set before starting the client.
- `functions`: This is a list of the functions that your client can execute. These functions will be called when the server sends a function call.
- `use_common_plugin`: This is a boolean value that determines whether to use common plugins. If it's set to `True`, the client will use the common plugins provided by the server.
- `host` and `port`: These are the address and port of the server that the client will connect to.
- `start`: This is a function that starts the client. It checks if the API key is set, creates an instance of `PluginClient`, and starts the client's event loop.
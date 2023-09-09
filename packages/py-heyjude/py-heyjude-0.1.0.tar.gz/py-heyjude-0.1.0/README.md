# py-heyjude

A Python wrapper for the HeyJude API.

## Installation

```bash
pip install py-heyjude
```


## Usage
```
from heyjude.api import HeyJudeAPI

api = HeyJudeAPI(email="your_email@example.com", password="your_password", api_token="<x-api-token here check your network tab for this>")
print(api.get_subscription_status())

```

## Features
- Authenticate and retrieve token.
- Refresh token.
- Get subscription status.
- Retrieve open tasks.
- Get details of a specific task by its ID.
- Send a message related to a specific task.
- Create a new task.


## License
This project is licensed under the MIT License. See the LICENSE file for details.
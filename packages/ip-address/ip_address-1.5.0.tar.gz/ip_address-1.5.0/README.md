# IP-Address

A Python module to fetch your public IP address.

[![PyPi Version](https://img.shields.io/pypi/v/ip-address.svg)](https://pypi.org/project/ip-address/)
[![MIT License](https://img.shields.io/pypi/l/ip-address.svg)](https://github.com/dewittethomas/ip-address/blob/master/LICENSE)

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
  - [Get](#get)
- [Contributing](#contributing)
- [License](#license)

## Installation

You can install the `ip-address` module using pip:

```bash
pip install ip-address
```

## Usage

### Get

You can use this module to retrieve your public IP address. Here's a basic example:

```python
import ip_address as ip

address = ip.get()
print("Your public IP address is:", address)
```

## Contributing

Contributions to this project are welcome. If you have any improvements or bug fixes, please submit a pull request.

## License

This project is licensed under the MIT License.
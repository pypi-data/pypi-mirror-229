import os
import re
from setuptools import setup,find_packages


requires = ["pycryptodome==3.16.0","aiohttp==3.8.3","asyncio==3.4.3", "requests==2.31.0"]
_long_description = """

## NanyBale

> Elegant And Modern Bale MTProto API framework in Python for users and bots

<p align="center">
    <img src="https://s2.uupload.ir/files/img_20230208_141501_035_f545.jpg" alt="NanyBale" width="128">
    <br>
    <b>library NanyBale</b>
    <br>
</p>

###  Nanymous


### How to import the Rubik's library

``` bash
from Nanylex import Bale
```

### How to import the anti-advertising class

### How to install the library

``` bash
pip3 install NanyBale==1.0.0
```

### My ID in Telegram

``` bash
@Nanymous
```
## An example:
``` python
from NanyBale import Bale

bot = Bale("Your Token Account")

gap = "Your Chat ID Or Gap Or pv Or Channel"

bot.sendMessage(gap, "NanyBale Library")
```
Made by Team Nanymous

### Key Features

- **Ready**: Install NanyBale with pip and start building your applications right away.
- **Easy**: Makes the Bale API simple and intuitive, while still allowing advanced usages.
- **Elegant**: Low-level details are abstracted and re-presented in a more convenient way.
- **Fast**: Boosted up by pycryptodome, a high-performance cryptography library written in C.
- **Async**: Fully asynchronous (also usable synchronously if wanted, for convenience).
- **Powerful**: Full access to Bale's API to execute any official client action and more.


### Our Channel in messengers

``` bash
Our Channel In Ita

https://eitaa.com/Nanymous_Team

Our Channel In Soroush Plus

https://splus.ir/Nanymous_Team

Our Channel In Rubika

https://rubika.ir/Nanymous_Team

Our Channel In The Bale

https://ble.ir/Nanymous_Team

Our Channel on Telegram

https://t.me/Nanymous_Team
```
"""

setup(
    name = "NanyBale",
    version = "1.0.0",
    author = "Mohammad _GeNeRal_",
    author_email = "Manymous@gmail.com",
    description = ("Library Bale Robot"),
    license = "MIT",
    keywords = ["Nany","NanyBale","NanyBale","nany","bot","Bot","BOT","Robot","ROBOT","robot","self","api","API","Api","Bale","Bale","Bale","Python","python","aiohttp","asyncio"],
    packages = ['Nanylex'],
    long_description=_long_description,
    long_description_content_type = 'text/markdown',
    install_requires=requires,
    classifiers=[
    'Development Status :: 3 - Alpha',
    'Intended Audience :: Developers',
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',
    "Programming Language :: Python :: Implementation :: PyPy",
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: 3.8',
    'Programming Language :: Python :: 3.9',
    'Programming Language :: Python :: 3.10',
    'Programming Language :: Python :: 3.11'
    ],
)

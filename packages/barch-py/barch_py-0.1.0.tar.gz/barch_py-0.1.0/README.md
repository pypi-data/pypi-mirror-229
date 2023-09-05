<div align="center">
    <h1>barch.py</h1>
</div>

## What is this?

An asynchronous wrapper for the fanmade [Blue Archive API](https://github.com/torikushiii/BlueArchiveAPI).

## Why and what's the use?

Idk.... built it coz I don't have anything better to do.

## Installation

Python version 3.10 or greater is required to use barch.py.

```sh
pip install barch-py
```

## Features

- Get all the characters - EN and JP version
- Get a character details by id or name - EN and JP version
- Get characters based on different parameters like position, role etc
- Get current, ongoing and upcoming raids - EN and JP versions

## Usage

- Example of getting all the characters - EN and JP versions

```Python
from  barch  import  Client

client = Client()

characters_result = await client.character.get_all_characters()
characters_result_jp = await client.character.get_all_characters_jp()

if characters_result.is_success:
    characters = characters_result.value

if characters_result.is_error:
    error = characters_result.error

if characters_result_jp.is_success:
    characters_jp = characters_result_jp.value

if characters_result_jp.is_error:
    error_jp = characters_result_jp.error

await  client.close()
```

- Example of getting raid details - EN and JP versions

```python
from barch import Client

client = Client()

raids_result = await client.raid.get_raids()
raids_result_jp = await client.raid.get_raids_jp()

if raids_result.is_success:
    raids = raids_result.value

if raids_result.is_error:
    error = raids_result.error

if raids_result_jp.is_success:
    raids_jp = raids_result_jp.value

if raids_result_jp.is_error:
    error_jp = raids_result_jp.error

await  client.close()
```

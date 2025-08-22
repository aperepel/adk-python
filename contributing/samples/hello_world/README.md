# Hello World Sample Agent

This sample demonstrates a basic agent in the Agent Development Kit (ADK) that can roll dice and check if numbers are prime.

## Overview

The Hello World sample consists of a single agent that can perform two main tasks:
- Rolling a die with a specified number of sides.
- Checking if a list of numbers contains any prime numbers.

## Key Features

- **`roll_die(sides: int)`**: A tool that simulates rolling a die. It takes the number of sides as input and returns the result.
- **`check_prime(nums: list[int])`**: A tool that checks for prime numbers in a given list of integers.

## Usage

To run this agent, use the `adk web` command from the root of the repository:

```bash
adk web contributing/samples/
```

Then, navigate to the web interface and select the "hello_world" agent.

## Example Interactions

**Rolling a die:**
```
User: Roll a 20-sided die
```

**Checking for prime numbers:**
```
User: Is 13 a prime number?
```

**Combined operation:**
```
User: Roll a 10-sided die and tell me if the result is a prime number.
```

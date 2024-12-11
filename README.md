# Chatroom Application - Network Programming Project @ FMI 2024

## Table of Contents

1. [Introduction](#introduction)
2. [How to Run the Application](#how-to-run-the-application)
3. [Architecture](#architecture)

## Introduction
This is a chatroom application consisting of a server and client written in Python. Key features:
- Broadcast messages
- Features like private messaging and listing of active users
- User login and logout

## How to Run the Application

### Prerequisites
Ensure Python 3.x is installed on your system. No additional libraries needed.

### Installation
1. Clone/Download this Repoditory
`git clone <repository_url>`
`cd <project_directory>`
2. Create and Activate a Virtual Environment 
- on Windows 
`python -m venv venv`
`venv\Scripts\avtivate`
- on Linux/Mac 
`python3 -m venv venv`
`source venv/bin/activate`
3. Run the Server 
Open a terminal, navigate to the project directory and start the server
`python server.py`
4. Run the Client 
Open a separate terminal (or multiple terminals to simulate multiple users). Ensure the virtual environment is activated and start the client
`python client.py` 
5. Join the Chatroom
Enter a username when prompted in the client and start sending messages
6. Exit the Virtual Emvironment

## Architecture

### Server (server.py)
The server is responsible for:
- Accepting and managing client connections.
- Broadcasting messages to all users.
- Supporting commands like:
    `!who` - list active users;
    `!msg` - enables private messaging;
    `!logout` - handles user disconnections.

Design Choice:
The server uses the select module to monitor multiple client sockets simultaneously, allowing for new connections, incoming messages, and disconnections, without blocking or requiring additional threads for each connection.

Tools used:
- The socket and select libraries.

### Client (client.py)
The client enables users to:
- Send and receive messages in real-time.
- Execute chatroom commands.
- Log out cleanly.

Design Choice:
The client uses multithreading to handle sending and receiving messages concurrently, ensuring real-time communication without blocking the user interface.

Tools used:
- The socket, threading, and errno libraries.
# Flask Application

## Description

This repository hosts a Flask application that functions as a webhook for a Webex bot, facilitating seamless interaction between users and a ChatGPT assistant. The application acts as middleware, receiving direct messages sent to the Webex bot, processing incoming data via a webhook registered to a public URL, and tunneling it to the Flask server. It then extracts messages from the Webex bot payload, forwards them to the ChatGPT assistant, and sends the assistant's responses back to the user engaged with the Webex bot.

## Prerequisites

Before you begin, ensure you have Python installed on your system. This application requires Python 3.x.

## Setting Up the Environment

To set up the project environment and run the application, follow these steps:

### 1. Create a Virtual Environment

#### For MacOS/Linux:

Create a virtual environment in the repository directory by running:

```
python3 -m venv .
```

Activate the virtual environment with:

```
source ./bin/activate
```

#### For Windows:

Create a virtual environment in the repository directory by running:

```
python -m venv .
```

Activate the virtual environment with:

```
.\Scripts\activate
```

### 2. Install Dependencies

With the virtual environment activated, install the project dependencies with:

```
pip install -r requirements.txt
```

## Running the Application

To start the Flask app, run the following command in the terminal with the active virtual environment:

```
python app.py
```

## Additional Information

- To stop the application, navigate to the terminal in which it is running and press `Ctrl + C`
- To deactivate the virtual environment when you are done, simply run:

```
deactivate
```

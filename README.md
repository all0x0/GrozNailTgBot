<p align="center">
  <a href="" rel="noopener">
 <img width=200px height=200px src="https://i.imgur.com/FxL5qM0.jpg" alt="Bot logo"></a>
</p>

<h3 align="center">Project Title</h3>

---

## 📝 Table of Contents

- [About](#about)
- [Demo / Working](#demo)
- [How it works](#working)
- [Usage](#usage)
- [Getting Started](#getting_started)
- [Deploying your own bot](#deployment)
- [Built Using](#built_using)
- [TODO](#todo_list)

## 🧐 About <a name = "about"></a>

Firstly, this bot has been created for my wife and her nail(beauty) business. Potential clients can easily get an actual price list, get free dates and hours (further in the text just slots) calendar and choose the appropriate one in a few clicks. After that you should only wait that day and that's it! There is no long correspondence in chats, useless calls, etc! Isn't that cool?

## 🎥 Demo (eng soon) <a name = "demo"></a>

![Alt text](demo.gif)

## 💭 How it works <a name = "working"></a>

This bot like a "middleware" between a client and a master (nail artist).  
The master first should add new slots using hidden commands. After that these slots will be available for getting appointments.

The bot has the ability to send messages to both master and client in an appropriate circumstances, e.g. a client chose a free slot, immediately sends a message to the master with options like accept and reject, depending on what the master chose the client receives a respond message.

The entire bot is written in Python 3.9 and hosted on [Vercel](https://vercel.com/)!

## 🎈 Usage <a name = "usage"></a>

To use the bot, type:

```
!dict word
```

The first part, i.e. "!dict" **is not** case sensitive.

The bot will then give you the Oxford Dictionary (or Urban Dictionary; if the word does not exist in the Oxford Dictionary) definition of the word as a comment reply.

### Example:

> !dict what is love

**Definition:**

Baby, dont hurt me~
Dont hurt me~ no more.

**Example:**

Dude1: Bruh, what is love?
Dude2: Baby, dont hurt me, dont hurt me- no more!
Dude1: dafuq?

**Source:** https://www.urbandictionary.com/define.php?term=what%20is%20love

---

<sup>Beep boop. I am a bot. If there are any issues, contact my [Master](https://www.reddit.com/message/compose/?to=PositivePlayer1&subject=/u/Wordbook_Bot)</sup>

<sup>Want to make a similar reddit bot? Check out: [GitHub](https://github.com/kylelobo/Reddit-Bot)</sup>

## 🏁 Getting Started <a name = "getting_started"></a>

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See [deployment](#deployment) for notes on how to deploy the project on a live system.

### Prerequisites

What things you need to install the software and how to install them.

```
Give examples
```

### Installing

A step by step series of examples that tell you how to get a development env running.

Say what the step will be

```
Give the example
```

And repeat

```
until finished
```

End with an example of getting some data out of the system or using it for a little demo.

## 🚀 Deploying your own bot <a name = "deployment"></a>

To see an example project on how to deploy your bot, please see my own configuration:

- **Heroku**: https://github.com/kylelobo/Reddit-Bot#deploying_the_bot

## ⛏️ Built Using <a name = "built_using"></a>

- [python-telegram-bot V13.13](https://docs.python-telegram-bot.org/en/v13.13/) - This library provides a pure Python interface for the [Telegram Bot API](https://core.telegram.org/bots/api)
- [Flask](https://flask.palletsprojects.com/en/3.0.x/) - a web framework
- [sqlalchemy](https://www.sqlalchemy.org/) - The Python SQL Toolkit
- [Supabase](https://supabase.com/) - an open source Firebase alternative
- [alembic](https://alembic.sqlalchemy.org/en/latest/) for migrations (I use it only locally)

## 🗒️ TODO list <a name = "todo_list"></a>

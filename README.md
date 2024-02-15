<p align="center">
  <a href="" rel="noopener">
 <img width=200px height=200px src="https://i.imgur.com/FxL5qM0.jpg" alt="Bot logo"></a>
</p>

<h3 align="center">No-name (yet) bot</h3>

---

## 📝 Table of Contents

- [About](#about)
- [What this bot can do?](#just_do_it)
- [Demo / Working](#demo)
- [How it works](#working)
- [Built Using](#built_using)
- [TODO](#todo_list)

## 🧐 About <a name = "about"></a>

Firstly, this bot has been created for my wife and her nail(beauty) business. Potential clients can easily get an actual price list, get free dates and hours (further in the text just slots) calendar and choose the appropriate one in a few clicks. After that you should only wait that day and that's it! There is no long correspondence in chats, useless calls, etc! Isn't that cool?

## 🗒️ What this bot can do? <a name = "just_do_it"></a>

For clients:

- [x] Get a price list
- [x] Make an appointment
- [x] Register new clients through the making their first appointments
- [x] Cancel the appointment
- [x] Reschedule the appointment
- [x] Send notifications to master about new appointments and its cancellations

For masters, as for clients, plus:

- [x] Accept or reject the request for new appointments
- [x] Send notifications to clients about accepting or rejecting with additional info
- [x] Hidden commands (works only for masters):
  - [x] Add free slots (date and time)
  - [x] Delete free slots
  - [x] Clear days of free slots

## 🎥 Demo <a name = "demo"></a>

![Alt text](demo.gif)

## 💭 How it works <a name = "working"></a>

This bot like a "middleware" between a client and a master (nail artist).  
The master first should add new slots using hidden commands. After that these slots will be available for making appointments.

The bot has the ability to send messages to both master and client in an appropriate circumstances, e.g. a client chose a free slot, immediately sends a message to the master with options like accept and reject, depending on what the master chose the client receives a respond message.

The entire bot is written in Python 3.9 and hosted on [Vercel](https://vercel.com/)!


## ⛏️ Built Using <a name = "built_using"></a>

- [python-telegram-bot V13.13](https://docs.python-telegram-bot.org/en/v13.13/) - This library provides a pure Python interface for the [Telegram Bot API](https://core.telegram.org/bots/api)
- [Flask](https://flask.palletsprojects.com/en/3.0.x/) - a web framework
- [sqlalchemy](https://www.sqlalchemy.org/) - The Python SQL Toolkit
- [alembic](https://alembic.sqlalchemy.org/en/latest/) - migrations (I use it only locally)


## 🗒️ TODO list <a name = "todo_list"></a>

- [ ] update a price by sending a price image or url
- [ ] google calendar integration (for master)
- [x] new menu button for a master with an ability to send a reminder about upcoming appointments
- [ ] loyalty program
- [ ] administration menu or commands
- [ ] registration new masters through the administration menu or commands
- [ ] blacklist (banning)
- [ ] english language support

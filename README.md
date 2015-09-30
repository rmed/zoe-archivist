# Zoe archivist ![Agent version](https://img.shields.io/badge/Zoe_Agent-0.2.4-blue.svg "Zoe archivist")

Archive management using small information cards.

## Requirements

This agent requires [infocards](https://github.com/rmed/infocards), which is automatically installed by the `postinst` script.

**If you are updating from version 0.1.0, you should first uninstall the agent.**

## Why?

From time to time I come across something that seems very interesting and think on how I could use it in a project or combine it with other things. Usually, I bookmark the page, but I end up forgetting what I wanted to do with that, so now Zoe  is going to remember that for me.

## How does it work?

Information is stored in `cards` that can also be associated to `sections`. All users recognized by Zoe are/should be able to search and retrieve cards from the archive. However, if you want to edit, add or perform more priviledged tasks, you should create a new group in the `ZOE_HOME/etc/zoe-users.conf` and add the `archivists` group:

```
[group archivists]
members = admin
```

The natural commands are pretty self-explanatory, however there are a couple of interactions with the agent to take into account:

### Card creation

When creating a card, you must send a mail with subject `Archivist new` and mail body:

```
title: title of the card
desc: small description of the card

tags: tags for searching, separated by whitespace

content: main content of the card.
Can also be multiline, but you should end it with
/content
```

The order for these is irrelevant.

### Card edition

Similar to card creation, but subject should be `Archivist edit` and mail body:

```
id: ID of the card

title: new title of the card
desc: new small description of the card

tags: new tags for searching, separated by whitespace

content: new main content of the card.
Can also be multiline, but you should end it with
/content
```

Basically, you can omit any from *title, desc, tags, content* that you do not want to edit. Meaning that the fields that you do include will overwrite those already stored.

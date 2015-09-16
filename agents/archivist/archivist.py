#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Zoe archivist
# https://github.com/rmed/zoe-archivist
#
# Copyright (c) 2015 Rafael Medina García <rafamedgar@gmail.com>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import sys
sys.path.append('./lib')

import gettext
import zoe
from infocards.archive import Archive
from os import environ as env
from os.path import join as path
from zoe.deco import Agent, Message
from zoe.models.users import Users

gettext.install("archivist")

with open(path(env["ZOE_HOME"], "etc", "archivist.conf"), "r") as f:
    DB_PATH = f.readline().strip()

LOCALEDIR = path(env["ZOE_HOME"], "locale")
ZOE_LOCALE = env["ZOE_LOCALE"] or "en"


@Agent(name="archivist")
class Archivist:

    @Message(tags=["add-section"])
    def add_card_to_section(self, parser):
        """ Adds a card to the given section.

            cid*   - card id
            sname* - card title
            sender - sender of the message
            src    - channel by which the message was delivered
        """
        cid, sname, sender, src = self.multiparse(
            parser, ['cid', 'sname', 'sender', 'src'])

        self.set_locale(sender)

        if not self.has_permissions(sender):
            self.logger.info("%s cannot modify section relations" % sender)
            return self.feedback(_("You don't have permissions to do that"),
                sender, src)

        try:
            ar = self.connect()
            result = ar.add_card_to_section(cid=int(cid), sname=sname)

        except Exception as e:
            return self.feedback("Error: " + str(e), sender, src)

        if result:
            return self.feedback(
                _("Added card to section '%s'") % sname, sender, src)

        return self.feedback(
            _("Failed to add card to section '%s'") % sname, sender, src)

    @Message(tags=["card-list"])
    def card_list(self, parser):
        """ List all the cards in the archive.

            sender* - sender of the message
            src*    - channel by which the message was delivered
        """
        sender, src = self.multiparse(parser, ['sender', 'src'])

        self.set_locale(sender)

        msg = ""

        try:
            ar = self.connect()
            cards = ar.cards()

            for card in cards:
                msg += "- [%d] %s: %s\n" % (
                    card.id, card.title, card.desc)

        except Exception as e:
            return self.feedback("Error: " + str(e), sender, src)

        if not msg:
            msg = _("No cards found")

        return self.feedback(msg, sender, src)

    @Message(tags=["card-sections"])
    def card_sections(self, parser):
        """ Show all the sections a card appears in.

            cid*   - card id
            sender - sender of the message
            src    - channel by which the message was delivered
        """
        cid, sender, src = self.multiparse(
            parser, ['cid', 'sender', 'src'])

        self.set_locale(sender)

        msg = ""

        try:
            ar = self.connect()
            card = ar.get_card(cid=int(cid))

            if not card:
                return self.feedback(_("Card %s does not exist") % cid,
                    sender, src)

            sections = card.sections()
            for section in sections:
                msg += "- %s\n" % section.name

        except Exception as e:
            return self.feedback("Error: " + str(e), sender, src)

        if not msg:
            msg = _("No sections found")

        return self.feedback(msg, sender, src)

    @Message(tags=["delete-card"])
    def delete_card(self, parser):
        """ Remove a card from the archive.

            cid*   - card id
            sender - sender of the message
            src    - channel by which the message was delivered
        """
        cid, sender, src = self.multiparse(
            parser, ['cid', 'sender', 'src'])

        self.set_locale(sender)

        if not self.has_permissions(sender):
            self.logger.info("%s cannot remove cards" % sender)
            return self.feedback(_("You don't have permissions to do that"),
                sender, src)

        try:
            ar = self.connect()
            result = ar.delete_card(cid=int(cid))

        except Exception as e:
            return self.feedback("Error: " + str(e), sender, src)

        if result:
            return self.feedback(
                _("Removed card '%s'") % cid, sender, src)

        return self.feedback(_("Failed to remove card '%s'") % cid, sender, src)

    @Message(tags=["delete-section"])
    def delete_section(self, parser):
        """ Remove a section from the archive.

            name*  - section name
            sender - sender of the message
            src    - channel by which the message was delivered
        """
        name, sender, src = self.multiparse(
            parser, ['name', 'sender', 'src'])

        self.set_locale(sender)

        if not self.has_permissions(sender):
            self.logger.info("%s cannot remove cards" % sender)
            return self.feedback(_("You don't have permissions to do that"),
                sender, src)

        try:
            ar = self.connect()
            result = ar.delete_section(name=name)

        except Exception as e:
            return self.feedback("Error: " + str(e), sender, src)

        if result:
            return self.feedback(
                _("Removed section '%s'") % name, sender, src)

        return self.feedback(_("Failed to remove '%s'") % name, sender, src)

    @Message(tags=["get-cards"])
    def get_cards(self, parser):
        """ Obtain information from a list of cards and send it to the user
            through the chosen communication method.

            cids*   - list of card ids
            method* - delivery method
            sender  - sender of the message
            src     - channel by which the message was delivered
            to      - optional recipient of the cards
        """
        cids, method, sender, src, to = self.multiparse(
            parser, ['cids', 'method', 'sender', 'src', 'to'])

        self.set_locale(sender)

        try:
            ar = self.connect()

            msg = ""

            for cid in cids.split(" "):
                card = ar.get_card(cid=int(cid))

                if card:
                    msg += "%s\n\n" % self.build_card_msg(card)
                    continue

                msg += _("Card %s not found") % cid
                msg += "\n"

        except Exception as e:
            return self.feedback("Error: " + str(e), sender, src)

        if not to:
            to = sender

        if method == "mail":
            return (
                self.feedback(_("Sending..."), sender, src),
                self.feedback(msg, to, subject="Archivist")
            )

        return self.feedback(msg, to, src)

    @Message(tags=["get-section"])
    def get_section(self, parser):
        """ Obtain information from the cards contained in a given section.

            sname*  - section name
            method* - delivery method
            sender  - sender of the message
            src     - channel by which the message was delivered
            to      - optional recipient of the cards
        """
        sname, method, sender, src, to = self.multiparse(
            parser, ['sname', 'method', 'sender', 'src', 'to'])

        self.set_locale(sender)

        try:
            ar = self.connect()
            section = ar.get_section(name=sname)

            if not section:
                return self.feedback(
                    _("Section %s does not exist") % sname, sender, src)

            cards = section.cards()

            msg = ""
            for card in cards:
                msg += "%s\n\n" % self.build_card_msg(card)

        except Exception as e:
            return self.feedback("Error: " + str(e), sender, src)

        if not to:
            to = sender

        if method == "mail":
            return (
                self.feedback(_("Sending..."), sender, src),
                self.feedback(msg, to, subject="Archivist")
            )

        return self.feedback(msg, to, src)

    @Message(tags=["modify-card"])
    def modify_card(self, parser):
        """ Modify an existing card.

            cid*    - card id
            title   - unique title of the card
            desc    - description of the card
            content - main content of the card
            tags    - space separated tags
            sender  - sender of the message
            src     - channel by which the message was delivered
        """
        cid, title, desc, content, tags, sender, src= self.multiparse(
            parser, ['cid', 'title', 'desc', 'content', 'tags',
                'sender', 'src'])

        self.set_locale(sender)

        if not self.has_permissions(sender):
            self.logger.info("%s cannot create sections" % sender)
            return self.feedback(_("You don't have permissions to do that"),
                sender, src)

        try:
            ar = self.connect()

            # Obtain current information
            card = ar.get_card(cid=int(cid))

            newcard = ar.modify_card(
                cid=int(cid),
                title=title or card.title,
                desc=desc or card.desc,
                content=content.replace('_NL_', '\n'),
                tags=tags or card.tags,
                author=sender or "UNKNOWN"
            )

        except Exception as e:
            return self.feedback("Error: " + str(e), sender, src)

        if newcard:
            return self.feedback(_("Modified card '%s'") % cid, sender, src)

        return self.feedback(_("Failed to modify card '%s'") % cid,
            sender, src)

    @Message(tags=["new-card"])
    def new_card(self, parser):
        """ Add a new card to the archive. Cards are added by sending
            an email with a specific format.

            Timestamp is obtained automatically.

            title*   - unique title of the card
            desc*    - description of the card
            content* - main content of the card
            tags*    - space separated tags
            sender   - sender of the message
        """
        title, desc, content, tags, sender = self.multiparse(
            parser, ['title', 'desc', 'content', 'tags', 'sender'])

        self.set_locale(sender)

        dst = None
        subject = None
        if sender:
            dst = Users().subject(sender).get("preferred", "mail")

            if dst == "mail":
                subject = "Archivist"

        if not self.has_permissions(sender):
            self.logger.info("%s cannot add cards" % sender)
            return self.feedback(_("You don't have permissions to do that"),
                sender, dst, subject=subject)

        try:
            ar = self.connect()

            newcard = ar.new_card(
                title,
                desc,
                content.replace('_NL_', '\n'),
                tags,
                sender or "UNKNOWN"
            )

        except Exception as e:
            return self.feedback("Error: " + str(e), sender, dst,
                subject=subject)

        if newcard:
            return self.feedback(
                _("Created new card [%d]") % newcard.id, sender, dst,
                subject=subject)

        return self.feedback(_("Failed to create card"), sender, dst,
            subject=subject)

    @Message(tags=["new-section"])
    def new_section(self, parser):
        """ Create a new section in the archive.

            name*  - unique name for the section
            sender - sender of the message
            src    - channel by which the message was delivered
        """
        name, sender, src = self.multiparse(
            parser, ['name', 'sender', 'src'])

        self.set_locale(sender)

        if not self.has_permissions(sender):
            self.logger.info("%s cannot create sections" % sender)
            return self.feedback(_("You don't have permissions to do that"),
                sender, src)

        try:
            ar = self.connect()
            result = ar.new_section(name)

        except Exception as e:
            return self.feedback("Error: " + str(e), sender, src)

        if result:
            return self.feedback(_("Created section '%s'") % name,
                sender, src)

        return self.feedback(_("Could not create section '%s'") % name,
            sender, src)

    @Message(tags=["remove-section"])
    def remove_card_from_section(self, parser):
        """ Remove a card from a given section.

            cid*   - card id
            sname* - section name
            sender - sender of the message
            src    - channel by which the message was delivered
        """
        cid, sname, sender, src = self.multiparse(
            parser, ['cid', 'sname', 'sender', 'src'])

        self.set_locale(sender)

        if not self.has_permissions(sender):
            self.logger.info("%s cannot modify section relations" % sender)
            return self.feedback(_("You don't have permissions to do that"),
                sender, src)

        try:
            ar = self.connect()
            result = ar.remove_card_from_section(cid=int(cid), sname=sname)

        except Exception as e:
            return self.feedback("Error: " + str(e), sender, src)

        if result:
            return self.feedback(
                _("Removed card"), sender, src)

        return self.feedback(
            _("Could not remove card"), sender, src)

    @Message(tags=["rename-section"])
    def rename_section(self, parser):
        """ Rename a section of the archive.

            name*    - original section name
            newname* - new section name
            sender   - sender of the message
            src      - channel by which the message was delivered
        """
        name, newname, sender, src = self.multiparse(
            parser, ['name', 'newname', 'sender', 'src'])

        self.set_locale(sender)

        if not self.has_permissions(sender):
            self.logger.info("%s cannot modify section relations" % sender)
            return self.feedback(_("You don't have permissions to do that"),
                sender, src)

        try:
            ar = self.connect()
            result = ar.rename_section(newname, oldname=name)

        except Exception as e:
            return self.feedback("Error: " + str(e), sender, src)

        if result:
            return self.feedback(
                _("Renamed section"), sender, src)

        return self.feedback(
            _("Could not rename"), sender, src)

    @Message(tags=["search"])
    def search(self, parser):
        """ Traverse a section and find cards relevant to the query.

            query*  - search query
            sender* - sender of the message
            section - narrow search results to the specified section
            src     - channel by which the message was delivered
        """
        query, sender, section, src = self.multiparse(
            parser, ['query', 'sender', 'section', 'src'])

        self.set_locale(sender)

        if not query:
            return self.feedback(_("No query specified"), sender, src)

        result = ""

        try:
            ar = self.connect()
            cards = ar.search(query, sname=section)

            for card in cards:
                result += "- [%d] %s: %s\n" % (
                    card.id, card.title, card.desc)

        except Exception as e:
            return self.feedback("Error: " + str(e), sender, src)

        if not result:
            result = _("No cards found")

        return self.feedback(result, sender, src)

    @Message(tags=["section-list"])
    def section_list(self, parser):
        """ Show all the sections in the archive.

            sender* - sender of the message
            src*    - channel by which the message was delivered
        """
        sender, src = self.multiparse(parser, ['sender', 'src'])

        self.set_locale(sender)

        try:
            ar = self.connect()
            sections = ar.sections()

            msg = ""
            for section in sections:
                msg += "- %s\n" % section.name

        except Exception as e:
            return self.feedback("Error: " + str(e), sender, src)

        if not msg:
            msg = _("No sections found")

        return self.feedback(msg, sender, src)

    @Message(tags=["section-cards"])
    def section_cards(self, parser):
        """ Show all the cards present in a section.

            name*   - section name
            sender* - sender of the message
            src*    - channel by which the message was delivered
        """
        name, sender, src = self.multiparse(
            parser, ['name', 'sender', 'src'])

        self.set_locale(sender)

        msg = ""

        try:
            ar = self.connect()
            section = ar.get_section(name=name)

            if not section:
                return self.feedback(
                    _("Section %s does not exist") % name, sender, src)

            cards = section.cards()
            for card in cards:
                msg += "- [%d] %s: %s\n" % (
                    card.id, card.title, card.desc)

        except Exception as e:
            return self.feedback("Error: " + str(e), sender, src)

        if not msg:
            msg = _("No cards found")

        return self.feedback(msg, sender, src)

    def build_card_msg(self, card):
        """ Format the card's information for easier reading. """
        msg = "\n--------------------\n"
        msg += "[%d] %s" % (card.id, card.title)
        msg += "\n--------------------\n\n"
        msg += "%s\n\n" % card.desc
        msg += "Last modified <%s> - %s\n" % (
            str(card.modified), card.modified_by)
        msg += "Tags: %s\n\n" % card.tags
        msg += card.content

        return msg

    def connect(self):
        return Archive(db_type='sqlite', db_name=DB_PATH)

    def feedback(self, msg, user, dst=None, subject=None, att=None):
        """ Send a message or mail to a given user.

            msg     - message text or attachment
            user    - user to send the feedback to
            subject - if using mail feedback, subject for the mail
            dst     - destination of the message: 'jabber' or 'tg'
            att     - mail attachment
        """
        if not user:
            return

        to_send = {
            "dst": "relay",
            "to": user
        }

        if not subject:
            to_send["relayto"] = dst
            to_send["msg"] = msg

        else:
            to_send["relayto"] = "mail"
            if att:
                to_send["att"] = att.str()
            to_send["txt"] = msg or ""
            to_send["subject"] = subject

        return zoe.MessageBuilder(to_send)

    def has_permissions(self, user):
        """ Check if the user has permissions necessary to interact with the
            agent manager (belongs to group 'archivists').
        """
        # No user, manual commands from terminal
        if not user or user in Users().membersof("archivists"):
            return True

        return False

    def multiparse(self, parser, keys):
        """ Obtain several elements from the parser, identified by the
            list of keys.

            Values are returned in the order specified by the keys list.
        """
        result = []
        for k in keys:
            result.append(parser.get(k))

        return result

    def set_locale(self, user):
        """ Set the locale for messages based on the locale of the sender.

            If no locale is povided, Zoe's default locale is used or
            English (en) is used by default.
        """
        if not user:
            locale = ZOE_LOCALE

        else:
            conf = Users().subject(user)
            locale = conf.get("locale", ZOE_LOCALE)

        lang = gettext.translation("archivist", localedir=LOCALEDIR,
            languages=[locale,])

        lang.install()

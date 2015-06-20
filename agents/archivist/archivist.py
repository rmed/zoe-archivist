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

import gettext
import os
import re
import sqlite3
import zoe
from datetime import datetime
from os import environ as env
from os.path import join as path
from zoe.deco import *
from zoe.models.users import Users

gettext.install("archivist")

MSG_NO_PERM = _("You don't have permissions to do that")

DB_PATH = path(env["ZOE_HOME"], "etc", "archivist", "archive.db")
LOCALEDIR = path(env["ZOE_HOME"], "locale")
USERS = Users()

# Mind table names and prevent sql injection
Q_CREATE = """create table %s (
        id integer primary key, title text unique, desc text, content text,
        tags text, modified timestamp, modified_by text)"""
Q_DELETE = "delete from %s where id = ?"
Q_DROP = "drop table %s"
Q_EXISTS = "select name from sqlite_master where type='table' and name='?'"
Q_INSERT = "insert into %s values(NULL, ?, ?, ?, ?, ?, ?)"

REGEX_TABLE = re.compile("\A[a-zA-Z0-9_]+\Z")

@Agent(name="archivist")
class Archivist:

    @Message(tags=["new", "card"])
    def add_card(self, section, title, desc, content, tags, sender=None):
        """ Add a new card to the given section.

            Timestamp is obtained automatically.
        """
        if not self.has_permissions(sender):
            print(MSG_NO_PERM)
            return self.feedback(MSG_NO_PERM, sender)

        if not REGEX_TABLE.match(section):
            msg = _("'%s' is not a valid section name") % section
            return self.feedback(msg, sender)

        try:
            conn, cur = self.connect()

            tstamp = datetime.now()
            user = sender or "UNKNOWN"

            cur.execute(Q_INSERT % section, (
                title, desc, content, tags, tstamp, user))

            conn.commit()

            cur.close()
            conn.close()

        except sqlite3.OperationalError as e:
            return self.feedback(e, sender)

        except sqlite3.IntegrityError as e:
            return self.feedback(e, sender)

        msg = _("Added card '%s' to section '%s'") % (title, section)
        return self.feedback(msg, sender)

    @Message(tags=["backup"])
    def backup_archive(self, sender=None, dst_user=None):
        """ Create a SQL dump file of the archive and send it to
            the provided mail or the sender's mail.
        """
        if not self.has_permissions(sender):
            print(MSG_NO_PERM)
            return self.feedback(MSG_NO_PERM, sender)

        to = dst_user or sender or None
        if not to:
            return

        conn, cur = self.connect()
        tstamp = datetime.now().strftime("%Y%m%d%H%M%S")

        fname = path("/", "tmp", "archive_%s.dump" % tstamp)

        with open(fname, "w") as dump:
            for line in conn.iterdump():
                dump.write("%s\n" % line)

        with open(fname, "rb") as dump:
            data = dump.read()

        b64 = base64.standard_b64encode(data).decode("utf-8")
        attachment = zoe.Attachment(
            b64, "application/octet-stream", "archive_%s.dump" % tstamp)

        subject = _("Archive dump - %s") % tstamp
        msg = _("Sending dump to %s") % to

        # Send dump to user
        return (
            self.feedback(msg, to),
            self.feedback(attachment, to, subject)
        )

    @Message(tags=["new", "section"])
    def create_section(self, name, sender=None):
        """ Create a new table in the database if it does not exist.

            The name of the table is dynamic, hence it must be checked
            beforehand to prevent injections.
        """
        if not self.has_permissions(sender):
            print(MSG_NO_PERM)
            return self.feedback(MSG_NO_PERM, sender)

        if not REGEX_TABLE.match(name):
            msg = _("'%s' is not a valid section name") % name
            return self.feedback(msg, sender)

        try:
            conn, cur = self.connect()
            cur.execute(Q_CREATE % name)

            cur.close()
            conn.close()

        except sqlite3.OperationalError as e:
            return self.feedback(e, sender)

        msg = _("Created section '%s'") % name
        return self.feedback(msg, sender)

    def remove_card(self, section, cid, sender=None):
        pass

    def get_card(self, section, cid, sender=None):
        pass

    def get_cards(self, section, sender=None):
        pass

    def list_sections(self, sender=None):
        pass

    def remove_section(self, section, sender=None):
        pass

    def search(self, section, query, sender=None):
        pass

    def check_permissions(self, user):
        return False

    def connect(self):
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()

        return conn, cur

    def feedback(self, data, user, subject=None):
        """ Send a message or mail to a given user.

            data    - message text or attachment
            user    - user to send the feedback to
            subject - if using mail feedback, subject for the mail
        """
        if not user:
            return

        to_send = {
            "dst": "relay",
            "tag": "relay",
            "to": user
        }

        if not subject:
            to_send["relayto"] = "jabber"
            to_send["msg"] = data

        else:
            to_send["relayto"] = "mail"
            to_send["att"] = data.str()
            to_send["subject"] = subject

        return zoe.MessageBuilder(to_send)

    def has_permissions(self, user):
        """ Check if the user has permissions necessary to interact with the
            agent manager (belongs to group 'archivists').
        """
        # No user, manual commands from terminal
        if not user or user in USERS.membersof("archivists"):
            return True

        return False
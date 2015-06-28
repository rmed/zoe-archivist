#!/usr/bin/env perl
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

use Getopt::Long qw(:config pass_through);

my $get;
my $run;
my $backup_me;
my $backup_user;
my $create_sec;
my $get_cards;
my $get_cards_me;
my $get_cards_snd;
my $list_cards;
my $list_sec;
my $remove_card;
my $remove_sec;
my $search;

my $sender;
my @strings;
my @integers;
my $mail;

GetOptions("get"                   => \$get,
           "run"                   => \$run,
           "msg-sender-uniqueid=s" => \$sender,
           "bm"                    => \$backup_me,
           "bu"                    => \$backup_user,
           "cs"                    => \$create_sec,
           "gc"                    => \$get_cards,
           "gcm"                   => \$get_cards_me,
           "gcs"                   => \$get_cards_snd,
           "lc"                    => \$list_cards,
           "ls"                    => \$list_sec,
           "rc"                    => \$remove_card,
           "rs"                    => \$remove_sec,
           "s"                     => \$search,
           "string=s"              => \@strings,
           "integer=i"             => \@integers,
           "mail=s"                => \$mail);

if ($get) {
  &get;
} elsif ($run and $backup_me) {
  &backup_me;
} elsif ($run and $backup_user) {
  &backup_user;
} elsif ($run and $create_sec) {
  &create_sec;
} elsif ($run and $get_cards) {
  &get_cards;
} elsif ($run and $get_cards_me) {
  &get_cards_me;
} elsif ($run and $get_cards_snd) {
  &get_cards_snd;
} elsif ($run and $list_cards) {
  &list_cards;
} elsif ($run and $list_sec) {
  &list_sec;
} elsif ($run and $remove_card) {
  &remove_card;
} elsif ($run and $remove_sec) {
  &remove_sec;
} elsif ($run and $search) {
  &search;
}

#
# Commands in the script
#
sub get {
  print("--bm send me archive backup\n");
  print("--bu send archive backup to <mail>\n");
  print("--cs create /new section <string>\n");
  print("--gc show /me card/cards <integer> /from <string>\n");
  print("--gcm send me card/cards <integer> /from <string>\n");
  print("--gcs send card/cards <integer> /from <string> to <user>\n");
  print("--lc list cards /in <string>\n");
  print("--ls list sections\n");
  print("--rc remove card <integer> /from <string>\n");
  print("--rs remove section <string>\n");
  print("--s search /for <string> /in <string>\n");

  print("--bm mándame backup /del archivo\n");
  print("--bu manda backup /del archivo a <mail>\n");
  print("--cs crea /nueva sección <string>\n");
  print("--gc muestra/muéstrame tarjeta/tarjetas <integer> /de <string>\n");
  print("--gcm mándame tarjeta/tarjetas <integer> /de <string>\n");
  print("--gcs manda tarjeta/tarjetas <integer> /de <string> a <user>\n");
  print("--lc lista /de tarjetas /en <string>\n");
  print("--ls lista /de secciones\n");
  print("--rc elimina tarjeta <integer> /de <string>\n");
  print("--rs elimina sección <string>\n");
  print("--s busca <string> /en <string>\n");
}

#
# Create a dump of the database and send it to the sender
#
sub backup_me {
  print("message dst=archivist&tag=backup&sender=$sender\n");
}

#
# Create a dump of the database and send it to the specified user
#
sub backup_user {
  print("message dst=archivist&tag=backup&to=$mail&sender=$sender\n");
}

#
# Create a new section/table
#
sub create_sec {
  print("message dst=archivist&tag=new-section&name=$strings[0]&sender=$sender\n");
}

#
# Get specified cards and send them to specified user by jabber
#
sub get_cards {
  print("message dst=archivist&tag=get-cards&section=$strings[0]&idcs=@integers&method=jabber&sender=$sender\n");
}

#
# Get specified cards and send them to sender by mail
#
sub get_cards_me {
  print("message dst=archivist&tag=get-cards&section=$strings[0]&idcs=@integers&method=mail&sender=$sender\n");
}

#
# Get specified cards and send them to specified user by mail
#
sub get_cards_snd {
  print("message dst=archivist&tag=get-cards&section=$strings[0]&idcs=@integers&method=mail&to=$mail&sender=$sender\n");
}

#
# List all cards in the specified section
#
sub list_cards {
  print("message dst=archivist&tag=list-cards&section=$strings[0]&sender=$sender\n");
}

#
# List all sections/tables in the archive
#
sub list_sec {
  print("message dst=archivist&tag=list-sections&sender=$sender\n");
}

#
# Remove a card from a given section
#
sub remove_card {
  print("message dst=archivist&tag=remove-card&section=$strings[0]&idc=$integers[0]&sender=$sender\n");
}

#
# Remove a section from the archive
#
sub remove_sec {
  print("message dst=archivist&tag=remove-section&section=$strings[0]&sender=$sender\n");
}

#
# Search in the given section for relevant cards
#
sub search {
  print("message dst=archivist&tag=search&query=$strings[0]&section=$strings[1]&sender=$sender\n");
}

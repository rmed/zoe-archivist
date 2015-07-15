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
my $add_section;
my $card_list;
my $card_sections;
my $delete_card;
my $delete_sec;
my $get_cards;
my $get_cards_me;
my $get_cards_snd;
my $new_section;
my $remove_section;
my $rename_section;
my $search;
my $search_section;
my $section_list;
my $section_cards;

my $sender;
my @strings;
my @integers;
my $mail;

GetOptions("get"                   => \$get,
           "run"                   => \$run,
           "msg-sender-uniqueid=s" => \$sender,
           "as"                    => \$add_section,
           "cl"                    => \$card_list,
           "cs"                    => \$card_sections,
           "dc"                    => \$delete_card,
           "ds"                    => \$delete_sec,
           "gc"                    => \$get_cards,
           "gcm"                   => \$get_cards_me,
           "gcs"                   => \$get_cards_snd,
           "ns"                    => \$new_section,
           "rs"                    => \$remove_section,
           "rns"                   => \$rename_section,
           "s"                     => \$search,
           "ss"                    => \$search_section,
           "sl"                    => \$section_list,
           "sc"                    => \$section_cards,
           "string=s"              => \@strings,
           "integer=i"             => \@integers,
           "mail=s"                => \$mail);

if ($get) {
  &get;
} elsif ($run and $add_section) {
  &add_section;
} elsif ($run and $card_list) {
  &card_list;
} elsif ($run and $card_sections) {
  &card_sections;
} elsif ($run and $delete_card) {
  &delete_card;
} elsif ($run and $delete_sec) {
  &delete_section;
} elsif ($run and $get_cards) {
  &get_cards;
} elsif ($run and $get_cards_me) {
  &get_cards_me;
} elsif ($run and $get_cards_snd) {
  &get_cards_snd;
} elsif ($run and $new_card) {
  &new_card;
} elsif ($run and $new_section) {
  &new_section;
} elsif ($run and $remove_section) {
  &remove_section;
} elsif ($run and $rename_section) {
  &rename_section;
} elsif ($run and $search) {
  &search;
} elsif ($run and $search_section) {
  &search_section;
} elsif ($run and $section_list) {
  &section_list;
} elsif ($run and $section_cards) {
  &section_cards;
}

#
# Commands in the script
#
sub get {
  print("--as add /card <integer> /to <string>\n");
  print("--cl show /me /all cards\n");
  print("--cs show /me sections /of /card <integer>\n");
  print("--dc delete /card <integer>\n");
  print("--ds delete /section <string>\n");
  print("--gc show /me card/cards <integer>\n");
  print("--gcm send me card/cards <integer>\n");
  print("--gcs send card/cards <integer> /to <user>\n");
  print("--ns create /new section <string>\n");
  print("--rs remove /card <integer> /from <string>\n");
  print("--rns rename /section <string> to <string>\n");
  print("--s search /for <string>\n");
  print("--ss search /for <string> /in <string>\n");
  print("--sl show /me /all sections\n");
  print("--sc show /me cards /of /section <string>\n");

  print("--as añade /la /tarjeta <integer> /a <string>\n");
  print("--cl dame /todas /las tarjetas\n");
  print("--cs dame /las secciones /de /la /tarjeta <integer>\n");
  print("--dc elimina /tarjeta <integer>\n");
  print("--ds elimina /sección <string>\n");
  print("--gc dame tarjeta/tarjetas <integer>\n");
  print("--gcm envíame tarjeta/tarjetas <integer>\n");
  print("--gcs envía tarjeta/tarjetas <integer> /a <user>\n");
  print("--ns crea /nueva sección <string>\n");
  print("--rs quita /la /tarjeta <integer> /de <string>\n");
  print("--rns renombra /la /sección <string> a <string>\n");
  print("--s busca <string>\n");
  print("--ss busca <string> en <string>\n");
  print("--sl dame /todas /las secciones\n");
  print("--sc dame /las tarjetas /de /la /sección <string>\n");
}

#
# Create a card-section relation
#
sub add_section {
  print("message dst=archivist&tag=add-section&cid=$integers[0]&sname=$strings[0]&sender=$sender\n");
}

#
# List all cards in the archive
#
sub card_list {
  print("message dst=archivist&tag=card-list&sender=$sender\n");
}

#
# List all sections a card appears in
#
sub card_sections {
  print("message dst=archivist&tag=card-sections&cid=$integers[0]&sender=$sender\n");
}

#
# Remove a card from the archive
#
sub delete_card {
  print("message dst=archivist&tag=delete-card&cid=$integers[0]&sender=$sender\n");
}

#
# Remove a section from the archive
#
sub delete_section {
  print("message dst=archivist&tag=delete-section&name=$strings[0]&sender=$sender\n");
}

#
# Get specified cards and send them to specified user by jabber
#
sub get_cards {
  print("message dst=archivist&tag=get-cards&cids=@integers&method=jabber&sender=$sender\n");
}

#
# Get specified cards and send them to sender by mail
#
sub get_cards_me {
  print("message dst=archivist&tag=get-cards&cids=@integers&method=mail&sender=$sender\n");
}

#
# Get specified cards and send them to specified user by mail
#
sub get_cards_snd {
  print("message dst=archivist&tag=get-cards&cids=@integers&method=mail&to=$mail&sender=$sender\n");
}

#
# Create a new section
#
sub new_section {
  print("message dst=archivist&tag=new-section&name=$strings[0]&sender=$sender\n");
}

#
# Remove a card-section relation
#
sub remove_section {
  print("message dst=archivist&tag=remove-section&cid=$integers[0]&sname=$strings[0]&sender=$sender\n");
}

#
# Rename a section
#
sub rename_section {
  print("message dst=archivist&tag=rename-section&name=$strings[0]&newname=$strings[1]&sender=$sender\n");
}

#
# Search in the archive for relevant cards
#
sub search {
  print("message dst=archivist&tag=search&query=$strings[0]&sender=$sender\n");
}

#
# Search in the given section of the archive for relevant cards
#
sub search_section {
  print("message dst=archivist&tag=search&query=$strings[0]&section=$strings[1]&sender=$sender\n");
}

#
# List all sections in the archive
#
sub section_list {
  print("message dst=archivist&tag=section-list&sender=$sender\n");
}

#
# List all cards in a given section
#
sub section_cards {
  print("message dst=archivist&tag=section-cards&name=$strings[0]&sender=$sender\n");
}

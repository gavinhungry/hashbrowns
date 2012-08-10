#!/usr/bin/env python2
#
# Name: hashbrowns
# Auth: Gavin Lloyd <gavinhungry@gmail.com>
# Date: 31 Jul 2011 (last updated 10 Aug 2012)
# Desc: Provides hashes for a file, intended for context menu
#

import os, sys
import pygtk, gtk
import hashlib
import pango
import re


class Hashbrowns:

  def __init__(self, filename):
    self.hash_algs = ['md5', 'sha1', 'sha256', 'sha512', 'whirlpool']
    self.filename = filename

    # attempt to open the file for reading
    try:
      self.fd = open(self.filename, 'rb')
    except IOError:
      error = 'File is not readable: ' + self.filename;
      dlg = gtk.MessageDialog(type=gtk.MESSAGE_ERROR,
                              buttons=gtk.BUTTONS_OK, 
                              message_format=error)
      dlg.run()
      sys.exit(error)

    # with the file opened, setup the window
    window = gtk.Window(gtk.WINDOW_TOPLEVEL)
    window.set_title('Hashbrowns: ' + os.path.basename(self.filename))
    window.connect('key-press-event', lambda w,e:
                   e.keyval == gtk.keysyms.Escape and gtk.main_quit())
    window.connect('destroy', self.quit)

    window.set_position(gtk.WIN_POS_CENTER)
    window.set_border_width(5)
    window.set_resizable(False)

    vbox  = gtk.VBox(homogeneous=False, spacing=5)
    hboxt = gtk.HBox(homogeneous=False, spacing=5)
    hboxh = gtk.HBox(homogeneous=False, spacing=5)

    self.hash_box = gtk.Entry()
    self.hash_box.modify_font(pango.FontDescription('monospace'))
    self.hash_box.set_editable(False)
    self.hash_box.set_width_chars(48)
    hboxt.add(self.hash_box)      

    # create button for each hash
    for alg in sorted(self.hash_algs):
      try:
        hashlib.new(alg)
      except ValueError:
        sys.stderr.write(alg + ': not supported, skipping\n')
      else:
        # uppercase label for algorithms that end with a number, eg: SHA512
        # capitalized labels for the rest, eg: Whirlpool
        label = alg.upper() if re.search("\d$", alg) else alg.capitalize()
        button = gtk.Button(label)

        button.connect('clicked', self.get_hash, alg)
        hboxh.add(button)

    button = gtk.Button('Copy to Clipboard')
    button.connect('clicked', self.copy)
    hboxh.add(button)

    vbox.add(hboxt)
    vbox.add(hboxh)

    window.add(vbox)
    window.show_all()
    gtk.main()


  # hash file and place output in text box
  def get_hash(self, button, alg):
    m = hashlib.new(alg)

    for data in iter(lambda: self.fd.read(128 * m.block_size), ''):
      m.update(data)

    self.fd.seek(0)
    self.hash = m.hexdigest()
    self.hash_box.set_text(self.hash)


  # copy to clipboard
  def copy(self, button):
    if (len(self.hash) > 0):
      clipboard.set_text(self.hash)
      clipboard.store()


  def quit(self, window):
    self.fd.close()
    gtk.main_quit()


if __name__ == '__main__':
  clipboard = gtk.clipboard_get()

  if len(sys.argv) != 2:
    sys.exit('usage: ' + sys.argv[0] + ' FILE')

  hb = Hashbrowns(sys.argv[1])

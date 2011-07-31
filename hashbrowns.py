#!/usr/bin/env python2
#
# Name: hashbrowns
# Auth: Gavin Lloyd <gavinhungry@gmail.com>
# Date: 31 Jul 2011
# Desc: Provides a few hashes for a file, intended for use in a context menu
#

import os, sys
import pygtk, gtk
import hashlib
import pango

HASHES = {}
HASHES['MD5'] = 'md5'
HASHES['SHA1'] = 'sha1'
HASHES['SHA256'] = 'sha256'
HASHES['SHA512'] = 'sha512'
HASHES['Whirlpool'] = 'whirlpool'


def hashbrowns(file):

  window = gtk.Window(gtk.WINDOW_TOPLEVEL)

  window.set_title('Hashbrowns: ' + os.path.basename(file))
  window.connect('key-press-event', lambda w,e: e.keyval == gtk.keysyms.Escape and gtk.main_quit())
  window.connect('destroy', gtk.main_quit)
  window.set_position(gtk.WIN_POS_CENTER)
  window.set_border_width(5)
  window.set_resizable(False)
  window.set_property('skip-taskbar-hint', True)

  vbox = gtk.VBox(homogeneous=False, spacing=5)
  hboxt = gtk.HBox(homogeneous=False, spacing=5)
  hboxh = gtk.HBox(homogeneous=False, spacing=5)

  hashBox = gtk.Entry()
  hashBox.modify_font(pango.FontDescription('monospace'))
  hashBox.set_editable(False)
  hashBox.set_width_chars(48)
  hashBox.set_text('')

  hboxt.add(hashBox)

  for hashName in sorted(HASHES):
    try:
      hashlib.new(HASHES[hashName])
    except ValueError:
      sys.stderr.write(HASHES[hashName] + ': not supported, skipping\n')
    else:
      button = gtk.Button(hashName)
      button.connect('clicked', checksum, file, HASHES[hashName], hashBox)
      hboxh.add(button)

  vbox.add(hboxt)
  vbox.add(hboxh)

  window.add(vbox)
  window.show_all()
  gtk.main()



def checksum(button, file, hash, hashBox):

  try:
    fd = open(file, 'rb')
  except IOError:
    hashBox.set_text('Can\'t open file')
    return

  m = hashlib.new(hash)

  for data in iter(lambda: fd.read(128 * m.block_size), ''):
    m.update(data)

  hashBox.set_text(m.hexdigest())
  fd.close()



if __name__ == '__main__':
  if len(sys.argv) != 2:
    sys.exit('usage: ' + sys.argv[0] + ' FILE')

  file = sys.argv[1]
  hashbrowns(file)


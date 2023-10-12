#!/usr/bin/env python
#
# hashbrowns: Provides cryptographic hashes with a minimal UI
# https://github.com/gavinhungry/hashbrowns

import gi
import hashlib
import os
import re
import signal
import sys

import warnings
warnings.filterwarnings('ignore', category=DeprecationWarning)

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, Pango

class Hashbrowns:
  def getHasher(self, alg):
    try:
      return getattr(hashlib, alg)()
    except:
      return hashlib.new(alg)

  def __init__(self, filename):
    self.hash_algs = ['md5', 'sha1', 'sha256', 'sha512', 'sha3_256', 'sha3_512']
    self.filename = filename
    self.key_pressed = False

    # attempt to open the file for reading
    try:
      self.fd = open(self.filename, 'rb')
    except IOError:
      text = 'File is not readable'
      secondary_text = self.filename
      dialog = Gtk.MessageDialog(message_type=Gtk.MessageType.ERROR,
                              buttons=Gtk.ButtonsType.OK,
                              text=text,
                              secondary_text=secondary_text)

      dialog.set_title('Hashbrowns')
      dialog.run()
      sys.exit(text + ': ' + secondary_text)

    # with the file opened, setup the window
    window = Gtk.Window()
    window.set_title('Hashbrowns: ' + os.path.basename(self.filename))
    window.connect('key-press-event', self.on_keypress)
    window.connect('destroy', self.quit)

    window.set_border_width(5)
    window.set_resizable(False)

    vbox = Gtk.VBox(homogeneous=False, spacing=4)

    hash_input_box = Gtk.HBox(homogeneous=False, spacing=4)
    self.hash_input = Gtk.Entry()
    self.hash_input.override_font(Pango.FontDescription('JetBrains Mono 9'))
    self.hash_input.set_width_chars(48)
    self.hash_input.set_placeholder_text('Enter comparison hash')
    self.hash_input.connect('changed', self.update_check)
    hash_input_box.add(self.hash_input)

    hash_output_box = Gtk.HBox(homogeneous=False, spacing=4)
    self.hash_output = Gtk.Entry()
    self.hash_output.override_font(Pango.FontDescription('JetBrains Mono 9'))
    self.hash_output.set_editable(False)
    self.hash_output.set_width_chars(48)
    hash_output_box.add(self.hash_output)

    # create button for each hash
    button_row_box = Gtk.HBox(homogeneous=False, spacing=4)
    for alg in self.hash_algs:
      try:
        self.getHasher(alg)
      except:
        sys.stderr.write(alg + ': not supported, skipping\n')
      else:
        # uppercase for algorithms that end with a number, eg: SHA512
        # capitalized labels for the rest, eg: Whirlpool
        label = alg.upper() if re.search("\d$", alg) else alg.capitalize()
        label = label.replace('_', '-')

        button = Gtk.Button(label=label)

        button.connect('clicked', self.update_hash, alg)
        button_row_box.add(button)

    self.copy_button = Gtk.Button()
    copy_label = Gtk.Label()
    copy_label.set_markup('<b>Copy to Clipboard</b>')
    self.copy_button.add(copy_label)

    self.copy_button.set_sensitive(False)
    self.copy_button.connect('clicked', self.copy)
    button_row_box.add(self.copy_button)

    vbox.add(hash_input_box)
    vbox.add(hash_output_box)
    vbox.add(button_row_box)

    window.add(vbox)
    window.show_all()

    _hidden = Gtk.Entry()
    vbox.add(_hidden)
    _hidden.grab_focus()

    signal.signal(signal.SIGINT, Gtk.main_quit)
    Gtk.main()

  def on_keypress(self, entry, e):
    if not self.key_pressed:
      self.key_pressed = True
      self.hash_input.grab_focus()

    if e.keyval == Gdk.KEY_Escape:
      Gtk.main_quit()

  def get_hash(self, alg):
    m = self.getHasher(alg)

    for data in iter(lambda: self.fd.read(m.block_size), ''):
      if len(data) == 0:
        break

      m.update(data)

    self.fd.seek(0)

    # Python 3.11.0
    # digest = hashlib.file_digest(fd, alg)
    # return hexdigest.hexdigest()

    return m.hexdigest()

  # hash file and place output in text box
  def update_hash(self, button, alg):
    self.hash = self.get_hash(alg)

    self.hash_output.set_text(self.hash)
    self.copy_button.set_sensitive(True)

    self.update_check(self.hash_input)

  def update_check(self, _entry):
    input_hash = self.hash_input.get_text().strip().lower()
    output_hash = self.hash_output.get_text().strip().lower()

    is_empty = len(input_hash) == 0 or len(output_hash) == 0
    is_valid = self.hash_output.get_text() == input_hash

    icon_name = 'checkmark' if is_valid else 'error'
    if is_empty:
      icon_name = ''

    self.hash_input.set_icon_from_icon_name(
      Gtk.EntryIconPosition.SECONDARY,
      icon_name
    )

  # copy to clipboard
  def copy(self, button):
    if (len(self.hash) > 0):
      clipboard.set_text(self.hash, -1)
      clipboard.store()

  def quit(self, window):
    self.fd.close()
    Gtk.main_quit()


if __name__ == '__main__':
  clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)

  if len(sys.argv) != 2:
    sys.exit('usage: ' + sys.argv[0] + ' FILE')

  hb = Hashbrowns(sys.argv[1])

# -*- coding: utf-8 -*-

"""
gui.py: This is the graphical user interface. It displays the frequency
lists, allows selection by part-of-speech (pos) and sub-pos. Clicking
on a word opens a window displaying sentences containing that word.
"""

import gtk
import gobject

import config

""" GTK View for having a list with scroll bars that can dynamically
load new entries. Has signals for clicking on an entry and clicking
the row to extend the view."""
class ExtendedView(gtk.ScrolledWindow):
  __gsignals__ = {
          'row-selected' : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE,
           (int,)),
          'row-extended' : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE,
           ())
  }

  def __init__(self, *types):
    gtk.ScrolledWindow.__init__(self)
    # internal list store
    self.store = gtk.ListStore(*types)
    self.store_end_iter = None
    # scrollable list view
    self.set_shadow_type(gtk.SHADOW_ETCHED_IN)
    self.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
    self.view = gtk.TreeView(self.store)
    self.view.set_rules_hint(True)
    self.view.connect('row-activated', self.row_activated)
    self.add(self.view)

  """ add a column displaying the text at text_index """
  def add_column(self, title, text_index):
    rt = gtk.CellRendererText()
    column = gtk.TreeViewColumn(title, rt, text=text_index)
    column.set_expand(True)
    column.set_resizable(True)
    self.view.append_column(column)

  def get_row(self, index):
    return self.store[index]

  def set_column_title(self, index, title):
    self.view.get_column(index).set_title(title)

  """ append item. it will extend the list if extender is true. """
  def append(self, row, extender=False):
    it = self.store.append(row)
    if extender:
      self.store_end_iter = it

  def clear(self):
    self.store.clear()
    self.store_end_iter = None

  def row_activated(self, view, path, col):
    if self.store_end_iter != None and self.store.get_path(self.store_end_iter) == path:
      self.store.remove(self.store_end_iter)
      self.emit('row-extended')
    else:
      row = self.store[path]
      self.emit('row-selected', path[0])

gobject.type_register(ExtendedView)

class FreqGUI():
  def __init__(self, db, listsize):
    self.database = db
    self.listsize = listsize
    self.wordstore = []
    self.freqmode = 0
    self.select_position = 0
    self.word = u''
    self.posvalues = [config.ALL]*config.mecab_fields
    self.update_mode = False
    self.create_layout()
    self.create_sentence_layout()
    self.update()
    self.window.show_all()

  def create_window(self, title):
    window = gtk.Window(gtk.WINDOW_TOPLEVEL)
    window.connect('delete_event', self.delete_event)
    window.set_default_size(800, 600)
    window.set_title(title)
    window.set_border_width(5)
    return window

  def create_sentence_layout(self):
    # sentence window
    self.sentence_window = self.create_window('Sentence Browser')
    # sentences displayed in scrollable list view
    self.sentenceview = ExtendedView(str)
    self.sentenceview.add_column(u'Sentences', 0)
    self.sentenceview.connect('row-extended', self.load_sentences)
    self.sentence_window.add(self.sentenceview)

  def display_sentences(self, view, index):
    wid = self.viewstore[index][0]
    sentences = self.database.select_sentences(wid)
    self.sentenceview.clear()
    self.load_sentences(self.sentenceview)
    self.sentence_window.show_all()

  def load_sentences(self, view):
    results = self.database.select_sentences_results(self.listsize)
    for r in results:
      view.append((r[0],))
    if len(results) >= self.listsize:
      view.append((u'Load more…',), True)

  def create_layout(self):
    # main window
    self.window = self.create_window('Frequency Browser')
    self.window.connect('destroy', self.destroy)
    # words displayed in scrollable list view
    self.view = ExtendedView(float, str, *([str]*config.mecab_fields))
    self.view.add_column(u'Frequency (%)', 0)
    self.view.add_column(u'Word', 1)
    for i in range(config.mecab_fields):
      self.view.add_column(u'POS' + unicode(i + 1), i + 2)
    self.view.connect('row-selected', self.display_sentences)
    self.view.connect('row-extended', self.load_words)
    # split with selection boxes, word list and status bar
    topbox = gtk.VBox(False, 10)
    hbox = gtk.HBox(True, 10)
    self.status = gtk.Statusbar()
    topbox.pack_start(hbox, False, False)
    topbox.pack_start(self.view, True, True)
    topbox.pack_start(self.status, False, False)
    self.window.add(topbox)
    # create selection vars
    # frequency display selection box
    vbox = gtk.VBox(False, 0)
    lb = gtk.Label('Frequency')
    cb = gtk.combo_box_new_text()
    cb.append_text('Relative')
    cb.append_text('Absolute')
    cb.set_active(0)
    cb.set_size_request(50, -1)
    cb.connect('changed', self.changed_freq)
    vbox.pack_start(lb, False, False, 0)
    vbox.pack_start(cb, False, False, 0)
    hbox.pack_start(vbox, True, True, 0)
    # word selection box
    vbox = gtk.VBox(False, 0)
    lb = gtk.Label('Word')
    entry = gtk.Entry(max=40)
    entry.connect('activate', self.changed_word)
    entry.set_width_chars(5)
    vbox.pack_start(lb, False, False, 0)
    vbox.pack_start(entry, False, False, 0)
    hbox.pack_start(vbox, True, True, 0)
    # pos selection boxes
    self.pos_boxes = []
    self.pos_stores = []
    for i in range(config.mecab_fields):
      vbox = gtk.VBox(False, 0)
      store = gtk.ListStore(str)
      cell = gtk.CellRendererText()
      cb = gtk.ComboBox(store)
      cb.pack_start(cell, True)
      cb.add_attribute(cell, 'text', 0)
      cb.set_size_request(50, -1)
      cb.connect('changed', self.changed_pos, i)
      lb = gtk.Label('POS ' + str(i + 1))
      vbox.pack_start(lb, False, False, 0)
      vbox.pack_start(cb, False, False, 0)
      hbox.pack_start(vbox, True, True, 0)
      self.pos_boxes.append(cb)
      self.pos_stores.append(store)

  def update_selections(self):
    self.update_mode = True
    # get valid selections
    # reset higher positions
    for i in range(self.select_position, config.mecab_fields):
      self.posvalues[i] = config.ALL
    # update selection boxes
    for i in range(self.select_position, config.mecab_fields):
      cb = self.pos_boxes[i]
      store = self.pos_stores[i]
      cb.hide()
      store.clear()
      store.append(config.ALL)
      # update next box if needed
      if i == self.select_position and \
          (self.select_position == 0 or\
           self.posvalues[self.select_position - 1] != config.ALL):
        options = self.database.select_options(self.word, self.posvalues, i)
        for opt in options:
          store.append((opt,))
        cb.set_sensitive(True)
      else:
        cb.set_sensitive(False)
      cb.set_active(0)
      cb.show()
    self.update_mode = False

  def update_list(self):
    result = self.database.select_frequencies(self.word, self.posvalues)
    self.dsum = 0
    self.fsum = result[0]
    rows = result[1]
    self.status.push(0, u'Query matches %s unique words appearing a total of %s times.' % (rows, self.fsum))

    self.view.clear()
    self.viewstore = []
    self.load_words(self.view)

  def load_words(self, view):
    results = self.database.select_frequency_results(self.listsize)
    for r in results:
      rl = list(r)[1:]
      self.dsum = self.dsum + rl[0] 
      if not self.freqmode:
        rl[0] = 100.00 * rl[0] / self.fsum
      view.append(rl)
      self.viewstore.append(r)
    if len(results) >= self.listsize:
      remaining = self.fsum - self.dsum
      if not self.freqmode:
        remaining = 100.00 * remaining / self.fsum
      view.append([remaining, u'Load more…'] + [u'']*config.mecab_fields, True)

  def delete_event(self, window, event, data=None):
    if window == self.sentence_window:
      # just hide sentence window
      self.sentence_window.hide()
      return True
    else:
      # allow window to be destroyed by delete event
      return False

  def destroy(self, widget, data=None):
    gtk.main_quit()

  def update(self):
    if not self.update_mode: # to prevent recursive updates
      self.update_selections()
      self.update_list()

  def changed_word(self, entry):
    self.word = entry.get_text().decode('utf-8')
    self.update()

  def changed_freq(self, freqbox):
    index = freqbox.get_active()
    self.freqmode = freqbox.get_active()
    if self.freqmode:
      self.view.set_column_title(0, u'Frequency (#)')
    else:
      self.view.set_column_title(0, u'Frequency (%)')
    self.update()

  def changed_pos(self, combobox, number):
    if not self.update_mode:
      self.select_position = number + 1
      index = combobox.get_active()
      self.posvalues[number] = self.pos_stores[number][index][0].decode('utf-8')
      self.update()

  def show(self):
    gtk.main()


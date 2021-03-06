# (c) 2013 Joost Yervante Damad <joost@damad.be>
# License: GPL

import uuid

from PySide import QtGui, QtCore

from defaultsettings import default_settings, color_schemes

import export.eagle

def color_scheme_combo(parent, current):
  l_combo = QtGui.QComboBox()
  for k in color_schemes.keys():
    l_combo.addItem(k, k)
    if k == current:
      l_combo.setCurrentIndex(l_combo.count()-1)
  return l_combo

def library_combo(parent):
  l_combo = QtGui.QComboBox()
  selected = parent.selected_library
  if selected == None:
    selected = parent.active_library
  for x in parent.lib_dir.items():
    l_combo.addItem(x[0], x)
    if not parent.lib_exist[x[0]]:
      i = l_combo.model().index(l_combo.count()-1, 0) 
      # trick to make disabled
      l_combo.model().setData(i, 0, QtCore.Qt.UserRole-1)
    elif selected == None:
      selected = x[0]
    if x[0] == selected:
      l_combo.setCurrentIndex(l_combo.count()-1)
  return l_combo

def select_library(obj):
  result = QtGui.QFileDialog.getOpenFileName(
    obj,
    "Select Library", filter="Eagle CAD Library (*.lbr);;XML file (*.xml)")
  filename = result[0]
  if (filename == ''): return
  try:
    version = export.eagle.check_xml_file(filename)
    return ('eagle', version, filename)
  except Exception as ex:
    QtGui.QMessageBox.critical(obj, "error", str(ex))
    return None

class LibrarySelectDialog(QtGui.QDialog):

  def __init__(self, parent=None):
    super(LibrarySelectDialog, self).__init__(parent)
    self.setWindowTitle('Select Library')
    self.resize(640,160) # TODO, there must be a better way to do this
    vbox = QtGui.QVBoxLayout()
    form_layout = QtGui.QFormLayout()
    lib_widget = QtGui.QWidget()
    lib_hbox = QtGui.QHBoxLayout()
    self.lib_filename = QtGui.QLineEdit()
    self.lib_filename.setReadOnly(True)
    self.lib_filename.setPlaceholderText("press Browse")
    lib_button = QtGui.QPushButton("Browse")
    self.filename = None
    lib_button.clicked.connect(self.get_file)
    lib_hbox.addWidget(self.lib_filename)
    lib_hbox.addWidget(lib_button)
    lib_widget.setLayout(lib_hbox)
    form_layout.addRow("library", lib_widget) 
    self.lib_type = QtGui.QLineEdit()
    self.lib_type.setReadOnly(True)
    form_layout.addRow("type", self.lib_type) 
    vbox.addLayout(form_layout)
    buttons = QtGui.QDialogButtonBox.Ok | QtGui.QDialogButtonBox.Cancel
    self.button_box = QtGui.QDialogButtonBox(buttons, QtCore.Qt.Horizontal)
    self.button_box.accepted.connect(self.accept)
    self.button_box.rejected.connect(self.reject)
    self.button_box.button(QtGui.QDialogButtonBox.Ok).setDisabled(True)
    vbox.addWidget(self.button_box)
    self.setLayout(vbox)

  def get_file(self):
    result = select_library(self)
    if result == None: return
    (self.filetype, version, self.filename) = result
    self.lib_filename.setText(self.filename)
    self.lib_type.setText(version)
    self.button_box.button(QtGui.QDialogButtonBox.Ok).setDisabled(False)
    self.button_box.button(QtGui.QDialogButtonBox.Ok).setFocus()

# Clone, New, ... are all quite simular, maybe possible to condense?

class CloneFootprintDialog(QtGui.QDialog):

  def __init__(self, parent, old_meta, old_code):
    super(CloneFootprintDialog, self).__init__(parent)
    self.new_id = uuid.uuid4().hex
    self.setWindowTitle('Clone Footprint')
    self.resize(640,160) # TODO, there must be a better way to do this
    vbox = QtGui.QVBoxLayout()
    gbox_existing = QtGui.QGroupBox("existing")
    gbox_new = QtGui.QGroupBox("new")
    existing_fl = QtGui.QFormLayout()
    existing_fl.addRow("name:", QtGui.QLabel(old_meta['name']))
    existing_fl.addRow("id:", QtGui.QLabel(old_meta['id']))
    existing_fl.addRow("library:", QtGui.QLabel(parent.active_library))
    gbox_existing.setLayout(existing_fl)
    vbox.addWidget(gbox_existing) 
    self.name_edit = QtGui.QLineEdit()
    self.name_edit.setText(old_meta['name']+"_"+self.new_id)
    new_fl = QtGui.QFormLayout()
    new_fl.addRow("name:", self.name_edit)
    new_fl.addRow("id:", QtGui.QLabel(self.new_id))
    self.l_combo = library_combo(parent)
    new_fl.addRow("library:", self.l_combo)
    gbox_new.setLayout(new_fl)
    vbox.addWidget(gbox_new) 
    buttons = QtGui.QDialogButtonBox.Ok | QtGui.QDialogButtonBox.Cancel
    self.button_box = QtGui.QDialogButtonBox(buttons, QtCore.Qt.Horizontal)
    self.button_box.accepted.connect(self.accept)
    self.button_box.rejected.connect(self.reject)
    vbox.addWidget(self.button_box)
    self.setLayout(vbox)

  def get_data(self):
    return (self.new_id, self.name_edit.text(), self.l_combo.currentText())

class NewFootprintDialog(QtGui.QDialog):

  def __init__(self, parent):
    super(NewFootprintDialog, self).__init__(parent)
    self.new_id = uuid.uuid4().hex
    self.setWindowTitle('New Footprint')
    self.resize(640,160) # TODO, there must be a better way to do this
    vbox = QtGui.QVBoxLayout()
    gbox_new = QtGui.QGroupBox("new")
    self.name_edit = QtGui.QLineEdit()
    self.name_edit.setText("TODO_"+self.new_id)
    new_fl = QtGui.QFormLayout()
    new_fl.addRow("name:", self.name_edit)
    new_fl.addRow("id:", QtGui.QLabel(self.new_id))
    self.l_combo = library_combo(parent)
    new_fl.addRow("library:", self.l_combo)
    gbox_new.setLayout(new_fl)
    vbox.addWidget(gbox_new) 
    buttons = QtGui.QDialogButtonBox.Ok | QtGui.QDialogButtonBox.Cancel
    self.button_box = QtGui.QDialogButtonBox(buttons, QtCore.Qt.Horizontal)
    self.button_box.accepted.connect(self.accept)
    self.button_box.rejected.connect(self.reject)
    vbox.addWidget(self.button_box)
    self.setLayout(vbox)

  def get_data(self):
    return (self.new_id, self.name_edit.text(), self.l_combo.currentText())

class MoveFootprintDialog(QtGui.QDialog):

  def __init__(self, parent, old_meta):
    super(MoveFootprintDialog, self).__init__(parent)
    self.setWindowTitle('Move Footprint')
    self.resize(640,160) # TODO, there must be a better way to do this
    vbox = QtGui.QVBoxLayout()
    gbox_from = QtGui.QGroupBox("from")
    from_fl = QtGui.QFormLayout()
    from_fl.addRow("name:", QtGui.QLabel(old_meta['name']))
    from_fl.addRow("library:", QtGui.QLabel(parent.active_library))
    gbox_from.setLayout(from_fl)
    vbox.addWidget(gbox_from) 
    gbox_to = QtGui.QGroupBox("to")
    to_fl = QtGui.QFormLayout()
    self.name_edit = QtGui.QLineEdit()
    self.name_edit.setText(old_meta['name'])
    to_fl.addRow("name:", self.name_edit)
    self.l_combo = library_combo(parent)
    to_fl.addRow("library:", self.l_combo)
    gbox_to.setLayout(to_fl)
    vbox.addWidget(gbox_to) 
    buttons = QtGui.QDialogButtonBox.Ok | QtGui.QDialogButtonBox.Cancel
    self.button_box = QtGui.QDialogButtonBox(buttons, QtCore.Qt.Horizontal)
    self.button_box.accepted.connect(self.accept)
    self.button_box.rejected.connect(self.reject)
    vbox.addWidget(self.button_box)
    self.setLayout(vbox)

  def get_data(self):
    return (self.name_edit.text(), self.l_combo.currentText())

class DisconnectLibraryDialog(QtGui.QDialog):

  def __init__(self, parent):
    super(DisconnectLibraryDialog, self).__init__(parent)
    self.setWindowTitle('Disconnect Library')
    self.resize(640,160) # TODO, there must be a better way to do this
    vbox = QtGui.QVBoxLayout()
    fl = QtGui.QFormLayout()
    self.l_combo = library_combo(parent)
    fl.addRow("library:", self.l_combo)
    vbox.addLayout(fl)
    buttons = QtGui.QDialogButtonBox.Ok | QtGui.QDialogButtonBox.Cancel
    button_box = QtGui.QDialogButtonBox(buttons, QtCore.Qt.Horizontal)
    button_box.accepted.connect(self.accept)
    button_box.rejected.connect(self.reject)
    vbox.addWidget(button_box)
    self.setLayout(vbox)

  def get_data(self):
    return self.l_combo.currentText()

class AddLibraryDialog(QtGui.QDialog):

  def __init__(self, parent):
    super(AddLibraryDialog, self).__init__(parent)
    self.parent = parent
    self.setWindowTitle('Add Library')
    self.resize(640,160) # TODO, there must be a better way to do this
    vbox = QtGui.QVBoxLayout()
    fl = QtGui.QFormLayout()
    self.name_edit = QtGui.QLineEdit()
    self.name_edit.textChanged.connect(self.name_changed)
    fl.addRow("name:", self.name_edit)
    self.dir_edit = QtGui.QLineEdit()
    self.dir_edit.setReadOnly(True)
    hbox = QtGui.QHBoxLayout()
    hbox.addWidget(self.dir_edit)
    lib_button = QtGui.QPushButton("Browse")
    self.filename = None
    lib_button.clicked.connect(self.get_directory)
    hbox.addWidget(lib_button)
    hbox_w = QtGui.QWidget()
    hbox_w.setLayout(hbox)
    fl.addRow("library", hbox_w)
    self.dir_error = 'select a directory'
    self.name_error = 'provide a name'
    self.name_ok = False
    self.dir_ok = False
    self.issue = QtGui.QLineEdit()
    self.issue.setReadOnly(True)
    fl.addRow('issue:', self.issue)
    vbox.addLayout(fl)
    buttons = QtGui.QDialogButtonBox.Ok | QtGui.QDialogButtonBox.Cancel
    button_box = QtGui.QDialogButtonBox(buttons, QtCore.Qt.Horizontal)
    button_box.accepted.connect(self.accept)
    button_box.rejected.connect(self.reject)
    self.ok_button = button_box.button(QtGui.QDialogButtonBox.Ok)
    self.update_ok_button()
    vbox.addWidget(button_box)
    self.setLayout(vbox)

  def get_directory(self):
    result = QtGui.QFileDialog.getExistingDirectory(self, "Select Directory")
    if result == '': return
    self.dir_edit.setText(result)
    if result in self.parent.lib_dir.values():
      self.dir_error = 'directory already exists as library'
      self.dir_ok = False
    else:
      self.dir_ok = True
    self.update_ok_button()

  def name_changed(self):
    name = self.name_edit.text()
    if name == '':
      self.name_error = 'please provide a name'
      self.name_ok = False
    elif name in self.parent.lib_dir.keys():
      self.name_error = 'name is already in use'
      self.name_ok = False
    else:
      self.name_ok = True
    self.update_ok_button()

  def update_ok_button(self):
    self.ok_button.setDisabled(not (self.name_ok and self.dir_ok))
    if (not self.name_ok) and (not self.dir_ok):
      self.issue.setText(self.name_error + " and " + self.dir_error)
    elif not self.name_ok:
      self.issue.setText(self.name_error)
    elif not self.dir_ok:
      self.issue.setText(self.dir_error)
    else:
      self.issue.clear()
   

  def get_data(self):
    return (self.name_edit.text(), self.dir_edit.text())

class ImportFootprintsDialog(QtGui.QDialog):

  def __init__(self, parent):
    super(ImportFootprintsDialog, self).__init__(parent)
    self.setWindowTitle('Import Footprints')
    self.resize(640,640) # TODO, there must be a better way to do this
    vbox = QtGui.QVBoxLayout()
    form_layout = QtGui.QFormLayout()
    lib_widget = QtGui.QWidget()
    lib_hbox = QtGui.QHBoxLayout()
    self.lib_filename = QtGui.QLineEdit()
    self.lib_filename.setReadOnly(True)
    self.lib_filename.setPlaceholderText("press Browse")
    lib_button = QtGui.QPushButton("Browse")
    self.filename = None
    lib_button.clicked.connect(self.get_file)
    lib_hbox.addWidget(self.lib_filename)
    lib_hbox.addWidget(lib_button)
    lib_widget.setLayout(lib_hbox)
    form_layout.addRow("import from:", lib_widget) 
    self.lib_type = QtGui.QLineEdit()
    self.lib_type.setReadOnly(True)
    form_layout.addRow("type", self.lib_type) 
    vbox.addLayout(form_layout)
    vbox.addWidget(QtGui.QLabel("select footprint(s):"))
    tree = QtGui.QTreeView()
    tree.setModel(self.make_model())
    tree.setRootIsDecorated(False)
    tree.resizeColumnToContents(0)
    tree.setSelectionMode(QtGui.QAbstractItemView.MultiSelection)
    self.tree_selection_model = tree.selectionModel()
    self.tree_selection_model.selectionChanged.connect(self.selection_changed)
    vbox.addWidget(tree)
    form_layout2 = QtGui.QFormLayout()
    self.l_combo = library_combo(parent)
    form_layout2.addRow("import to:", self.l_combo)
    vbox.addLayout(form_layout2)
    buttons = QtGui.QDialogButtonBox.Ok | QtGui.QDialogButtonBox.Cancel
    self.button_box = QtGui.QDialogButtonBox(buttons, QtCore.Qt.Horizontal)
    self.button_box.accepted.connect(self.accept)
    self.button_box.rejected.connect(self.reject)
    self.button_box.button(QtGui.QDialogButtonBox.Ok).setDisabled(True)
    vbox.addWidget(self.button_box)
    self.setLayout(vbox)
 
  def get_file(self):
    result = select_library(self)
    if result == None: return
    (self.filetype, version, self.filename) = result
    self.lib_filename.setText(self.filename)
    self.lib_type.setText(version)
    self.populate_model()

  def make_model(self):
    self.model = QtGui.QStandardItemModel()
    self.model.setColumnCount(1)
    self.model.setHorizontalHeaderLabels(['name'])
    self.root = self.model.invisibleRootItem()
    return self.model

  def populate_model(self):
    self.root.removeRows(0, self.root.rowCount())
    self.importer = export.eagle.Import(self.filename)
    name_desc_list = self.importer.list_names()
    name_desc_list = sorted(name_desc_list, lambda (n1,d1),(n2,d2): cmp(n1,n2))
    for (name, desc) in name_desc_list:
      name_item = QtGui.QStandardItem(name)
      name_item.setToolTip(desc)
      name_item.setEditable(False)
      self.root.appendRow([name_item])

  def selection_changed(self, selected, deselected):
    has = self.tree_selection_model.hasSelection()
    self.button_box.button(QtGui.QDialogButtonBox.Ok).setDisabled(not has)

  def get_data(self):
    indices = self.tree_selection_model.selectedIndexes()
    return ([self.model.data(i) for i in indices], self.importer, self.l_combo.currentText())

class PreferencesDialog(QtGui.QDialog):

  def __init__(self, parent):
    super(PreferencesDialog, self).__init__(parent)
    self.parent = parent
    vbox = QtGui.QVBoxLayout()
    form_layout = QtGui.QFormLayout()
    self.gldx = QtGui.QLineEdit(str(parent.setting('gl/dx')))
    self.gldx.setValidator(QtGui.QIntValidator(100,1000))
    form_layout.addRow("GL dx", self.gldx) 
    self.gldy = QtGui.QLineEdit(str(parent.setting('gl/dy')))
    self.gldy.setValidator(QtGui.QIntValidator(100,1000))
    form_layout.addRow("GL dy", self.gldy) 
    self.glzoomf = QtGui.QLineEdit(str(parent.setting('gl/zoomfactor')))
    self.glzoomf.setValidator(QtGui.QIntValidator(1,250))
    form_layout.addRow("zoom factor", self.glzoomf) 
    self.key_idle = QtGui.QLineEdit(str(parent.setting('gui/keyidle')))
    self.key_idle.setValidator(QtGui.QDoubleValidator(0.0,5.0,2))
    form_layout.addRow("key idle", self.key_idle) 
    self.color_scheme = color_scheme_combo(self, str(parent.setting('gl/colorscheme')))
    form_layout.addRow("color scheme", self.color_scheme) 
    vbox.addLayout(form_layout)
    buttons = QtGui.QDialogButtonBox.Ok | QtGui.QDialogButtonBox.RestoreDefaults | QtGui.QDialogButtonBox.Cancel
    button_box = QtGui.QDialogButtonBox(buttons, QtCore.Qt.Horizontal)
    rest_but = button_box.button(QtGui.QDialogButtonBox.RestoreDefaults)
    rest_but.clicked.connect(self.settings_restore_defaults)
    button_box.accepted.connect(self.settings_accepted)
    button_box.rejected.connect(self.reject)
    vbox.addWidget(button_box)
    settings_widget = QtGui.QWidget()
    self.setLayout(vbox)

  def settings_restore_defaults(self):
    self.gldx.setText(str(default_settings['gl/dx']))
    self.gldy.setText(str(default_settings['gl/dy']))
    self.glzoomf.setText(str(default_settings['gl/zoomfactor']))
    self.key_idle.setText(str(default_settings['gui/keyidle']))
    default_color_scheme = str(default_settings['gui/colorscheme'])
    for i in range(0, self.color_scheme.count()):
      if self.color_scheme.itemText(i) == default_color_scheme:
        self.color_scheme.setCurrentIndex(i)
        break

  def settings_accepted(self):
    settings = self.parent.settings
    settings.setValue('gl/dx', self.gldx.text())
    settings.setValue('gl/dy', self.gldy.text())
    settings.setValue('gl/zoomfactor', self.glzoomf.text())
    settings.setValue('gui/keyidle', self.key_idle.text())
    settings.setValue('gl/colorscheme', self.color_scheme.currentText())
    self.parent.status("Settings updated.")
    self.accept()

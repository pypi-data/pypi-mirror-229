from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
import platform
import qdarktheme
from shutil import rmtree
from .tools import *
from .dictionary import *
from .dictmanager import *
from .fieldmatcher import FieldMatcher

BoldStyles = ["<disabled>", "Font weight", "Underscores"]

class SettingsDialog(QDialog):
    def __init__(self, parent, ):
        super().__init__(parent)
        self.settings = parent.settings
        user_note_type = self.settings.value("note_type")
        self.parent = parent
        self.resize(500,400)
        self.setWindowTitle("Configure VocabSieve")
        self.initWidgets()
        self.initTabs()
        try:
            self.setupWidgets()
            self.setupAutosave()
            self.setupProcessing()
            self.deactivateProcessing()
            self.getMatchedCards()
            self.twodictmode = self.settings.value(
                "dict_source2", "<disabled>") != "<disabled>"
        except TypeError as e:
            print(e)
            print(
                "TypeError encountered while trying to setup settings dialog,",
                "resetting all settings to default")
            self.settings.clear()
            self.close()
        if not user_note_type and not self.settings.value("internal/added_default_note_type"):
            try:
                self.onDefaultNoteType()
                self.settings.setValue("internal/added_default_note_type", True)
            except Exception:
                pass


    def initWidgets(self):
        self.bar = QStatusBar()
        self.allow_editing = QCheckBox(
            "Allow directly editing definition fields")
        self.primary = QCheckBox("Use primary selection")
        self.register_config_handler(self.allow_editing, "allow_editing", True)
        self.capitalize_first_letter = QCheckBox(
            "Capitalize first letter of sentence")
        self.capitalize_first_letter.setToolTip(
            "Capitalize the first letter of clipboard's content before pasting into the sentence field. Does not affect dictionary lookups.")
        self.lemmatization = QCheckBox(
            "Use lemmatization for dictionary lookups")
        self.lemmatization.setToolTip(
            "Lemmatization means to get the original form of words." +
            "\nFor example, 'books' will be converted to 'book' during lookup if this option is set.")
        self.lem_greedily = QCheckBox(
            "Lemmatize words greedily")
        self.lem_greedily.setToolTip(
            "Try a bit harder to lemmatize words. In Spanish for example, this results "
            "\nin the successful lemmatization 'conocer' of 'conocerlo'.")
        self.lemfreq = QCheckBox("Lemmatize before looking up frequency")
        self.lemfreq.setToolTip(
            "Lemmatize words before trying to find them in the frequency list." +
            "\nUse this for frequency lists displayed on FLT.org, but do not use it " +
            "\nfor frequency lists from Migaku. ")
        self.target_language = QComboBox()
        self.deck_name = QComboBox()
        self.tags = QLineEdit()
        self.dict_source = QComboBox()
        self.dict_source2 = QComboBox()
        self.freq_source = QComboBox()
        self.gtrans_lang = QComboBox()
        self.note_type = QComboBox()
        self.sentence_field = QComboBox()
        self.reader_font = QComboBox()
        self.reader_font.addItems(["serif", "sans-serif"])
        self.reader_fontsize = QSpinBox()
        self.reader_fontsize.setMinimum(4)
        self.reader_fontsize.setMaximum(200)
        self.reader_hlcolor = QPushButton(self.settings.value("reader_hlcolor", "#66bb77"))
        self.reader_hlcolor.clicked.connect(self.save_color)

        self.word_field = QComboBox()
        self.frequency_field = QComboBox()
        self.definition_field = QComboBox()
        self.definition2_field = QComboBox()
        self.pronunciation_field = QComboBox()
        self.audio_dict = QComboBox()
        self.bold_style = QComboBox()
        self.bold_style.setToolTip(
            '"Font weight" bolds words directly on the textbox.\n'
            '"Underscores" displays bolded words in double underscores, __word__\n'
            '(Both will look the same in Anki)\n'
            '"<disabled>" disables bolding words in both Vocabsieve and Anki')


        self.web_preset = QComboBox()
        self.custom_url = QLineEdit()
        self.custom_url.setText("https://example.com/@@@@")
        self.custom_url.setEnabled(False)

        self.orientation = QComboBox()
        self.text_scale = QSlider(Qt.Horizontal)

        self.text_scale.setTickPosition(QSlider.TicksBelow)
        self.text_scale.setTickInterval(10)
        self.text_scale.setSingleStep(5)
        self.text_scale.setValue(100)
        self.text_scale.setMinimum(50)
        self.text_scale.setMaximum(250)
        self.text_scale_label = QLabel("1.00x")
        self.text_scale_box = QWidget()
        self.text_scale_box_layout = QHBoxLayout()
        self.text_scale_box.setLayout(self.text_scale_box_layout)
        self.text_scale_box_layout.addWidget(self.text_scale)
        self.text_scale_box_layout.addWidget(self.text_scale_label)

        self.orientation.addItems(["Vertical", "Horizontal"])
        self.gtrans_api = QLineEdit()
        self.anki_api = QLineEdit()

        self.api_enabled = QCheckBox("Enable VocabSieve local API")
        self.api_host = QLineEdit()
        self.api_port = QSpinBox()
        self.api_port.setMinimum(1024)
        self.api_port.setMaximum(49151)

        self.reader_enabled = QCheckBox("Enable VocabSieve Web Reader")
        self.reader_host = QLineEdit()
        self.reader_port = QSpinBox()
        self.reader_port.setMinimum(1024)
        self.reader_port.setMaximum(49151)

        self.importdict = QPushButton('Manage local resources..')

        self.importdict.clicked.connect(self.dictmanager)

        self.postproc_selector = QComboBox()
        self.display_mode = QComboBox()
        self.skip_top = QSpinBox()
        self.skip_top.setSuffix(" lines")
        self.cleanup_html = QCheckBox()
        self.cleanup_html.setDisabled(True)
        self.collapse_newlines = QSpinBox()
        self.collapse_newlines.setSuffix(" newlines")

        self.reset_button = QPushButton("Reset settings")
        self.reset_button.setStyleSheet('QPushButton {color: red;}')
        self.nuke_button = QPushButton("Delete data")
        self.nuke_button.setStyleSheet('QPushButton {color: red;}')

        self.enable_anki = QCheckBox("Enable sending notes to Anki")
        self.check_updates = QCheckBox("Check for updates")

        self.img_format = QComboBox()
        self.img_format.addItems(
            ['png', 'jpg', 'gif', 'bmp']
        )
        supported_img_formats = list(map(lambda s: bytes(s).decode(), QImageWriter.supportedImageFormats()))
        # WebP requires a plugin, which is commonly but not always installed
        if 'webp' in supported_img_formats:
            self.img_format.addItem('webp')

        self.img_quality = QSpinBox()
        self.img_quality.setMinimum(-1)
        self.img_quality.setMaximum(100)

        self.image_field = QComboBox()

        self.freq_display_mode = QComboBox()
        self.freq_display_mode.addItems([
            "Stars",
            "Rank"
            #"Rank (LCD number)", # TODO implement these
            #"Zipf scale (text field)",
            #"Zipf scale (LCD number)"
        ])

        self.anki_query_mature = QLineEdit()
        self.mature_count_label = QLabel("")
        self.anki_query_young = QLineEdit()
        self.young_count_label = QLabel("")

        self.default_notetype_button = QPushButton("Use default note type ('vocabsieve-notes', will be created if it does not exist)")
        self.default_notetype_button.setToolTip("This will use the default note type provided by VocabSieve. It will be created if it does not exist.")
        self.default_notetype_button.clicked.connect(self.onDefaultNoteType)

        self.preview_young_button = QPushButton("Preview in Anki Browser")
        self.preview_mature_button = QPushButton("Preview in Anki Browser")

        self.known_data_lifetime = QSpinBox()
        self.known_data_lifetime.setSuffix(" seconds")
        self.known_data_lifetime.setMinimum(0)
        self.known_data_lifetime.setMaximum(1000000)
        self.known_threshold = QSpinBox()
        self.known_threshold.setMinimum(1)
        self.known_threshold.setMaximum(1000)
        self.known_threshold_cognate = QSpinBox()
        self.known_threshold_cognate.setMinimum(1)
        self.known_threshold_cognate.setMaximum(1000)
        self.w_seen = QSpinBox()
        self.w_seen.setMinimum(0)
        self.w_seen.setMaximum(1000)
        self.w_lookup = QSpinBox()
        self.w_lookup.setMinimum(0)
        self.w_lookup.setMaximum(1000)
        self.w_anki_ctx = QSpinBox()
        self.w_anki_ctx.setMinimum(0)
        self.w_anki_ctx.setMaximum(1000)
        self.w_anki_word = QSpinBox()
        self.w_anki_word.setMinimum(0)
        self.w_anki_word.setMaximum(1000)
        self.w_anki_ctx_y = QSpinBox()
        self.w_anki_ctx_y.setMinimum(0)
        self.w_anki_ctx_y.setMaximum(1000)
        self.w_anki_word_y = QSpinBox()
        self.w_anki_word_y.setMinimum(0)
        self.w_anki_word_y.setMaximum(1000)

        self.theme = QComboBox()
        self.theme.addItems(qdarktheme.get_themes())

        self.accent_color = QPushButton()
        self.accent_color.setText(self.settings.value("accent_color", "default"))
        self.accent_color.setToolTip("Hex color code (e.g. #ff0000 for red)")
        self.accent_color.clicked.connect(self.save_accent_color)


        self.known_langs = QLineEdit("en")
        self.known_langs.setToolTip("Comma-separated list of languages that you know. These will be used to determine whether a word is cognate or not.")

        self.open_fieldmatcher = QPushButton("Match fields (required for using Anki data)")

    def dictmanager(self):
        importer = DictManager(self)
        importer.exec()
        self.loadDictionaries()
        self.loadFreqSources()
        self.loadAudioDictionaries()
            

    def initTabs(self):
        self.tabs = QTabWidget()
        self.tab_d = QWidget()  # Dictionary
        self.tab_d.layout = QFormLayout(self.tab_d)
        self.tab_a = QWidget()  # Anki
        self.tab_a.layout = QFormLayout(self.tab_a)
        self.tab_n = QWidget()  # Network
        self.tab_n.layout = QFormLayout(self.tab_n)
        self.tab_i = QWidget()  # Interface
        self.tab_i.layout = QFormLayout(self.tab_i)
        self.tab_p = QWidget()  # Processing
        self.tab_p.layout = QFormLayout(self.tab_p)
        self.tab_m = QWidget()  # Miscellaneous
        self.tab_m.layout = QFormLayout(self.tab_m)
        self.tab_t = QWidget()  # Tracking
        self.tab_t.layout = QFormLayout(self.tab_t)


        self.tabs.resize(400, 400)

        self.layout = QVBoxLayout(self)
        self.layout.addWidget(self.tabs)
        self.layout.addWidget(self.bar)

        self.tabs.addTab(self.tab_d, "Dictionary")
        self.tabs.addTab(self.tab_p, "Processing")
        self.tabs.addTab(self.tab_a, "Anki")
        self.tabs.addTab(self.tab_n, "Network")
        self.tabs.addTab(self.tab_t, "Tracking")
        self.tabs.addTab(self.tab_i, "Interface")
        self.tabs.addTab(self.tab_m, "Misc")

    def save_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.settings.setValue("reader_hlcolor", color.name())
            self.reader_hlcolor.setText(color.name())

    def save_accent_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.settings.setValue("accent_color", color.name())
            self.accent_color.setText(color.name())
            qdarktheme.setup_theme(
                self.settings.value("theme", "dark"),
                custom_colors={"primary": color.name()}
                )

    def reset_settings(self):
        answer = QMessageBox.question(
            self,
            "Confirm Reset<",
            "<h1>Danger!</h1>"
            "Are you sure you want to reset all settings? "
            "This action cannot be undone. "
            "This will also close the configuration window.",
            defaultButton=QMessageBox.StandardButton.No
        )
        if answer == QMessageBox.Yes:
            self.settings.clear()
            self.close()

    def nuke_profile(self):
        datapath = QStandardPaths.writableLocation(QStandardPaths.DataLocation)
        answer = QMessageBox.question(
            self,
            "Confirm Reset",
            "<h1>Danger!</h1>"
            "Are you sure you want to delete all user data? "
            "The following directory will be deleted:<br>" + datapath
            + "<br>This action cannot be undone. "
            "This will also close the program.",
            defaultButton=QMessageBox.StandardButton.No
        )
        if answer == QMessageBox.Yes:
            self.settings.clear()
            rmtree(datapath)
            os.mkdir(datapath)
            self.parent.close()

    def onDefaultNoteType(self):
        try:
            addDefaultModel(self.settings.value("anki_api", 'http://127.0.0.1:8765'))
        except Exception:
            pass
        self.loadDecks()
        self.loadFields()
        self.note_type.setCurrentText("vocabsieve-notes")
        self.sentence_field.setCurrentText("Sentence")
        self.word_field.setCurrentText("Word")
        self.definition_field.setCurrentText("Definition")
        self.definition2_field.setCurrentText("Definition#2")
        self.pronunciation_field.setCurrentText("Pronunciation")
        self.image_field.setCurrentText("Image")

    def setupWidgets(self):
        self.target_language.addItems(langs_supported.values())
        self.web_preset.addItems([
            "English Wiktionary",
            "Monolingual Wiktionary",
            "Reverso Context",
            "Tatoeba",
            "Custom (Enter below)"
        ])
        self.bold_style.addItems([
            BoldStyles[1],
            BoldStyles[2],
            BoldStyles[0]
        ])
        self.gtrans_lang.addItems(langs_supported.values())
        self.display_mode.addItems(["Raw", "Plaintext", "Markdown", "HTML", "Markdown-HTML"])
        self.tab_d.layout.addRow(QLabel("<h3>Dictionary sources</h3>"))
        self.tab_d.layout.addRow(self.lemmatization)
        self.tab_d.layout.addRow(self.lem_greedily)
        self.tab_d.layout.addRow(self.lemfreq)
        self.tab_d.layout.addRow(
            QLabel("Target language"),
            self.target_language)
        self.tab_d.layout.addRow(
            QLabel("Dictionary source 1"),
            self.dict_source)
        self.tab_d.layout.addRow(
            QLabel("Dictionary source 2"),
            self.dict_source2)

        self.tab_d.layout.addRow(QLabel("Bold words"), self.bold_style)

        self.tab_d.layout.addRow(
            QLabel("Pronunciation source"),
            self.audio_dict)
        self.tab_d.layout.addRow(QLabel("Frequency list"), self.freq_source)
        self.tab_d.layout.addRow(
            QLabel("Google translate: To"),
            self.gtrans_lang)
        self.tab_d.layout.addRow(QLabel("Web lookup preset"), self.web_preset)
        self.tab_d.layout.addRow(QLabel("Custom URL pattern"), self.custom_url)
        self.tab_d.layout.addRow(self.importdict)

        self.tab_a.layout.addRow(QLabel("<h3>Anki settings</h3>"))
        self.tab_a.layout.addRow(self.enable_anki)
        self.tab_a.layout.addRow(
            QLabel("<i>◊ If disabled, notes will not be sent to Anki, but only stored in a local database.</i>")
        )
        self.tab_a.layout.addRow(QLabel("<hr>"))
        self.tab_a.layout.addRow(QLabel('AnkiConnect API'), self.anki_api)
        self.tab_a.layout.addRow(QLabel("Deck name"), self.deck_name)
        self.tab_a.layout.addRow(QLabel('Default tags'), self.tags)
        self.tab_a.layout.addRow(QLabel("<hr>"))
        self.tab_a.layout.addRow(self.default_notetype_button)
        self.tab_a.layout.addRow(QLabel("Note type"), self.note_type)
        self.tab_a.layout.addRow(
            QLabel('Field name for "Sentence"'),
            self.sentence_field)
        self.tab_a.layout.addRow(
            QLabel('Field name for "Word"'),
            self.word_field)
        #self.tab_a.layout.addRow(
        #    QLabel('Field name for "Frequency Stars"'),
        #    self.frequency_field)
        self.tab_a.layout.addRow(
            QLabel('Field name for "Definition"'),
            self.definition_field)
        self.tab_a.layout.addRow(
            QLabel('Field name for "Definition#2"'),
            self.definition2_field)
        self.tab_a.layout.addRow(
            QLabel('Field name for "Pronunciation"'),
            self.pronunciation_field)
        self.tab_a.layout.addRow(
            QLabel('Field name for "Image"'),
            self.image_field)


        self.tab_n.layout.addRow(QLabel(
            '<h3>Network settings</h3>'
            '◊ All settings on this tab require a restart to take effect.'
            '<br>◊ Most users should not need to change these settings.</i>'
        ))
        self.tab_n.layout.addRow(self.check_updates)
        self.tab_n.layout.addRow(QLabel("<h4>Local API</h4>"))
        self.tab_n.layout.addRow(self.api_enabled)
        self.tab_n.layout.addRow(QLabel("API host"), self.api_host)
        self.tab_n.layout.addRow(QLabel("API port"), self.api_port)
        self.tab_n.layout.addRow(QLabel("<h4>Web Reader</h4>"))
        self.tab_n.layout.addRow(self.reader_enabled)
        self.tab_n.layout.addRow(QLabel("Web reader host"), self.reader_host)
        self.tab_n.layout.addRow(QLabel("Web reader port"), self.reader_port)
        self.tab_n.layout.addRow(
            QLabel("Google Translate API"),
            self.gtrans_api)

        self.tab_i.layout.addRow(
            QLabel("<h3>Interface settings</h3>")
        )
        self.tab_i.layout.addRow(
            QLabel("<h4>Settings marked * require a restart to take effect.</h4>"))
        if platform.system() == "Linux":
            # Primary selection is only available on Linux
            self.tab_i.layout.addRow(self.primary)
        self.tab_i.layout.addRow("Theme", self.theme)
        self.tab_i.layout.addRow("Accent color", self.accent_color)
        self.tab_i.layout.addRow(self.allow_editing)
        self.tab_i.layout.addRow(QLabel("Frequency display mode"), self.freq_display_mode)
        self.tab_i.layout.addRow(QLabel("*Interface layout orientation"), self.orientation)
        self.tab_i.layout.addRow(QLabel("*Text scale"), self.text_scale_box)
        self.tab_i.layout.addRow(
            QLabel("<h4>These settings require a page refresh to take effect.</h4>"))
        self.tab_i.layout.addRow(QLabel("Reader font"), self.reader_font)
        self.tab_i.layout.addRow(QLabel("Reader font size"), self.reader_fontsize)
        self.tab_i.layout.addRow(QLabel("Reader highlight color"), self.reader_hlcolor)

        self.tab_p.layout.addRow(QLabel("<h3>Per-dictionary postprocessing options</h3>"))
        self.tab_p.layout.addRow(QLabel("Configure for dictionary:"), self.postproc_selector)
        self.tab_p.layout.addRow(QLabel("<hr>"))
        self.tab_p.layout.addRow(QLabel("Display mode"), self.display_mode)
        self.tab_p.layout.addRow(QLabel("<i>◊ HTML mode does not support editing/processing. "
                                        "Your edits will not be saved!</i>"))
        self.tab_p.layout.addRow(QLabel("Do not display the top"), self.skip_top)
        self.tab_p.layout.addRow(QLabel(
            "<i>◊ Use this if your dictionary repeats the word in the first line.</i>"))
        self.tab_p.layout.addRow(QLabel("Collapse continuous newlines into"), self.collapse_newlines)
        self.tab_p.layout.addRow(QLabel(
            "<i>◊ Set to 1 to remove blank lines. 0 will leave them intact.</i>"))
        self.tab_p.layout.addRow(QLabel("Attempt to clean up HTML"), self.cleanup_html)
        self.tab_p.layout.addRow(QLabel(
            "<i>◊ Try this if your mdx dictionary does not work.</i> (NOT IMPLEMENTED)"))

        self.text_scale.valueChanged.connect(
            lambda _: self.text_scale_label.setText(
                format(
                    self.text_scale.value() / 100,
                    "1.2f") + "x"))

        self.tab_m.layout.addRow(self.capitalize_first_letter)
        self.tab_m.layout.addRow(QLabel("<h3>Images</h3>"))
        self.tab_m.layout.addRow(QLabel("Image format"), self.img_format)
        self.tab_m.layout.addRow(QLabel("<i>◊ WebP, JPG, GIF are lossy, which create smaller files.</i>"))
        self.tab_m.layout.addRow(QLabel("Image quality"), self.img_quality)
        self.tab_m.layout.addRow(QLabel("<i>◊ Between 0 and 100. -1 uses the default value from Qt.</i>"))
        self.tab_m.layout.addRow(QLabel("<h3>Reset</h3>"))
        self.tab_m.layout.addRow(QLabel("Your data will be lost forever! There is NO cloud backup."))
        self.tab_m.layout.addRow(QLabel("<strong>Reset all settings to defaults</strong>"), self.reset_button)
        self.tab_m.layout.addRow(QLabel("<strong>Delete all user data</strong>"), self.nuke_button)

        self.tab_t.layout.addRow(QLabel("<h3>Anki tracking</h3>"))
        self.tab_t.layout.addRow(QLabel("Use the Anki Card Browser to make a query string. "
            "<br>Mature cards are excluded from the list of young cards automatically"))

        self.tab_t.layout.addRow(QLabel("Query string for 'mature' cards"), self.anki_query_mature)
        self.tab_t.layout.addRow(self.mature_count_label, self.preview_mature_button)
        self.tab_t.layout.addRow(QLabel("Query string for 'young' cards"), self.anki_query_young)
        self.tab_t.layout.addRow(self.young_count_label, self.preview_young_button)
        self.tab_t.layout.addRow(self.open_fieldmatcher)
        self.tab_t.layout.addRow(QLabel("<h3>Word scoring</h3>"))
        self.tab_t.layout.addRow(QLabel("Known languages (use commas)"), self.known_langs)
        self.tab_t.layout.addRow(QLabel("Known data lifetime"), self.known_data_lifetime)
        self.tab_t.layout.addRow(QLabel("Known threshold score"), self.known_threshold)
        self.tab_t.layout.addRow(QLabel("Known threshold score (cognate)"), self.known_threshold_cognate)
        self.tab_t.layout.addRow(QLabel("Score: seen"), self.w_seen)
        self.tab_t.layout.addRow(QLabel("Score: lookup (max 1 per day)"), self.w_lookup)
        self.tab_t.layout.addRow(QLabel("Score: mature Anki target word"), self.w_anki_word)
        self.tab_t.layout.addRow(QLabel("Score: mature Anki card context"), self.w_anki_ctx)
        self.tab_t.layout.addRow(QLabel("Score: young Anki target word"), self.w_anki_word_y)
        self.tab_t.layout.addRow(QLabel("Score: young Anki card context"), self.w_anki_ctx_y)



        self.reset_button.clicked.connect(self.reset_settings)
        self.nuke_button.clicked.connect(self.nuke_profile)

    def getMatchedCards(self):
        if self.settings.value("enable_anki", True):
            try:
                _ = getVersion(api:=self.settings.value('anki_api', 'http://127.0.0.1:8765'))    
                query_mature = self.anki_query_mature.text()
                mature_notes = findNotes(api, query_mature)
                self.mature_count_label.setText(f"Matched {str(len(mature_notes))} notes")
                query_young = self.anki_query_young.text()
                young_notes = findNotes(api, query_young)
                young_notes = [note for note in young_notes if note not in mature_notes]
                self.young_count_label.setText(f"Matched {str(len(young_notes))} notes")
            except:
                pass

    def setupProcessing(self):
        """This will allow per-dictionary configurations.
        Whenever dictionary changes, the QSettings key name must change.
        """
        curr_dict = self.postproc_selector.currentText()
        # Remove all existing connections
        try:
            self.display_mode.currentTextChanged.disconnect()
            self.skip_top.valueChanged.disconnect()
            self.collapse_newlines.valueChanged.disconnect()
            self.cleanup_html.clicked.disconnect()
        except TypeError:
            # When there are no connected functions, it raises a TypeError
            # 2022-12-28 Apparently now in PyQt5 it returns RuntimeError instead
            pass
        # Reestablish config handlers
        self.register_config_handler(self.display_mode,
                                     f"{curr_dict}/" + "display_mode", "Markdown")
        self.display_mode.currentTextChanged.connect(
            self.deactivateProcessing
        )
        self.register_config_handler(self.skip_top,
                                     f"{curr_dict}/" + "skip_top", 0)
        self.register_config_handler(self.collapse_newlines,
                                     f"{curr_dict}/" + "collapse_newlines", 0)
        self.register_config_handler(self.cleanup_html,
                                     f"{curr_dict}/" + "cleanup_html", False)
        self.deactivateProcessing()

    def deactivateProcessing(self):
        curr_display_mode = self.display_mode.currentText()
        if curr_display_mode == 'HTML':
            self.skip_top.setDisabled(True)
            self.collapse_newlines.setDisabled(True)
        else:
            self.skip_top.setEnabled(True)
            self.collapse_newlines.setEnabled(True)

    def setupAutosave(self):
        if self.settings.value("config_ver") is None \
            and self.settings.value("target_language") is not None:
            # if old config is copied to new location, nuke it
            self.settings.clear()
        self.settings.setValue("config_ver", 1)
        self.register_config_handler(
            self.anki_api, 'anki_api', 'http://127.0.0.1:8765')
        self.register_config_handler(
            self.target_language,
            'target_language',
            'en',
            code_translate=True)

        self.register_config_handler(self.check_updates, 'check_updates', False, True)

        self.register_config_handler(self.enable_anki, 'enable_anki', True)
        self.enable_anki.clicked.connect(self.toggle_anki_settings)
        self.toggle_anki_settings(self.enable_anki.isChecked())
        api = self.anki_api.text()
        try:
            _ = getVersion(api)
        except Exception as e:
            self.toggle_anki_settings(False)
            pass
            # self.errorNoConnection(e)
        else:
            self.loadDecks()
            self.loadFields()
            self.register_config_handler(
                self.deck_name, 'deck_name', 'Default')
            self.register_config_handler(self.tags, 'tags', 'vocabsieve')
            self.register_config_handler(self.note_type, 'note_type', 'Basic')
            self.register_config_handler(
                self.sentence_field, 'sentence_field', 'Sentence')
            self.register_config_handler(self.word_field, 'word_field', 'Word')
            self.register_config_handler(self.frequency_field, 'frequency_field', 'Frequency Stars')
            self.register_config_handler(
                self.definition_field, 'definition_field', 'Definition')
            self.register_config_handler(
                self.definition2_field,
                'definition2_field',
                '<disabled>')
            self.register_config_handler(
                self.pronunciation_field,
                'pronunciation_field',
                "<disabled>")
            self.register_config_handler(self.image_field, 'image_field', "<disabled>")

        self.loadDictionaries()
        self.loadAudioDictionaries()
        self.loadFreqSources()

        self.dict_source2.currentTextChanged.connect(self.changeMainLayout)
        self.postproc_selector.currentTextChanged.connect(self.setupProcessing)
        self.note_type.currentTextChanged.connect(self.loadFields)
        self.api_enabled.clicked.connect(self.setAvailable)
        self.reader_enabled.clicked.connect(self.setAvailable)
        self.register_config_handler(self.lemmatization, 'lemmatization', True)
        self.register_config_handler(self.lem_greedily, 'lem_greedily', False)
        self.register_config_handler(self.lemfreq, 'lemfreq', True)

        self.bold_style.setCurrentText(BoldStyles[
            self.settings.value("bold_style", 1, type=int)])
        self.bold_style.currentTextChanged.connect(
            lambda t: self.settings.setValue(
                "bold_style", BoldStyles.index(t) if t in BoldStyles else 1))

        self.register_config_handler(
            self.gtrans_lang,
            'gtrans_lang',
            'en',
            code_translate=True)
        self.register_config_handler(
            self.dict_source,
            'dict_source',
            'Wiktionary (English)')
        self.register_config_handler(
            self.dict_source2, 'dict_source2', '<disabled>')
        self.register_config_handler(self.audio_dict, 'audio_dict', 'Forvo (all)')
        self.register_config_handler(
            self.freq_source, 'freq_source', '<disabled>')
        self.register_config_handler(
            self.web_preset,
            'web_preset',
            'English Wiktionary')
        self.register_config_handler(self.custom_url, 'custom_url', "https://en.wiktionary.org/wiki/@@@@")

        self.register_config_handler(self.api_enabled, 'api_enabled', True)
        self.register_config_handler(self.api_host, 'api_host', '127.0.0.1')
        self.register_config_handler(self.api_port, 'api_port', 39284)
        self.register_config_handler(
            self.reader_enabled, 'reader_enabled', True)
        self.register_config_handler(
            self.reader_host, 'reader_host', '127.0.0.1')
        self.register_config_handler(self.reader_port, 'reader_port', 39285)
        self.register_config_handler(
            self.gtrans_api,
            'gtrans_api',
            'https://lingva.lunar.icu')

        self.register_config_handler(self.reader_font, "reader_font", "serif")
        self.register_config_handler(self.reader_fontsize, "reader_fontsize", 14)
        self.register_config_handler(self.freq_display_mode, "freq_display", "Stars (like Migaku)")
        self.register_config_handler(self.allow_editing, 'allow_editing', True)
        self.register_config_handler(self.primary, 'primary', False)
        self.register_config_handler(
            self.orientation, 'orientation', 'Vertical')
        self.register_config_handler(self.text_scale, 'text_scale', '100')

        self.register_config_handler(self.capitalize_first_letter, 'capitalize_first_letter', False)
        self.register_config_handler(self.img_format, 'img_format', 'jpg')
        self.register_config_handler(self.img_quality, 'img_quality', -1)

        self.register_config_handler(self.anki_query_mature, 'tracking/anki_query_mature', "prop:ivl>=14")
        self.register_config_handler(self.anki_query_young, 'tracking/anki_query_young', "prop:ivl<14 is:review")
        self.register_config_handler(self.known_threshold, 'tracking/known_threshold', 100)
        self.register_config_handler(self.known_threshold_cognate, 'tracking/known_threshold_cognate', 25)
        self.register_config_handler(self.known_langs, 'tracking/known_langs', 'en')
        self.register_config_handler(self.w_seen, 'tracking/w_seen', 8)
        self.register_config_handler(self.w_lookup, 'tracking/w_lookup', 15)
        self.register_config_handler(self.w_anki_word, 'tracking/w_anki_word', 70)
        self.register_config_handler(self.w_anki_ctx, 'tracking/w_anki_ctx', 30)
        self.register_config_handler(self.w_anki_word_y, 'tracking/w_anki_word_y', 40)
        self.register_config_handler(self.w_anki_ctx_y, 'tracking/w_anki_ctx_y', 20)
        self.register_config_handler(self.known_data_lifetime, 'tracking/known_data_lifetime', 1800)

        self.register_config_handler(self.theme, 'theme', 'auto')
        self.theme.currentTextChanged.connect(qdarktheme.setup_theme)

        self.target_language.currentTextChanged.connect(self.loadDictionaries)
        self.target_language.currentTextChanged.connect(
            self.loadAudioDictionaries)
        self.target_language.currentTextChanged.connect(self.loadFreqSources)
        self.target_language.currentTextChanged.connect(self.loadUrl)
        self.web_preset.currentTextChanged.connect(self.loadUrl)
        self.gtrans_lang.currentTextChanged.connect(self.loadUrl)
        self.anki_query_mature.editingFinished.connect(self.getMatchedCards)
        self.anki_query_young.editingFinished.connect(self.getMatchedCards)
        self.preview_young_button.clicked.connect(self.previewYoung)
        self.preview_mature_button.clicked.connect(self.previewMature)
        self.open_fieldmatcher.clicked.connect(self.openFieldMatcher)
        self.loadUrl()

    def setAvailable(self):
        self.api_host.setEnabled(self.api_enabled.isChecked())
        self.api_port.setEnabled(self.api_enabled.isChecked())
        self.reader_host.setEnabled(self.reader_enabled.isChecked())
        self.reader_port.setEnabled(self.reader_enabled.isChecked())

    def openFieldMatcher(self):
        fieldmatcher = FieldMatcher(self)
        fieldmatcher.exec()

    def toggle_anki_settings(self, value: bool):
        self.anki_api.setEnabled(value)
        self.tags.setEnabled(value)
        self.note_type.setEnabled(value)
        self.deck_name.setEnabled(value)
        self.sentence_field.setEnabled(value)
        self.word_field.setEnabled(value)
        self.frequency_field.setEnabled(value)
        self.definition_field.setEnabled(value)
        self.definition2_field.setEnabled(value)
        self.pronunciation_field.setEnabled(value)
        self.image_field.setEnabled(value)
        self.anki_query_mature.setEnabled(value)
        self.anki_query_young.setEnabled(value)
        self.preview_mature_button.setEnabled(value)
        self.preview_young_button.setEnabled(value)
        self.open_fieldmatcher.setEnabled(value)

    def loadAudioDictionaries(self):
        custom_dicts = json.loads(self.settings.value("custom_dicts", '[]'))
        self.audio_dict.blockSignals(True)
        self.audio_dict.clear()
        dicts = getAudioDictsForLang(
            langcodes.inverse[self.target_language.currentText()], custom_dicts)
        self.audio_dict.addItems(dicts)
        self.audio_dict.setCurrentText(
            self.settings.value(
                'audio_dict', "Forvo (all)"))
        self.audio_dict.blockSignals(False)

    def loadDictionaries(self):
        custom_dicts = json.loads(self.settings.value("custom_dicts", '[]'))
        self.dict_source.blockSignals(True)
        self.dict_source.clear()
        self.dict_source.addItem("<disabled>")
        self.dict_source2.blockSignals(True)
        self.dict_source2.clear()
        self.dict_source2.addItem("<disabled>")
        self.postproc_selector.blockSignals(True)
        self.postproc_selector.clear()
        dicts = getDictsForLang(
            langcodes.inverse[self.target_language.currentText()], custom_dicts)

        self.dict_source.addItems(dicts)
        self.dict_source2.addItems(dicts)
        self.postproc_selector.addItems(dicts)
        self.dict_source.setCurrentText(
            self.settings.value(
                'dict_source',
                'Wiktionary (English)'))
        self.dict_source2.setCurrentText(
            self.settings.value(
                'dict_source2', '<disabled>'))
        self.dict_source.blockSignals(False)
        self.dict_source2.blockSignals(False)
        self.postproc_selector.blockSignals(False)

    def loadFreqSources(self):
        custom_dicts = json.loads(self.settings.value("custom_dicts", '[]'))
        sources = getFreqlistsForLang(
            langcodes.inverse[self.target_language.currentText()], custom_dicts)
        self.freq_source.blockSignals(True)
        self.freq_source.clear()
        self.freq_source.addItem("<disabled>")
        for item in sources:
            self.freq_source.addItem(item)
        self.freq_source.setCurrentText(
            self.settings.value(
                "freq_source", "<disabled>"))
        self.freq_source.blockSignals(False)

    def previewMature(self):
        try:
            _ = getVersion(api:=self.settings.value('anki_api', 'http://127.0.0.1:8765'))
            guiBrowse(api, self.anki_query_mature.text())
        except Exception as e:
            print(repr(e))


    def previewYoung(self):
        try:
            _ = getVersion(api:=self.settings.value('anki_api', 'http://127.0.0.1:8765'))
            guiBrowse(api, self.anki_query_young.text())
        except Exception as e:
            print(repr(e))

    def loadUrl(self):
        lang = self.settings.value("target_language", "en")
        tolang = self.settings.value("gtrans_lang", "en")
        langfull = langcodes[lang]
        tolangfull = langcodes[tolang]
        self.presets = bidict({
            "English Wiktionary": "https://en.wiktionary.org/wiki/@@@@#" + langfull,
            "Monolingual Wiktionary": f"https://{lang}.wiktionary.org/wiki/@@@@",
            "Reverso Context": f"https://context.reverso.net/translation/{langfull.lower()}-{tolangfull.lower()}/@@@@",
            "Tatoeba": "https://tatoeba.org/en/sentences/search?query=@@@@"
        })

        if self.web_preset.currentText() == "Custom (Enter below)":
            self.custom_url.setEnabled(True)
            self.custom_url.setText(self.settings.value("custom_url"))
        else:
            self.custom_url.setEnabled(False)
            self.custom_url.setText(
                self.presets[self.web_preset.currentText()])

    def loadDecks(self):
        self.status("Loading decks")
        api = self.anki_api.text()
        decks = getDeckList(api)
        self.deck_name.blockSignals(True)
        self.deck_name.clear()
        self.deck_name.addItems(decks)
        self.deck_name.setCurrentText(self.settings.value("deck_name"))
        self.deck_name.blockSignals(False)

        note_types = getNoteTypes(api)
        self.note_type.blockSignals(True)
        self.note_type.clear()
        self.note_type.addItems(note_types)
        self.note_type.setCurrentText(self.settings.value("note_type"))
        self.note_type.blockSignals(False)

    def loadFields(self):
        self.status("Loading fields")
        api = self.anki_api.text()

        current_type = self.note_type.currentText()
        if current_type == "":
            return

        fields = getFields(api, current_type)
        # Temporary store fields
        sent = self.sentence_field.currentText()
        word = self.word_field.currentText()
        freq_stars = self.frequency_field.currentText()
        def1 = self.definition_field.currentText()
        def2 = self.definition2_field.currentText()
        pron = self.pronunciation_field.currentText()
        img = self.image_field.currentText()

        # Block signals temporarily to avoid warning dialogs
        self.sentence_field.blockSignals(True)
        self.word_field.blockSignals(True)
        self.frequency_field.blockSignals(True)
        self.definition_field.blockSignals(True)
        self.definition2_field.blockSignals(True)
        self.pronunciation_field.blockSignals(True)
        self.image_field.blockSignals(True)

        self.sentence_field.clear()
        self.sentence_field.addItems(fields)

        self.word_field.clear()
        self.word_field.addItems(fields)

        self.frequency_field.clear()
        self.frequency_field.addItem("<disabled>")
        self.frequency_field.addItems(fields)

        self.definition_field.clear()
        self.definition_field.addItems(fields)

        self.definition2_field.clear()
        self.definition2_field.addItem("<disabled>")
        self.definition2_field.addItems(fields)

        self.pronunciation_field.clear()
        self.pronunciation_field.addItem("<disabled>")
        self.pronunciation_field.addItems(fields)

        self.image_field.clear()
        self.image_field.addItem("<disabled>")
        self.image_field.addItems(fields)

        self.sentence_field.setCurrentText(self.settings.value("sentence_field"))
        self.word_field.setCurrentText(self.settings.value("word_field"))
        self.frequency_field.setCurrentText(self.settings.value("frequency_field"))
        self.definition_field.setCurrentText(self.settings.value("definition_field"))
        self.definition2_field.setCurrentText(self.settings.value("definition2_field"))
        self.pronunciation_field.setCurrentText(self.settings.value("pronunciation_field"))
        self.image_field.setCurrentText(self.settings.value("image_field"))

        if self.sentence_field.findText(sent) != -1:
            self.sentence_field.setCurrentText(sent)
        if self.word_field.findText(word) != -1:
            self.word_field.setCurrentText(word)
        if self.frequency_field.findText(freq_stars) != -1:
            self.frequency_field.setCurrentText(freq_stars)
        if self.definition_field.findText(def1) != -1:
            self.definition_field.setCurrentText(def1)
        if self.definition2_field.findText(def2) != -1:
            self.definition2_field.setCurrentText(def2)
        if self.pronunciation_field.findText(pron) != -1:
            self.pronunciation_field.setCurrentText(pron)
        if self.image_field.findText(img) != -1:
            self.image_field.setCurrentText(img)

        self.sentence_field.blockSignals(False)
        self.word_field.blockSignals(False)
        self.frequency_field.blockSignals(False)
        self.definition_field.blockSignals(False)
        self.definition2_field.blockSignals(False)
        self.pronunciation_field.blockSignals(False)
        self.image_field.blockSignals(False)
        self.status("Done")

    def errorNoConnection(self, error):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setText("Error")
        msg.setInformativeText(
            str(error) + "\nAnkiConnect must be running to set Anki-related options."
            "\nIf you have AnkiConnect set up at a different endpoint, set that now "
            "and reopen the config tool.")
        msg.exec()

    def changeMainLayout(self):
        if self.dict_source2.currentText() != "<disabled>":
            # This means user has changed from one source to two source mode,
            # need to redraw main window
            if self.settings.value("orientation", "Vertical") == "Vertical":
                self.parent.layout.removeWidget(self.parent.definition)
                self.parent.layout.addWidget(
                    self.parent.definition, 7, 0, 2, 3)
                self.parent.layout.addWidget(
                    self.parent.definition2, 9, 0, 2, 3)
                self.parent.definition2.setVisible(True)
            else:
                self.parent.layout.removeWidget(self.parent.definition)
                self.parent.layout.addWidget(
                    self.parent.definition, 2, 3, 4, 1)
                self.parent.layout.addWidget(
                    self.parent.definition2, 2, 4, 4, 1)
                self.parent.definition2.setVisible(True)
        else:
            self.parent.layout.removeWidget(self.parent.definition)
            self.parent.layout.removeWidget(self.parent.definition2)
            self.parent.definition2.setVisible(False)
            if self.settings.value("orientation", "Vertical") == "Vertical":
                self.parent.layout.addWidget(
                    self.parent.definition, 7, 0, 4, 3)
            else:
                self.parent.layout.addWidget(
                    self.parent.definition, 2, 3, 4, 2)

    def status(self, msg):
        self.bar.showMessage(self.parent.time() + " " + msg, 4000)

    def register_config_handler(
            self,
            widget,
            key,
            default,
            code_translate=False,
            no_initial_update=False):
        name = widget.objectName()
        def update(v): return self.settings.setValue(key, v)

        def update_map(v): return self.settings.setValue(
            key, langcodes.inverse[v])
        if type(widget) == QCheckBox:
            widget.setChecked(self.settings.value(key, default, type=bool))
            widget.clicked.connect(update)
            if not no_initial_update:
                update(widget.isChecked())
        if type(widget) == QLineEdit:
            widget.setText(self.settings.value(key, default))
            widget.textChanged.connect(update)
            update(widget.text())
        if type(widget) == QComboBox:
            if code_translate:
                widget.setCurrentText(
                    langcodes[self.settings.value(key, default)])
                widget.currentTextChanged.connect(update_map)
                update_map(widget.currentText())
            else:
                widget.setCurrentText(self.settings.value(key, default))
                widget.currentTextChanged.connect(update)
                update(widget.currentText())
        if type(widget) == QSlider or type(widget) == QSpinBox:
            widget.setValue(self.settings.value(key, default, type=int))
            widget.valueChanged.connect(update)
            update(widget.value())

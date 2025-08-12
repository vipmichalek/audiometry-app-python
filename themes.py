# theme file for main program, please do not alter it

LIST_STYLE = """
        QListWidget {
            background-color: #2d2d2d;
            border: 1px solid #4e4e4e;
            background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                        stop:1 #3e3e3e, stop:0 #1f1f1f);
        }
        QListWidget::item {
            border-bottom: 1px solid #4e4e4e;
            padding: 5px;
            color: white;
        }
        QListWidget::item:selected {
            background-color: qlineargradient(
            x1: 0, y1: 0, x2: 0, y2: 1,
            stop: 0 #ffb74d,
            stop: 0.499 #ffa014,
            stop: 0.501 #d65600,
            stop: 1 #ff8c00
            );
            color: black;
            border: 1px solid #cc7000;
            border-radius: 4px;
            margin: 1px;
        }
        QListWidget::item:focus {
            outline: none;
        }                              
        QListWidget {
            outline: none;
        }
    """

CHROME_BUTTON_STYLE = """
QPushButton {
    background-color: qlineargradient(
        x1:0, y1:0, x2:0, y2:1,
        stop:0 #5a5a5a,
        stop:0.499 #3f3f3f,
        stop:0.501 #2a2a2a, 
        stop:1 #636363
    );

    color: white;
    border: 1px solid #d0d0d0;
    border-radius: 4px;
    padding: 6px 12px;
}
QPushButton:hover {
    background-color: qlineargradient(
        x1:0, y1:0, x2:0, y2:1,
        stop:0 #aaaaaa,
        stop:0.499 #7f7f7f,
        stop:0.501 #4a4a4a, 
        stop:1 #636363
    );
}
QPushButton:pressed {
    background-color: qlineargradient(
        x1:0, y1:0, x2:0, y2:1,
        stop:0 #8a8a8a,
        stop:0.499 #5f5f5f,
        stop:0.501 #2a2a2a, 
        stop:1 #434343
    );
}
QPushButton:disabled {
    background-color: qlineargradient(
        x1:0, y1:0, x2:0, y2:1,
        stop:0 #adadad,
        stop:0.499 #9f9f9f,
        stop:0.501 #6f6f6f, 
        stop:1 #838383
    );
}
"""

CHROME_TEXTBOX_STYLE = """
 QLineEdit, QTextEdit {
    background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                    stop:1 #3e3e3e, stop:0 #1f1f1f);
    border: 1px solid #8f8f8f;
    border-radius: 6px;
    padding: 4px;
    color: white;
}
QLineEdit:focus, QTextEdit:focus {
    border: 1px solid #8f8f8f;
    background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                    stop:1 #525252, stop:0 #303030);
    color: white;
}
"""

MESSAGE_BOX_STYLE = """
QMessageBox {
    background-color: #2d2d2d;
}
QMessageBox QLabel {
    color: white;
}
QMessageBox QPushButton {
    background-color: qlineargradient(
        x1:0, y1:0, x2:0, y2:1,
        stop:0 #5a5a5a,
        stop:0.499 #3f3f3f,
        stop:0.501 #2a2a2a, 
        stop:1 #636363
    );
    color: white;
    border: 1px solid #d0d0d0;
    border-radius: 4px;
    padding: 6px 12px;
}
QMessageBox QPushButton:hover {
    background-color: qlineargradient(
        x1:0, y1:0, x2:0, y2:1,
        stop:0 #aaaaaa,
        stop:0.499 #7f7f7f,
        stop:0.501 #4a4a4a, 
        stop:1 #636363
    );
}
QMessageBox QPushButton:pressed {
    background-color: qlineargradient(
        x1:0, y1:0, x2:0, y2:1,
        stop:0 #8a8a8a,
        stop:0.499 #5f5f5f,
        stop:0.501 #2a2a2a, 
        stop:1 #434343
    );
}
"""

TITLE_BAR_BTN_STYLE = """
            QPushButton {
                background-color: qlineargradient(
                    x1:0, y1:0, x2:0, y2:1,
                    stop:0 #5a5a5a,
                    stop:0.499 #3f3f3f,
                    stop:0.501 #2a2a2a,
                    stop:1 #636363
                );
                color: white;
                border: 1px solid #d0d0d0;
                border-radius: 4px;
                padding: 3px;
            }
            QPushButton:hover {
                background-color: qlineargradient(
                    x1:0, y1:0, x2:0, y2:1,
                    stop:0 #aaaaaa,
                    stop:0.499 #7f7f7f,
                    stop:0.501 #4a4a4a,
                    stop:1 #636363
                );
            }
            QPushButton:pressed {
                background-color: qlineargradient(
                    x1:0, y1:0, x2:0, y2:1,
                    stop:0 #8a8a8a,
                    stop:0.499 #5f5f5f,
                    stop:0.501 #2a2a2a,
                    stop:1 #434343
                );
            }
        """

CLOSE_BTN_STYLE = """
            QPushButton {
                background-color: qlineargradient(
                    x1:0, y1:0, x2:0, y2:1,
                    stop:0 #af0000,
                    stop:0.499 #7c0000,
                    stop:0.501 #4a0000,
                    stop:1 #bf0000
                );
                color: white;
                border: 1px solid #d0d0d0;
                border-radius: 4px;
                padding: 3px;
            }
            QPushButton:hover {
                background-color: qlineargradient(
                    x1:0, y1:0, x2:0, y2:1,
                    stop:0 #df0000,
                    stop:0.499 #ac0000,
                    stop:0.501 #8a0000,
                    stop:1 #ef0000
                );
            }
            QPushButton:pressed {
                background-color: qlineargradient(
                    x1:0, y1:0, x2:0, y2:1,
                    stop:0 #7f0000,
                    stop:0.499 #5c0000,
                    stop:0.501 #2a0000,
                    stop:1 #8f0000
                );
            }
        """

COMBO_STYLE = """
            QComboBox {
                background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                        stop:0 #3e3e3e, stop:1 #1f1f1f);
                padding: 4px;
                color: white;
                border: 1px solid #8f8f8f;
                border-radius: 4px;
            }
            QComboBox::drop-down {
                border: 0px; /* Usuwa domyślną strzałkę */
            }
            QComboBox::down-arrow {
                image: url(data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAABmJLR0QA/wD/AP+gvaeTAAAAVElEQVQ4jWNgGAWjYBSMglGwAkYGBkZGBgYGhiwGIAYxMTAw/g/E/wXih2FmYGBgYGJgYGD4D4z/B8J/hJGBgQGYGNgAAgABBgYGBgYGBgYGBgAAADfE/14A+P8AAAAASUVORK5CYII=); /* Własna strzałka */
                width: 16px;
                height: 16px;
            }
        """

START_BUTTON_STYLE = """
            QPushButton {
                background-color: qlineargradient(
                x1: 0, y1: 0, x2: 0, y2: 1,
                stop: 0 #ffb74d,
                stop: 0.499 #ffa014,
                stop: 0.501 #d65600,
                stop: 1 #ff8c00
                );
                border-radius: 5px;
                color: white;
                font-weight: bold;
                padding: 5px;
                border: 1px solid #d0d0d0;
            }
            QPushButton:hover {
                background-color: qlineargradient(
                x1: 0, y1: 0, x2: 0, y2: 1,
                stop: 0 #ffc97a,
                stop: 0.499 #fcab32,
                stop: 0.501 #d6793a,
                stop: 1 #ffa12e
                );
            }
            QPushButton:pressed {
                background-color: qlineargradient(
                x1: 0, y1: 0, x2: 0, y2: 1,
                stop: 0 #faa72d,
                stop: 0.499 #d18515,
                stop: 0.501 #ab4500,
                stop: 1 #cf7100
                );
            }
            QPushButton:disabled {
                background-color: qlineargradient(
                x1: 0, y1: 0, x2: 0, y2: 1,
                stop:0 #adadad,
                stop:0.499 #9f9f9f,
                stop:0.501 #6f6f6f, 
                stop:1 #838383
                );
                color: black;
            }
        """

def get_ListStyleA():
    return LIST_STYLE

def get_ChromeBStyleA():
    return CHROME_BUTTON_STYLE

def get_ChromeTStyleA():
    return CHROME_TEXTBOX_STYLE

def get_MsgBoxStyleA():
    return MESSAGE_BOX_STYLE

def get_TitleBtnStyleA():
    return TITLE_BAR_BTN_STYLE

def get_CloseBtnStyleA():
    return CLOSE_BTN_STYLE

def get_ComboStyleA():
    return COMBO_STYLE

def get_StartStyleA():
    return START_BUTTON_STYLE
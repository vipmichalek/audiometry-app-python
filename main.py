import sys
import sqlite3
import json
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QComboBox, QLineEdit, QStatusBar,
    QFrame, QSizePolicy, QDialog, QFormLayout, QTableWidget,
    QTableWidgetItem, QHeaderView, QDialogButtonBox, QMessageBox,
    QListWidget, QListWidgetItem, QSplashScreen, QProgressBar,
    QTextEdit, QSplitter
)
from PySide6.QtCore import Qt, QTimer, QThread, Signal, QSize
from PySide6.QtGui import QFont, QCloseEvent, QColor, QPalette, QIcon, QPixmap, QMouseEvent, QPainter, QLinearGradient
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
import numpy as np
import pygame
import time
import os
import threading
from datetime import datetime
from PySide6.QtWidgets import QHBoxLayout
from PySide6.QtCore import QPoint

# Inicjalizacja pygame do obsługi dźwięku
pygame.mixer.init()

# Dane do wykresów
FREQUENCIES = [100, 250, 500, 750, 1000, 1500, 2000, 4000]
DB_HL = np.arange(0, 105, 5) # od 0 do 100 co 5 dB
PULSE_DURATION = 0.1 # czas trwania pulsacji
PULSE_PAUSE = 0.1 # przerwa między pulsacjami

# Reusable Styles

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



def convert_numpy(obj):
    """
    Konwertuje obiekty numpy (np.integer, np.floating, np.ndarray) na standardowe typy Pythona.
    Używane do serializacji danych do formatu JSON, ponieważ json.dumps nie obsługuje bezpośrednio typów numpy.
    """
    if isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, dict):
        return {k: convert_numpy(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_numpy(i) for i in obj]
    else:
        return obj

class CustomTitleBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.setFixedHeight(30)

        # Stylizacja obramowania (zaokrąglenia tylko góra)
        self.setStyleSheet("""
            QWidget {
                border-top-left-radius: 10px;
                border-top-right-radius: 10px;
                /* Usuwamy tło w stylu, bo malujemy ręcznie */
                background: transparent;
            }
        """)

        # Główny layout poziomy
        layout = QHBoxLayout(self)
        # Marginesy: left, top, right, bottom
        # Left - trochę na "oddech" dla napisu
        # Right - więcej miejsca na przyciski z marginesem od krawędzi
        layout.setContentsMargins(8, 3, 3, 3)
        layout.setSpacing(4)  # Odstęp między widgetami (m.in. między przyciskami)

        # Label z tytułem po lewej
        self.title_label = QLabel("HB Audio Suite")
        self.title_label.setFont(QFont("Arial", 11, QFont.Bold))
        self.title_label.setStyleSheet("background-color: transparent; color: white;")
        layout.addWidget(self.title_label)

        layout.addStretch()  # Wypełni miejsce między tytułem a przyciskami

        # Przyciski sterujące oknem
        self.minimize_button = QPushButton()
        self.maximize_button = QPushButton()
        self.close_button = QPushButton()

        # Ikony - ścieżka do folderu z ikonami
        icons_dir = "icons"
        self.minimize_button.setIcon(QIcon(os.path.join(icons_dir, "min.png")))
        self.maximize_button.setIcon(QIcon(os.path.join(icons_dir, "max.png")))
        self.close_button.setIcon(QIcon(os.path.join(icons_dir, "close.png")))

        # Rozmiar przycisków mniejszy niż wcześniej (np. 26x26)
        button_size = QSize(24, 24)

        # Wspólne style dla min i max (z gradientem, zaokrąglone)
        button_style = """
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

        for btn in [self.minimize_button, self.maximize_button]:
            btn.setFixedSize(button_size)
            btn.setIconSize(QSize(14, 14))
            btn.setStyleSheet(button_style)

        # Specjalny styl dla przycisku zamykania (czerwony gradient)
        close_style = """
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

        self.close_button.setFixedSize(button_size)
        self.close_button.setIconSize(QSize(14, 14))
        self.close_button.setStyleSheet(close_style)

        # Dodajemy przyciski do layoutu (będą po prawej dzięki stretch)
        layout.addWidget(self.minimize_button)
        layout.addWidget(self.maximize_button)
        layout.addWidget(self.close_button)

        # Podłączenie sygnałów do okna nadrzędnego
        self.minimize_button.clicked.connect(self.parent_window.showMinimized)
        self.maximize_button.clicked.connect(self.toggle_maximize_restore)
        self.close_button.clicked.connect(self.parent_window.close)

        self._start_pos = None

    def toggle_maximize_restore(self):
        if self.parent_window.isMaximized():
            self.parent_window.showNormal()
            self.maximize_button.setIcon(QIcon(os.path.join("icons", "max.png")))
        else:
            self.parent_window.showMaximized()
            self.maximize_button.setIcon(QIcon(os.path.join("icons", "restore.png")))

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self._start_pos = event.globalPos()

    def mouseMoveEvent(self, event: QMouseEvent):
        if self._start_pos and event.buttons() == Qt.LeftButton:
            delta = event.globalPos() - self._start_pos
            self.parent_window.move(self.parent_window.pos() + delta)
            self._start_pos = event.globalPos()

    def mouseReleaseEvent(self, event: QMouseEvent):
        self._start_pos = None

    def paintEvent(self, event):
        painter = QPainter(self)
        gradient = QLinearGradient(0, 0, 0, self.height())  # gradient pionowy
        gradient.setColorAt(0, QColor("#555555"))
        gradient.setColorAt(0.499, QColor("#393939"))
        gradient.setColorAt(0.501, QColor("#161616"))
        gradient.setColorAt(1, QColor("#484848"))
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(gradient)
        painter.setPen(Qt.NoPen)

        rect = self.rect()
        painter.drawRoundedRect(rect, 0, 0)  # większe zaokrąglenie dla ładniejszego efektu

class CustomDialogTitleBar(QWidget):
    def __init__(self, parent=None, title="Dialog"):
        super().__init__(parent)
        self.parent_dialog = parent
        self.setFixedHeight(30)
        self.setStyleSheet("""
            QWidget {
                border-top-left-radius: 10px;
                border-top-right-radius: 10px;
                background: transparent;
            }
        """)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 3, 3, 3)
        layout.setSpacing(4)
        
        self.title_label = QLabel(title)
        self.title_label.setFont(QFont("Arial", 11, QFont.Bold))
        self.title_label.setStyleSheet("background-color: transparent; color: white;")
        layout.addWidget(self.title_label)
        
        layout.addStretch()
        
        self.close_button = QPushButton()
        icons_dir = "icons"
        self.close_button.setIcon(QIcon(os.path.join(icons_dir, "close.png")))
        
        button_size = QSize(24, 24)
        close_style = """
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
        self.close_button.setFixedSize(button_size)
        self.close_button.setIconSize(QSize(14, 14))
        self.close_button.setStyleSheet(close_style)
        
        layout.addWidget(self.close_button)
        self.close_button.clicked.connect(self.parent_dialog.reject)
        
        self._start_pos = None

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self._start_pos = event.globalPos()

    def mouseMoveEvent(self, event: QMouseEvent):
        if self._start_pos and event.buttons() == Qt.LeftButton:
            delta = event.globalPos() - self._start_pos
            self.parent_dialog.move(self.parent_dialog.pos() + delta)
            self._start_pos = event.globalPos()

    def mouseReleaseEvent(self, event: QMouseEvent):
        self._start_pos = None

    def paintEvent(self, event):
        painter = QPainter(self)
        gradient = QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(0, QColor("#555555"))
        gradient.setColorAt(0.499, QColor("#393939"))
        gradient.setColorAt(0.501, QColor("#161616"))
        gradient.setColorAt(1, QColor("#484848"))
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(gradient)
        painter.setPen(Qt.NoPen)
        rect = self.rect()
        painter.drawRoundedRect(rect, 0, 0)
        
class AudiometryWorker(QThread):
    """
    Wątek do przeprowadzania testu audiometrycznego w tle, aby nie blokować interfejsu użytkownika.
    Obsługuje różne typy sygnałów (sinus, kwadrat, puls) i tryby testowania (lewe ucho, prawe ucho, obuusznie).
    """
    
    status_update = Signal(str) # Sygnał do aktualizacji paska statusu
    point_found = Signal(int, int, str) # Sygnał do rysowania pojedynczego punktu na wykresie
    test_finished = Signal(dict) # Sygnał wysyłany po zakończeniu testu, zawiera wyniki

    def __init__(self, db_fs_correction, signal_type, test_mode, parent=None):
        """
        Inicjalizuje wątek roboczy.
        :param db_fs_correction: Korekcja dB FS na dB HL.
        :param signal_type: Typ generowanego sygnału ('sine', 'square', 'pulse').
        :param test_mode: Tryb testu ('Obuusznie', 'Ucho lewe', 'Ucho prawe').
        :param parent: Rodzic obiektu PySide6.
        """
        super().__init__(parent)
        self.db_fs_correction = db_fs_correction
        self.signal_type = signal_type
        self.test_mode = test_mode # Nowy parametr: tryb testu
        self.is_running = True
        self.space_pressed = False
        self.results = {'left': {}, 'right': {}}
        self.lock = threading.Lock() # Blokada do synchronizacji dostępu do zmiennych współdzielonych

    def run(self):
        """
        Główna pętla wykonawcza wątku. Przeprowadza testy w zależności od wybranego trybu.
        """
        self.is_running = True
        self.results = {'left': {}, 'right': {}}

        # Test lewego ucha, jeśli tryb to 'Obuusznie' lub 'Ucho lewe'
        if self.test_mode in ["Obuusznie", "Ucho lewe"]:
            for i, freq in enumerate(FREQUENCIES):
                if not self.is_running: # Sprawdzenie, czy test nie został zatrzymany
                    self.test_finished.emit(self.results)
                    return
                self.status_update.emit(f"Test - ucho lewe: {freq} Hz ({self.signal_type})")
                self.run_frequency_test(freq, i, 'left')
        
        # Test prawego ucha, jeśli tryb to 'Obuusznie' lub 'Ucho prawe'
        if self.is_running and self.test_mode in ["Obuusznie", "Ucho prawe"]:
            for i, freq in enumerate(FREQUENCIES):
                if not self.is_running: # Sprawdzenie, czy test nie został zatrzymany
                    self.test_finished.emit(self.results)
                    return
                self.status_update.emit(f"Test - ucho prawe: {freq} Hz ({self.signal_type})")
                self.run_frequency_test(freq, i, 'right')
        
        if self.is_running:
            self.status_update.emit("Test zakończony!")
        self.test_finished.emit(self.results)

    def run_frequency_test(self, freq, freq_index, ear):
        """
        Przeprowadza test dla pojedynczej częstotliwości i ucha, szukając progu słyszenia.
        :param freq: Częstotliwość w Hz.
        :param freq_index: Indeks częstotliwości w liście FREQUENCIES.
        :param ear: Ucho do testowania ('left' lub 'right').
        """
        threshold_found = False
        for db_hl in DB_HL: # Iteracja po poziomach dB HL
            if not self.is_running or threshold_found:
                return
            
            db_fs = db_hl + self.db_fs_correction # Obliczenie poziomu dB FS
            volume = 10**(db_fs / 20) # Konwersja na głośność liniową
            
            self.play_tone(freq, volume, ear, self.signal_type) # Odtwarzanie tonu
            
            self.wait_for_space() # Oczekiwanie na naciśnięcie spacji przez użytkownika
            
            with self.lock:
                if self.is_running and self.space_pressed: # Jeśli spacja została naciśnięta
                    self.results[ear][freq_index] = db_hl # Zapisanie progu
                    self.point_found.emit(freq_index, db_hl, ear) # Sygnalizacja znalezienia punktu
                    threshold_found = True
                    self.space_pressed = False
                    
        if not threshold_found: # Jeśli próg nie został znaleziony (użytkownik nie nacisnął spacji)
            self.results[ear][freq_index] = 100 # Ustawienie progu na maksymalną wartość
            self.point_found.emit(freq_index, 100, ear)

    def play_tone(self, frequency, volume, ear, signal_type):
        """
        Odtwarza ton o określonej częstotliwości, głośności i typie sygnału.
        :param frequency: Częstotliwość tonu w Hz.
        :param volume: Głośność tonu (liniowa).
        :param ear: Ucho, w którym ma być odtworzony ton ('left' lub 'right').
        :param signal_type: Typ sygnału ('sine', 'square', 'pulse').
        """
        sample_rate = 44100
        duration = 1 # 1 sekunda
        
        if signal_type == "pulse":
            self._play_pulse_tone(frequency, volume, ear)
            return

        t = np.linspace(0, duration, int(sample_rate * duration), False)
        
        if signal_type == "sine":
            signal_wave = np.sin(2 * np.pi * frequency * t) * volume
        elif signal_type == "square":
            signal_wave = np.sign(np.sin(2 * np.pi * frequency * t)) * volume
        else: # Domyślnie sinus
            signal_wave = np.sin(2 * np.pi * frequency * t) * volume
        
        if ear == 'left':
            sound_data = np.zeros((len(signal_wave), 2))
            sound_data[:, 0] = signal_wave # Sygnał tylko w lewym kanale
        else:
            sound_data = np.zeros((len(signal_wave), 2))
            sound_data[:, 1] = signal_wave # Sygnał tylko w prawym kanale
        
        sound_data = (sound_data * 32767).astype(np.int16) # Konwersja na 16-bitowe liczby całkowite
        sound = pygame.sndarray.make_sound(sound_data)
        sound.play()
        
    def _play_pulse_tone(self, frequency, volume, ear):
        """
        Odtwarza ton pulsacyjny.
        :param frequency: Częstotliwość tonu w Hz.
        :param volume: Głośność tonu (liniowa).
        :param ear: Ucho, w którym ma być odtworzony ton ('left' lub 'right').
        """
        sample_rate = 44100
        
        pulse_duration_samples = int(sample_rate * PULSE_DURATION)
        pause_duration_samples = int(sample_rate * PULSE_PAUSE)
        
        t_pulse = np.linspace(0, PULSE_DURATION, pulse_duration_samples, False)
        sine_wave_pulse = np.sin(2 * np.pi * frequency * t_pulse) * volume
        
        pause_wave = np.zeros(pause_duration_samples)
        
        full_wave = np.array([])
        num_pulses = int(1 / (PULSE_DURATION + PULSE_PAUSE))
        for _ in range(num_pulses):
            full_wave = np.concatenate((full_wave, sine_wave_pulse, pause_wave))
        
        full_wave = full_wave[:sample_rate] # Przycięcie do 1 sekundy
        
        if ear == 'left':
            sound_data = np.zeros((len(full_wave), 2))
            sound_data[:, 0] = full_wave
        else:
            sound_data = np.zeros((len(full_wave), 2))
            sound_data[:, 1] = full_wave
        
        sound_data = (sound_data * 32767).astype(np.int16)
        sound = pygame.sndarray.make_sound(sound_data)
        sound.play()

    def wait_for_space(self):
        """Oczekuje na naciśnięcie spacji przez określony czas."""
        with self.lock:
            self.space_pressed = False
        start_time = time.time()
        while time.time() - start_time < 2: # Czas oczekiwania na odpowiedź
            time.sleep(0.1)
            with self.lock:
                if self.space_pressed:
                    time.sleep(0.5) # Krótka pauza po naciśnięciu spacji
                    break
    
    def on_space_pressed(self):
        """Ustawia flagę space_pressed na True po naciśnięciu spacji."""
        with self.lock:
            self.space_pressed = True

    def stop(self):
        """Zatrzymuje wykonywanie wątku."""
        self.is_running = False

# -----------------------------------------------------------------------------
# Database and Dialogs
# -----------------------------------------------------------------------------

class PatientDatabase:
    """Klasa do zarządzania bazą danych pacjentów i wyników testów."""
    def __init__(self, db_name="audiometry_database.db"):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self._setup_database()
        self.current_patient = None

    def _setup_database(self):
        """Tworzy tabele w bazie danych, jeśli nie istnieją."""
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS patients (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                surname TEXT NOT NULL,
                dob TEXT NOT NULL,
                pesel TEXT,
                gender TEXT,
                notes TEXT
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS tests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id TEXT,
                timestamp TEXT,
                results TEXT, -- Będzie przechowywać JSON z wynikami i trybem testu
                FOREIGN KEY (patient_id) REFERENCES patients(id)
            )
        ''')
        self.conn.commit()

    def add_patient(self, name, surname, dob, patient_id, pesel, gender, notes):
        """
        Dodaje nowego pacjenta do bazy danych.
        :return: True jeśli dodano, False jeśli ID już istnieje.
        """
        try:
            self.cursor.execute("INSERT INTO patients (id, name, surname, dob, pesel, gender, notes) VALUES (?, ?, ?, ?, ?, ?, ?)",
                                 (patient_id, name, surname, dob, pesel, gender, notes))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def update_patient_notes(self, patient_id, notes):
        """Aktualizuje notatki dla danego pacjenta."""
        self.cursor.execute("UPDATE patients SET notes = ? WHERE id = ?", (notes, patient_id))
        self.conn.commit()

    def get_patients(self):
        """Pobiera listę wszystkich pacjentów."""
        self.cursor.execute("SELECT id, name, surname, dob, pesel, gender, notes FROM patients ORDER BY surname, name")
        patients_data = self.cursor.fetchall()
        patients = [{'id': p[0], 'name': p[1], 'surname': p[2], 'dob': p[3], 'pesel': p[4], 'gender': p[5], 'notes': p[6]} for p in patients_data]
        return patients
    
    def get_patient_by_id(self, patient_id):
        """Pobiera dane pacjenta po jego ID."""
        self.cursor.execute("SELECT id, name, surname, dob, pesel, gender, notes FROM patients WHERE id = ?", (patient_id,))
        p = self.cursor.fetchone()
        if p:
            return {'id': p[0], 'name': p[1], 'surname': p[2], 'dob': p[3], 'pesel': p[4], 'gender': p[5], 'notes': p[6]}
        return None

    def get_tests_by_patient_id(self, patient_id):
        """
        Pobiera historię testów dla danego pacjenta.
        Zwraca listę słowników, gdzie każdy słownik zawiera 'timestamp', 'results' i 'test_mode'.
        """
        self.cursor.execute("SELECT timestamp, results FROM tests WHERE patient_id = ? ORDER BY timestamp DESC", (patient_id,))
        tests_data = self.cursor.fetchall()
        tests = []
        for test_data_row in tests_data:
            loaded_json = json.loads(test_data_row[1])
            # Zakładamy, że 'results' w JSON zawiera 'left', 'right' i 'test_mode'
            # Jeśli 'test_mode' nie istnieje (stare dane), domyślnie ustawiamy na 'Obuusznie'
            tests.append({
                'timestamp': test_data_row[0],
                'results': {
                    'left': loaded_json.get('left', {}),
                    'right': loaded_json.get('right', {})
                },
                'test_mode': loaded_json.get('test_mode', 'Obuusznie') 
            })
        return tests

    def add_test_result(self, patient_id, test_result, test_mode):
        """
        Dodaje wynik testu do bazy danych dla danego pacjenta.
        :param patient_id: ID pacjenta.
        :param test_result: Słownik z wynikami testu dla lewego i prawego ucha.
        :param test_mode: Tryb testu, w którym został przeprowadzony test.
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Konwertujemy klucze int na stringi dla kompatybilności JSON
        results_to_save = {
            'left': {str(k): v for k, v in test_result.get('left', {}).items()},
            'right': {str(k): v for k, v in test_result.get('right', {}).items()},
            'test_mode': test_mode # Zapisujemy tryb testu
        }
        
        results_json = json.dumps(convert_numpy(results_to_save))
        self.cursor.execute("INSERT INTO tests (patient_id, timestamp, results) VALUES (?, ?, ?)",
                             (patient_id, timestamp, results_json))
        self.conn.commit()
        return True
        
    def delete_patient(self, patient_id):
        """Usuwa pacjenta i wszystkie jego testy z bazy danych."""
        self.cursor.execute("DELETE FROM tests WHERE patient_id = ?", (patient_id,))
        self.cursor.execute("DELETE FROM patients WHERE id = ?", (patient_id,))
        self.conn.commit()
        if self.current_patient and self.current_patient['id'] == patient_id:
            self.current_patient = None
            
    def close(self):
        """Zamyka połączenie z bazą danych."""
        self.conn.close()


class AddPatientDialog(QDialog):
    """Okno dialogowe do dodawania nowego pacjenta."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(400, 450)
        self.set_dark_mode()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0,0,0,0)
        
        self.title_bar = CustomDialogTitleBar(self, "Dodaj nowego pacjenta")
        main_layout.addWidget(self.title_bar)
        
        content_widget = QWidget()
        self.layout = QFormLayout(content_widget)
        
        self.name_input = QLineEdit()
        self.surname_input = QLineEdit()
        self.dob_input = QLineEdit()
        self.id_input = QLineEdit()
        self.pesel_input = QLineEdit()
        self.notes_input = QTextEdit()

        self.name_input.setStyleSheet(CHROME_TEXTBOX_STYLE)
        self.surname_input.setStyleSheet(CHROME_TEXTBOX_STYLE)
        self.dob_input.setStyleSheet(CHROME_TEXTBOX_STYLE)
        self.id_input.setStyleSheet(CHROME_TEXTBOX_STYLE)
        self.pesel_input.setStyleSheet(CHROME_TEXTBOX_STYLE)
        self.notes_input.setStyleSheet(CHROME_TEXTBOX_STYLE)
        
        self.gender_combo = QComboBox()
        self.gender_combo.addItems(["Mężczyzna", "Kobieta", "Inne"])
        self.gender_combo.setStyleSheet(
            """
            QComboBox {
                background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                        stop:1 #3e3e3e, stop:0 #1f1f1f);
                padding: 4px;
                color: white;
                border: 1px solid #8f8f8f;
                border-radius: 4px;
            }
            QComboBox::drop-down {
                border: 0px;
            }
            QComboBox::down-arrow {
                image: url(data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAABmJLR0QA/wD/AP+gvaeTAAAAVElEQVQ4jWNgGAWjYBSMglGwAkYGBkZGBgYGhiwGIAYxMTAw/g/E/wXih2FmYGBgYGJgYGD4D4z/B8J/hJGBgQGYGNgAAgABBgYGBgYGBgYGBgAAADfE/14A+P8AAAAASUVORK5CYII=);
                width: 16px;
                height: 16px;
            }
        """)

        self.layout.addRow("Imię:", self.name_input)
        self.layout.addRow("Nazwisko:", self.surname_input)
        self.layout.addRow("Data urodzenia:", self.dob_input)
        self.layout.addRow("ID pacjenta:", self.id_input)
        self.layout.addRow("PESEL:", self.pesel_input)
        self.layout.addRow("Płeć:", self.gender_combo)
        self.layout.addRow("Notatki:", self.notes_input)

        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        
        for button in self.button_box.buttons():
            button.setStyleSheet(CHROME_BUTTON_STYLE)

        self.layout.addWidget(self.button_box)
        main_layout.addWidget(content_widget)

    def set_dark_mode(self):
        """Ustawia ciemny motyw dla okna dialogowego."""
        palette = self.palette()
        dark_mode_color = QColor("#1e1e1e")
        text_color = QColor("#f0f0f0")
        palette.setColor(QPalette.Window, dark_mode_color)
        palette.setColor(QPalette.WindowText, text_color)
        palette.setColor(QPalette.Base, QColor("#2d2d2d"))
        palette.setColor(QPalette.Text, text_color)
        self.setPalette(palette)

    def get_data(self):
        """Zwraca dane wprowadzone przez użytkownika."""
        return (
            self.name_input.text(),
            self.surname_input.text(),
            self.dob_input.text(),
            self.id_input.text(),
            self.pesel_input.text(),
            self.gender_combo.currentText(),
            self.notes_input.toPlainText()
        )

class PatientDetailsDialog(QDialog):
    """Okno dialogowe do wyświetlania i edycji szczegółów pacjenta."""
    def __init__(self, patient_data, database, parent=None):
        super().__init__(parent)
        self.resize(500, 500)
        self.set_dark_mode()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.patient_data = patient_data
        self.database = database
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0,0,0,0)
        
        self.title_bar = CustomDialogTitleBar(self, f"Szczegóły pacjenta: {patient_data['name']} {patient_data['surname']}")
        main_layout.addWidget(self.title_bar)
        
        content_widget = QWidget()
        layout = QFormLayout(content_widget)
        
        self.name_label = QLabel(f"Imię: {self.patient_data['name']}")
        self.surname_label = QLabel(f"Nazwisko: {self.patient_data['surname']}")
        self.dob_label = QLabel(f"Data urodzenia: {self.patient_data['dob']}")
        self.id_label = QLabel(f"ID pacjenta: {self.patient_data['id']}")
        self.pesel_label = QLabel(f"PESEL: {self.patient_data['pesel']}")
        self.gender_label = QLabel(f"Płeć: {self.patient_data['gender']}")
        
        self.notes_label = QLabel("Notatki:")
        self.notes_edit = QTextEdit()
        self.notes_edit.setPlainText(self.patient_data['notes'])
        
        # Zastosowanie stylu do QTextEdit
        self.notes_edit.setStyleSheet(CHROME_TEXTBOX_STYLE)

        layout.addRow(self.name_label)
        layout.addRow(self.surname_label)
        layout.addRow(self.dob_label)
        layout.addRow(self.id_label)
        layout.addRow(self.pesel_label)
        layout.addRow(self.gender_label)
        layout.addRow(self.notes_label)
        layout.addRow(self.notes_edit)
        
        self.button_box = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        self.button_box.button(QDialogButtonBox.Save).setText("Zapisz notatki")
        self.button_box.accepted.connect(self.save_notes)
        self.button_box.rejected.connect(self.reject)
        
        # Zastosowanie stylu do przycisków
        for button in self.button_box.buttons():
            button.setStyleSheet(CHROME_BUTTON_STYLE)
            
        layout.addWidget(self.button_box)
        main_layout.addWidget(content_widget)
        
    def set_dark_mode(self):
        """Ustawia ciemny motyw dla okna dialogowego."""
        palette = self.palette()
        dark_mode_color = QColor("#1e1e1e")
        text_color = QColor("#f0f0f0")
        palette.setColor(QPalette.Window, dark_mode_color)
        palette.setColor(QPalette.WindowText, text_color)
        palette.setColor(QPalette.Base, QColor("#2d2d2d"))
        palette.setColor(QPalette.Text, text_color)
        self.setPalette(palette)
        
    def save_notes(self):
        """Zapisuje zmienione notatki do bazy danych."""
        new_notes = self.notes_edit.toPlainText()
        self.database.update_patient_notes(self.patient_data['id'], new_notes)
        
        msg_box = QMessageBox(self)
        msg_box.setStyleSheet(MESSAGE_BOX_STYLE)
        msg_box.setWindowTitle("Zapisano")
        msg_box.setText("Notatki zostały zaktualizowane.")
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec()
        
        self.accept()


class ShowResultDialog(QDialog):
    """Okno dialogowe do wyświetlania wyników pojedynczego testu."""
    def __init__(self, patient_data, test_data, parent=None):
        super().__init__(parent)
        self.resize(800, 500)
        self.set_dark_mode()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0,0,0,0)
        
        self.title_bar = CustomDialogTitleBar(self, f"Wyniki testu dla {patient_data['name']} {patient_data['surname']}")
        main_layout.addWidget(self.title_bar)
        
        content_widget = QWidget()
        layout = QVBoxLayout(content_widget)
        
        # Używamy jednego wykresu dla obu uszu
        self.fig, self.ax = plt.subplots(figsize=(10, 5))
        self.fig.set_facecolor('#1e1e1e')
        
        self.canvas = FigureCanvas(self.fig)
        layout.addWidget(self.canvas)
        
        self.setup_plot(self.ax)
        self.draw_audiogram_from_results(test_data)
        
        main_layout.addWidget(content_widget)

    def set_dark_mode(self):
        """Ustawia ciemny motyw dla okna dialogowego."""
        palette = self.palette()
        dark_mode_color = QColor("#1e1e1e")
        text_color = QColor("#f0f0f0")
        palette.setColor(QPalette.Window, dark_mode_color)
        palette.setColor(QPalette.WindowText, text_color)
        palette.setColor(QPalette.Base, QColor("#2d2d2d"))
        palette.setColor(QPalette.Text, text_color)
        self.setPalette(palette)

    def setup_plot(self, ax):
        """
        Konfiguruje wygląd pojedynczego wykresu audiogramu.
        :param ax: Obiekt osi matplotlib.
        """
        ax.set_title("Audiogram", color='white')
        ax.set_xlabel("Częstotliwość (Hz)", color='white')
        ax.set_ylabel("Poziom (dB HL)", color='white')
        
        ax.set_xlim(-0.5, len(FREQUENCIES) - 0.5)
        ax.set_xticks(range(len(FREQUENCIES)))
        ax.set_xticklabels([str(f) for f in FREQUENCIES], color='white')
        
        ax.set_ylim(110, -10) # Odwrócona oś Y
        ax.set_yticks(np.arange(0, 110, 10))
        ax.set_yticklabels([str(db) for db in np.arange(0, 110, 10)], color='white')
        
        ax.grid(True, linestyle='--', alpha=0.6, color='gray')
        
        ax.spines['bottom'].set_color('white')
        ax.spines['top'].set_color('white')
        ax.spines['left'].set_color('white')
        ax.spines['right'].set_color('white')
        ax.tick_params(axis='x', colors='white')
        ax.tick_params(axis='y', colors='white')

    def draw_audiogram_from_results(self, test_data):
        """
        Rysuje audiogram na podstawie wyników testu i trybu testu na jednym wykresie.
        :param test_data: Słownik zawierający 'results' (z 'left' i 'right') oraz 'test_mode'.
        """
        self.ax.clear()
        self.setup_plot(self.ax)
        
        results = test_data.get('results', {'left': {}, 'right': {}})
        test_mode = test_data.get('test_mode', 'Obuusznie') # Domyślnie 'Obuusznie' dla starszych danych

        left_results = results.get('left', {})
        right_results = results.get('right', {})

        if left_results and test_mode in ["Obuusznie", "Ucho lewe"]:
            freq_indices = sorted([int(k) for k in left_results.keys()])
            dbs = [left_results[str(i)] for i in freq_indices]
            self.ax.plot(freq_indices, dbs, 'o-', color='blue', markersize=8, label='Ucho lewe')
            
        if right_results and test_mode in ["Obuusznie", "Ucho prawe"]:
            freq_indices = sorted([int(k) for k in right_results.keys()])
            dbs = [right_results[str(i)] for i in freq_indices]
            self.ax.plot(freq_indices, dbs, 'x-', color='red', markersize=8, label='Ucho prawe')
            
        self.ax.legend(loc='lower right', facecolor='#1e1e1e', edgecolor='white', labelcolor='white')
        
        self.canvas.draw()


# -----------------------------------------------------------------------------
# Main Application Window
# -----------------------------------------------------------------------------

class AudiometryApp(QMainWindow):
    """Główna aplikacja audiometryczna."""

    def __init__(self):
        super().__init__()
        # self.setWindowTitle("HB Audio Suite") # No longer needed with custom title bar
        self.setGeometry(100, 100, 1600, 1225)

        # Set frameless window hint before creating the layout
        self.setWindowFlags(Qt.FramelessWindowHint)

        self.set_dark_mode()
        self.database = PatientDatabase()
        self.current_patient = None
        self.patient_tests = []
        self.worker_thread = None
        self.results = {'left': {}, 'right': {}}

        self.create_widgets()
        self.setup_connections()
        self.update_patient_list()

        # ... (disable buttons logic) ...
        self.start_button.setEnabled(False)
        self.delete_patient_button.setEnabled(False)
        self.patient_details_button.setEnabled(False)


    def set_dark_mode(self):
        """Ustawia ciemny motyw dla całej aplikacji."""
        palette = self.palette()
        dark_mode_color = QColor("#1e1e1e")
        text_color = QColor("#f0f0f0")
        
        palette.setColor(QPalette.Window, dark_mode_color)
        palette.setColor(QPalette.WindowText, text_color)
        palette.setColor(QPalette.Base, QColor("#2d2d2d"))
        palette.setColor(QPalette.AlternateBase, QColor("#3c3c3c"))
        palette.setColor(QPalette.ToolTipBase, dark_mode_color)
        palette.setColor(QPalette.ToolTipText, text_color)
        palette.setColor(QPalette.Text, text_color)
        palette.setColor(QPalette.Button, QColor("#4e4e4e"))
        palette.setColor(QPalette.ButtonText, text_color)
        palette.setColor(QPalette.BrightText, QColor("red"))
        palette.setColor(QPalette.Highlight, QColor("#1f67b5"))
        palette.setColor(QPalette.HighlightedText, QColor("black"))
        
        self.setPalette(palette)
        
    def create_widgets(self):
        """Tworzy wszystkie elementy interfejsu użytkownika."""
        # Main layout for the entire window
        main_container = QWidget()
        self.setCentralWidget(main_container)
        main_layout = QVBoxLayout(main_container)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Add the custom title bar at the top
        self.title_bar = CustomTitleBar(self)
        main_layout.addWidget(self.title_bar)

        # The rest of your existing application content
        app_content = QWidget()
        app_content_layout = QHBoxLayout(app_content)
        main_layout.addWidget(app_content)
        
        # Lewy panel - baza pacjentów i historia testów
        left_panel = QSplitter(Qt.Vertical)
        
        # Panel bazy pacjentów
        patient_panel = QFrame()
        patient_panel.setFrameShape(QFrame.StyledPanel)
        patient_layout = QVBoxLayout(patient_panel)
        
        patient_label = QLabel("Baza pacjentów")
        patient_label.setFont(QFont("Arial", 12, QFont.Bold))
        patient_layout.addWidget(patient_label, alignment=Qt.AlignLeft)
        
        # Pasek wyszukiwania pacjentów
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Wyszukaj pacjenta (imię, nazwisko, ID)")
        self.search_bar.setStyleSheet(CHROME_TEXTBOX_STYLE)
        patient_layout.addWidget(self.search_bar)
        
        self.patient_list = QListWidget()
        self.patient_list.setStyleSheet("""
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
    """)
        patient_layout.addWidget(self.patient_list)

        # Sekcja przycisków
        button_layout = QVBoxLayout()

        add_patient_button = QPushButton("Dodaj nowego pacjenta")
        button_layout.addWidget(add_patient_button)
        add_patient_button.clicked.connect(self.add_patient)
        
        self.patient_details_button = QPushButton("Szczegóły pacjenta")
        button_layout.addWidget(self.patient_details_button)
        self.patient_details_button.clicked.connect(self.show_patient_details)

        self.delete_patient_button = QPushButton("Usuń pacjenta")
        button_layout.addWidget(self.delete_patient_button)
        self.delete_patient_button.clicked.connect(self.delete_patient)
        
        patient_layout.addLayout(button_layout)

        # Panel historii testów
        history_panel = QFrame()
        history_panel.setFrameShape(QFrame.StyledPanel)
        history_layout = QVBoxLayout(history_panel)
        history_label = QLabel("Zapisane sesje")
        history_label.setFont(QFont("Arial", 12, QFont.Bold))
        history_layout.addWidget(history_label)

        self.test_history_list = QListWidget()
        self.test_history_list.setStyleSheet(self.patient_list.styleSheet())
        history_layout.addWidget(self.test_history_list)

        left_panel.addWidget(patient_panel)
        left_panel.addWidget(history_panel)
        left_panel.setSizes([350, 350])
        

        # Styl dla przycisków
        add_patient_button.setStyleSheet(CHROME_BUTTON_STYLE)
        self.delete_patient_button.setStyleSheet(CHROME_BUTTON_STYLE)
        self.patient_details_button.setStyleSheet(CHROME_BUTTON_STYLE)

        app_content_layout.addWidget(left_panel) # Use app_content_layout here
        
        # Prawy panel - audiometria
        audiometry_panel = QFrame()
        audiometry_panel.setFrameShape(QFrame.StyledPanel)
        audiometry_layout = QVBoxLayout(audiometry_panel)
        
        self.patient_info_label = QLabel("Najpierw wybierz pacjenta.")
        self.patient_info_label.setFont(QFont("Arial", 12, QFont.Bold))
        self.patient_info_label.setAlignment(Qt.AlignLeft)
        audiometry_layout.addWidget(self.patient_info_label)

        # Wykresy (pojedynczy wykres)
        chart_frame = QFrame()
        chart_frame.setFrameShape(QFrame.StyledPanel)
        chart_layout = QHBoxLayout(chart_frame)

        plt.style.use('dark_background')
        self.fig, self.ax = plt.subplots(figsize=(10, 5))
        self.fig.set_facecolor('#1e1e1e')

        self.canvas = FigureCanvas(self.fig)
        self.canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        chart_layout.addWidget(self.canvas)
        
        self.setup_plot(self.ax)
        
        audiometry_layout.addWidget(chart_frame)

        # Ramka na kontrolki
        control_frame = QFrame()
        control_frame.setFrameShape(QFrame.StyledPanel)
        control_layout = QHBoxLayout(control_frame)
        
        # Ramka na ustawienia
        settings_frame = QFrame()
        settings_layout = QHBoxLayout(settings_frame)
        settings_layout.setContentsMargins(0, 0, 0, 0)
        
        settings_label = QLabel("Ustawienia sygnału:")
        settings_label.setFont(QFont("Arial", 10, QFont.Bold))
        settings_layout.addWidget(settings_label)
        
        # Wybór typu sygnału
        self.signal_type_combo = QComboBox()
        self.signal_type_combo.addItems(["sine", "square", "pulse"])
        settings_layout.addWidget(QLabel("Typ sygnału:"))
        settings_layout.addWidget(self.signal_type_combo)
        
        combo_style = """
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

        self.signal_type_combo.setStyleSheet(combo_style)

        # Nowy: Dropdown Tryb testu
        self.test_mode_combo = QComboBox()
        self.test_mode_combo.addItems(["Obuusznie", "Ucho lewe", "Ucho prawe"])
        settings_layout.addWidget(QLabel("Tryb testu:"))
        settings_layout.addWidget(self.test_mode_combo)
        self.test_mode_combo.setStyleSheet(combo_style) # Zastosowanie tego samego stylu
        self.test_mode_combo.currentIndexChanged.connect(self.on_test_mode_changed)


        # Korekcja dB FS
        self.db_fs_entry = QLineEdit("-40.0")
        self.db_fs_entry.setFixedWidth(50)
        settings_layout.addWidget(QLabel("Korekcja dBFS na dBHL:"))
        settings_layout.addWidget(self.db_fs_entry)
        
        control_layout.addWidget(settings_frame)
        
        self.db_fs_entry.setStyleSheet(CHROME_TEXTBOX_STYLE)

        # Przycisk "Start" z gradientem
        self.start_button = QPushButton("Start")
        self.start_button.setFixedWidth(100)
        self.start_button.setStyleSheet("""
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
        """)
        control_layout.addWidget(self.start_button)
        control_layout.addStretch()
        
        audiometry_layout.addWidget(control_frame)

        app_content_layout.addWidget(audiometry_panel)
        
        # Pasek statusu
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Gotowy do testu.")
        
    def setup_connections(self):
        """Konfiguruje połączenia sygnałów i slotów."""
        self.start_button.clicked.connect(self.start_test)
        self.setFocusPolicy(Qt.StrongFocus)
        self.setFocus()
        self.patient_list.itemClicked.connect(self.select_patient)
        self.search_bar.textChanged.connect(self.filter_patients)
        self.test_history_list.itemDoubleClicked.connect(self.show_test_results_from_history)

        
    def add_patient(self):
        """Otwiera okno dialogowe do dodawania nowego pacjenta."""
        dialog = AddPatientDialog(self)
        if dialog.exec() == QDialog.Accepted:
            name, surname, dob, patient_id, pesel, gender, notes = dialog.get_data()
            if not all([name, surname, dob, patient_id]):
                msg_box = QMessageBox(self)
                msg_box.setStyleSheet(MESSAGE_BOX_STYLE)
                msg_box.setWindowTitle("Błąd")
                msg_box.setText("Pola: Imię, Nazwisko, Data urodzenia i ID pacjenta muszą być wypełnione.")
                msg_box.setIcon(QMessageBox.Warning)
                msg_box.setStandardButtons(QMessageBox.Ok)
                msg_box.exec()
                return
            
            if not self.database.add_patient(name, surname, dob, patient_id, pesel, gender, notes):
                msg_box = QMessageBox(self)
                msg_box.setStyleSheet(MESSAGE_BOX_STYLE)
                msg_box.setWindowTitle("Błąd")
                msg_box.setText("Pacjent o podanym ID już istnieje.")
                msg_box.setIcon(QMessageBox.Warning)
                msg_box.setStandardButtons(QMessageBox.Ok)
                msg_box.exec()
                return

            self.update_patient_list()
            msg_box = QMessageBox(self)
            msg_box.setStyleSheet(MESSAGE_BOX_STYLE)
            msg_box.setWindowTitle("Sukces")
            msg_box.setText(f"Dodano nowego pacjenta: {name} {surname}")
            msg_box.setIcon(QMessageBox.Information)
            msg_box.setStandardButtons(QMessageBox.Ok)
            msg_box.exec()

    def show_patient_details(self):
        """Otwiera okno z detalami pacjenta, w tym z edycją notatek."""
        if not self.current_patient:
            msg_box = QMessageBox(self)
            msg_box.setStyleSheet(MESSAGE_BOX_STYLE)
            msg_box.setWindowTitle("Błąd")
            msg_box.setText("Proszę wybrać pacjenta, aby zobaczyć szczegóły.")
            msg_box.setIcon(QMessageBox.Warning)
            msg_box.setStandardButtons(QMessageBox.Ok)
            msg_box.exec()
            return

        dialog = PatientDetailsDialog(self.current_patient, self.database, self)
        if dialog.exec() == QDialog.Accepted:
            # Ponownie wczytaj dane pacjenta, aby zaktualizować 'current_patient'
            self.current_patient = self.database.get_patient_by_id(self.current_patient['id'])
            self.update_patient_list()

    def delete_patient(self):
        """Usuwa wybranego pacjenta z bazy danych."""
        if not self.current_patient:
            msg_box = QMessageBox(self)
            msg_box.setStyleSheet(MESSAGE_BOX_STYLE)
            msg_box.setWindowTitle("Błąd")
            msg_box.setText("Proszę wybrać pacjenta do usunięcia.")
            msg_box.setIcon(QMessageBox.Warning)
            msg_box.setStandardButtons(QMessageBox.Ok)
            msg_box.exec()
            return
        
        msg_box = QMessageBox(self)
        msg_box.setStyleSheet(MESSAGE_BOX_STYLE)
        msg_box.setWindowTitle("Potwierdź usunięcie")
        msg_box.setText(f"Czy na pewno chcesz usunąć pacjenta {self.current_patient['name']} {self.current_patient['surname']} (ID: {self.current_patient['id']}) wraz z całą jego historią testów?")
        msg_box.setIcon(QMessageBox.Question)
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg_box.setDefaultButton(QMessageBox.No)

        reply = msg_box.exec()

        if reply == QMessageBox.Yes:
            self.database.delete_patient(self.current_patient['id'])
            self.update_patient_list()
            self.clear_patient_selection()
            
            msg_box = QMessageBox(self)
            msg_box.setStyleSheet(MESSAGE_BOX_STYLE)
            msg_box.setWindowTitle("Sukces")
            msg_box.setText("Pacjent został usunięty.")
            msg_box.setIcon(QMessageBox.Information)
            msg_box.setStandardButtons(QMessageBox.Ok)
            msg_box.exec()

    def update_patient_list(self):
        """Aktualizuje listę pacjentów w interfejsie."""
        self.patient_list.clear()
        for patient in self.database.get_patients():
            self.patient_list.addItem(f"{patient['name']} {patient['surname']} ({patient['id']})")
            
    def select_patient(self, item):
        """
        Obsługuje wybór pacjenta z listy.
        Aktualizuje informacje o pacjencie i wyświetla jego historię testów.
        """
        patient_id = item.text().split('(')[-1].replace(')', '')
        self.current_patient = self.database.get_patient_by_id(patient_id)
        self.patient_info_label.setText(f"Wybrano pacjenta: {self.current_patient['name']} {self.current_patient['surname']} (ID: {self.current_patient['id']})")
        
        self.start_button.setEnabled(True)
        self.delete_patient_button.setEnabled(True)
        self.patient_details_button.setEnabled(True)
        
        self.clear_plots()
        self.update_test_history_list()
        
    def update_test_history_list(self):
        """
        Pobiera i wyświetla historię testów dla aktualnie wybranego pacjenta.
        """
        self.test_history_list.clear()
        if self.current_patient:
            self.patient_tests = self.database.get_tests_by_patient_id(self.current_patient['id'])
            for test in self.patient_tests:
                display_text = f"{test['timestamp']} (Tryb: {test['test_mode']})"
                self.test_history_list.addItem(display_text)
            
            # Wyświetl automatycznie ostatni test, jeśli istnieje
            if self.patient_tests:
                self.draw_audiogram_on_main_window(self.patient_tests[0])

    def show_test_results_from_history(self, item):
        """
        Wyświetla szczegółowe wyniki wybranego testu z panelu historii.
        """
        timestamp_from_item = item.text().split(' (Tryb:')[0]
        selected_test = next((test for test in self.patient_tests if test['timestamp'] == timestamp_from_item), None)
        
        if selected_test:
            self.draw_audiogram_on_main_window(selected_test)

    def filter_patients(self, text):
        """Filtruje listę pacjentów na podstawie wprowadzonego tekstu."""
        self.patient_list.clear()
        search_text = text.lower()
        for patient in self.database.get_patients():
            full_name = f"{patient['name']} {patient['surname']}".lower()
            patient_id = patient['id'].lower()
            if search_text in full_name or search_text in patient_id:
                self.patient_list.addItem(f"{patient['name']} {patient['surname']} ({patient['id']})")

    def clear_patient_selection(self):
        """Czyści wybór pacjenta i resetuje interfejs."""
        self.current_patient = None
        self.patient_info_label.setText("Proszę wybrać pacjenta z listy.")
        self.clear_plots()
        self.test_history_list.clear()
        self.start_button.setEnabled(False)
        self.delete_patient_button.setEnabled(False)
        self.patient_details_button.setEnabled(False)
        self.patient_tests = []

    def clear_plots(self):
        """Czyści wykres i resetuje jego stan."""
        self.ax.clear()
        self.setup_plot(self.ax)
        self.results = {'left': {}, 'right': {}}
        self.canvas.draw()

    def draw_audiogram_on_main_window(self, test_data):
        """
        Rysuje audiogram na głównym oknie na podstawie wyników testu i trybu testu, na jednym wykresie.
        :param test_data: Słownik zawierający 'results' (z 'left' i 'right') oraz 'test_mode'.
        """
        self.clear_plots() # Wyczyść przed rysowaniem
        
        results = test_data.get('results', {'left': {}, 'right': {}})
        test_mode = test_data.get('test_mode', 'Obuusznie') # Domyślnie 'Obuusznie' dla starszych danych

        left_results = results.get('left', {})
        right_results = results.get('right', {})
        
        lines_to_draw = []

        if left_results and test_mode in ["Obuusznie", "Ucho lewe"]:
            freq_indices = sorted([int(k) for k in left_results.keys()])
            dbs = [left_results[str(i)] for i in freq_indices]
            lines_to_draw.append(('left', freq_indices, dbs))

        if right_results and test_mode in ["Obuusznie", "Ucho prawe"]:
            freq_indices = sorted([int(k) for k in right_results.keys()])
            dbs = [right_results[str(i)] for i in freq_indices]
            lines_to_draw.append(('right', freq_indices, dbs))
        
        # Rysowanie linii i punktów
        for ear, freqs, dbs in lines_to_draw:
            color = 'blue' if ear == 'left' else 'red'
            marker = 'o' if ear == 'left' else 'x'
            label = 'Ucho lewe' if ear == 'left' else 'Ucho prawe'

            # Rysowanie linii
            self.ax.plot(freqs, dbs, '-', color=color)
            # Rysowanie punktów
            self.ax.plot(freqs, dbs, marker, color=color, markersize=8, label=label)

        if lines_to_draw:
            self.ax.legend(loc='lower right', facecolor='#1e1e1e', edgecolor='white', labelcolor='white')
        
        self.canvas.draw()

    def on_test_mode_changed(self, index):
        """
        Obsługuje zmianę trybu testu w dropdownie.
        Wyczyść wykresy po zmianie trybu, aby uniknąć mylących danych.
        """
        self.clear_plots()


    def keyPressEvent(self, event):
        """Obsługuje naciśnięcia klawiszy, w tym spację do sygnalizowania odpowiedzi."""
        if event.key() == Qt.Key_Space:
            if self.worker_thread and self.worker_thread.isRunning():
                self.worker_thread.on_space_pressed()

    def start_test(self):
        """Rozpoczyna test audiometryczny."""
        if not self.current_patient:
            msg_box = QMessageBox(self)
            msg_box.setStyleSheet(MESSAGE_BOX_STYLE)
            msg_box.setWindowTitle("Błąd")
            msg_box.setText("Proszę wybrać pacjenta z listy, aby rozpocząć test.")
            msg_box.setIcon(QMessageBox.Warning)
            msg_box.setStandardButtons(QMessageBox.Ok)
            msg_box.exec()
            return

        self.start_button.setEnabled(False)
        self.status_bar.showMessage("Rozpoczynanie testu...")
        
        self.clear_plots() # Wyczyść wykresy przed nowym testem
        
        try:
            db_fs_correction = float(self.db_fs_entry.text())
        except ValueError:
            self.status_bar.showMessage("Błąd: Nieprawidłowa wartość korekcji dB FS.")
            self.start_button.setEnabled(True)
            return

        signal_type = self.signal_type_combo.currentText()
        test_mode = self.test_mode_combo.currentText() # Pobieranie wybranego trybu testu

        # Inicjalizacja i uruchomienie wątku roboczego z nowym parametrem test_mode
        self.worker_thread = AudiometryWorker(db_fs_correction, signal_type, test_mode)
        self.worker_thread.status_update.connect(self.status_bar.showMessage)
        self.worker_thread.point_found.connect(self.draw_point)
        self.worker_thread.test_finished.connect(self.on_test_finished)
        self.worker_thread.start()

    def setup_plot(self, ax):
        """
        Konfiguruje wygląd pojedynczego wykresu audiogramu.
        :param ax: Obiekt osi matplotlib.
        """
        ax.set_title("Audiogram", color='white')
        ax.set_xlabel("Częstotliwość (Hz)", color='white')
        ax.set_ylabel("Poziom (dB HL)", color='white')
        
        ax.set_xlim(-0.5, len(FREQUENCIES) - 0.5)
        ax.set_xticks(range(len(FREQUENCIES)))
        ax.set_xticklabels([str(f) for f in FREQUENCIES], color='white')
        
        ax.set_ylim(110, -10)
        ax.set_yticks(np.arange(0, 110, 10))
        ax.set_yticklabels([str(db) for db in np.arange(0, 110, 10)], color='white')
        
        ax.grid(True, linestyle='--', alpha=0.6, color='gray')
        
        # Ustawienie kolorów dla ramek i etykiet
        ax.spines['bottom'].set_color('white')
        ax.spines['top'].set_color('white')
        ax.spines['left'].set_color('white')
        ax.spines['right'].set_color('white')
        ax.tick_params(axis='x', colors='white')
        ax.tick_params(axis='y', colors='white')

        self.canvas.draw()
        
    def draw_point(self, freq_index, db_hl, ear):
        """
        Rysuje pojedynczy punkt na wykresie audiogramu.
        :param freq_index: Indeks częstotliwości.
        :param db_hl: Poziom dB HL.
        :param ear: Ucho ('left' lub 'right').
        """
        # Musimy przekonwertować klucze int na stringi dla serializacji/deserializacji JSON
        self.results[ear][str(freq_index)] = db_hl
        
        color = 'blue' if ear == 'left' else 'red'
        marker = 'o' if ear == 'left' else 'x'
        
        self.ax.plot(freq_index, db_hl, marker, color=color, markersize=8)
            
        self.canvas.draw()

        # Narysuj linię, jeśli mamy już co najmniej 2 punkty
        if len(self.results[ear]) >= 2:
            self.draw_audiogram_line(ear)

    def draw_audiogram_line(self, ear):
        """
        Rysuje linię łączącą punkty na audiogramie dla danego ucha.
        :param ear: Ucho ('left' lub 'right').
        """
        freq_indices = sorted([int(k) for k in self.results[ear].keys()])
        if not freq_indices:
            return

        dbs = [self.results[ear][str(i)] for i in freq_indices]
        
        color = 'blue' if ear == 'left' else 'red'
        self.ax.plot(freq_indices, dbs, '-', color=color)
            
        self.canvas.draw()
        
    def on_test_finished(self, results):
        """
        Obsługuje zakończenie testu. Zapisuje wyniki i resetuje stan aplikacji.
        :param results: Słownik z wynikami testu.
        """
        self.status_bar.showMessage("Gotowy do testu.")
        self.start_button.setEnabled(True)
        self.worker_thread = None
        
        if self.current_patient:
            test_mode_used = self.test_mode_combo.currentText() # Pobieramy tryb testu użyty w teście
            self.database.add_test_result(self.current_patient['id'], results, test_mode_used)
            msg_box = QMessageBox(self)
            msg_box.setStyleSheet(MESSAGE_BOX_STYLE)
            msg_box.setWindowTitle("Test zakończony")
            msg_box.setText(f"Zapisano wyniki dla pacjenta: {self.current_patient['name']} {self.current_patient['surname']}")
            msg_box.setIcon(QMessageBox.Information)
            msg_box.setStandardButtons(QMessageBox.Ok)
            msg_box.exec()
            self.update_test_history_list()

    def closeEvent(self, event: QCloseEvent):
        """Obsługuje zdarzenie zamknięcia aplikacji."""
        if self.worker_thread and self.worker_thread.isRunning():
            self.worker_thread.stop()
            self.worker_thread.wait()
        self.database.close()
        event.accept()

def show_main_window(splash, window):
    """Closes the splash screen and shows the main window."""
    splash.close()
    window.show()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Wczytaj obrazek splash screen
    splash_pixmap = QPixmap("splash.png")
    
    # Utwórz splash screen z obrazkiem
    splash = QSplashScreen(splash_pixmap)
    splash.show()
    
    window = AudiometryApp()
    # Symuluj ładowanie aplikacji
    QTimer.singleShot(1500, lambda: show_main_window(splash, window))
    
    sys.exit(app.exec())
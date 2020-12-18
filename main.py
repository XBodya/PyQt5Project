# Импорт всех необходимых библиотек
from MainWindow import Ui_MainWindow
from TextEditor import Ui_Editor
from ImageView import Ui_ImageView
from DeleteHistory import Ui_DeleteHistory
from MusicPlayer import Ui_MusicPlayer

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtMultimedia import *
from PyQt5.QtCore import *
from PyQt5.QtMultimediaWidgets import *

import sys
import csv
import sqlite3
from datetime import datetime
from pathlib import Path

from PIL import Image

LastFiles = []
OpenedFiles = []


# Ф-ция для определения размера файла
def file_size(path):
    file = Path(path)
    size = file.stat().st_size
    if size < 1024:
        return '{} {}'.format(size, 'B')
    names = {
        0: 'B',
        1: 'KB',
        2: 'MB',
        3: 'GB',
        4: 'TB',
        5: 'PB'
    }
    n = 1
    while (not (size >> (10 * n))) and n <= 4:
        n += 1
    return '{} {}'.format(size >> (10 * n), names[n])


# Добавление данных в БД
def add_database_history(filepath, filename, filetype):
    connect = sqlite3.connect('historyfiles.db')
    cursor = connect.cursor()
    res = cursor.execute("""
    SELECT id FROM TYPES
    """).fetchall()
    if not res:
        cursor.execute("""
        INSERT INTO TYPES(id, type) VALUES(1, '{}')
        """.format(filetype))
        connect.commit()
    else:
        search_type = cursor.execute("""
        SELECT id FROM TYPES
            WHERE type = '{}'
        """.format('{}'.format(filetype))).fetchall()
        if not search_type:
            current_id = max(list(map(lambda x: x[0], res))) + 1
            cursor.execute("""
            INSERT INTO TYPES(id, type) VALUES({}, '{}')
            """.format(current_id, filetype))
            connect.commit()
        else:
            current_id = search_type[0][0]
    connect.commit()
    id_type = cursor.execute("""
    SELECT id FROM TYPES
        WHERE type = '{}'
    """.format(filetype)).fetchall()[0][0]
    check_repeats = cursor.execute("""
    SELECT title FROM HISTORY
        WHERE (title = '{}') AND (type = {}) AND (size = '{}') AND (path = '{}')
    """.format(filename, id_type, file_size(filepath), filepath)).fetchall()
    if check_repeats:
        cursor.execute("""
        UPDATE HISTORY
        SET opentime = '{}'
        WHERE (title = '{}')
            AND (type = {})
                AND (size = '{}')
                    AND (path = '{}')
        """.format(datetime.today(), filename, id_type, file_size(filepath), filepath))
    else:
        cursor.execute("""
        INSERT INTO HISTORY(title, type, opentime, size, path)
            VALUES('{}', {}, '{}', '{}', '{}')
        """.format(filename, id_type, datetime.today(), file_size(filepath), filepath))
    connect.commit()
    connect.close()


# Окно для просмотра БД
class SecondFormDBViewer(QMainWindow):
    def __init__(self, parent):
        self.parents = parent
        super().__init__(parent)
        self.setWindowIcon(QIcon('driveharddisk_92587.ico'))
        self.menu_bar = self.menuBar()
        self.db_operation = self.menu_bar.addMenu('БД')
        self.db_operation.addAction(self.delete_all_action())
        connect = sqlite3.connect('historyfiles.db')
        cursor = connect.cursor()
        sql_table = cursor.execute("""
        SELECT title, type, opentime, size, path FROM HISTORY
        """).fetchall()
        sql_type_file = cursor.execute("""
        SELECT id, type FROM TYPES  
        """).fetchall()
        type_files = {}
        for i in sql_type_file:
            type_files[i[0]] = i[1]
        self.setMinimumSize(880, 90)
        self.setWindowTitle("БД по файлам")
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        grid_layout = QGridLayout()
        central_widget.setLayout(grid_layout)
        self.table = QTableWidget(self)
        self.table.setColumnCount(5)
        self.table.setRowCount(len(sql_table))
        self.table.setHorizontalHeaderLabels(["Название файла", "Расширение файла",
                                              "Время открытия файла", "Вес файла", "Путь файла"])
        self.table.horizontalHeaderItem(0).setTextAlignment(Qt.AlignLeft)
        self.table.horizontalHeaderItem(1).setTextAlignment(Qt.AlignHCenter)
        self.table.horizontalHeaderItem(2).setTextAlignment(Qt.AlignHCenter)
        self.table.horizontalHeaderItem(3).setTextAlignment(Qt.AlignHCenter)
        self.table.horizontalHeaderItem(4).setTextAlignment(Qt.AlignRight)
        for i in range(len(sql_table)):
            for j in range(5):
                if j == 1:
                    self.table.setItem(i, j,
                                       QTableWidgetItem("{}".format(type_files[sql_table[i][j]])))
                else:
                    self.table.setItem(i, j, QTableWidgetItem("{}".format(sql_table[i][j])))
        self.table.resizeColumnsToContents()
        self.table.setDisabled(True)
        grid_layout.addWidget(self.table, 0, 0)

    def delete_all(self):
        connect = sqlite3.connect('historyfiles.db')
        cursor = connect.cursor()
        res = cursor.execute("""
        DELETE from TYPES
        """)
        cursor.execute("""
        DELETE from HISTORY
        """)
        connect.commit()
        self.__init__(self.parents)
        connect.close()
        self.table.clear()

    def delete_all_action(self):
        delete_all = QAction('Очистить БД', self)
        delete_all.setShortcut('Ctrl+DEL')
        delete_all.triggered.connect(self.delete_all)
        return delete_all

    def keyPressEvent(self, QKeyEvent):
        if int(QKeyEvent.modifiers()) == Qt.CTRL:
            if QKeyEvent.key() == Qt.Key_Delete:
                self.delete_all()
                self.table.clear()


# Окно для просмотра текстовых файлов
class SecondFormText(QMainWindow, Ui_Editor):
    def __init__(self, *args):
        self.args = list(args)
        super().__init__()
        self.setupUi(self)
        self.text_menu_bar = self.menuBar()
        catalog_file = self.text_menu_bar.addMenu('Файл')
        self.setWindowIcon(QIcon('driveharddisk_92587.ico'))
        catalog_file.addAction(self.create_save_text())
        self.setWindowTitle(self.args[2])
        try:
            self.file = open(self.args[1], mode='r', encoding='utf8')
            self.lines = list(map(str, self.file.readlines()))
            self.textEdit.setText(''.join(self.lines))
            self.file.close()
        except EOFError:
            pass
        except FileNotFoundError:
            pass

    def save(self):
        try:
            self.file = open(self.args[1], mode='w', encoding='utf8')
            self.text = self.textEdit.toPlainText()
            self.file.write(self.text)
            self.file.close()
        except EOFError:
            pass
        except FileNotFoundError:
            pass

    def closeEvent(self, event):
        if [self.args[1]] not in LastFiles:
            LastFiles.append([self.args[1]])
        else:
            LastFiles.remove([self.args[1]])
            LastFiles.append([self.args[1]])
        with open('LastFiles.csv', "w", newline='', encoding='utf8') as csv_file:
            writer = csv.writer(csv_file, delimiter=';')
            for line in LastFiles:
                writer.writerow(line)
        self.args[0].history_list.clear()
        self.args[0].history_list.addItems(list(map(lambda x: x[0], LastFiles[::-1])))
        add_database_history(self.args[1], self.args[2], self.args[3])
        OpenedFiles.pop()

    def create_save_text(self):
        save_text = QAction('Сохранить', self)
        save_text.setShortcut('Ctrl+S')
        save_text.setStatusTip('Сохранить файл')
        save_text.triggered.connect(self.save)
        return save_text

    def keyPressEvent(self, QKeyEvent):
        if int(QKeyEvent.modifiers()) == Qt.CTRL:
            if QKeyEvent.key() == Qt.Key_S:
                self.save()


# Окно для просмотра изображений
class SecondFormImage(QMainWindow, Ui_ImageView):
    def __init__(self, *args):
        self.args = list(args)
        self.save = False
        super().__init__()
        self.setWindowIcon(QIcon('driveharddisk_92587.ico'))
        self.image_label = QLabel(self)
        self.setupUi()

    def setupUi(self):
        super().setupUi(self)
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        grid_layout = QGridLayout()
        central_widget.setLayout(grid_layout)
        self.pixMapImage = QPixmap(self.args[1])
        self.pilImage = Image.open(self.args[1])
        self.cPilImage = self.pilImage.copy()
        self.cPilImage.thumbnail((900, 600),
                                 Image.ANTIALIAS)
        self.image_label.setPixmap(self.pixMapImage)
        self.setWindowTitle(self.args[2])
        grid_layout.addWidget(self.image_label, 0, 0)

    def closeEvent(self, event):
        if not self.save:
            self.cPilImage = self.pilImage.copy()
            self.pixels = self.cPilImage.load()
            self.cPilImage.save(self.args[1])
            self.pixMapImage = QPixmap(self.args[1])
        if [self.args[1]] not in LastFiles:
            LastFiles.append([self.args[1]])
        else:
            LastFiles.remove([self.args[1]])
            LastFiles.append([self.args[1]])
        with open('LastFiles.csv', "w", newline='', encoding='utf8') as csv_file:
            writer = csv.writer(csv_file, delimiter=';')
            for line in LastFiles:
                writer.writerow(line)
        self.args[0].history_list.clear()
        self.args[0].history_list.addItems(list(map(lambda x: x[0], LastFiles[::-1])))
        add_database_history(self.args[1], self.args[2], self.args[3])
        OpenedFiles.pop()


# Окно для удаления истории
class SecondFormDeleteHistory(QMainWindow, Ui_DeleteHistory):
    def __init__(self, *args):
        self.args = list(args)
        super().__init__()
        self.setupUi()

    def setupUi(self):
        super().setupUi(self)
        self.setWindowIcon(QIcon('driveharddisk_92587.ico'))
        self.setFixedSize(self.width(), self.height())
        self.pushButton_delete_last.clicked.connect(self.delete_last)
        self.pushButton_delete_last_fives.clicked.connect(self.delete_last_fives)
        self.pushButton_delete_interval.clicked.connect(self.delete_interval)
        self.pushButton_delete_all.clicked.connect(self.delete_all)

    def delete_last(self):
        try:
            copy_last_files = []
            with open('LastFiles.csv', encoding="utf8") as csvfile:
                reader = csv.reader(csvfile, delimiter=';', quotechar='"')
                for index, row in enumerate(reader):
                    copy_last_files.append(row)
            copy_last_files.pop()
            with open('LastFiles.csv', "w", newline='', encoding='utf8') as csv_file:
                writer = csv.writer(csv_file, delimiter=';')
                for line in copy_last_files:
                    writer.writerow(line)
            self.args[0].history_list.clear()
            self.args[0].history_list.addItems(list(map(lambda x: x[0], copy_last_files[::-1])))

        except IndexError:
            pass

    def delete_last_fives(self):
        try:
            copy_last_files = []
            with open('LastFiles.csv', encoding="utf8") as csvfile:
                reader = csv.reader(csvfile, delimiter=';', quotechar='"')
                for index, row in enumerate(reader):
                    copy_last_files.append(row)
            for i in range(5 if len(copy_last_files) >= 5 else len(copy_last_files)):
                copy_last_files.pop()
            with open('LastFiles.csv', "w", newline='', encoding='utf8') as csv_file:
                writer = csv.writer(csv_file, delimiter=';')
                for line in copy_last_files:
                    writer.writerow(line)
            self.args[0].history_list.clear()
            self.args[0].history_list.addItems(list(map(lambda x: x[0], copy_last_files[::-1])))
        except IndexError:
            pass

    def delete_interval(self):
        try:
            delta_index = 0
            copy_last_files = []
            with open('LastFiles.csv', encoding="utf8") as csvfile:
                reader = csv.reader(csvfile, delimiter=';', quotechar='"')
                for index, row in enumerate(reader):
                    copy_last_files.append(row)
            copy_last_files.reverse()
            self.interval = list(map(lambda x: x.split('-'), self.lineEdit.text().split(',')))
            for i in self.interval:
                if len(i) == 2:
                    ind = int(i[0].strip()) - 1
                    ind2 = int(i[1].strip()) - 1
                    for j in range(ind, ind2 + 1):
                        copy_last_files.pop(j - delta_index)
                        delta_index += 1
                else:
                    copy_last_files.pop(int(i[0].strip()) - 1 - delta_index)
                delta_index += 1
            copy_last_files.reverse()
            with open('LastFiles.csv', "w", newline='', encoding='utf8') as csv_file:
                writer = csv.writer(csv_file, delimiter=';')
                for line in copy_last_files:
                    writer.writerow(line)
            self.args[0].history_list.clear()
            self.args[0].history_list.addItems(list(map(lambda x: x[0], copy_last_files[::-1])))
        except Exception:
            pass

    def delete_all(self):
        LastFiles.clear()
        with open('LastFiles.csv', "w", newline='', encoding='utf8') as csv_file:
            writer = csv.writer(csv_file, delimiter=';')
            for line in LastFiles:
                writer.writerow(line)
        self.args[0].history_list.clear()


# Окно для музыкального проигрывателя
class SecondFormMusicPlayer(QMainWindow, Ui_MusicPlayer):
    def __init__(self, *args):
        self.args = list(args)
        super().__init__()
        self.setupUi()
        self.setWindowIcon(QIcon('driveharddisk_92587.ico'))
        self.music_list = QMediaPlaylist()
        self.music_player = QMediaPlayer()
        self.current_index_of_music = 0
        self.play_back_mode = 1
        iter_music_list = QDirIterator('/'.join(self.args[1].split('/')[:-1]))
        iter_music_list.next()
        self.music_list.addMedia(QMediaContent(QUrl.fromLocalFile(self.args[1])))
        while iter_music_list.hasNext():
            if not iter_music_list.fileInfo().isDir() and iter_music_list.filePath() != '.':
                file_info = iter_music_list.fileInfo()
                if file_info.suffix() in ({'mp3', 'ogg', 'wav'}):
                    self.music_list.addMedia(
                        QMediaContent(QUrl.fromLocalFile(iter_music_list.filePath())))
            iter_music_list.next()
        self.music_list.setPlaybackMode(QMediaPlaylist.CurrentItemInLoop)
        self.flag_of_play = 0
        self.music_player.currentMediaChanged.connect(self.song_title_change)
        self.music_player.mediaStatusChanged.connect(self.song_change)
        self.music_player.positionChanged.connect(self.song_position_change)
        self.music_player.volumeChanged.connect(self.volume_position_change)
        self.music_player.stateChanged.connect(self.state_changed)
        self.volume_slider.setTracking(False)
        self.volume_slider.setMinimum(0)
        self.volume_slider.setMaximum(100)
        self.volume_slider.setValue(60)
        self.volume_slider.sliderMoved.connect(self.change_volume)
        self.volume_slider.valueChanged[int].connect(self.change_volume)
        self.melody_running_slider.setMinimum(0)
        self.melody_running_slider.setMaximum(100)
        self.melody_running_slider.sliderMoved.connect(self.change_position)
        self.melody_running_slider.setTracking(False)
        self.music_player.setVolume(60)
        self.start_music()
        self.music_player.play()

    def setupUi(self):
        super().setupUi(self)
        self.setFixedSize(self.width(), self.height())
        self.setWindowTitle(self.args[2][:-4])
        self.start_button.clicked.connect(self.start_music)
        self.pause_button.clicked.connect(self.pause_music)
        self.stop_button.clicked.connect(self.stop_music)
        self.previous_button.clicked.connect(self.prev_music)
        self.next_button.clicked.connect(self.next_music)
        self.plus_volume_button.clicked.connect(self.add_volume)
        self.minus_volume_button.clicked.connect(self.sub_volume)
        self.mode_playing_button.clicked.connect(self.change_mode_playback)

    def next_music(self):
        self.music_player.playlist().next()

    def prev_music(self):
        self.music_player.playlist().previous()

    def closeEvent(self, event):
        if [self.args[1]] not in LastFiles:
            LastFiles.append([self.args[1]])
        else:
            LastFiles.remove([self.args[1]])
            LastFiles.append([self.args[1]])
        with open('LastFiles.csv', "w", newline='', encoding='utf8') as csv_file:
            writer = csv.writer(csv_file, delimiter=';')
            for line in LastFiles:
                writer.writerow(line)
        self.args[0].history_list.clear()
        self.args[0].history_list.addItems(list(map(lambda x: x[0], LastFiles[::-1])))
        self.music_player.stop()
        add_database_history(self.args[1], self.args[2], self.args[3])
        OpenedFiles.pop()

    def start_music(self):
        self.flag_of_play = 1
        if self.music_player.state() == QMediaPlayer.StoppedState:
            if self.music_player.mediaStatus() == QMediaPlayer.NoMedia:
                if self.music_list.mediaCount() != 0:
                    self.music_player.setPlaylist(self.music_list)
            elif self.music_player.mediaStatus() == QMediaPlayer.LoadedMedia:
                self.music_player.play()
            elif self.music_player.mediaStatus() == QMediaPlayer.BufferedMedia:
                self.music_player.play()
        elif self.music_player.state() == QMediaPlayer.PausedState:
            self.music_player.play()

    def pause_music(self):
        self.flag_of_play = 2
        self.music_player.pause()

    def stop_music(self):
        self.flag_of_play = 0
        self.music_player.stop()

    def song_title_change(self, media):
        if not media.isNull():
            url = media.canonicalUrl()
            self.setWindowTitle(str(url.fileName())[:-4])

    def song_position_change(self, position, senderType=False):
        if not senderType:
            self.melody_running_slider.setValue(position)
        self.time_label.setText('%d:%02d' % (int(position / 60000), int((position / 1000) % 60)))

    def change_position(self, position):
        sender = self.sender()
        if isinstance(sender, QSlider):
            if self.music_player.isSeekable():
                self.music_player.setPosition(position)

    def song_change(self):
        duration_music = self.music_player.duration()
        self.melody_running_slider.setRange(0, duration_music)
        self.melody_running_slider.setPageStep(duration_music // 100)
        self.time_label_2.setText('%d:%02d' % (int(duration_music / 60000),
                                               int((duration_music / 1000) % 60)))

    def add_volume(self):
        self.music_player.setVolume(min(self.music_player.volume() + 5, 100))

    def sub_volume(self):
        self.music_player.setVolume(max(self.music_player.volume() - 5, 0))

    def state_changed(self):
        if self.music_player.state() == QMediaPlayer.StoppedState:
            self.music_player.stop()

    def change_volume(self, position):
        sender = self.sender()
        if isinstance(sender, QSlider):
            self.music_player.setVolume(position)

    def volume_position_change(self, position, senderType=False):
        if not senderType:
            self.volume_slider.setValue(position)

    def change_mode_playback(self):
        self.play_back_mode = (self.play_back_mode + 1) % 2
        if self.play_back_mode:
            self.sender().setText('Повторять текущей трек')
            self.music_list.setPlaybackMode(QMediaPlaylist.CurrentItemInLoop)
        else:
            self.sender().setText('Повторять плейлист')
            self.music_list.setPlaybackMode(QMediaPlaylist.Sequential)


# Окно для видеопроигрывателя
class SecondFormVideoPlayer(QWidget):
    def __init__(self, *args):
        try:
            super().__init__()
            self.pause_or_play = False
            self.args = list(args)
            self.setWindowTitle(args[2])
            self.resize(1024, 576)
            self.setWindowIcon(QIcon('driveharddisk_92587.ico'))
            self.video_player = QMediaPlayer(None, QMediaPlayer.VideoSurface)
            self.video_plain = QVideoWidget()
            self.play_button = QPushButton('Воспроизвести', self)
            self.play_button.setFixedHeight(24)
            self.stop_button = QPushButton('Стоп', self)
            self.stop_button.setFixedHeight(24)
            self.pause_button = QPushButton('Пауза', self)
            self.pause_button.setFixedHeight(24)
            self.video_slider = QSlider(Qt.Horizontal)
            self.video_slider.setRange(0, 100)
            self.video_player.setVolume(60)
            self.video_player.positionChanged.connect(self.video_position_change)
            self.volume_slider = QSlider(Qt.Horizontal)
            self.volume_slider.setTracking(False)
            self.volume_slider.setRange(0, 100)
            self.volume_slider.setValue(60)
            self.volume_slider.valueChanged[int].connect(self.change_volume)
            self.volume_slider.sliderMoved.connect(self.change_volume)
            self.volume_up_button = QPushButton('+', self)
            self.volume_up_button.setFixedHeight(24)
            self.volume_down_button = QPushButton('-', self)
            self.volume_down_button.setFixedHeight(24)
            self.time_text_left = QLabel('00:00', self)
            self.time_text_right = QLabel('00:00', self)
            self.time_text_left.setFixedHeight(24)
            self.time_text_right.setFixedHeight(24)
            self.control_layout = QHBoxLayout()
            self.control_layout.setContentsMargins(0, 0, 0, 0)
            self.control_layout.addWidget(self.play_button)
            self.control_layout.addWidget(self.stop_button)
            self.control_layout.addWidget(self.pause_button)
            self.volume_layout = QHBoxLayout()
            self.volume_layout.setContentsMargins(0, 0, 0, 0)
            self.volume_layout.addWidget(self.volume_down_button)
            self.volume_layout.addWidget(self.volume_slider)
            self.volume_layout.addWidget(self.volume_up_button)
            self.video_time_layout = QHBoxLayout()
            self.video_time_layout.setContentsMargins(0, 0, 0, 0)
            self.video_time_layout.addWidget(self.time_text_left)
            self.video_time_layout.addWidget(self.video_slider)
            self.video_time_layout.addWidget(self.time_text_right)
            self.main_layout = QVBoxLayout()
            self.main_layout.addWidget(self.video_plain)
            self.main_layout.addLayout(self.control_layout)
            self.main_layout.addLayout(self.video_time_layout)
            self.main_layout.addLayout(self.volume_layout)
            self.setLayout(self.main_layout)
            self.video_list = QMediaPlaylist()
            self.video_list.addMedia(QMediaContent(QUrl.fromLocalFile(self.args[1])))
            self.video_list.setPlaybackMode(QMediaPlaylist.CurrentItemInLoop)
            self.video_player.setVideoOutput(self.video_plain)
            self.video_player.volumeChanged.connect(self.volume_position_change)
            self.video_player.positionChanged.connect(self.video_position_change)
            self.video_slider.sliderMoved.connect(self.change_position)
            self.video_player.mediaStatusChanged.connect(self.video_change)
            self.volume_up_button.clicked.connect(self.add_volume)
            self.volume_down_button.clicked.connect(self.sub_volume)
            self.video_player.setPlaylist(self.video_list)
            self.video_slider.setTracking(False)
            self.video_player.play()
            self.play_button.clicked.connect(self.play_video)
            self.stop_button.clicked.connect(self.stop_video)
            self.pause_button.clicked.connect(self.pause_video)
        except Exception:
            pass

    def video_change(self):
        duration_music = self.video_player.duration()
        self.video_slider.setRange(0, duration_music)
        self.video_slider.setPageStep(duration_music // 100)
        self.time_text_right.setText('%d:%02d' % (int(duration_music / 60000),
                                                  int((duration_music / 1000) % 60)))

    def stop_video(self):
        self.video_player.stop()

    def pause_video(self):
        self.video_player.pause()

    def play_video(self):
        if self.video_player.state() == QMediaPlayer.StoppedState:
            if self.video_player.mediaStatus() == QMediaPlayer.LoadedMedia:
                self.video_player.play()
            elif self.video_player.mediaStatus() == QMediaPlayer.BufferedMedia:
                self.video_player.play()
        elif self.video_player.state() == QMediaPlayer.PausedState:
            self.video_player.play()

    def closeEvent(self, event):
        if [self.args[1]] not in LastFiles:
            LastFiles.append([self.args[1]])
        else:
            LastFiles.remove([self.args[1]])
            LastFiles.append([self.args[1]])
        with open('LastFiles.csv', "w", newline='', encoding='utf8') as csv_file:
            writer = csv.writer(csv_file, delimiter=';')
            for line in LastFiles:
                writer.writerow(line)
        self.args[0].history_list.clear()
        self.args[0].history_list.addItems(list(map(lambda x: x[0], LastFiles[::-1])))
        self.video_player.stop()
        add_database_history(self.args[1], self.args[2], self.args[3])
        OpenedFiles.pop()

    def add_volume(self):
        self.video_player.setVolume(min(self.video_player.volume() + 5, 100))
        self.video_slider.setValue(self.video_player.volume())

    def sub_volume(self):
        self.video_player.setVolume(max(self.video_player.volume() - 5, 0))
        self.video_slider.setValue(self.video_player.volume())

    def video_position_change(self, position, senderType=False):
        if not senderType:
            self.video_slider.setValue(position)
        self.time_text_left.setText('%d:%02d' % (int(position / 60000),
                                                 int((position / 1000) % 60)))

    def change_volume(self, position):
        sender = self.sender()
        if isinstance(sender, QSlider):
            self.video_player.setVolume(position)

    def volume_position_change(self, position, senderType=False):
        if not senderType:
            self.volume_slider.setValue(position)

    def change_position(self, position):
        sender = self.sender()
        if isinstance(sender, QSlider):
            if self.video_player.isSeekable():
                self.video_player.setPosition(position)

    def keyPressEvent(self, QKeyEvent):
        if QKeyEvent.key() == Qt.Key_K:
            if self.pause_or_play:
                self.video_player.play()
                self.pause_or_play = False
            else:
                self.video_player.pause()
                self.pause_or_play = True
        if QKeyEvent.key() == Qt.Key_J:
            self.video_player.setPosition(max(0, int(self.video_player.position()) - 5000))
        if QKeyEvent.key() == Qt.Key_L:
            self.video_player.setPosition(min(self.video_player.duration(),
                                              int(self.video_player.position()) + 5000))


# Основное окно приложения
class MyApp(QMainWindow, Ui_MainWindow):
    def __init__(self, file_path=None):
        super().__init__()
        self.setupUi(self)
        self.second_form = None
        self.help_form = SecondFormDeleteHistory(self)
        self.main_menu_bar = self.menuBar()
        self.main_menu_bar.addAction(self.create_open_file_action())
        self.main_menu_bar.addAction(self.create_delete_history_action())
        self.main_menu_bar.addAction(self.create_user_help_action())
        self.setWindowIcon(QIcon('driveharddisk_92587.ico'))
        with open('LastFiles.csv', encoding="utf8") as csvfile:
            reader = csv.reader(csvfile, delimiter=';', quotechar='"')
            for index, row in enumerate(reader):
                LastFiles.append(row)
        if not LastFiles:
            pass
        else:
            self.history_list.addItems(list(map(lambda x: x[0], LastFiles[::-1])))
        self.history_list.itemClicked.connect(self.click_on_last_file)
        if not (file_path is None):
            self.open_file(giving_file_path=file_path)

    def open_file(self, giving_file_path=None):
        try:
            if not bool(giving_file_path):
                self.filepath = QFileDialog.getOpenFileName(self, 'Выбрать файл', '')[0]
                if not self.filepath:
                    raise ValueError
            else:
                self.filepath = giving_file_path
            self.filename = ''.join(self.filepath.split('/')[-1].split('.')[:-1])
            self.filetype = self.filepath.split('.')[-1]
            try:
                OpenedFiles.append(SecondFormText(self, self.filepath, self.filename,
                                                  self.filetype))
                OpenedFiles[-1].show()
            except UnicodeDecodeError:
                try:
                    OpenedFiles.append(SecondFormImage(self, self.filepath, self.filename,
                                                       self.filetype))
                    OpenedFiles[-1].show()
                except Exception:
                    try:
                        if self.filetype in {'mp3', 'wav', 'ogg'}:
                            OpenedFiles.append(SecondFormMusicPlayer(self, self.filepath,
                                                                     self.filename,
                                                                     self.filetype))
                            OpenedFiles[-1].show()
                        elif self.filetype in {'mp4', 'mkv', 'mpeg', 'mpg', 'avi', 'webm',
                                               'wmv'}:
                            try:
                                OpenedFiles.append(SecondFormVideoPlayer(self, self.filepath,
                                                                         self.filename,
                                                                         self.filetype))
                                OpenedFiles[-1].show()
                            except Exception:
                                pass
                        else:
                            error_form = QMessageBox()
                            error_form.setWindowTitle('Ошибка')
                            error_form.setText('Извините, это расширение файла не поддерживается')
                            error_form.exec_()
                    except Exception:
                        pass
        except Exception:
            pass

    def click_on_last_file(self, item):
        self.open_file(giving_file_path=str(item.text()))

    def create_open_file_action(self):
        file_open = QAction('Открыть файл', self)
        file_open.setStatusTip('Открыть файл')
        file_open.triggered.connect(self.open_file)
        return file_open

    def create_delete_history_action(self):
        delete_history = QAction('Удалить историю', self)
        delete_history.setStatusTip('Удалить историю')
        delete_history.triggered.connect(self.help_form.show)
        return delete_history

    def create_user_help_action(self):
        open_db = QAction('Открыть БД по файлам', self)
        open_db.setStatusTip('Открывает БД по файлам, которые открывались')
        open_db.triggered.connect(self.open_database)
        return open_db

    def open_database(self):
        database = SecondFormDBViewer(self)
        database.show()

    def keyPressEvent(self, QKeyEvent):
        if int(QKeyEvent.modifiers()) == Qt.CTRL:
            if QKeyEvent.key() == Qt.Key_O:
                self.open_file()
        if int(QKeyEvent.modifiers()) == Qt.CTRL:
            if QKeyEvent.key() == Qt.Key_Delete:
                self.help_form.show()


# Запуск приложения
if __name__ == '__main__':
    app = QApplication([sys.argv[0]])
    app.setStyle("fusion")
    if len(sys.argv) >= 2:
        launch = MyApp(file_path=sys.argv[1])
    else:
        launch = MyApp()
    launch.show()
    sys.exit(app.exec_())

import os
import sys
from PIL import Image, ImageDraw


class RgbMatrix:
    """
    Basisklasse RGB_matrix - bietet eine Simulationsumgebung, Inhalt RGB Matrix wird in .png Dateien gespeichert
    """
    def __init__(self, directory='__default_dir_rgb_matrix', default_color=(0, 0, 0)):
        """
        RGB_matrix Objekt Konstruktor
        :param directory: string, bestimmt in welcher Ordner die Bilder sowie die LOG-Datei gespeichert werden
        :param default_color: tupel, [R, G, B] -> [0..255, 0..255, 0..255], Standard = (0, 0, 0)
        https://de.wikipedia.org/wiki/RGB-Farbraum

        Attribut: "rgb_matrix[zeile][spalte]" wird mit default_color initialisiert (zeile = 0..7, spalte = 0..7)
        """
        self.directory = directory
        self.basefilename = 'rgb-matrix'
        self.logfile = None
        self.default_color = default_color
        self.rgb_matrix = self.init_rgb_matrix()
        self.index = 0  # jedes Bild wird in eine separate Datei mit Suffix '_index' gespeichert

    def init_rgb_matrix(self):
        """
        Initialisierung der 8 x 8 x 3 Matrix für die vereinfachte Farbzuweisung.
        Dimension 8 x 8 ist fix definiert!
        """
        rgb_matrix = []
        for i in range(0, 8, 1):
            led = []
            for j in range(0, 8, 1):
                rgb_def_color = self.default_color
                led.extend([rgb_def_color])
            rgb_matrix.extend([led])
        return rgb_matrix

    def draw_rgb_to_png(self, faktor=255):
        img = Image.new('RGB', (410,410), color='gray')
        draw = ImageDraw.Draw(img)
        # zeichne Pixel
        for i in range(0, 8 , 1):
            for j in range(0, 8, 1):
                rot = self.rgb_matrix[i][j][0] * faktor
                gruen = self.rgb_matrix[i][j][1] * faktor
                blau = self.rgb_matrix[i][j][2] * faktor
                if rot > 255:
                    rot = 255
                if gruen > 255:
                    gruen = 255
                if blau > 255:
                    blau = 255
                rgb_color = rot * 0x01 + gruen * 0x100 + blau * 0x10000
                box = [(j * 50 + 10), (i * 50 + 10), (j * 50 + 50), (i * 50 + 50)]
                draw.ellipse(box, outline=rgb_color, fill=rgb_color)
        image_filename = '{0}_{1}.png'.format(self.basefilename, self.index)
        img.save(os.path.join(self.directory, image_filename))
        self.index += 1

    def open(self):
        """
        Erstellen Ordner und .log Datei, falls bereits exisitiert => Programm beenden
        """
        if os.path.exists(self.directory):
            print('directory already exists --> abort program')
            sys.exit()
        else:
            os.makedirs(self.directory)
            log_filename = self.basefilename + '.log'
            self.logfile = open(os.path.join(self.directory, log_filename), 'w')
            self.logfile.write('logfile created: {0}\n'.format(str(self)))

    def close(self):
        """
        Schliessen .log Datei
        """
        self.logfile.write('logfile closed: {0}\n'.format(str(self)))
        self.logfile.close()

    def write(self):
        """
        Entsprechende Matrix im Image darstellen.
        """
        self.draw_rgb_to_png()
        self.logfile.write('picture file added: {0}\n'.format(str(self)))

    def __str__(self):
        """
        Klartextausgabe der Klasseneigenschaften
        """
        return 'RGB_matrix(directory={0}, default_color={1}, index={2})'.format(self.directory, self.default_color, self.index)

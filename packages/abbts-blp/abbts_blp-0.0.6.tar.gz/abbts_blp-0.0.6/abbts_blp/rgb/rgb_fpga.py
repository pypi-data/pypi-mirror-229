import sys
import serial
from .rgb_matrix import RgbMatrix


class RgbFpga(RgbMatrix):
    """
    Abgeleitete Klasse von RgbMatrix für das Senden von Bilder über der UART-FPGA Schnittstelle
    https://de.wikipedia.org/wiki/Universal_Asynchronous_Receiver_Transmitter
    """
    def __init__(self, enable=True, port='COM6', directory='__default_dir_rgb_FPGA', default_color=(0, 0, 0)):
        """
        RGB_FPGA Objekt Konstruktor
        :param enable: boolean, Schnittstelle aktivieren?
        :param port: string, COM-Port -> siehe Geräte-Manager
        :param directory: string, bestimmt in welcher Ordner die Bilder sowie die LOG-Datei gespeichert werden
        """
        RgbMatrix.__init__(self, directory=directory, default_color=default_color)
        self.enable = enable
        self.port = port
        self.instanz = None
        self.rgb_bytestream = self.init_rgb_bytestream()

    @staticmethod
    def init_rgb_bytestream():
        """
        Initialisierung des 8 x 8 x 3 Bytestreams (Snake-Line), welcher für die Übertragung an die RGB-Matrix (HW)
        Dimension 8 x 8 ist fix definiert!
        https://www.led-genial.de/DIGI-DOT-Panel-8x8-HD-mit-64-x-Digital-LEDs
        """
        rgb_bytestream = []
        for i in range(0, (8 * 8 * 3), 1):
            rgb_bytestream.extend([0])
        return rgb_bytestream


    def rgb_matrix_to_rgb_bytestream(self):
        """
        Transformation der Matrix-Darstellung in die entsprechende Bytestream-Darstellung (Datenstrom).
        """
        lookup = [7, 8, 23, 24, 39, 40, 55, 56]
        for col in range(0, 8, 1):
            for row in range(0, 8, 1):
                n_lookup = lookup[col]
                if (col % 2) == 0:
                    self.rgb_bytestream[n_lookup * 3 - (row * 3) + 0] = self.rgb_matrix[row][col][1]  # ROT
                    self.rgb_bytestream[n_lookup * 3 - (row * 3) + 1] = self.rgb_matrix[row][col][0]  # GRUEN
                    self.rgb_bytestream[n_lookup * 3 - (row * 3) + 2] = self.rgb_matrix[row][col][2]  # BLAU
                else:
                    self.rgb_bytestream[n_lookup * 3 + (row * 3) + 0] = self.rgb_matrix[row][col][1]  # ROT
                    self.rgb_bytestream[n_lookup * 3 + (row * 3) + 1] = self.rgb_matrix[row][col][0]  # GRUEN
                    self.rgb_bytestream[n_lookup * 3 + (row * 3) + 2] = self.rgb_matrix[row][col][2]  # BLAU

    # def rgb_matrix_to_rgb_bytestream(self):
    #     """
    #     Umsetzung RGB-Matrix Standalone
    #     Transformation der Matrix-Darstellung in die entsprechende Bytestream-Darstellung (Datenstrom).
    #     """
    #     for i in range(0, 8, 1):
    #         for j in range(0, 8, 1):
    #             if (i % 2) == 0:
    #                 self.rgb_bytestream[(i * 8 * 3) + (j * 3) + 0] = self.rgb_matrix[i][j][1]  # ROT
    #                 self.rgb_bytestream[(i * 8 * 3) + (j * 3) + 1] = self.rgb_matrix[i][j][0]  # GRUEN
    #                 self.rgb_bytestream[(i * 8 * 3) + (j * 3) + 2] = self.rgb_matrix[i][j][2]  # BLAU
    #             else:
    #                 self.rgb_bytestream[(i * 8 * 3) + (j * 3) + 0] = ((self.rgb_matrix[i])[::-1])[j][1]  # ROT
    #                 self.rgb_bytestream[(i * 8 * 3) + (j * 3) + 1] = ((self.rgb_matrix[i])[::-1])[j][0]  # GRUEN
    #                 self.rgb_bytestream[(i * 8 * 3) + (j * 3) + 2] = ((self.rgb_matrix[i])[::-1])[j][2]  # BLAU

    def open(self):
        """
        Oeffne UART mit der COM - Bezeichnung
        """
        if self.enable:
            try:
                self.instanz = serial.Serial(self.port, 921600, timeout=0, parity=serial.PARITY_NONE)
            except Exception as e:
                print('uart_open', e)
                sys.exit()
        else:
            print('RGB_FPGA: simulation mode - matrix pictures will be written to .png files')
            RgbMatrix.open(self)  # Aufruf der entsprechenden Methode der Basisklasse

    def write(self):
        """
        Schreiben auf den UART Kanal
        """
        if self.enable:
            self.rgb_matrix_to_rgb_bytestream()
            try:
                if len(self.rgb_bytestream) == 8 * 8 * 3:
                    for i in range(0, 8, 1):
                        uart_string = '<{:02x}'.format(i)  # https://pyformat.info/
                        for j in range(0, 8, 1):
                            uart_string += '{:02X}'.format(self.rgb_bytestream[(i * 8 * 3) + (j * 3) + 0])
                            uart_string += '{:02X}'.format(self.rgb_bytestream[(i * 8 * 3) + (j * 3) + 1])
                            uart_string += '{:02X}'.format(self.rgb_bytestream[(i * 8 * 3) + (j * 3) + 2])
                        uart_string += '>'
                        # print(uart_string)
                        self.instanz.write(uart_string.encode())  # write a string
            except Exception as e:
                print('uart_write', e)
                sys.exit()
        else:
            RgbMatrix.write(self)  # Aufruf der entsprechenden Methode der Basisklasse

    def close(self):
        """
        Schliessen des UART Kanals.
        """
        if self.enable:
            try:
                self.instanz.close()
            except Exception as e:
                print('uart_close', e)
                sys.exit()
        else:
            RgbMatrix.close(self)  # Aufruf der entsprechenden Methode der Basisklasse

    def __str__(self):
        """
        Klartextausgabe der Klasseneigenschaften
        """
        if self.enable:
            return 'RGB_FPGA(enable={0}, port={1})'.format(self.enable, self.port)
        else:
            return RgbMatrix.__str__(self)  # Aufruf der entsprechenden Methode der Basisklasse


if __name__ == '__main__':
    print('rgb_FPGA.py => __main__')
    rgb = RgbFpga(port='COM7')
    print(rgb)
    rgb.open()
    rgb.rgb_matrix[0][0] = [10, 0, 0]
    rgb.write()
    rgb.rgb_matrix[2][5] = [0, 10, 0]
    rgb.write()
    rgb.rgb_matrix[4][-1] = [0, 0, 10]
    rgb.write()
    rgb.close()

    rgb = RgbFpga(enable=False, port='COM7')
    print(rgb)
    rgb.open()
    rgb.rgb_matrix[1][1] = [10, 0, 0]
    rgb.write()
    rgb.rgb_matrix[3][6] = [0, 10, 0]
    rgb.write()
    rgb.rgb_matrix[5][-1] = [0, 0, 10]
    rgb.write()
    rgb.close()

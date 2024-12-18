import re
import anvil.server

# Verbinde dich mit dem Anvil-Server
anvil.server.connect("server_4MBZIOXABKL5OA42VYKHGSON-V32HZTFRXD5FJXZA")

@anvil.server.callable
def speichere_g_code(gesamter_text):
    print("Gesamter G-Code:", gesamter_text)

    # Extrahiere alle Positionswerte aus dem gesamten G-Code-Text
    motor_positions = extract_all_positions(gesamter_text)
    
    # Umrechnen der Positionswerte in Little-Endian Hex-Bytes und G1-Liste erstellen
    g1_list = []
    for positions in motor_positions:
        VAR_M1 = decimal_to_hex_bytes_little_endian(positions['motor1'])
        VAR_M2 = decimal_to_hex_bytes_little_endian(positions['motor2'])
        VAR_M3 = decimal_to_hex_bytes_little_endian(positions['motor3'])
        VAR_M4 = decimal_to_hex_bytes_little_endian(positions['motor4'])
        VAR_M5 = decimal_to_hex_bytes_little_endian(positions['motor5'])
        VAR_M6 = decimal_to_hex_bytes_little_endian(positions['motor6'])

        # G1-Befehl für diese Positionen erstellen
        g1_list.append([0x00, 0x23, 0x00, *VAR_M1, 0x00, 0x00, 10])
        g1_list.append([0x00, 0x23, 0x01, *VAR_M2, 0x00, 0x00, 5])
        g1_list.append([0x00, 0x23, 0x02, *VAR_M3, 0x00, 0x00, 5])
        g1_list.append([0x00, 0x23, 0x03, *VAR_M4, 0x00, 0x00, 5])
        g1_list.append([0x00, 0x23, 0x04, *VAR_M5, 0x00, 0x00, 5])
        g1_list.append([0x00, 0x23, 0x05, *VAR_M6, 0x00, 0x00, 5])

    # Rückgabe der G1-Liste
    return "Der Code wurde übersendet"

def extract_all_positions(text):
    """
    Extrahiert alle Positionswerte aus einem mehrzeiligen G-Code-Text.
    """
    motor_positions = []
    
    # Text in Zeilen aufteilen
    lines = text.splitlines()
    
    # Jede Zeile durchsuchen und Positionen extrahieren
    for line in lines:
        if line.startswith("G1"):  # Nur Zeilen mit G1-Befehl verarbeiten
            positions = extract_positions(line)
            motor_positions.append(positions)
    
    return motor_positions

def extract_positions(text):
    """
    Extrahiert die Positionswerte für A-F aus einer einzelnen Zeile G-Code.
    """
    # Verwenden eines regulären Ausdrucks, um A-F Werte zu extrahieren
    positions = re.findall(r'[A-F](-?\d+)', text)
    
    # Sicherstellen, dass 6 Positionswerte extrahiert wurden
    if len(positions) != 6:
        raise ValueError(f"Ungültiger G-Code: Es müssen genau 6 Positionswerte angegeben werden. Zeile: {text}")
    
    # Rückgabe der Positionen als Dictionary
    return {
        'motor1': int(positions[0]),
        'motor2': int(positions[1]),
        'motor3': int(positions[2]),
        'motor4': int(positions[3]),
        'motor5': int(positions[4]),
        'motor6': int(positions[5]),
    }

def decimal_to_hex_bytes_little_endian(decimal_value):
    """
    Konvertiert einen Dezimalwert (positiv oder negativ) in eine Liste von 4 Hexadezimalbytes 
    (32-Bit-Wert) im Little-Endian-Format.
    """
    if decimal_value < 0:
        decimal_value = (decimal_value + (1 << 32)) % (1 << 32)
    hex_value = f"{decimal_value:08X}"
    return [int(hex_value[i:i+2], 16) for i in range(6, -1, -2)]


#G0 = Referenzfahrt
G0 = [
    
    # Hardware Reset
    [0x00, 0xCC, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 5],
    
    
    # Motor 6 - Greifer
    [0x00, 0x13, 0x05, 0xD2, 0x00, 0x0A, 0x00, 0x00, 0x00, 0.01],
    [0x00, 0x14, 0x05, 0x19, 0x00, 0xFA, 0x00, 0x00, 0x00, 0.01],
    [0x00, 0x15, 0x05, 0x00, 0x00, 0x00, 0x00, 0x00, 0x04, 0.01],
    [0x00, 0x22, 0x05, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 3],
    
    # Motor 1 - Arm Drehen referenzieren
    [0x00, 0x13, 0x00, 0xC8, 0x00, 0x0A, 0x00, 0x00, 0x00, 0.01],
    [0x00, 0x14, 0x00, 0x19, 0x00, 0xFA, 0x00, 0x00, 0x00, 0.01],
    [0x00, 0x15, 0x00, 0x00, 0x00, 0x00, 0x00, 0x10, 0x40, 0.01],
    [0x00, 0x22, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0.01],
    
    # Motor 5 - Drehen Greifer
    [0x00, 0x13, 0x04, 0xF8, 0x00, 0xFA, 0x00, 0x00, 0x00, 0.01],
    [0x00, 0x14, 0x04, 0x19, 0x00, 0xFF, 0x00, 0x00, 0x00, 0.01],
    [0x00, 0x15, 0x04, 0x00, 0x00, 0x00, 0x00, 0x00, 0x40, 0.01],
    [0x00, 0x22, 0x04, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 25],
    [0x00, 0x23, 0x04, 0x30, 0x04, 0xFE, 0xFF, 0x00, 0x00, 5],
    
    # Motor 2 - Erster Arm
    [0x00, 0x13, 0x01, 0xB8, 0x00, 0x0A, 0x00, 0x00, 0x00, 0.01],
    [0x00, 0x14, 0x01, 0x19, 0x00, 0xFA, 0x00, 0x00, 0x00, 0.01],
    [0x00, 0x15, 0x01, 0x00, 0x00, 0x00, 0x00, 0x10, 0x40, 0.01],
    [0x00, 0x22, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 20],
    [0x00, 0x23, 0x01, 0xBC, 0x2E, 0x01, 0x00, 0x00, 0x00, 5],
    
    # Motor 4 - 2. Arm Oberes Gelenk - Referenz
    [0x00, 0x13, 0x03, 0xD8, 0x00, 0x0A, 0x00, 0x00, 0x00, 0.01],
    [0x00, 0x14, 0x03, 0x19, 0x00, 0xEA, 0x00, 0x00, 0x00, 0.01],
    [0x00, 0x15, 0x03, 0x00, 0x00, 0x00, 0x00, 0x10, 0x40, 0.01],
    [0x00, 0x22, 0x03, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 25],
    
    # Motor 4 - 2. Arm Oberes Gelenk - Sicherheitsposi
    [0x00, 0x13, 0x03, 0x64, 0x00, 0x0A, 0x00, 0x00, 0x00, 0.01],
    [0x00, 0x14, 0x03, 0x19, 0x00, 0xD5, 0x00, 0x00, 0x00, 0.01],
    [0x00, 0x15, 0x03, 0x00, 0x00, 0x00, 0x00, 0x10, 0x40, 0.01],
    [0x00, 0x23, 0x03, 0xC0, 0xD4, 0x01, 0x00, 0x00, 0x00, 5],
    
    
    # Motor 3 - 2. Arm Unten Gelenk - Referenz
    [0x00, 0x13, 0x02, 0xC8, 0x00, 0xFF, 0xA0, 0x00, 0x00, 0.01],
    [0x00, 0x14, 0x02, 0x19, 0x00, 0xFF, 0xCA, 0x00, 0x00, 0.01],
    [0x00, 0x15, 0x02, 0x00, 0x00, 0x00, 0x00, 0x10, 0x40, 0.01],
    [0x00, 0x22, 0x02, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 20],
    
    # Motor 3 - 2. Arm Unten Gelenk - Sicherheitsposi
    [0x00, 0x13, 0x02, 0x64, 0x00, 0x0A, 0x00, 0x00, 0x00, 0.01],
    [0x00, 0x14, 0x02, 0x19, 0x00, 0xC8, 0x00, 0x00, 0x00, 0.01],
    [0x00, 0x15, 0x02, 0x00, 0x00, 0x00, 0x00, 0x10, 0x40, 0.01],
    [0x00, 0x23, 0x02, 0xF8, 0x24, 0x01, 0x00, 0x00, 0x00, 5],
    
    # Motor 1 - Arm Drehen
    [0x00, 0x13, 0x00, 0x64, 0x00, 0x0A, 0x00, 0x00, 0x00, 0.01],
    [0x00, 0x14, 0x00, 0x19, 0x00, 0xFA, 0x00, 0x00, 0x00, 0.01],
    [0x00, 0x15, 0x00, 0x00, 0x00, 0x00, 0x00, 0x10, 0x40, 0.01],
    [0x00, 0x23, 0x00, 0x10, 0x98, 0x02, 0x00, 0x00, 0x00, 5],
    
   
    # Auf Grundlage der Referenzfahrt, Abfolge muss eingehalten werden
    
]


#dictionary für die Listen
commands = {
    "G0": G0,
    "G1": G1,
}

@anvil.server.callable
def gesamter_text(text):
    print(f"Text von Anvil: (text)")
print("Warte auf Anvil")
anvil.server.wait_forever()


# Serielle Verbindung konfigurieren
ser = serial.Serial(
    port='/dev/ttyUSB0',
    baudrate=19200,
    bytesize=serial.EIGHTBITS,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    timeout=1
)

time.sleep(2)

def send_command(command):
    """Sendet einen einzelnen Befehl über die serielle Schnittstelle."""
    ser.write(bytearray(command[:-1]))  # Letztes Element ist die Wartezeit, daher ausschließen
    ser.flush()  # Wartet, bis alle Daten gesendet wurden

# Sende alle Befehle mit angegebener Pause
for command in commands:
    wait_time = command[-1]  # Die Wartezeit ist das letzte Element des Befehls
    print("Sending command:", command[:-1])
    send_command(command)
    print(f"Waiting for {wait_time} seconds")
    time.sleep(wait_time)  # Wartezeit ausführen

# Verbindung schließen
ser.close()



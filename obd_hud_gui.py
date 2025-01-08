import serial.tools.list_ports  # Zum Scannen der verfügbaren Ports
import obd
import tkinter as tk


# Funktion zum Aufbau der Verbindung
def connect_to_obd():
    ports = [port.device for port in serial.tools.list_ports.comports()]  # Verfügbare Ports scannen
    print("Gefundene Ports:", ports)
    if ports:
        try:
            # Verbindung mit Port und Baudrate
            return obd.OBD(portstr=ports[0], baudrate=38400)  # Standard-Baudrate für ELM327
        except Exception as e:
            print(f"Fehler beim Verbinden mit dem Adapter: {e}")
            return None
    else:
        print("Kein OBD-II Adapter gefunden!")
        return None


# Erzeuge die Verbindung zum OBD-II-Adapter
connection = connect_to_obd()


class OBDHud:
    def __init__(self, root):
        self.root = root
        self.root.title("OBD HUD")
        self.root.geometry("400x300")

        # Setze das Layout der GUI mit tk-Widgets
        self.speed_label = tk.Label(self.root, text="Speed: 0 km/h", font=("Arial", 12))
        self.speed_label.pack(pady=10)

        self.rpm_label = tk.Label(self.root, text="RPM: 0", font=("Arial", 12))
        self.rpm_label.pack(pady=10)

        # Start des OBD-Update-Timers
        self.update_values()

    def update_values(self):
        """Diese Methode holt die OBD-Daten und aktualisiert die GUI."""
        if not connection or connection.status() != obd.OBDStatus.CAR_CONNECTED:
            self.root.after(1000, self.update_values)
            self.speed_label.config(text="Speed: N/A")
            self.rpm_label.config(text="RPM: N/A")
        else:
            # Geschwindigkeit abrufen
            speed_command = connection.query(obd.commands.SPEED)
            if speed_command and speed_command.value is not None:
                self.speed_label.config(text=f"Speed: {speed_command.value.to('km/h')}")
            else:
                self.speed_label.config(text="Speed: N/A")

            # RPM abrufen
            rpm_command = connection.query(obd.commands.RPM)
            if rpm_command and rpm_command.value is not None:
                self.rpm_label.config(text=f"RPM: {rpm_command.value}")
            else:
                self.rpm_label.config(text="RPM: N/A")

        self.root.after(1000, self.update_values)  # Timer fortsetzen


if __name__ == "__main__":
    root = tk.Tk()
    app = OBDHud(root)
    root.mainloop()
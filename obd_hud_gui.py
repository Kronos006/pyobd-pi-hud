import serial.tools.list_ports  # Zum Scannen der verfügbaren Ports
import obd
import wx


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


class OBDHud(wx.Frame):
    def __init__(self, parent, title):
        super(OBDHud, self).__init__(parent, title=title, size=(400, 300))

        # Setze das Layout der GUI
        panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)

        # Label für Geschwindigkeit
        self.speed_label = wx.StaticText(panel, label="Speed: 0 km/h")
        vbox.Add(self.speed_label, flag=wx.ALL, border=10)

        # Label für RPM
        self.rpm_label = wx.StaticText(panel, label="RPM: 0")
        vbox.Add(self.rpm_label, flag=wx.ALL, border=10)

        # Setze das Panel-Layout
        panel.SetSizer(vbox)

        # Start des OBD-Update-Timers
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.update_values, self.timer)
        self.timer.Start(1000)  # Aktualisiert alle 1000ms (1 Sekunde)

        self.Show()

    def update_values(self, event):
        """Diese Methode holt die OBD-Daten und aktualisiert die GUI."""
        if connection and connection.status() == obd.OBDStatus.CAR_CONNECTED:
            # Geschwindigkeit abrufen
            speed_command = connection.query(obd.commands.SPEED)
            if speed_command and speed_command.value is not None:
                self.speed_label.SetLabel(f"Speed: {speed_command.value.to('km/h')}")
            else:
                self.speed_label.SetLabel("Speed: N/A")

            # RPM abrufen
            rpm_command = connection.query(obd.commands.RPM)
            if rpm_command and rpm_command.value is not None:
                self.rpm_label.SetLabel(f"RPM: {rpm_command.value}")
            else:
                self.rpm_label.SetLabel("RPM: N/A")
        else:
            self.speed_label.SetLabel("Speed: N/A")
            self.rpm_label.SetLabel("RPM: N/A")


if __name__ == "__main__":
    app = wx.App(False)
    frame = OBDHud(None, "OBD HUD")
    app.MainLoop()

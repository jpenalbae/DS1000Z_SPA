import socket
import select

import socket
import select

class Scope:
    """
    A class representing an oscilloscope.

    Attributes:
    - socket: a socket object representing the connection to the oscilloscope.

    Methods:
    - __init__(self, host, port=5555): initializes the socket object and connects to the oscilloscope.
    - cmd(self, cmd): sends a command to the oscilloscope.
    - cmd_with_reply(self, cmd): sends a command to the oscilloscope and returns the reply.
    - get_memory_depth(self): returns the memory depth of the oscilloscope.
    - __del__(self): closes the socket connection.
    - get_chan(self, chan): returns the waveform data for a specified channel.
    - get_all_chans(self): returns the waveform data for all active channels.
    - active_channels(self): returns a list of active channels.
    """

    socket = None

    def __init__(self, host, port=5555):
        """
        Initializes the socket object and connects to the oscilloscope.

        Args:
        - host: a string representing the IP address of the oscilloscope.
        - port: an integer representing the port number to connect to (default is 5555).
        """
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))

    def cmd(self, cmd):
        """
        Sends a command to the oscilloscope.

        Args:
        - cmd: a string representing the command to send.
        """
        self.socket.send(("%s\n" % cmd).encode())

    def cmd_with_reply(self, cmd):
        """
        Sends a command to the oscilloscope and returns the reply.

        Args:
        - cmd: a string representing the command to send.

        Returns:
        - reply: a string representing the reply from the oscilloscope.
        """
        self.cmd(cmd)
        reply = self.socket.recv(1024)
        return reply[:-1].decode()
    
    def get_memory_depth(self):
        """
        Returns the memory depth of the oscilloscope.

        Returns:
        - mdep: an integer representing the memory depth of the oscilloscope.
        """
        # Define number of horizontal grid divisions for DS1054Z
        h_grid = 12

        # ACQuire:MDEPth
        mdep = self.cmd_with_reply(":ACQ:MDEP?")

        if mdep == "AUTO":
            srate = self.cmd_with_reply(":ACQ:SRAT?")
            scal = self.cmd_with_reply(":TIM:SCAL?")

            mdep = h_grid * float(scal) * float(srate)

        return int(mdep)
    
    def __del__(self):
        """
        Closes the socket connection.
        """
        self.socket.close()
    
    def get_chan(self, chan):
        """
        Returns the waveform data for a specified channel.

        Args:
        - chan: a string representing the channel to get the waveform data for.

        Returns:
        - response: a list of integers representing the waveform data for the specified channel.
        """
        self.cmd(":WAV:SOUR %s" % chan.upper())
        self.cmd(":WAV:MODE RAW")
        self.cmd(":WAV:FORM BYTE")

        # get memory depth
        mdep = self.get_memory_depth()

        response = b''
        for i in range(0, mdep, 250000):
            self.cmd(":WAV:STAR %d" % (i+1))
            self.cmd(":WAV:STOP %d" % min(i+250000, mdep))
            self.cmd(":WAV:DATA?")

            # Receive response over TCP connection until no more data
            response += self.socket.recv(260000)[11:]
            while True:
                rlist, _, _ = select.select([self.socket], [], [], 0.1)
                if not self.socket in rlist:
                    break
                response += self.socket.recv(260000)
            response = response[:-1]

        return list(response)
    
    def get_all_chans(self):
        """
        Returns the waveform data for all active channels.

        Returns:
        - chans: a dictionary where the keys are channel names and the values are lists of integers representing the waveform data for each channel.
        """
        chans = {}
        for channel in self.active_channels():
            chans[channel] = self.get_chan(channel)

        return chans

    def active_channels(self):
        """
        Returns a list of active channels.

        Returns:
        - chanlist: a list of strings representing the names of active channels.
        """
        chanlist = []
        for channel in ["CHAN1", "CHAN2", "CHAN3", "CHAN4"]:
            res = self.cmd_with_reply(":%s:DISP?" % channel)
            if res == "1":
                chanlist.append(channel)

        return chanlist


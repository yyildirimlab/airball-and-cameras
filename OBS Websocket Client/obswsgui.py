"""
Title           : obswsgui.py
Authors         : Miguel Maldonado
Date Created    : 03 Sepember 2025
Description     : Client to synchronize OBS recordings with DAQ trigger
"""
# import argparse
import nidaqmx
import obsws_python as obs
from tkinter import Label, Entry, OptionMenu, Button, StringVar, Tk, E, W, messagebox
import threading

class App:
    def __init__(self, root):
        self.root = root
        self.ws = None
        self.task = None
        self.task_block = threading.Event()
        self.task_block.clear()
        self.stop_thread = threading.Event()
        self.stop_thread.set()

        # Set the grid weights
        root.grid_columnconfigure(1, weight=1)
        root.protocol("WM_DELETE_WINDOW", self.on_close)

        # Create the labels and input fields
        Label(root, text="Host:").grid(row=0, column=0, sticky=E)
        self.host_entry = Entry(root)
        self.host_entry.insert(0, "LRI-110116")
        self.host_entry.grid(row=0, column=1, sticky=E+W)

        Label(root, text="Port:").grid(row=1, column=0, sticky=E)
        self.port_entry = Entry(root)
        self.port_entry.insert(0, "4455")
        self.port_entry.grid(row=1, column=1, sticky=E+W)

        Label(root, text="Password:").grid(row=2, column=0, sticky=E)
        self.password_entry = Entry(root, show="*")
        self.password_entry.insert(0, "ylabs123")
        self.password_entry.grid(row=2, column=1, sticky=E+W)

        # Create the label and dropdown for digital input
        Label(root, text="Digital Input:").grid(row=3, column=0, sticky=E)
        self.digital_input_var = StringVar(root)
        self.digital_input_var.set("Dev1/port0/line2")  # default value
        self.digital_input_options = ["Dev1/port0/line0", "Dev1/port0/line1", "Dev1/port0/line2", "Dev1/port0/line3", "Dev1/port0/line4", "Dev1/port0/line5", "Dev1/port0/line6", "Dev1/port0/line7"]
        self.digital_input_dropdown = OptionMenu(root, self.digital_input_var, *self.digital_input_options)
        self.digital_input_dropdown.grid(row=3, column=1, sticky=E+W)

        # Create the connection indicator
        self.connection_indicator = Label(root, text="Not connected", bg="red", font=("Helvetica", 10, "bold"))
        self.connection_indicator.grid(row=4, column=0, columnspan=2, ipady=5, sticky=E+W)

        # Create the connect/disconnect button
        self.connect_button = Button(root, text="Connect", command=self.connect)
        self.connect_button.grid(row=5, column=0, columnspan=2, ipady=5, sticky=E+W)

        # Update the window size
        root.update_idletasks()
        root.geometry(f'300x{root.winfo_height()}')
        
    def connect(self):
        import time
        if self.ws is not None:
            self.stop_thread.set()
            time.sleep(0.1)
            self.reset()
        else:
            # Connect to a new WebSocket connection
            print("Connecting to OBS Studio...")
            try:
                # Start a new thread to monitor the digital line
                self.ws = obs.ReqClient(host=self.host_entry.get(), port=int(self.port_entry.get()), password=self.password_entry.get())
                self.connection_indicator.config(text="Connected", bg="green")
                self.connect_button.config(text="Disconnect")

                # Create a new NI-DAQmx task
                self.task = nidaqmx.Task()
                self.task.di_channels.add_di_chan(self.digital_input_var.get())
                
                # Test if the line is working
                self.task.read()
                
                self.stop_thread.clear()
                time.sleep(0.1)
                threading.Thread(target=self.monitor_digital_line).start()
                print("Connected to OBS Studio.")

            except Exception as e:
                messagebox.showerror("Error", f"Failed to connect: {e}")

    def monitor_digital_line(self):
        import time
        prev_state = None
        print("Monitoring digital line...")
        try:
            while not self.stop_thread.is_set():
                # Read the current state of the digital line
                if not self.task_block.is_set():
                    curr_state = self.task.read()

                # If the line went from low to high, start recording
                if prev_state == False and curr_state == True:
                    self.ws.start_record()
                    print("Recording...")
                if prev_state == True and curr_state == False:
                    self.ws.stop_record()
                    print("Stopped recording.")

                prev_state = curr_state

                # Sleep for a short time to reduce CPU usage
                time.sleep(0.01)
        except nidaqmx.DaqError as e:
            messagebox.showerror("Error", f"Failed to read from the digital line: {e}")
        except Exception as e:
            messagebox.showerror("Error", f"Lost connection to OBS Studio: {e}")

        while self.task_block.is_set():
            print("Waiting for task to close...", end="\r")
            time.sleep(1)
        print("                            ")
        self.reset()
        print("Stopped monitoring digital line.")

    def reset(self):
        import time
        self.stop_thread.set()
        time.sleep(1)        
        try:
            if self.ws is not None:
                self.ws.disconnect()
        except:
            messagebox.showerror("Error", "Failed to disconnect from OBS Studio. Please restart the application.")
        self.ws = None
        try:
            if self.task is not None:
                self.task_block.set()
                self.task.close()
                self.task_block.clear()
        except:
            messagebox.showerror("Error", "Failed to close the NI-DAQmx task. Please restart the application.")
        self.task = None
        try:
            self.connection_indicator.config(text="Not connected", bg="red")
        except:
            pass
        try:            
            self.connect_button.config(text="Connect")
        except:
            pass

    def on_close(self):
        self.reset()
        self.root.destroy()
        self.root.quit()
        
if __name__ == "__main__":
    # # Create the parser
    # parser = argparse.ArgumentParser(description="Connect to OBS Studio via WebSocket.")

    # # Add the arguments
    # parser.add_argument("--host", default="LRI-110116", help="The host to connect to.")
    # parser.add_argument("--port", type=int, default=4455, help="The port to connect to.")
    # parser.add_argument("--password", default=None, help="The password for the WebSocket connection.")

    # # Parse the arguments
    # args = parser.parse_args()
    
    root = Tk()
    root.title("OBS WebSocket Client")

    app = App(root)
    
    root.mainloop()

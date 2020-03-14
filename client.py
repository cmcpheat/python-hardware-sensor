# ------ References
# https://www.youtube.com/watch?v=gjU3Lx8XMS8
# https://stackoverflow.com/questions/3352918/how-to-center-a-window-on-the-screen-in-tkinter
# https://stackoverflow.com/questions/16782047/how-to-add-an-icon-of-my-own-to-a-python-program
# https://www.youtube.com/playlist?list=PL6gx4Cwl9DGBwibXFtPtflztSNPGuIB_d
# https://stackoverflow.com/questions/18537918/set-window-icon
# https://stackoverflow.com/questions/1526747/ideal-size-for-ico
# https://www.youtube.com/watch?v=PSm-tq5M-Dc&list=PL6gx4Cwl9DGBwibXFtPtflztSNPGuIB_d&index=9
# https://matplotlib.org/gallery/user_interfaces/embedding_in_tk_canvas_sgskip.html
# https://pythonprogramming.net/tkinter-depth-tutorial-making-actual-program/
# https://stackoverflow.com/questions/31440167/placing-plot-on-tkinter-main-window-in-python
# https://stackoverflow.com/questions/4073660/python-tkinter-embed-matplotlib-in-gui
# https://stackoverflow.com/questions/2395431/using-tkinter-in-python-to-edit-the-title-bar
# https://pythonprogramming.net/embedding-live-matplotlib-graph-tkinter-gui/
# https://stackoverflow.com/questions/46495160/make-a-label-bold-tkinter
# https://matplotlib.org/users/text_intro.html
# https://matplotlib.org/users/legend_guide.html
# https://matplotlib.org/api/_as_gen/matplotlib.lines.Line2D.html
# https://stackoverflow.com/questions/12444716/how-do-i-set-the-figure-title-and-axes-labels-font-size-in-matplotlib
# https://docs.python.org/2/library/socket.html
# https://wiki.python.org/moin/TcpCommunication#Client
# https://docs.python.org/2/library/json.html

import socket
import json
from tcp_settings import IP, PORT
import tkinter
from tkinter import *
import tkinter.ttk as ttk
from functools import partial
import time
import numpy as np
import matplotlib as mpl
from matplotlib import style
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.patches as mpatches
import warnings
import matplotlib.cbook
warnings.filterwarnings("ignore",category=matplotlib.cbook.mplDeprecation)
# https://stackoverflow.com/questions/24502500/python-matplotlib-getting-rid-of-matplotlib-mpl-warning


style.use("ggplot") # style of graph
BG_COLOUR = "#f7f7f7" # bg colours
LARGE_FONT = ("Arial", 10, "bold") # large font for headings
SMALL_FONT = ("Arial", 8) # smaller font for 'About' window


# last pushed button
# changes state to value of button, to prevent data being reset/cleared if the button pushed is the same as the last
def enum(**named_values):
    return type('Enum', (), named_values)
LastPush = enum(TEMP='temp', LOAD='load', CLOCK='clock', POWER='power')

# GUI class
class ClientApp(tkinter.Frame):

    # init method - creates window, sets bg colour, starts timer to plot on X axis
    def __init__(self, master=None):
        tkinter.Frame.__init__(self, master)
        master.configure(background=BG_COLOUR)
        self.starttime = (time.time())
        self.CreateWidgets()

    # function creates all widgets
    def CreateWidgets(self):

        # ------ set title and icon of application
        self.winfo_toplevel().title("ScanWare")
        self.winfo_toplevel().iconbitmap(r'icon.ico')

        # ------ frames
        # creates left frame for labels and buttons
        leftFrame = Frame(master=root, width=150, height=300, bg=BG_COLOUR)
        leftFrame.grid(row=0, column=0, padx=10, pady=0)
        leftFrame.grid_propagate(0)
        # creates right frame for graph
        graphFrame = Frame(master=root, width=0, height=50)
        graphFrame.grid(row=0, column=1, pady=2)

        # ------ menus
        # dropdown menu bar
        menuBar = Menu(master=root)
        master=root.config(menu=menuBar)
        # 'File' menu
        fileMenu = Menu(menuBar, tearoff=0)
        menuBar.add_cascade(label="File", menu=fileMenu)
        fileMenu.add_command(label="Exit", command=root.destroy)
        # 'Edit' menu
        editMenu = Menu(menuBar, tearoff=0)
        menuBar.add_cascade(label="Edit", menu=editMenu)
        editMenu.add_command(label="Reset", command=lambda: self.ResetData())
        # 'Help' menu
        helpMenu = Menu(menuBar, tearoff=0)
        menuBar.add_cascade(label="Help", menu=helpMenu)
        helpMenu.add_command(label="About", command=lambda: self.AboutWindow())

        # ------ labels
        # cpu
        label_cpu = Label(leftFrame, text="CPU", font=LARGE_FONT)
        label_cpu.grid(row=0, column=0, padx=10, pady=10, sticky=W)
        # clocks
        label_clock = Label(leftFrame, text="Clocks", font=LARGE_FONT)
        label_clock.grid(row=4, column=0, padx=10, pady=10, sticky=W)

        # ------ buttons and commands
        # cpu temperatures
        self.temp_button = ttk.Button(leftFrame, text="Temperature", width=20, command=self.GetTemp)
        self.temp_button.grid(row=1, column=0, padx=10, pady=5, sticky=W)
        # cpu loads
        self.load_button = ttk.Button(leftFrame, text="Load", width=20, command=self.GetLoad)
        self.load_button.grid(row=2, column=0, padx=10, pady=5, sticky=W)
        # cpu powers
        self.power_button = ttk.Button(leftFrame, text="Power", width=20, command=self.GetPower)
        self.power_button.grid(row=3, column=0, padx=10, pady=5, sticky=W)
        # clock speeds
        self.clock_button = ttk.Button(leftFrame, text="Clock Speed", width=20, command=self.GetClock)
        self.clock_button.grid(row=5, column=0, padx=10, pady=5, sticky=W)
        # reset
        self.reset_button = ttk.Button(master=root, text="Reset", width=15, command=lambda: self.ResetData())
        self.reset_button.grid(row=2, column=1, pady=20)

        # ------ graph / figure
        # create figure and set size
        self.fig=plt.figure(figsize=(8,5), facecolor=BG_COLOUR)
        # multiple axes for multiple plots
        self.ax0 = self.fig.add_axes([0.1, 0.1, 0.8, 0.8], polar=False)
        self.ax1 = self.fig.add_axes([0.1, 0.1, 0.8, 0.8], polar=False)
        self.ax2 = self.fig.add_axes([0.1, 0.1, 0.8, 0.8], polar=False)
        self.ax3 = self.fig.add_axes([0.1, 0.1, 0.8, 0.8], polar=False)
        # creates graphs
        self.canvas = FigureCanvasTkAgg(self.fig, graphFrame)
        self.canvas.get_tk_widget().grid(row=0, column=1, padx=0)
        self.canvas.draw()

        # ------ empty lists for cpu temperature, cpu loads, clock speeds and cpu powers for X and Y axes
        # cpu temperatures
        self.temp_c1_x = [] # x axis - time
        self.temp_c1_y = [] # y axis core 1
        self.temp_c2_y = [] # y axis core 2
        # cpu load times
        self.load_c1_x = [] # x axis - time
        self.load_c1_y = [] # y axis core 1
        self.load_c2_y = [] # y axis core 2
        # clock speeds
        self.clock_c1_x = [] # x axis - time
        self.clock_c1_y = [] # y axis core 1
        self.clock_c2_y = [] # y axis core 2
        self.clock_bs_y = [] # y axis bus speed
        # cpu powers
        self.power_cd_x = [] # x asis - time
        self.power_cd_y = [] # y axis cpu dram
        self.power_cp_y = [] # y axis cpu package
        self.power_cc_y = [] # y axis cpu cores
        self.power_cg_y = [] # y axis cpu graphics

        # sets default button state to 'temp' - this will enumarate each time a different button is pressed
        self.prev_button_state = LastPush
        self.prev_button_state = LastPush.TEMP

    # function creates 'About' window
    def AboutWindow(msg):
        # creates 'About ScanWare' window
        about_window = Tk()
        about_window.config(bg=BG_COLOUR)
        about_window.winfo_toplevel().title("About ScanWare")
        about_window.winfo_toplevel().iconbitmap(r'icon.ico')
        # text box + information
        about_txt = Text(about_window, width=30, height=5, font=SMALL_FONT, bg=BG_COLOUR, relief=FLAT)
        about_txt.config(state=NORMAL)
        about_txt.insert(END, "© ScanWare\nVersion 1.0\nChris McPheat\nIntro to Software Development\nGRLA07002\nUWS")
        about_txt.config(state=DISABLED)
        about_txt.pack(side=TOP, fill="x", padx=50, pady=20)
        # 'OK' button, which kills window
        ok_btn = ttk.Button(about_window, text="OK", command=about_window.destroy)
        ok_btn.pack(pady=20)
        # loops the window
        about_window.mainloop()

    # function pulls out data from response from server
    def ExtractResponse(self, message, key):
        # extract value by key from the string message
        data_json = json.loads(message)
        val = int(data_json[key])
        return val

    # function is called when 'Temperature' button is pressed
    def GetTemp(self):

        if self.prev_button_state != LastPush.TEMP: # if last button pushed was not temperature, then reset graph
            self.ResetData()
            self.prev_button_state = LastPush.TEMP # set last push to temperature

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            # Connect to server and send data
            sock.connect((IP, PORT)) # import IP and port from tcp_settings module

            # request cpu temperature data from the server
            request = {"type": "request",
                       "param": "cpu_core_temp"}
            sock.sendall(bytes(json.dumps(request), "utf-8"))

            # receives response from server
            response = str(sock.recv(1024), "utf-8")
            val1 = self.ExtractResponse(response, "CPU Core #1") # cpu core #1 data
            val2 = self.ExtractResponse(response, "CPU Core #2") # cpu core #2 data

            x = time.time() # x axis is the time
            x = x - self.starttime
            y1 = val1 # for plotting cpu core #1 data on y axis
            y2 = val2 # for plotting cpu core #2 data on y axis

            self.temp_c1_x.append(x) # append time to list
            self.temp_c1_y.append(y1) # append cpu core #1 data to list
            self.temp_c2_y.append(y2) # append cpu core #2 data to list

            label_x = 'Time (s)' # sets x label
            label_y = 'Temperature (°C)' # sets y label
            legend_0 = mpatches.Patch(color='#5B76AC', label='CPU Core #1') # sets legend colour core #1
            legend_1 = mpatches.Patch(color='#F96B6F', label='CPU Core #2') # sets legend colour core #2

            plt.legend(handles=[legend_0, legend_1]) # plots the legend to the graph
            plt.xlabel(label_x, fontsize=8, labelpad=10) # plot x axis label to graph
            plt.ylabel(label_y, fontsize=7, labelpad=10) # plot y axis label to graph

            self.PlotData(self.temp_c1_x, self.temp_c1_y, 0) # plot data to graph
            self.PlotData(self.temp_c1_x, self.temp_c2_y, 1) # plot data to graph

    # function is called when 'Load' button is pressed
    def GetLoad(self):
        if self.prev_button_state != LastPush.LOAD: # if last button pushed was not load, then reset graph
            self.ResetData()
            self.prev_button_state = LastPush.LOAD # set last push to load

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            # Connect to server and send data
            sock.connect((IP, PORT)) # import IP and port from tcp_settings module

            # request cpu load data from the server
            request = {"type": "request",
                       "param": "cpu_core_load"}
            sock.sendall(bytes(json.dumps(request), "utf-8"))

            # Receive load data from the server
            response = str(sock.recv(2048), "utf-8")
            val1 = self.ExtractResponse(response, "CPU Core #1") # core #1 data
            val2 = self.ExtractResponse(response, "CPU Core #2") # core #2 data

            x = time.time() # x axis is time
            x = x - self.starttime
            y1 = val1 # for plotting core #1 on y axis
            y2 = val2 # for plotting core #2 on y axis

            self.load_c1_x.append(x) # append time to list
            self.load_c1_y.append(y1) # append core #1 to list
            self.load_c2_y.append(y2) # append core #2 to list

            label_x = 'Time (s)' # x axis label
            label_y = 'Load (%)' # y axis label
            legend_0 = mpatches.Patch(color='#5B76AC', label='CPU Core #1') # legenbd colour core #1
            legend_1 = mpatches.Patch(color='#F96B6F', label='CPU Core #2') # legend colour core #2

            plt.legend(handles=[legend_0, legend_1]) # plot legend to graph
            plt.xlabel(label_x, fontsize=8, labelpad=10) # plot x axis label to graph
            plt.ylabel(label_y, fontsize=8, labelpad=10) # plot y axis label to graph

            self.PlotData(self.load_c1_x, self.load_c1_y, 0) # plot data to graph
            self.PlotData(self.load_c1_x, self.load_c2_y, 1) # plot data to graph

    # function is called when 'Power' button is pressed
    def GetPower(self):
        if self.prev_button_state != LastPush.POWER: # if last button pushed was not power, then reset graph
            self.ResetData()
            self.prev_button_state = LastPush.POWER # set last push to power

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            # Connect to server and send data
            sock.connect((IP, PORT)) # import IP and port from tcp_settings module

            # request cpu load data from the server
            request = {"type": "request",
                       "param": "cpu_core_power"}
            sock.sendall(bytes(json.dumps(request), "utf-8"))

            # Receive load data from the server
            response = str(sock.recv(2048), "utf-8")

            val1 = self.ExtractResponse(response, "CPU DRAM") # cpu dram data
            val2 = self.ExtractResponse(response, "CPU Package") # cpu package data
            val3 = self.ExtractResponse(response, "CPU Cores") # cpu cores data
            val4 = self.ExtractResponse(response, "CPU Graphics") # cpu graphics data

            x = time.time() # x axis is time
            x = x - self.starttime
            y1 = val1 # for plotting cpu dram to graph
            y2 = val2 # for plotting cpu package to graph
            y3 = val3 # for plotting cpu cores to graph
            y4 = val4 # for plotting cpu graphics to graph

            self.power_cd_x.append(x) # append time to list
            self.power_cd_y.append(y1) # append dram data to list
            self.power_cp_y.append(y2) # append package data to list
            self.power_cc_y.append(y3) # append cores data to graph
            self.power_cg_y.append(y4) # append graphics data to graph

            label_x = 'Time (s)' # sets x axis label
            label_y = 'Power (W)' # sets y axis label
            legend_0 = mpatches.Patch(color='#5B76AC', label='DRAM') # legend colour dram
            legend_1 = mpatches.Patch(color='#F96B6F', label='Package') # legend colour package
            legend_2 = mpatches.Patch(color='#16A28F', label='Cores') # legend colour cores
            legend_3 = mpatches.Patch(color='#EAA846', label='Graphics') # legend colour graphics

            plt.legend(handles=[legend_0, legend_1, legend_2, legend_3]) # plots legend to graph
            plt.xlabel(label_x, fontsize=8, labelpad=10) # plots x axis label to graph
            plt.ylabel(label_y, fontsize=8, labelpad=10) # plots y axis label to graph


            self.PlotData(self.power_cd_x, self.power_cd_y, 0) # plot data to graph
            self.PlotData(self.power_cd_x, self.power_cp_y, 1) # plot data to graph
            self.PlotData(self.power_cd_x, self.power_cc_y, 2) # plot data to graph
            self.PlotData(self.power_cd_x, self.power_cg_y, 3) # plot data to graph

    # function is called when 'Clock Speed' button is pressed
    def GetClock(self):
        if self.prev_button_state != LastPush.CLOCK: # if last button pushed was not clock speed, then reset graph
            self.ResetData()
            self.prev_button_state = LastPush.CLOCK # sets last push to clock speed

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            # Connect to server and send data
            sock.connect((IP, PORT)) # import IP and port from tcp_settings module

            # request cpu load data from the server
            request = {"type": "request",
                       "param": "clock_speeds"}
            sock.sendall(bytes(json.dumps(request), "utf-8"))

            # Receive load data from the server
            response = str(sock.recv(2048), "utf-8")

            val1 = self.ExtractResponse(response, "CPU Core #1") # cpu core #1 data
            val2 = self.ExtractResponse(response, "CPU Core #2") # cpu core #2 data
            val3 = self.ExtractResponse(response, "Bus Speed") # bus speed data

            x = time.time() # x axis is the time
            x = x - self.starttime
            y1 = val1 # for plotting core #1 to graph
            y2 = val2 # for plotting core #2 to graph
            y3 = val3 # for plotting bus speed to graph

            self.clock_c1_x.append(x) # appends time to list
            self.clock_c1_y.append(y1) # append core #1 to list
            self.clock_c2_y.append(y2) # append core #2 to list
            self.clock_bs_y.append(y3) # append bus speed to list

            label_x = 'Time (s)' # x axis label
            label_y = 'Rate (MHz)' # y axis label
            legend_0 = mpatches.Patch(color='#5B76AC', label='CPU Core #1') # sets legend colour core #1
            legend_1 = mpatches.Patch(color='#F96B6F', label='CPU Core #2') # sets legend colour core #2
            legend_2 = mpatches.Patch(color='#16A28F', label='Bus Speed') # sets legend colour bus speed

            plt.legend(handles=[legend_0, legend_1, legend_2]) # plot legend to graph
            plt.xlabel(label_x, fontsize=8, labelpad=10) # plot x axis label to graph
            plt.ylabel(label_y, fontsize=8, labelpad=10) # plot y axis label to graph

            self.PlotData(self.clock_c1_x, self.clock_c1_y, 0) # plot data to graph
            self.PlotData(self.clock_c1_x, self.clock_c2_y, 1) # plot data to graph
            self.PlotData(self.clock_c1_x, self.clock_bs_y, 2) # plot data to graph

    # function plots data to the graph
    def PlotData(self, x, y, id):
    # multiple plots to the graph
        if id == 0:
            self.ax0.plot(x, y, color='#5B76AC', marker='.', linestyle='solid', linewidth=1, markersize=0) # blue
        elif id == 1:
            self.ax1.plot(x, y, color='#F96B6F', marker='.', linestyle='solid', linewidth=1, markersize=0) # red
        elif id == 2:
            self.ax2.plot(x, y, color='#16A28F', marker='.', linestyle='solid', linewidth=1, markersize=0) # green
        elif id == 3:
            self.ax3.plot(x, y, color='#EAA846', marker='.', linestyle='solid', linewidth=1, markersize=0) # yellow
        self.canvas.draw()

    # function clears the graph
    def ResetData(self):
        # ------ resets graph
        # clears axes
        self.ax0.clear()
        self.ax1.clear()
        self.ax2.clear()
        self.ax3.clear()
        # clears start time
        self.starttime = (time.time())
        # clears temp data
        self.temp_c1_x.clear()
        self.temp_c1_y.clear()
        self.temp_c2_y.clear()
        # clears load data
        self.load_c1_x.clear()
        self.load_c1_y.clear()
        self.load_c2_y.clear()
        # clears clock data
        self.clock_c1_x.clear()
        self.clock_c1_y.clear()
        self.clock_c2_y.clear()
        self.clock_bs_y.clear()
        # clears power data
        self.power_cd_x.clear()
        self.power_cd_y.clear()
        self.power_cp_y.clear()
        self.power_cc_y.clear()
        self.power_cg_y.clear()
        # re-draws blank canvas
        self.canvas.draw()


if __name__ == '__main__':
    # tkinter gui
    # create root
    root = Tk()
    client = ClientApp(master=root)
    client.mainloop()
    print("exiting...")

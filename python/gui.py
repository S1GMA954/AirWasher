# GUI imports
from tkinter import *
# Arduino connection
import serial
# parallel execution
import threading
# Delays
import time
# to generate random data
import random
# Custom List
from DataList import DataList
# Custom widget
from OwnWidgets import Card
# CSV import
import csv
# Matplotlib for Charts
import matplotlib.pyplot as plt
from matplotlib import pyplot
from matplotlib.animation import FuncAnimation
# Matplotlib + Tkinter
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# GUI config imports
from guiConfigs import colors, fonts, fcolors

# vars for global control
data_arduino = DataList(["airPower,particles,airFlow,waterFlow,faucetState,ppm"])
timeOfUpdate = 1000 # in Miliseconds

# Getting data

def reading_data(stopFlag):
    """
        This function allows to simulate the entry data from Arduino
    """
    #ser = serial.Serial('COM3', 9600)
    while not stopFlag.is_set():
        #data = ser.readline().decode('ascii').strip()
        dataList = DataList()
        for i in range(1,3,1):
            airPower = random.randrange(1,255, 1)
            particles = round(random.uniform(1,3), 1)
            airFlow = round(random.uniform(2,3), 1)
            waterFlow = round(random.uniform(2,3), 2)
            faucetState = 1
            ppm = random.randrange(1,254, 1)
            dataList.append(str(airPower))
            dataList.append(str(particles))
            dataList.append(str(airFlow))
            dataList.append(str(waterFlow))
            dataList.append(str(faucetState))
            dataList.append(str(ppm))
        
        separator = ","
        result = separator.join(dataList)
        data_arduino.append(result)
        time.sleep(1)


def controlsIf():
    ctrl = Toplevel()
    ctrl.title("Controles")
    ctrl.geometry("900x500")
    ctrl.config(bg=colors["fondo"])

    # config
    normal_x = 300

    # Data
    power = 0

    # Functionalities
    def on_slider_change(value):
        nonlocal power
        power = int(value)
        pass

    def on_checkbutton_toggle():
        if var.get() == 1:
            print("Interruptor encendido")
        else:
            print("Interruptor apagado")

    def onSubmit():
        print("sent")
        ctrl.destroy()

    # Controller to define the air aspire power
    currentValue = IntVar()
    slider = Scale(
            ctrl,
            from_=0,
            to=100,
            orient='horizontal',
            resolution=1,
            variable=currentValue,
            command= lambda value: on_slider_change(currentValue.get()),
        ).place(x=normal_x, y=190)
    
    var = IntVar()
    checkbutton = Checkbutton(
        ctrl, 
        text="En marcha/Detenido", 
        variable=var, 
        command=on_checkbutton_toggle
        ).place(x=normal_x, y=270)


    # Title 1
    t1 = Label(
        ctrl,
        text="Controles del sistema", 
        font=("Verdana", 12),
        bg = colors["fondo"],
        fg="white"
        ).place(x=300, y=20)
    
    
    # Labels 
    p1 = Label(
        ctrl,
        text=f'Advertencia: Cualquier cambio realizado aquí\ndebe confirmarse para aplicarlo sobre el sistema.', # insert the power percentage 
        font=("Verdana", 12),
        bg = colors["fondo"],
        fg="white"
        ).place(x=200, y=70)
    
    p2 = Label(
        ctrl,
        text=f'Potencia de aspirado en {power}%', # insert the power percentage 
        font=("Verdana", 12),
        bg = colors["fondo"],
        fg="white"
        ).place(x=normal_x, y=150)
    
    p3 = Label(
        ctrl,
        text=f'Estado de la llave de agua:', # insert the power percentage 
        font=("Verdana", 12),
        bg = colors["fondo"],
        fg="white"
    ).place(x=normal_x, y=230)

    submit = Button(
        ctrl,
        text="Confirmar",
        command=onSubmit,
    ).place(x=normal_x, y=350)


    

    
    
    
    ctrl.mainloop()


def root():

    # Data 
    lastData = {}
    waterFData = DataList()
    airFData = DataList()

    def updateData():
        try:
            csv_reader = csv.DictReader(data_arduino)
            rootWindow.after(timeOfUpdate, updateData)

            nonlocal lastData

            for i in csv_reader:
                lastData = i
                waterFData.append(i["waterFlow"])
                airFData.append(i["airFlow"])
            
            percentage = round((float(lastData["airPower"])/255) * 100, 0)
            airPower.set(f'Potencia de aspirado en {percentage}%')
            particles.set(f'Partículas en el aire: {lastData["particles"]} µg/m³')
            airFlow.set(f'Flujo de aire: {lastData["airFlow"]} L/min')
            waterFlow.set(f'Flujo de agua: {lastData["waterFlow"]} L/min')

            fstate = 'abierto' if lastData["faucetState"] == '1' else "cerrada"
            faucetState.set(f'Estado de la compuerta: {fstate}')

            ppm.set(f'Material disuelto: {lastData["ppm"]} ppm')
            
            pass
        except KeyboardInterrupt:
            pass
    
    
    # event of control
    stopFlag = threading.Event()

    # background tasks
    serial_thread = threading.Thread(target=reading_data, args=(stopFlag,))
    serial_thread.start()

    # GUI instance
    rootWindow = Tk()
    rootWindow.title("Sistema de monitoreo")
    rootWindow.geometry("900x500")
    rootWindow.resizable(width=False, height=False)
    # Menu
    menuBar = Menu(rootWindow)
    rootWindow.config(menu=menuBar,bg=colors["fondo"])
    # Menu options instances
    controls = Menu(menuBar, tearoff=0)
    controls.add_command(label="Abrir controles", command= controlsIf)
    shutdown = Menu(menuBar, tearoff=0)
    shutdown.add_command(label="Arrancar")
    shutdown.add_command(label="Detener")
    # Adding options to Menu
    menuBar.add_cascade(label="Controles", menu=controls)
    menuBar.add_cascade(label="Arrancar/Detener", menu=shutdown)

    sideBar = Frame(master=rootWindow)
    sideBar.config(bg=colors["sidebar"], width=180, border=1, relief='solid')
    sideBar.pack(side='left', fill=Y)


    sbOption1 = Label(
        master=sideBar, 
        text="Dashboard", 
        font=fonts["normal"], 
        fg=fcolors["sb-light-theme"], 
        bg=colors["sidebar"]
        )
    sbOption1.place(x=30,y=30)

    mainContent = Frame(master=rootWindow)
    mainContent.config(bg=colors["fondo"], border=1, relief='solid')
    mainContent.pack(side='right',expand=True, fill=X)
    scrollbar = Scrollbar(mainContent, orient=VERTICAL)
    scrollbar.pack(fill=Y, side=RIGHT, expand=FALSE)

    topFrame = Frame(mainContent)
    topFrame.pack(fill=X)

    card1 = Frame(topFrame)
    card1.config(bg=colors["card-green"], border=1, relief='solid')
    card1.grid(row=0,column=2, ipady=3, sticky='w')

    card2 = Frame(topFrame)
    card2.config(bg=colors["card-blue"], border=1, relief='solid')
    card2.grid(row=0, column=5, ipady=3, sticky='e')


    # Title 1
    t1 = Label(
        card1,
        text="Condiciones de entrada del aire", 
        font=fonts["normal"],
        bg = colors["card-green"],
        fg=fcolors["light-theme"]
        )#.place(x=60, y=20)
    t1.pack()

    # Labels 
    airPower = StringVar()
    airPower.set("Potencia de aspirado: Sin datos aún")
    p1 = Label(
        card1,
        textvariable=airPower, # insert the power percentage 
        font=fonts["normal"],
        bg = colors["card-green"],
        fg=fcolors["light-theme"]
        )#.place(x=60, y=100)
    p1.pack()

    airFlow = StringVar()
    airFlow.set('Flujo de aire: Sin datos aún')
    p2 = Label(
        card1,
        textvariable=airFlow, # insert air flow rate 
        font=fonts["normal"],
        bg = colors["card-green"],
        fg=fcolors["light-theme"]
        )#.place(x=60 , y=140)
    p2.pack()
    
    particles = StringVar()
    particles.set("Partículas en el aire: Sin datos aún")
    p3 = Label(
        card1,
        textvariable=particles, 
        font=fonts["normal"],
        bg = colors["card-green"],
        fg=fcolors["light-theme"]
        )#.place(x=60, y=180)
    p3.pack()
    
    # Title 2
    t2 = Label(
        card2,
        text="Condiciones del agua entrada", 
        font=fonts["normal"],
        bg = colors["card-blue"],
        fg=fcolors["light-theme"]
        )#.place(x=500, y=20)
    t2.pack()

    faucetState = StringVar()
    faucetState.set('Estado de la compuerta: Sin datos aún')
    p4 = Label(
        card2,
        textvariable=faucetState, # insert faucet state 
        font=fonts["normal"],
        bg = colors["card-blue"],
        fg=fcolors["light-theme"]
        )#.place(x=500, y=100)
    p4.pack()

    
    waterFlow = StringVar()
    waterFlow.set('Flujo de agua: sin datos aún')
    p5 = Label(
        card2,
        textvariable=waterFlow,   # insert water flow rate
        font=fonts["normal"],
        bg = colors["card-blue"],
        fg=fcolors["light-theme"]
        )#.place(x=500, y=140)
    p5.pack()
    
    ppm = StringVar()
    ppm.set('Material disuelto: sin datos aún')
    p6 = Label(
        card2,
        textvariable=ppm, # insert tds sensor value 
        font=fonts["normal"],
        bg = colors["card-blue"],
        fg=fcolors["light-theme"]
        )#.place(x=500, y=180)
    p6.pack()
    
    # Chart 1 : water flow rate VS air flow rate
    fig, ax1 = plt.subplots()
    ax2 = ax1.twinx()

    def animate(frame):
        ax1.clear()
        ax2.clear()
        ax1.plot(waterFData, color='tab:red') # water flow chart
        ax1.set_ylabel('caudal agua (L/min)', color='tab:red')
        ax1.yaxis.set_label_position('left')
        ax2.plot(airFData, color='tab:blue') # air flow chart
        ax2.set_ylabel('caudal aire (L/min)', color='tab:blue')  # we already handled the x-label with ax1
        ax2.yaxis.set_label_position('right')

        ax1.set_xlabel('tiempo (s)', loc='center')

        canvas.draw()


    animation = FuncAnimation(fig, animate, interval=1000, cache_frame_data=False)
    canvas = FigureCanvasTkAgg(fig, master=mainContent)
    canvas.get_tk_widget().pack()#.place(x=60, y=300)

    

    
    # END Chart 1 Configurations

    def onClosing():
        rootWindow.after_cancel(rootWindow)
        stopFlag.set()
        #serial_thread.join()
        rootWindow.quit()


    rootWindow.protocol("WM_DELETE_WINDOW", onClosing)

    rootWindow.after(1000, updateData)
    rootWindow.mainloop()

root()
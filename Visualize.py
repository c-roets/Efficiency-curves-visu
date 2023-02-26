from matplotlib import pyplot as plt
import numpy as np
import os
import re
import tkinter as tk
from tktooltip import ToolTip

# run ConverterLoss and EfficiencyCurves to generate data before running this file

# variable declaration
graphnumber = 1
graphnumberdc = 1


# functions
def atoi(text):
    return int(text) if text.isdigit() else text


# for numerical order instead of alphabetical (2,3... comes before 10)
def natural_keys(text):
    return [atoi(c) for c in re.split(r'(\d+)', text)]


def laadarraymetfilenamenuitmap(folder):
    filenames = os.listdir(folder)  # array with all filenames in folder
    # numeric instead of alphabetic sorting algoritm
    filenames.sort(key=natural_keys)
    return filenames


def data_effcurves(function_name, dir_path):
    global graphnumber
    global graphnumberdc
    arrays = laadarraymetfilenamenuitmap(dir_path)
    print(arrays)
    for array in arrays:
        file_path = os.path.join(dir_path, array)
        data = np.load(file_path)
        transposed_data = np.transpose(data)
        # voltage data is in columns and inverter load in rows, for visualization it is better to have all values of
        # 1 voltage range to plot for a given inverter load %
        func = globals()[function_name]
        func(transposed_data)
    # uncomment here to show to plots all at the same time <-> on by one (see plot functions for this)
    plt.show()
    # graphnumber back to one, so other functions can start from 1
    graphnumber = 1
    graphnumberdc = 1


def plot_effcurves_pv_ac(data):
    global graphnumber
    # create a separate plot for each row of the transposed array
    plt.figure(graphnumber)
    for i in range(data.shape[0]):
        plt.plot(data[i])
        # print(i)
    plt.title(f'{graphnumber} kW')
    # add a legend to the plot
    plt.legend([f"Voltage:{180 + i * 10}" for i in range(15)])
    plt.xlabel('Efficiency')
    plt.ylabel('Inverter load %')
    # uncomment to show the plots, one by one
    # plt.show()
    graphnumber += 1


def plot_effcurves_pv_dc(data):
    global graphnumber
    # create a separate plot for each row of the transposed array
    plt.figure(graphnumber)
    for i in range(data.shape[0]):
        plt.plot(data[i])
        # print(i)
    plt.title(f'{graphnumber * 5} kW')
    # add a legend to the plot
    plt.legend([f"Voltage:{230 + i * 10}" for i in range(27)])
    plt.xlabel('Efficiency')
    plt.ylabel('Inverter load %')
    # uncomment to show the plots, one by one
    # plt.show()
    graphnumber += 1


def plot_effcurves_battery_ac(data):
    global graphnumber
    # create a separate plot for each row of the transposed array
    plt.figure(graphnumber)
    for i in range(data.shape[0]):
        x = np.arange(-100, 100)
        y = data[i]
        plt.plot(x, y)
        # print(i)
    plt.title(f'{graphnumber} kW')
    # add a legend to the plot
    plt.legend([f"Voltage:{40 + i * 5}" for i in range(8)])
    plt.xlabel('Efficiency')
    plt.ylabel('Inverter load %')
    # uncomment to show the plots, one by one
    # plt.show()
    graphnumber += 1


def plot_effcurves_battery_dc(data):
    global graphnumber
    # print('Grafnummer: ' + str(graphnumber))
    plt.figure(graphnumber)
    for i in range(data.shape[0]):
        x = np.arange(-100, 101)
        y = data[i]
        plt.plot(x, y)
        # print(i)
    plt.title(f'{graphnumber * 25} kW')
    # add a legend to the plot
    plt.legend([f"Voltage:{690 + i * 10}" for i in range(28)])
    plt.xlabel('Efficiency')
    plt.ylabel('Inverter load %')
    # uncomment to show the plots, one by one
    # plt.show()
    graphnumber += 1


def plot_effcurves_evbattery_ac_dcdc(data):
    global graphnumber
    # print('Grafnummer: ' + str(graphnumber))
    p_ev = [2.3, 3.7, 5.8, 7.4]
    plt.figure(graphnumber)
    for i in range(data.shape[0]):
        x = np.arange(-100, 101)
        y = data[i]
        plt.plot(x, y)
        # print(i)
    plt.title(f'{p_ev[graphnumber - 1]} kW')
    # add a legend to the plot
    plt.legend([f"Voltage:{300 + i * 10}" for i in range(7)])
    plt.xlabel('Efficiency')
    plt.ylabel('Inverter load %')
    # uncomment to show the plots, one by one
    # plt.show()
    graphnumber += 1


def plot_effcurves_evbattery_ac_dcac(data):
    global graphnumber
    # print('Grafnummer: ' + str(graphnumber))
    p_ev = [2.3, 3.7, 5.8, 7.4]
    plt.figure(graphnumber)
    plt.plot(data)
    # print(i)
    plt.title(f'{p_ev[graphnumber - 1]} kW')
    # add a legend to the plot
    plt.legend(["Voltage: 325"])
    plt.xlabel('Efficiency')
    plt.ylabel('Inverter load %')
    # uncomment to show the plots, one by one
    # plt.show()
    graphnumber += 1


def plot_effcurves_evbattery_dc(data):
    global graphnumber
    global graphnumberdc
    p_ev = [2.3, 3.7, 5.8, 7.4]
    # transposed van 3D array zal eerste en derde swappen en tweede gelijk, dus hier P en Vdc geswapt
    # for p in range(len(P_ev)): wordt buiten de functie gedaan
    # create a separate plot for each row of the transposed array
    # print(data)
    # print(data.shape[0])
    # print(data.shape[1])
    # print(data.shape[2])
    for i in range(data.shape[0]):  # Vdc levels
        plt.figure(graphnumberdc)
        for j in range(data.shape[1]):  # Voltage levels
            plt.plot(data[i][j])
        plt.title(f'{p_ev[graphnumber - 1]} kW' + f" Vdc:{160 + i * 20}")  # en + {data.shape[j]} V')
        # add a legend to the plot
        plt.legend([f"Voltage:{250 + i * 10}" for i in range(12)])
        graphnumberdc += 1
    plt.xlabel('Efficiency')
    plt.ylabel('Inverter load %')
    # uncomment to show the plots, one by one
    # plt.show()
    graphnumber += 1


def plot_effcurves_evpv_dc(data):
    global graphnumber
    global graphnumberdc
    for i in range(data.shape[0]):  # Vi levels
        plt.figure(graphnumberdc)
        for j in range(data.shape[1]):  # Vo levels
            plt.plot(data[i][j])
        print(graphnumber)
        plt.title(f'{graphnumber * 5} kW' + f" Vi:{160 + i * 20}")  # en + {data.shape[j]} V')
        # add a legend to the plot
        plt.legend([f"Vo:{500 + i * 10}" for i in range(11)])
        graphnumberdc += 1
    plt.xlabel('Efficiency')
    plt.ylabel('Inverter load %')
    # uncomment to show the plots, one by one
    # plt.show()
    graphnumber += 1


def plot_effcurves_grid_ac_dcac(data):
    global graphnumber
    # create a separate plot for each row of the transposed array

    plt.figure(graphnumber)

    plt.plot(data)
    # print(i)
    plt.title(f'{graphnumber} kW 230Vac-325Vdc')
    # add a legend to the plot
    plt.xlabel('Efficiency')
    plt.ylabel('Inverter load %')
    # uncomment to show the plots, one by one
    # plt.show()
    graphnumber += 1


def plot_effcurves_grid_dc_dcac(data):
    global graphnumber
    # create a separate plot for each row of the transposed array

    plt.figure(graphnumber)

    plt.plot(data)
    # print(i)
    plt.title(f'{graphnumber * 80} kW 400Vac-700Vdc')
    # add a legend to the plot
    plt.xlabel('Efficiency')
    plt.ylabel('Inverter load %')
    # uncomment to show the plots, one by one
    # plt.show()
    graphnumber += 1


# main
root = tk.Tk()
root.title("Visualizatie efficientie curves")
root.geometry('1350x150')  # lengte x hoogte

button1 = tk.Button(root, text="PV in AC", width=20, font=("Arial", 16), bg="#2196f3",
                    relief="raised",
                    command=lambda: data_effcurves('plot_effcurves_pv_ac', r'data/effcurves/ac/dc-dc/pv'))
button2 = tk.Button(root, text="PV in DC", width=20, font=("Arial", 16), bg="#2196f3",
                    relief="raised",
                    command=lambda: data_effcurves('plot_effcurves_pv_dc', r'data\effcurves\dc\dc-dc\pv'))
button3 = tk.Button(root, text="Stationary Batterij in AC", width=20, font=("Arial", 16), bg="#2196f3",
                    relief="raised",
                    command=lambda: data_effcurves('plot_effcurves_battery_ac', r'data\effcurves\ac\dc-dc\bess'))
button4 = tk.Button(root, text="Stationary Battery in DC", width=20, font=("Arial", 16), bg="#2196f3",
                    relief="raised",
                    command=lambda: data_effcurves('plot_effcurves_battery_dc', r'data\effcurves\dc\dc-dc\bess'))
button5 = tk.Button(root, text="EV Batterij in AC: DCDC", width=20, font=("Arial", 16), bg="#2196f3",
                    relief="raised",
                    command=lambda: data_effcurves('plot_effcurves_evbattery_ac_dcdc', r'data\effcurves\ac\dc-dc\ev'))
button6 = tk.Button(root, text="EV Batterij in AC: DCAC", width=20, font=("Arial", 16), bg="#2196f3",
                    relief="raised",
                    command=lambda: data_effcurves('plot_effcurves_evbattery_ac_dcac', r'data\effcurves\ac\dc-ac\ev'))
button7 = tk.Button(root, text="EV Batterij in DC", width=20, font=("Arial", 16), bg="#2196f3",
                    relief="raised",
                    command=lambda: data_effcurves('plot_effcurves_evbattery_dc', r'data\effcurves\dc\dc-dc\ev'))
ToolTip(button7, msg="Meer dan 20 figuren, mogelijks warning")
button8 = tk.Button(root, text="EV PV in DC", width=20, font=("Arial", 16), bg="#2196f3",
                    relief="raised",
                    command=lambda: data_effcurves('plot_effcurves_evpv_dc', r'data\effcurves\dc\dc-dc\ev_pv'))
ToolTip(button8, msg="Veel figuren, intensief op RAM & CPU!")
button9 = tk.Button(root, text="Grid in AC: DCAC", width=20, font=("Arial", 16), bg="#2196f3",
                    relief="raised",
                    command=lambda: data_effcurves('plot_effcurves_grid_ac_dcac', r'data\effcurves\ac\dc-ac\grid'))
button10 = tk.Button(root, text="Grid in DC", width=20, font=("Arial", 16), bg="#2196f3",
                     relief="raised",
                     command=lambda: data_effcurves('plot_effcurves_grid_dc_dcac', r'data\effcurves\dc\dc-ac\grid'))

button1.grid(row=0, column=0, padx=10)
button2.grid(row=1, column=0, padx=10)
button3.grid(row=0, column=1, padx=10)
button4.grid(row=1, column=1, padx=10)
button5.grid(row=0, column=2, padx=10)
button6.grid(row=1, column=2, padx=10)
button7.grid(row=2, column=2, padx=10)
button8.grid(row=0, column=3, padx=10)
button9.grid(row=0, column=4, padx=10)
button10.grid(row=1, column=4, padx=10)

try:
    root.mainloop()
except Exception as e:
    print(f"An error occurred: {e}")
    root.quit()

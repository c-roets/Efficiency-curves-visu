from matplotlib import pyplot as plt
import numpy as np
import os
import re
import tkinter as tk

# run ConverterLoss and EfficiencyCurves to generate data before running this file

# variable declaration
graphnumber = 1


# functions
def atoi(text):
    return int(text) if text.isdigit() else text


def natural_keys(text):
    return [atoi(c) for c in re.split(r'(\d+)', text)]


def laadarraymetfilenamenuitmap(folder):
    filenames = os.listdir(folder)  # array with all filenames in folder
    # filenames.sort()
    # numeric instead of alphabetic sorting algoritm
    filenames.sort(key=natural_keys)
    return filenames


def data_effcurves(function_name, dir_path):
    global graphnumber
    arrays = laadarraymetfilenamenuitmap(dir_path)
    print(arrays)
    for array in arrays:
        file_path = os.path.join(dir_path, array)
        data = np.load(file_path)
        transposed_data = np.transpose(data)
        # voltage data zit in kolommen en inverter load in rijen, voor visualizatie is het beter om alle waarden van
        # 1 voltage range uit te zetten voor een bepaalde inverter load %
        func = globals()[function_name]
        func(transposed_data)
    # uncomment here to show to plots all at the same time <-> on by one (see next function for this)
    plt.show()
    # graphnumber back to one, if other function needs to be called
    graphnumber = 1


def plot_effcurves_pv_ac(data):
    global graphnumber
    # create a separate plot for each row of the transposed array
    for i in range(data.shape[0]):
        plt.figure(graphnumber)

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
    for i in range(data.shape[0]):
        plt.figure(graphnumber)
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
    for i in range(data.shape[0]):
        plt.figure(graphnumber)
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
    print('Grafnummer: ' + str(graphnumber))
    for i in range(data.shape[0]):
        plt.figure(graphnumber)
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


def plot_effcurves_evbattery_ac(data):
    global graphnumber
    print('Grafnummer: ' + str(graphnumber))
    P_ev = [2.3, 3.7, 5.8, 7.4]
    for i in range(data.shape[0]):
        plt.figure(graphnumber)
        x = np.arange(-100, 101)
        y = data[i]
        plt.plot(x, y)
        # print(i)
    plt.title(f'{P_ev[graphnumber-1]} kW')
    # add a legend to the plot
    plt.legend([f"Voltage:{300 + i * 10}" for i in range(7)])
    plt.xlabel('Efficiency')
    plt.ylabel('Inverter load %')
    # uncomment to show the plots, one by one
    # plt.show()
    graphnumber += 1


# main
root = tk.Tk()
root.title("Visualizatie efficientie curves")
root.geometry('600x400') # lengte x hoogte

button1 = tk.Button(root, text="Efficiency curves PV in AC", width=35, font=("Arial", 16), bg="#2196f3",
                    relief="raised",
                    command=lambda: data_effcurves('plot_effcurves_pv_ac', r'data/effcurves/ac/dc-dc/pv'))
button2 = tk.Button(root, text="Efficiency curves PV in DC", width=35, font=("Arial", 16), bg="#2196f3",
                    relief="raised",
                    command=lambda: data_effcurves('plot_effcurves_pv_dc', r'data\effcurves\dc\dc-dc\pv'))
button3 = tk.Button(root, text="Efficiency curves stationary Battery in AC", width=35, font=("Arial", 16), bg="#2196f3",
                    relief="raised",
                    command=lambda: data_effcurves('plot_effcurves_battery_ac', r'data\effcurves\ac\dc-dc\bess'))
button4 = tk.Button(root, text="Efficiency curves stationary Battery in DC", width=35, font=("Arial", 16), bg="#2196f3",
                    relief="raised",
                    command=lambda: data_effcurves('plot_effcurves_battery_dc', r'data\effcurves\dc\dc-dc\bess'))
button5 = tk.Button(root, text="Efficiency curves ev Battery in AC", width=35, font=("Arial", 16), bg="#2196f3",
                    relief="raised",
                    command=lambda: data_effcurves('plot_effcurves_evbattery_ac', r'data\effcurves\ac\dc-dc\ev'))
button1.pack(pady=10)
button2.pack(pady=10)
button3.pack(pady=10)
button4.pack(pady=10)
button5.pack(pady=10)

try:
    root.mainloop()
except Exception as e:
    print(f"An error occurred: {e}")
    root.quit()

# data_effcurves_pv_ac()
# plt.show()


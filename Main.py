"""
Main file
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

def calculateprofile(arrivalweekday, arrivalweekend, no_chargers, visu=False):
    # =============================================================================
    # EV PROFILE
    # =============================================================================
    print("Calculating arrival times distribution...")
    arrival_times_weekday = pd.read_csv(arrivalweekday, sep=';', parse_dates=True, decimal=',')[
        ['private']]
    arrival_times_weekday = arrival_times_weekday / np.sum(arrival_times_weekday)
    arrival_times_weekend = pd.read_csv(arrivalweekend, sep=';', parse_dates=True, decimal=',')[
        ['private']]
    arrival_times_weekend = arrival_times_weekend / np.sum(arrival_times_weekend)

    arrival_times = np.zeros([2, 96])  # 96 quarter hours in a day
    arrival_times[0, :] = arrival_times_weekday.values.ravel()  # first row
    arrival_times[1, :] = arrival_times_weekend.values.ravel()  # second row

    # =============================================================================
    # Visualize distribution of arrival
    # =============================================================================
    if visu:
        print("Loading graphs...")
        # Create a bar plot for each row in arrival_times
        fig, axs = plt.subplots(nrows=arrival_times.shape[0], figsize=(16, 12))
        for i in range(arrival_times.shape[0]):
            if i == 0:
                title = "Weekday Arrival Times"
            elif i == 1:
                title = "Weekend Arrival Times"
            else:
                title = f"Row {i + 1} Arrival Times"

            x_ticks = pd.date_range('00:00', '23:45', freq='15min').strftime('%H:%M')
            axs[i].bar(x_ticks, arrival_times[i], label=title)

            axs[i].set_title(title)
            axs[i].set_xlabel("Time")
            axs[i].set_ylabel("Probability")
            axs[i].set_xticks(x_ticks[::4])
            axs[i].set_xticklabels(x_ticks[::4], rotation=45, fontsize=10)
            axs[i].legend()
        fig.subplots_adjust(hspace=0.5)
        plt.show()
    print("Calculating arrival times distribution completed!")

    print("Calculating EV Energy needs...")
    # %% Distribution of Energy need - PhD Juan Van Roy  - based on OVSG
    a = 97.34
    b = 0.0003862
    c = -101.9
    d = -0.1413
    x = np.linspace(0, 70, 100)
    f = (a * np.exp(b * x)) + (c * np.exp(d * x))
    x[0] = 0
    f[0] = 0
    # omzetten naar gewone distributie
    np.set_printoptions(precision=15)
    distr = np.diff(f)
    energy_need = distr * (1. / distr.sum())

    E_charge_full = 60e3  # 60kWh Battery
    E_charge_needs = np.zeros([35040, no_chargers])
    E_charge_needs_day = np.zeros([365, no_chargers])
    day_index = 0
    if visu:
        start_date = pd.to_datetime('2022-01-01')
        datetimes = [start_date + pd.Timedelta(minutes=15 * i) for i in range(E_charge_needs.shape[0])]
        fig, ax = plt.subplots(figsize=(16, 6))
        colors = plt.cm.Set2(np.linspace(0, 1, no_chargers))

    for ch in range(0, no_chargers):
        print('charger number:' + str(ch))
        for qh in range(0, 35040):
            E_need = np.random.choice(np.linspace(1, E_charge_full / 96, 99), size=1, p=energy_need)
            # divide E_charge_full by 96 to get quarterly hourly charge requirements
            E_charge_needs[qh, ch] = E_need
            # compile every 96 quarter hours into a day
            if qh > 0 and (qh + 1) % 96 == 0:
                E_charge_needs_day[day_index, ch] = np.sum(E_charge_needs[(qh - 95):(qh + 1), ch])
                day_index += 1
        if visu:
            print("Loading graph...")
            # print(E_charge_needs.shape)
            print(E_charge_needs)

            ax.bar(datetimes, E_charge_needs[:, ch], width=pd.Timedelta(minutes=15), alpha=0.7,
                   label='Charger {}'.format(ch + 1), color=colors[ch])
        day_index = 0

    if visu:
        ax.set_xlabel('Day of year')
        ax.set_ylabel('Energy charge needs (kWh)')
        ax.set_title('Energy charge needs per quarter-hour')
        ax.legend(loc='upper left')
        print('Number of chargers plotted: {}'.format(no_chargers))
        plt.show()
    # if visu:

        # =============================================================================
        # Visualize energy needs per qh
        # =============================================================================


        # =============================================================================
        # Visualize energy needs per day
        # =============================================================================
        fig, ax = plt.subplots(figsize=(20, 8))
        colors = plt.cm.Set2(np.linspace(0, 1, no_chargers))
        for ch in range(no_chargers):
            ax.bar(range(365), E_charge_needs_day[:, ch], color=colors[ch], label='Charger {}'.format(ch + 1))

        # Set the axis labels and title
        ax.set_xlabel('Day of year')
        ax.set_ylabel('Energy charge needs (kWh)')
        ax.set_title('Energy charge needs per day')
        ax.legend(loc='upper left')
        plt.show()

    print("Summing charger values...")
    #Total energy demand of all chargers summed
    E_charge_needs_total = np.sum(E_charge_needs, axis=1)
    E_charge_needs_total = E_charge_needs_total.reshape((35040, 1))
    E_charge_needs_total = E_charge_needs_total.flatten()
    print(E_charge_needs_total)
    print("Summing charger values completed!")


    if visu:
        print("Loading graph...")
        fig, ax = plt.subplots(figsize=(20, 8))
        ax.bar(datetimes, E_charge_needs_total, width=pd.Timedelta(minutes=15), alpha=0.7, linewidth=2.0)
        ax.set_xlabel('Day of year')
        ax.set_ylabel('Energy charge needs (kWh) (sum of chargers)')
        ax.set_title('Energy charge needs per quater-hour summed')
        plt.show()

    print("Calculating EV Energy needs completed!")

    # =============================================================================
    # PV Profile
    # =============================================================================
    print("Loading PV Generation profile...")
    pv = np.load("pv_kWh_kWp.npy")
    print(pv.shape)
    print(pv)
    if visu:
        print("Loading graph...")
        start_date = pd.to_datetime('2022-01-01')
        datetimes = [start_date + pd.Timedelta(minutes=15 * i) for i in range(pv.size)]
        # Create a bar plot of the pv array
        fig, ax = plt.subplots(figsize=(16, 6))
        ax.bar(datetimes, pv, width=pd.Timedelta(minutes=15), alpha=0.7)

        # Customize the plot
        ax.set_xlabel('Date')
        ax.set_ylabel('PV Energy (kWh)')
        ax.set_title('PV Energy Generation by Quarter Hour')
        plt.show()
    print("Loading PV Generation profile completed!")
    # =============================================================================
    # Powerflow calculation
    # =============================================================================
    print("Calculating Net profile...")


    net_energy_use = E_charge_needs_total - pv

    if visu:
        print("Loading graph...")
        start_date = pd.to_datetime('2022-01-01')
        datetimes = [start_date + pd.Timedelta(minutes=15 * i) for i in range(net_energy_use.size)]
        # Create a bar plot of the pv array
        fig, ax = plt.subplots(figsize=(16, 6))
        ax.bar(datetimes, net_energy_use, width=pd.Timedelta(minutes=15), alpha=0.7)

        # Customize the plot
        ax.set_xlabel('Date')
        ax.set_ylabel('Net Energy (kWh)')
        ax.set_title('Net Energy Use by Quarter Hour')
        plt.show()
    print("Calculating Net profile completed!")
    return net_energy_use

def efficiencylosses(gridparams):
    # Part 1 DC-AC grid link (not existent for AC infrastructure) - converter 1
    vdc = gridparams["AC-DC CONVERTER 1"]["VDC"]
    vac = gridparams["AC-DC CONVERTER 1"]["VAC"]
    gridpower = 60e3
    directory = r'data\effcurves\dc\dc-ac\grid'

    # Get a list of available power levels
    power_levels = []
    for file in os.listdir(directory):
        if file.endswith(".npy"):
            power = int(file.split("_")[1].replace("kW", ""))
            power_levels.append(1000*power)
    # Round up the grid power to the nearest available power level
    nearest_power = min(power_levels, key=lambda x: abs(x - gridpower))


    for file in os.listdir(directory):
        # Check if the file is a numpy file
        if file.endswith(".npy"):
            # Extract the power value from the file name
            power = 1000*int(file.split("_")[1].replace("kW", ""))

            # Check if the power matches the target power
            if power == nearest_power:
                # Load the numpy file and do something with it
                file_path = os.path.join(directory, file)
                effcurve = np.load(file_path)
                print(f"Loaded file for converter 1:{file}")
                # Do something with the data here
                pp = round(100*gridpower/power)
                eff1 = effcurve[pp]
                print(f"Percentage load converter 1: {pp}%")
                print(f"DC Efficiency for converter 1: {round(100*eff1,2)}%")
                break  # Stop searching after finding the first match

    # Part 2 DC-AC / DC-DC EV charging - converter 2
    # Part 2.1 DC efficiency
    vdc = gridparams["AC-DC CONVERTER 1"]["VDC"]
    vac = gridparams["AC-DC CONVERTER 1"]["VAC"]
    evvdc = gridparams["DC-DC/AC-DC CONVERTER 2"]["EVVoltagedc"]
    evp = gridparams["DC-DC/AC-DC CONVERTER 2"]["EVPower"]
    directory = r'data\effcurves\dc\dc-dc\ev'

    power_levels = []
    for file in os.listdir(directory):
        if file.endswith(".npy"):
            power = float(file.split("_")[1].replace("kW", ""))
            power_levels.append(power*1000)
    # Round up the grid power to the nearest available power level
    nearest_power = min(power_levels, key=lambda x: abs(x - evp))
    for file in os.listdir(directory):
        # Check if the file is a numpy file
        if file.endswith(".npy"):
            # Extract the power value from the file name
            power = 1000*float(file.split("_")[1].replace("kW", ""))

            # Check if the power matches the target power
            if power == nearest_power:
                # Load the numpy file and do something with it
                file_path = os.path.join(directory, file)
                effcurve = np.load(file_path)
                print(f"Loaded file for DC converter 2:{file}")
                # Do something with the data here
                pp = round(100 * evp / power)
                V = np.arange(250, 370, 10) # FROM THE EFFICIENCY CURVES FILE
                Vdc = np.arange(160, 380, 20)
                # Find the index of the element in Vdc that is closest to voltage
                vv = np.argmin(np.abs(V - evvdc))
                print(f"Closest chosen EV voltage:{V[vv]} (actual:{evvdc}), element number: {vv}")
                jj = np.argmin(np.abs(Vdc - vdc))
                print(f"Closest chosen DC voltage:{Vdc[jj]} (actual:{vdc}), element number: {jj}")
                eff2dc = effcurve[pp, vv, jj]
                print(f"Percentage load DC converter 2: {pp}%")
                print(f"DC Efficiency for DC converter 2: {round(100 * eff2dc, 2)}%")
                break  # Stop searching after finding the first match

    # Part 2.1 AC efficiency
    directory = r'data\effcurves\ac\dc-ac\ev'

    power_levels = []
    for file in os.listdir(directory):
        if file.endswith(".npy"):
            power = float(file.split("_")[1].replace("kW", ""))
            power_levels.append(power * 1000)
    # Round up the grid power to the nearest available power level
    nearest_power = min(power_levels, key=lambda x: abs(x - evp))
    for file in os.listdir(directory):
        # Check if the file is a numpy file
        if file.endswith(".npy"):
            # Extract the power value from the file name
            power = 1000 * float(file.split("_")[1].replace("kW", ""))

            # Check if the power matches the target power
            if power == nearest_power:
                # Load the numpy file and do something with it
                file_path = os.path.join(directory, file)
                effcurve = np.load(file_path)
                print(f"Loaded file for AC converter 2:{file}")
                # Do something with the data here
                pp = round(100 * evp / power)
                eff2ac = effcurve[pp]
                print(f"Percentage load AC converter 2: {pp}%")
                print(f"AC Efficiency for converter 2: {round(100 * eff2ac, 2)}%")
                break  # Stop searching after finding the first match

    # Part 3 DC-AC / DC-DC PV generation - converter 3
    # Part 3.1 DC efficiency
    vdc = gridparams["AC-DC CONVERTER 1"]["VDC"]
    vac = gridparams["AC-DC CONVERTER 1"]["VAC"]
    pvvdc = gridparams["DC-DC/AC-DC CONVERTER 3"]["PVVoltagedc"]
    pvp = gridparams["DC-DC/AC-DC CONVERTER 3"]["PVPower"]
    directory = r'data\effcurves\dc\dc-dc\pv'

    power_levels = []
    for file in os.listdir(directory):
        if file.endswith(".npy"):
            power = float(file.split("_")[1].replace("kW", ""))
            power_levels.append(power * 1000)
    # Round up the grid power to the nearest available power level
    nearest_power = min(power_levels, key=lambda x: abs(x - evp))
    for file in os.listdir(directory):
        # Check if the file is a numpy file
        if file.endswith(".npy"):
            # Extract the power value from the file name
            power = 1000 * float(file.split("_")[1].replace("kW", ""))

            # Check if the power matches the target power
            if power == nearest_power:
                # Load the numpy file and do something with it
                file_path = os.path.join(directory, file)
                effcurve = np.load(file_path)
                print(f"Loaded file for DC converter 3:{file}")
                # Do something with the data here
                pp = round(100 * pvp / power)
                if pp == 100:  # nodig omdat 100% waarde niet bestaat in effcurve voor pv
                    pp = 99
                V=np.arange(230, 490, 10)  # FROM THE EFFICIENCY CURVES FILE
                # Find the index of the element in Vdc that is closest to voltage
                vv = np.argmin(np.abs(V - pvvdc))
                print(f"Closest chosen PV voltage:{V[vv]} (actual:{pvvdc}), element number: {vv}")
                eff3dc = effcurve[pp, vv]
                print(f"Percentage load DC converter 3: {pp}%")
                print(f"DC Efficiency for DC converter 3: {round(100 * eff3dc, 2)}%")
                break  # Stop searching after finding the first match
    """
    # data\effcurves\ac\dc-ac\pv doesn't exist
    # Part 3.1 AC efficiency
    directory = r'data\effcurves\ac\dc-ac\pv'
    """

    # Part 4 DC-AC / DC-DC EV charging - converter 4
    # Part 4.1 DC efficiency
    vdc = gridparams["AC-DC CONVERTER 1"]["VDC"]
    vac = gridparams["AC-DC CONVERTER 1"]["VAC"]
    bessvdc = gridparams["DC-DC/AC-DC CONVERTER 4"]["BESSVoltagedc"]
    bessp = gridparams["DC-DC/AC-DC CONVERTER 4"]["BESSPower"]
    directory = r'data\effcurves\dc\dc-dc\bess'

    power_levels = []
    for file in os.listdir(directory):
        if file.endswith(".npy"):
            power = float(file.split("_")[1].replace("kW", ""))
            power_levels.append(power * 1000)
    # Round up the grid power to the nearest available power level
    nearest_power = min(power_levels, key=lambda x: abs(x - evp))
    for file in os.listdir(directory):
        # Check if the file is a numpy file
        if file.endswith(".npy"):
            # Extract the power value from the file name
            power = 1000 * float(file.split("_")[1].replace("kW", ""))

            # Check if the power matches the target power
            if power == nearest_power:
                # Load the numpy file and do something with it
                file_path = os.path.join(directory, file)
                effcurve = np.load(file_path)
                print(f"Loaded file for DC converter 4:{file}")
                # Do something with the data here
                pp = round(100 * bessp / power)
                if pp == 100:
                    pp = 99
                V=np.arange(690, 960, 10)  # FROM THE EFFICIENCY CURVES FILE
                # Find the index of the element in Vdc that is closest to voltage
                vv = np.argmin(np.abs(V - bessvdc))
                print(f"Closest chosen BESS voltage:{V[vv]} (actual:{bessvdc}), element number: {vv}")
                eff4dc = effcurve[pp, vv]
                print(f"Percentage load DC converter 4: {pp}%")
                print(f"DC Efficiency for DC converter 4: {round(100 * eff4dc, 2)}%")
                break  # Stop searching after finding the first match

    """
    # data\effcurves\ac\dc-ac\bess doesn't exist
    # Part 4.1 AC efficiency
    directory = r'data\effcurves\ac\dc-ac\bess'
    """

# Distribution of arrival EVs CSV file names
wkd = 'distribution-of-arrival.csv'
wke = 'distribution-of-arrival (1).csv'

# amount of chargers
numb_chargers = 2

# =============================================================================
# Grid parameters
# =============================================================================
gridparameters = {
    "AC-DC CONVERTER 1": {
        "VDC": 700,
        "VAC": 400
    },
    "DC-DC/AC-DC CONVERTER 2": {
        "EVPower": 2e3,
        "EVVoltagedc": 360
    },
    "DC-DC/AC-DC CONVERTER 3": {
        "PVPower": 5e3,
        "PVVoltagedc": 480
    },
    "DC-DC/AC-DC CONVERTER 4": {
        "BESSPower": 25e3,
        "BESSVoltagedc": 950
    }
}

VisualizeProfiles = False  # visualization of 35040 data points can
# take a while (c.a. 30 sec on I7 8th gen -16GB RAM) and spin up your pc

# NetEnergy = calculateprofile(wkd, wke, numb_chargers, VisualizeProfiles)
# NetEnergy is an array with net energy use per quarter-hour for one whole year
# print(NetEnergy)

efficiencylosses(gridparameters)

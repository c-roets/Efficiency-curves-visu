"""
Main file
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


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
            print(E_charge_needs.shape)
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
    if visu:

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

    print("Calculating EV Energy needs completed!")

    # =============================================================================
    # PV Profile
    # =============================================================================
    print("Loading PV Generation profile...")
    pv = np.load("pv_kWh_kWp.npy")
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
    net_energy_use = E_charge_needs.flatten() - pv

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


# Distribution of arrival EVs CSV file names
wkd = 'distribution-of-arrival.csv'
wke = 'distribution-of-arrival (1).csv'

# amount of chargers
numb_chargers = 6

# =============================================================================
# Grid parameters
# =============================================================================
# AC-DC LINK parameters (AC-DC CONVERTER 1)
VDC = 700
VAC = 400

# EV Charging parameters (DC-DC/AC-DC CONVERTER 1)
EVPower = 10e3
EVVoltagedc = 360

# PV Generation parameters (DC-DC/AC-DC CONVERTER 2)
PVPower = 5e3
PVVoltagedc = 480

# BESS parameters (DC-DC/AC-DC CONVERTER 3)
BESSpower = 25e3
BESSvoltagedc = 950

VisualizeProfiles = True  # visualization of 35040 data points can
# take a while (c.a. 30 sec on I7 8th gen) and spin up your pc
NetEnergy = calculateprofile(wkd, wke, numb_chargers, VisualizeProfiles)
# NetEnergy array with net energy use per quarter-hour for one whole year
print(NetEnergy)
print(len(NetEnergy))

"""
Main file
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os


def calculateprofile(arrivalweekday, arrivalweekend, acprofile, acdatacolumn, pvprofile, no_chargers, gridparams,
                     visu=False):
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

    E_charge_needs = 0; E_charge_needs_total = 0
    """
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
    powerlimit = gridparams["DC-DC/AC-DC CONVERTER 2"][
                     "EVPower"] * 0.25  # max amount of Wh charging possible in 15 min accounting for charging power
    E_charge_needs = np.zeros([35040, no_chargers])
    E_charge_needs_day = np.zeros([365, no_chargers])
    day_index = 0
    buffer = 0
    if visu:
        start_date = pd.to_datetime('2022-01-01')
        datetimes = [start_date + pd.Timedelta(minutes=15 * i) for i in range(E_charge_needs.shape[0])]
        fig, ax = plt.subplots(figsize=(16, 6))
        colors = plt.cm.Set2(np.linspace(0, 1, no_chargers))

    for ch in range(0, no_chargers):
        print('charger number:' + str(ch))
        for qh in range(0, 35040):
            E_need = np.random.choice(np.linspace(1, E_charge_full, 99), size=1, p=energy_need)
            E_need += buffer
            buffer = 0
            if E_need > powerlimit:
                buffer = E_need - powerlimit
                E_need = powerlimit
            E_charge_needs[qh, ch] = E_need
            # compile every 96 quarter hours into a day
            if qh > 0 and (qh + 1) % 96 == 0:
                E_charge_needs_day[day_index, ch] = np.sum(E_charge_needs[(qh - 95):(qh + 1), ch])
                day_index += 1
        if visu:
            print("Loading graph...")
            # print(E_charge_needs.shape)
            print(E_charge_needs)

            ax.bar(datetimes[:96], E_charge_needs[:96, ch], width=pd.Timedelta(minutes=15), alpha=0.7,
                   label='Charger {}'.format(ch + 1), color=colors[ch])
        day_index = 0

    if visu:
        ax.set_xlabel('Day of year')
        ax.set_ylabel('Energy charge needs (Wh)')
        ax.set_title('Energy charge needs per quarter-hour')
        ax.legend(loc='upper left')
        print('Number of chargers plotted: {}'.format(no_chargers))
        plt.show()
        # =============================================================================
        # Visualize energy needs per day
        # =============================================================================
        fig, ax = plt.subplots(figsize=(20, 8))
        colors = plt.cm.Set2(np.linspace(0, 1, no_chargers))
        for ch in range(no_chargers):
            ax.bar(range(365), E_charge_needs_day[:, ch], color=colors[ch], label='Charger {}'.format(ch + 1))

        # Set the axis labels and title
        ax.set_xlabel('Day of year')
        ax.set_ylabel('Energy charge needs (Wh)')
        ax.set_title('Energy charge needs per day')
        ax.legend(loc='upper left')
        plt.show()

    print("Summing charger values...")
    # Total energy demand of all chargers summed
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
        ax.set_ylabel('Energy charge needs (Wh) (sum of chargers)')
        ax.set_title('Energy charge needs per quater-hour chargers summed')
        plt.show()

    print("Calculating EV Energy needs completed!")
    """
    # =============================================================================
    # PV Profile
    # =============================================================================
    print("Loading PV Generation profile...")
    pv = np.load(pvprofile)
    # print(pv.shape)
    # print(pv)
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
    # AC profile
    # =============================================================================
    '''Load demand profiles (slp S12)'''

    E_demand = 100e6
    df_lp = pd.read_csv(acprofile, index_col=0)
    lp_profile = df_lp[acdatacolumn] * 4 * E_demand;
    aclp = lp_profile.values
    if visu:
        print("Loading graph...")
        start_date = pd.to_datetime('2022-01-01')
        datetimes = [start_date + pd.Timedelta(minutes=15 * i) for i in range(lp_profile.size)]
        fig, ax = plt.subplots(figsize=(16, 6))
        ax.bar(datetimes, lp_profile.values, width=pd.Timedelta(minutes=15), alpha=0.7)
        # ax.bar(x=lp_profile.index, height=lp_profile.values)
        ax.set_xlabel('Quarter Hour')
        ax.set_ylabel('Energy Demand (Wh)')
        ax.set_title('Load Profile')
        plt.show()

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
    print()
    return E_charge_needs, pv, aclp


def efficiencylosses(gridparams, evprofile, evprofilev, pvprofile, acprofile, bessprofile):
    # Part 1 DC-AC grid link (not existent for AC infrastructure) - converter 1
    vdc = gridparams["AC-DC CONVERTER 1"]["VDC"]
    vac = gridparams["AC-DC CONVERTER 1"]["VAC"]
    gridpower = gridparams["AC-DC CONVERTER 1"]["Gridpower"]
    directory = r'data\effcurves\dc\dc-ac\grid'

    # Get a list of available power levels
    power_levels = []
    for file in os.listdir(directory):
        if file.endswith(".npy"):
            power = int(file.split("_")[1].replace("kW", ""))
            power_levels.append(1000 * power)
    # Round up the grid power to the nearest available power level
    nearest_power = min(power_levels, key=lambda x: abs(x - gridpower))

    for file in os.listdir(directory):
        # Check if the file is a numpy file
        if file.endswith(".npy"):
            # Extract the power value from the file name
            power = 1000 * int(file.split("_")[1].replace("kW", ""))

            # Check if the power matches the target power
            if power == nearest_power:
                # Load the numpy file and do something with it
                file_path = os.path.join(directory, file)
                effcurve = np.load(file_path)
                print()
                print(f"Loaded converter file for converter 1 (AC-DC) for AC profile:{file}")
                eff1 = np.zeros(len(acprofile))
                # Do something with the data here
                for i in range(acprofile.shape[0]):
                    pp = round(100 * (acprofile[i] / (
                                power * 0.25)))  # divide by 25 to convert kWh in quarter-hour to average kW for 15 min
                    # converter gets overloaded error
                    eff1[i] = effcurve[pp]  # array with converter efficiency in each quarter-hour
                eff1 = eff1.reshape((-1, 1))
                print("Efficiencies for DC-AC: AC-profile conversion:")
                print(eff1)
                acprofile = acprofile.reshape((-1, 1))
                print("Losses for DC-AC: AC-profile conversion:")
                eff1losses = acprofile - (acprofile * eff1)
                print(eff1losses)
                print("Total Energy losses for 1 year at DC-AC grid link on DC grid:", end=' ')
                print(format(np.sum(eff1losses),',.1f'))
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
                print()
                print(f"Loaded file for DC converter 2:{file}")
                # Do something with the data here
                V = np.arange(250, 370, 10)  # FROM THE EFFICIENCY CURVES FILE
                Vdc = np.arange(160, 380, 20)
                eff2dc = np.zeros((evprofile.shape[0], evprofile.shape[1]))
                for i in range(evprofile.shape[1]):  # iterate over chargers
                    for j in range(evprofile.shape[0]):  # iterate over energy values
                        pp = round(100 * (evprofile[j, i] / (power)))
                        if pp > 100:  # sometimes power is 7420W on 7400W charging
                            pp = 100
                        evvdc = evprofilev[j,i]
                        vv = np.argmin(np.abs(V - evvdc))   # Find the index of the element in Vdc that is closest to voltage
                        jj = np.argmin(np.abs(Vdc - vdc))
                        eff2dc[j, i] = effcurve[pp, vv, jj]

                print("Efficiencies for DC-DC: EV-profile conversion in DC:")
                print(eff2dc)
                print("Losses for DC-DC: EV-profile conversion in DC:")
                eff2dclosses = evprofile - (evprofile * eff2dc)
                print(eff2dclosses)
                print("Total Energy losses for 1 year at DC-DC EV charging on DC grid:", end=' ')
                print(format(np.sum(eff2dclosses),',.1f'))
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
                print()
                print(f"Loaded file for AC converter 2:{file}")
                # Do something with the data here
                eff2ac = np.zeros((evprofile.shape[0], evprofile.shape[1]))
                for i in range(evprofile.shape[1]):
                    for j in range(evprofile.shape[0]):
                        pp = round(100 * (evprofile[j, i] / (power)))
                        if pp > 99:
                            pp = 99
                        eff2ac[j, i] = effcurve[pp]
                print("Efficiencies for DC-AC: EV-profile conversion in AC:")
                print(eff2ac)
                print("Losses for DC-AC: EV-profile conversion in DC in AC:")
                eff2aclosses = evprofile - (evprofile * eff2ac)
                print(eff2aclosses)
                print("Total Energy losses for 1 year at AC-DC EV charging on AC grid:", end=' ')
                print(format(np.sum(eff2aclosses),',.1f'))
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
    nearest_power = min(power_levels, key=lambda x: abs(x - pvp))
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
                print()
                print(f"Loaded file for DC-DC converter PV on DC grid:{file}")
                # Do something with the data here
                V = np.arange(230, 490, 10)  # FROM THE EFFICIENCY CURVES FILE
                # Find the index of the element in Vdc that is closest to voltage
                vv = np.argmin(np.abs(V - pvvdc))
                eff3dc = np.zeros(len(pvprofile))
                for i in range(pvprofile.shape[0]):
                    pp = round(100 * (pvprofile[i] / (
                                power * 0.25)))  # divide by 25 to convert kWh in quarter-hour to average kW for 15 min
                    if pp == 100:  # nodig omdat 100% waarde niet bestaat in effcurve voor pv
                        pp = 99
                    eff3dc[i] = effcurve[pp, vv]  # array with converter efficiency in each quarter-hour
                eff3dc = eff3dc.reshape((-1, 1))
                print("Efficiencies for DC-DC: PV-profile conversion in DC:")
                # np.set_printoptions(threshold=np.inf)
                print(eff3dc)  # looks like it's all zero but that's just first and last values
                # no pv generation at midnight during year transition
                # np.set_printoptions()
                print("Losses for DC-DC: PV-profile conversion in DC:")
                pvprofile_re = pvprofile.reshape((-1, 1))
                eff3dclosses = pvprofile_re - (pvprofile_re * eff3dc)
                print(eff3dclosses)
                print("Total Energy losses for 1 year at DC-DC PV generation on DC grid:", end=' ')
                print(format(np.sum(eff3dclosses),',.1f'))
                break  # Stop searching after finding the first match

    # Part 3.2 DC efficiency on AC grid
    directory = r'data\effcurves\ac\dc-dc\pv'

    power_levels = []
    for file in os.listdir(directory):
        if file.endswith(".npy"):
            power = float(file.split("_")[1].replace("kW", ""))
            power_levels.append(power * 1000)
    # Round up the grid power to the nearest available power level
    nearest_power = min(power_levels, key=lambda x: abs(x - pvp))
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
                print()
                print(f"Loaded file for DC-DC converter PV on AC grid:{file}")
                # Do something with the data here
                V = np.arange(180, 325, 10)  # FROM THE EFFICIENCY CURVES FILE
                # Find the index of the element in Vdc that is closest to voltage
                vv = np.argmin(np.abs(V - pvvdc))
                # eff3dc = np.zeros(pvprofile.shape[0],pvprofile.shape[1])
                eff3dc_ac = np.zeros(len(pvprofile))
                for i in range(pvprofile.shape[0]):
                    pp = round(100 * (pvprofile[i] / (
                                power * 0.25)))  # divide by 25 to convert kWh in quarter-hour to average kW for 15 min
                    if pp == 100:  # nodig omdat 100% waarde niet bestaat in effcurve voor pv
                        pp = 99
                    eff3dc_ac[i] = effcurve[pp, vv]  # array with converter efficiency in each quarter-hour
                eff3dc_ac = eff3dc_ac.reshape((-1, 1))
                print("Efficiencies for DC-DC: PV-profile conversion in AC:")
                # np.set_printoptions(threshold=np.inf)
                print(eff3dc_ac)  # looks like it's all zero but that's just first and last values
                # no pv generation at midnight during year transition
                # np.set_printoptions()
                print("Losses for DC-DC: PV-profile conversion in DC in AC:")
                eff3dc_aclosses = pvprofile_re - (pvprofile_re * eff3dc_ac)
                print(eff3dc_aclosses)
                print("Total Energy losses for 1 year at DC-DC PV generation on AC grid:", end=' ')
                print(format(np.sum(eff3dc_aclosses),',.1f'))
                break  # Stop searching after finding the first match

    # Part 4 DC-DC / DC-DC BESS - converter 4
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
                print()
                print(f"Loaded file for DC converter 4:{file}")
                # Do something with the data here
                V = np.arange(690, 960, 10)
                vv = np.argmin(np.abs(V - bessvdc))
                print(f"Closest chosen BESS voltage:{V[vv]} (actual:{bessvdc}), element number: {vv}")
                eff4dc = np.zeros(len(bessprofile))
                for i in range(bessprofile.shape[0]):
                    pp = np.around(100 * (bessprofile[i] / (power * 0.25)), decimals=2)
                    pp = int(pp[0])
                    eff4dc[i] = effcurve[pp, vv]
                eff4dc = eff4dc.reshape((-1, 1))
                print("Efficiencies for DC-DC: BESS-profile conversion in DC:")
                print(eff4dc)
                print("Losses for DC-DC: BESS-profile conversion in DC:")
                eff4dclosses = bessprofile - (bessprofile * eff4dc)  # check if shape of bessprofile is correct first!
                print(eff4dclosses)
                print("Total Energy losses for 1 year at DC-DC BESS on DC grid:", end=' ')
                print(format(np.sum(eff4dclosses),',.1f'))
                break  # Stop searching after finding the first match

    # Part 4.1 DC efficiency on AC grid
    directory = r'data\effcurves\ac\dc-dc\bess'

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
                print()
                print(f"Loaded file for DC converter 4:{file}")
                # Do something with the data here
                V = np.arange(40, 75, 5)
                vv = np.argmin(np.abs(V - bessvdc))
                print(f"Closest chosen BESS voltage:{V[vv]} (actual:{bessvdc}), element number: {vv}")
                eff4dc_ac = np.zeros(len(bessprofile))
                for i in range(bessprofile.shape[0]):
                    pp = np.around(100 * (bessprofile[i] / (power * 0.25)), decimals=2)
                    pp = int(pp[0])
                    eff4dc_ac[i] = effcurve[pp, vv]
                eff4dc_ac = eff4dc_ac.reshape((-1, 1))
                print("Efficiencies for DC-DC: BESS-profile conversion in DC:")
                print(eff4dc_ac)
                print("Losses for DC-DC: BESS-profile conversion in DC:")
                eff4dc_aclosses = bessprofile - (
                            bessprofile * eff4dc_ac)  # check if shape of bessprofile is correct first!
                print(eff4dc_aclosses)
                print("Total Energy losses for 1 year at DC-DC BESS on AC grid:", end=' ')
                print(format(np.sum(eff4dc_aclosses),',.1f'))
                break  # Stop searching after finding the first match

    return 1
    # Part 5 Bidirectional DC-AC PV & BESS converter 5
    directory = r'data\effcurves\ac\dc-ac\pv_bess'

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
                print(f"Loaded file for DC-AC converter 5:{file}")
                # Do something with the data here

                """ ADD CODE FOR EFFICIENCY DC-AC BI HERE"""

    return 1


# file names
wkd = 'distribution-of-arrival.csv'
wke = 'distribution-of-arrival (1).csv'
acp = 'data/LoadProfiles/slp_industrie.csv'
acdata = 'S12 56-100KVA'  # kolom in acp met de actuele data van ac verbruik
pvp = "pv_kWh_kWp.npy"
# amount of chargers
numb_chargers = 4

# =============================================================================
# Grid parameters
# =============================================================================
gridparameters = {
    "AC-DC CONVERTER 1": {
        "VDC": 700,
        "VAC": 400,
        "Gridpower": 90e3
    },
    "DC-DC/AC-DC CONVERTER 2": {
        "EVPower": 7000,
        "EVVoltagedc": 360
    },
    "DC-DC/AC-DC CONVERTER 3": {
        "PVPower": 20e3,
        "PVVoltagedc": 320
    },
    "DC-DC/AC-DC CONVERTER 4": {
        "BESSPower": 25e3,
        "BESSVoltagedc": 950
    }
}

# functies aanroepen

VisualizeProfiles = False  # visualization of 35040 data points can
# take a while (c.a. 30 sec on I7 8th gen -16GB RAM) and spin up your pc

EVprofile, PVprofile, ACprofile = calculateprofile(wkd, wke, acp, acdata, pvp, numb_chargers, gridparameters, VisualizeProfiles)

BESSprofile = np.zeros((35040,1))

v_ev_arr = np.load(r'data\results_ev\voltage_ev.npy')  # three dim. [i,j,k] with k corresponding to (2.3, 3.7, 5.8, and 7.4 kW)
p_ev_arr = np.load(r'data\results_ev\power_ev.npy')
power_levels = np.array([2.3, 3.7, 5.8, 7.4])
closest_power_idx = np.argmin(np.abs(power_levels - gridparameters["DC-DC/AC-DC CONVERTER 2"]["EVPower"]))  # index of the closest power level
closest_power = power_levels[closest_power_idx]  # value of the closest power level
print(closest_power, end=' ')
print(f"kW charging chosen as input parameter with {numb_chargers} chargers")

EVprofile = np.abs(p_ev_arr[:, :numb_chargers, closest_power_idx])  # extract the third dimension of p_ev_arr corresponding to the closest power level
EVprofileV = v_ev_arr[:,:numb_chargers, closest_power_idx]

efficiencylosses(gridparameters, EVprofile, EVprofileV, PVprofile, ACprofile, BESSprofile)

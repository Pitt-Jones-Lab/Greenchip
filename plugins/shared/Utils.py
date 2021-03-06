import os
from plugins.loaders import *
from tkinter import *
from tkinter import ttk
import plugins.shared.Config as settingsConfig
from plugins.shared.GreenChip import *
from tkinter import messagebox
from tkinter import colorchooser
from tkinter import simpledialog
from tkinter import filedialog
import subprocess
import math
from mpl_toolkits.axes_grid1.inset_locator import InsetPosition
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import glob

def colorFader(c1,c2,mix=0): #fade (linear interpolate) from color c1 (at mix=0) to c2 (mix=1)
    c1=np.array(mpl.colors.to_rgb(c1))
    c2=np.array(mpl.colors.to_rgb(c2))
    return mpl.colors.to_hex((1-mix)*c1 + mix*c2)

if settingsConfig.nativePlotting:
    import matplotlib
    matplotlib.use("TkAgg")
    from matplotlib import pyplot as plt
    import numpy as np
    from matplotlib.colors import LinearSegmentedColormap
    from matplotlib.widgets import Button



class utils(object):
    @staticmethod
    def powerPatcherCore(filename, chipAreaDram, technode):
        filename = os.path.normpath(filename)
        exec(open(filename).read(), globals())
        if power['DRAM']['Area'] != 0:
            MsgBox = messagebox.askquestion ('DRAM Chip Area','DRAM Chip Area in ' + filename + ' is ' + str(power['DRAM']['Area']) + '. Do you wish to overwrite this data?' ,icon = 'warning')
            if MsgBox == 'yes':
                power['DRAM']['Area'] = chipAreaDram
        else:
            power['DRAM']['Area'] = chipAreaDram

        power['DRAM']['ProcessSize'] = technode

        filepower = open(filename, "r+")
        replace =  " 'DRAM': {'Area': " + str( power['DRAM']['Area']) + ',\n'
        replace2 = "          'Technology Node': '" + technode + "',\n"
        filelist = filepower.readlines()
        location = -1
        for i in range(len(filelist)):
            if 'DRAM' in filelist[i]:
                location = i
                filelist[i] = replace
                if 'Technology' not in filelist[i+1]:
                    filelist.insert(i+1, replace2)
                else:
                    MsgBox = messagebox.askquestion ('DRAM Technology Node','DRAM Technology Node in ' + filename + ' is ' + str(power['DRAM']['Technology Node']) + '. Do you wish to overwrite this data?' ,icon = 'warning')
                    if MsgBox == 'yes':
                        filelist[i+1] = replace2
                break

        if location == -1:
            messagebox.showerror ('DRAM Specification Error', 'DRAM Specification not found! Check and make sure your power.py is not empty')
            exit()

        filepower.truncate(0)
        filepower.seek(0)  
        filepower.writelines(filelist)
        filepower.close()
    
    @staticmethod
    def powerPatcher(dirname, chipAreaDram, technode):
        powerlist = glob.glob(dirname+'/**/power.py', recursive=True)
        for i in powerlist:
            utils.powerPatcherCore(i, chipAreaDram, technode)
        messagebox.showinfo('Patch Complete', 'Patch has been completed! You may close this window and run your analysis', icon='info')
    
    @staticmethod
    def powerPrompter():
        dirname = filedialog.askdirectory()
        if dirname == '':
            return
        chipAreaDram = simpledialog.askinteger('DRAM Chip Area', 'Please input the desired DRAM chip area for the selected files.')
        if chipAreaDram is None:
            return
        technode = simpledialog.askstring('DRAM Technology Node', 'Please input the desired DRAM technology node for the selected files. The supported tech nodes are ' + "55, 57, 90, 130, 180, and 250.")
        if technode is None:
            return
        while technode not in ['55', '57', '90', '130', '180', '250']:
            MsgBox = messagebox.askquestion ('DRAM Technology Node','This technology node is not supported. Do you wish to try again?' ,icon = 'error')
            if MsgBox == 'yes':
                technode = simpledialog.askstring('DRAM Technology Node', 'Please input the desired DRAM technology node for the selected files. The supported tech nodes are ' + "55, 57, 90, 130, 180, and 250.")
            else:
                return
        utils.powerPatcher(dirname, chipAreaDram, technode)
    @staticmethod
    def abbreviate(benchmark):
        my_renaming = {'canneal_x264_blackscholes_vips': 'CXBV', 'rtview_fluidanimate_freqmine_bodytrack': 'RFFB',
                       'blackscholes_vips_streamcluster_swaptions': 'BVSS', 'canneal_x264_freqmine_dedup': 'CXFD',
                       'bzip_gobmk_hmmer_libquantum': 'BGHL', 'GemsFDTD_lbm_milc_namd': 'GLMN',
                       'mcf_sjeng_cactusADM_calculix': 'MSCC', 'bzip2_zeusmp_cactusADM_bwaves': 'BZCB',
                       'lbm_perlbench_leslie3d_astar': 'LPLA', 'povray_h264ref_calculix_soplex': 'PHCS',
                       'bzip2_gcc_mcf_zeusmp_cactusADM_GemsFDTD_milc_soplex': 'HIGH8',
                       'lbm_perlbench_calculix_soplex_gobmk_namd_bzip2_gcc': 'MIX8',
                       'gobmk_hmmer_h264ref_gromacs_namd_povray_tonto_libquantum': 'LOW8'}
        if benchmark in my_renaming:
            return my_renaming[benchmark]
        return benchmark
    
    @staticmethod
    def is_adjacent_generation(x, y):
        care_generations = False
        if x == '135':
            if y == '90':
                care_generations = True
        elif x == '90':
            if y == '135' or y == '65':
                care_generations = True
        elif x == '65':
            if y == '90' or y == '45':
                care_generations = True
        elif x == '45':
            if y == '65' or y == '28':
                care_generations = True
        elif x == '28':
            if y == '45' or y == '22':
                care_generations = True
        elif x == '22' and y == '28':
            care_generations = True

        if x == '135nm':
            if y == '90nm':
                care_generations = True
        elif x == '90nm':
            if y == '135nm' or y == '65nm':
                care_generations = True
        elif x == '65nm':
            if y == '90nm' or y == '45nm':
                care_generations = True
        elif x == '45nm':
            if y == '65nm' or y == '28nm':
                care_generations = True
        elif x == '28nm':
            if y == '45nm' or y == '22nm':
                care_generations = True
        elif x == '22nm' and y == '28nm':
            care_generations = True

        return care_generations
        #return True

    @staticmethod
    def is_adjacent_cachesize(x, y):
        care_cachesize = False
        if x == '16':
            if y == '8':
                care_cachesize = True
        elif x == '8':
            if y == '16' or y == '4':
                care_cachesize = True
        elif x == '4':
            if y == '8' or y == '2':
                care_cachesize = True
        elif x == '2':
            if y == '4' or y == '1':
                care_cachesize = True
        elif x == '1':
            if y == '2' or y == 'half':
                care_cachesize = True
        elif x == 'half' and y == '1':
            care_cachesize = True

        return care_cachesize

    @staticmethod
    def snapshot_reasonable(entry1_out, entry2_out):
        entry1_in = entry1_out.replace(',', ':')
        entry2_in = entry2_out.replace(',', ':')
        items1 = entry1_in.split(':')
        items2 = entry2_in.split(':')

        reasonable = utils.is_adjacent_generation(items1[1], items2[1])
        return reasonable

    @staticmethod
    def snapshot_gather(entry1_out, entry2_out):
        entry1_in = entry1_out.replace(',', ':')
        entry2_in = entry2_out.replace(',', ':')

        items1 = entry1_in.split(':')
        items2 = entry2_in.split(':')

        if items1[2] == 'half':
            items1[2] = '0.5'

        filename = '_vs_'.join([items1[1], items2[1]])
        label = ':'.join([utils.abbreviate(items1[3]), items1[2] + "MB"])
        return filename, label

    @staticmethod
    def rename(entry, forTitle):
        entry2 = entry.replace(',', ':')
        items = entry2.split(':')

        items[1] += 'nm'
        if items[2] == 'half':
            items[2] = '0.5'
        items[2] += 'MB'
        items[3] = utils.abbreviate(items[3])

        if forTitle:
            entry2 = ",".join([items[1], items[3], items[2]])
        else:
            entry2 = ':'.join([items[1], items[3], items[2]])
        return entry2

    @staticmethod
    def build_config(database, entry, path_to_output_directory, writeMe = True, configNum = 1):
        global_cycle_time = 0.000000000375
        config = {}
        mcpat, mcpat_was_loaded = database.get_item(entry, 'power.py', mcpat_dict_loader)
        if mcpat is None:
            return None
        entries = entry.split(database.delim)
        tmpdict = database.DB[database.DB_name]
        for i in entries:
            tmpdict = tmpdict[i]
        if 'run_out.txt' in tmpdict.keys():    
            dramsim, dramsim_was_loaded = database.get_item(entry, 'run_out.txt', dramsim_dict_loader)
            config['staticMemory'] = dramsim['static_memory']
            config['dynamicMemory'] = dramsim['dynamic_memory']
        else:
           Msgbox = messagebox.askquestion('run_out.txt Missing', 'run_out.txt is missing from ' + entry + '. DRAM Static Power and Dynamic Power will be pulled from Sniper instead. Do you want to proceed?', icon = 'warning')
           if Msgbox == 'yes':
                config['staticMemory'] = mcpat['DRAM']['Subthreshold Leakage with power gating'] + mcpat['DRAM']['Gate Leakage']
                config['dynamicMemory'] = mcpat['DRAM']['Runtime Dynamic']
           else:
                return
        ipc, ipc_was_loaded = database.get_item(entry, 'sim.out', ipc_dict_loader)
        if ipc is None:
            return None

        config['chipArea'] = mcpat['Processor']['Area']
        config['dynamicPower'] = mcpat['Processor']['Runtime Dynamic']
        config['staticPower'] = mcpat['Processor']['Subthreshold Leakage with power gating'] + mcpat['Processor'][
            'Gate Leakage']
        config['MPKI'] = ipc['mpki']
        config['IPC'] = ipc['ipc']
        config['cycles'] = ipc['cycles']
        config['layers'] = 1
        mcpat_cfg, mcpat_config_was_loaded = database.get_item(entry, 'power.xml', mcpat_cfg_loader)
        config['processSize'] = int(mcpat_cfg[0][14].attrib['value'])
        config['chipAreaDram'] = mcpat['DRAM']['Area']
        
        if config['chipAreaDram'] == 0 and configNum == 1:
            messagebox.showerror('DRAM Chip Area Error', 'DRAM Chip Area in power.py for the Top System is 0. If you are ignoring DRAM, input 0 in the next window.')
            config['chipAreaDram'] = simpledialog.askinteger(title='DRAM Chip Area', prompt= 'Input the total area of all DRAM die in mm^2 (0 if ignoring DRAM)')
            if config['chipAreaDram'] is None:
                    return
                    
        if config['chipAreaDram'] == 0 and configNum == 2:
            messagebox.showerror('DRAM Chip Area Error', 'DRAM Chip Area in power.py for the Bottom System is 0. If you are ignoring DRAM, input 0 in the next window.')
            config['chipAreaDram'] = simpledialog.askinteger(title='DRAM Chip Area', prompt= 'Input the total area of all DRAM die in mm^2 (0 if ignoring DRAM)')
            if config['chipAreaDram'] is None:
                    return
                    
        if configNum == 1:
            config['processSizeDram'] = simpledialog.askstring(title='Tech Node', prompt= 'Input Tech Node for the DRAM of the Top System (55, 57, 90, 130 180, 250)')
            while config['processSizeDram'] not in ['55', '57', '90', '130', '180', '250']:
                if config['processSizeDram'] is None:
                    return
                messagebox.showerror('Tech Node Error', 'Invalid Tech Node! Please use the list given in the next prompt.')
                config['processSizeDram'] = simpledialog.askstring(title='Tech Node', prompt= 'Input Tech Node for the DRAM of the Top System (55, 57, 90, 130 180, 250)')
                
        if configNum == 2:
            config['processSizeDram'] = simpledialog.askstring(title='Tech Node', prompt= 'Input Tech Node for the DRAM of the Bottom System (55, 57, 90, 130 180, 250)')
            while config['processSizeDram'] not in ['55', '57', '90', '130', '180', '250']:
                if config['processSizeDram'] is None:
                    return
                messagebox.showerror('Tech Node Error', 'Invalid Tech Node! Please use the list given in the next prompt.')
                config['processSizeDram'] = simpledialog.askstring(title='Tech Node', prompt= 'Input Tech Node for the DRAM of the Bottom System (55, 57, 90, 130 180, 250)')
                    
        if configNum == 3:
            config['processSizeDram'] = mcpat['DRAM']['Technology Node']
        config['FREQ'] = float(mcpat_cfg[0][15].attrib['value'])/1000.0

        if mcpat_was_loaded:

            if writeMe:
                entry = utils.rename(entry, False)
                with open(path_to_output_directory + "Power.csv", "a") as power_file:
                    power_file.write(entry + "," + str(config['staticMemory']) + "," + str(config['staticPower']) + "," +
                                     str(config['dynamicMemory']) + "," + str(config['dynamicPower']) + "\n")

                with open(path_to_output_directory + "MPKI.csv", "a") as mpki_file:
                    mpki_file.write(entry + "," + str(ipc['mpki']) + "\n")

                with open(path_to_output_directory + "IPC.csv", "a") as ipc_file:
                    ipc_file.write(entry + "," + str(ipc['ipc']) + "\n")

                with open(path_to_output_directory + "Energy.csv", "a") as energy_file:
                    energy_file.write(
                        entry + "," + str(config['staticMemory'] * config['cycles'] * global_cycle_time) +
                        "," + str(config['staticPower'] * config['cycles'] * global_cycle_time) + "," +
                        str(config['dynamicMemory'] * config['cycles'] * global_cycle_time) + "," +
                        str(config['dynamicPower'] * config['cycles'] * global_cycle_time) + "\n")

        return config

    @staticmethod
    def make_plot(first_entry, second_entry, entry1, entry2, res, snapshot_label, path_to_output_directory):
        if settingsConfig.nativePlotting:
			
            fontSize = 13;
            axisLabelSize = 16;

            matplotlib.rc('xtick', labelsize=fontSize)
            matplotlib.rc('ytick', labelsize=fontSize)

            if first_entry is None or second_entry is None:
                return
                
            settingsFile = settingsConfig.advancedSettingsFile

            res_keys = sorted(res.keys())
            #cols = []
            #for x in range(0, 11):
            #    cols.append(round(x * .1, 1))
            data = []
            #rows = []
            for key in res_keys:
                innerres = res[key]
                inner_keys = sorted(innerres.keys())
                #rows.append(round(key * .1, 1))
                inner_data = []
                for inner_key in inner_keys:
                    inner_data.append(innerres[inner_key])
                data.append(np.asarray(inner_data))
            arr = np.asarray(data).T
            #column_labels = cols
            #row_labels = rows
            fig, ax = plt.subplots()

            cdict2 = OurConstants.get_cdict2()

            cdict1 = OurConstants.get_cdict1()

            customgray = LinearSegmentedColormap('customgray', cdict1)
            customspectrum = LinearSegmentedColormap('customspectrum', cdict2)
            c = (0, 0, 0, 0)
            my_cmap = plt.get_cmap(customspectrum)
            my_cmap.set_under(color='white')
            second_cmap = plt.get_cmap(customgray)
            second_cmap.set_under(color=c)

            heatmap = ax.pcolormesh(arr, cmap=my_cmap, vmax=3650, vmin=0)
            heatbar = heatmap
            heatmap = ax.pcolormesh(arr, cmap=second_cmap, vmax=36000, vmin=4000)
            heatbar2 = heatmap

            # [x][y]
            e = np.e

            if settingsFile is not None:
                with open(settingsFile, "r") as settingsObject:
                    for line in settingsObject:
                        linevars = line.split(" ");
                        if (linevars[0].upper()=="M"):
                            if len(linevars)==5:
                                Sleep = int(linevars[1])
                                if (Sleep<0 or Sleep>100):
                                    messagebox.showerror("Error", "Sleep Ratio out of bounds!")
                                    break
                                Activity = int(linevars[2])
                                if (Activity<0 or Activity>100):
                                    messagebox.showerror("Error", "Activity Ratio out of bounds!")
                                    break
                                Label = linevars[3]
                                Color = linevars[4].lower().strip();
                                plt.plot([Sleep], [Activity], 'k.', markersize=35.0, markeredgecolor='black', mew=3, markerfacecolor="None")
                                plt.plot([Sleep], [Activity], 'k.', markersize=30.0, markeredgecolor='white', mew=3, markerfacecolor="None")
                                if (Sleep>50):
                                    if (Activity<50):                    
                                        ax.text(Sleep - 4/math.sqrt(2) - 0.5,Activity + 4/math.sqrt(2) + 0.5, Label, color = Color, verticalalignment = 'top', horizontalalignment = 'right')
                                    else:
                                        ax.text(Sleep - 4/math.sqrt(2) - 0.5,Activity - 4/math.sqrt(2) - 0.5, Label, color = Color, verticalalignment = 'bottom', horizontalalignment = 'right')
                                else:
                                    if (Activity<50):                    
                                        ax.text(Sleep + 4/math.sqrt(2) + 0.5,Activity + 4/math.sqrt(2) + 0.5, Label, color = Color, verticalalignment = 'top', horizontalalignment = 'left')
                                    else:
                                        ax.text(Sleep + 4/math.sqrt(2) + 0.5,Activity - 4/math.sqrt(2) - 0.5, Label, color = Color, verticalalignment = 'bottom', horizontalalignment = 'left')
                            else:
                                Sleep = int(linevars[1])
                                if (Sleep<0 or Sleep>100):
                                    messagebox.showerror("Error", "Sleep Ratio out of bounds!")
                                    break
                                Activity = int(linevars[2])
                                if (Activity<0 or Activity>100):
                                    messagebox.showerror("Error", "Activity Ratio out of bounds!")
                                    break
                                Label = linevars[3].strip()
                                plt.plot([Sleep], [Activity], 'k.', markersize=35.0, markeredgecolor='black', mew=3, markerfacecolor="None")
                                plt.plot([Sleep], [Activity], 'k.', markersize=30.0, markeredgecolor='white', mew=3, markerfacecolor="None")
                                if (Sleep>50):
                                    if (Activity<50):                    
                                        ax.text(Sleep - 4/math.sqrt(2) - 0.5,Activity + 4/math.sqrt(2) + 0.5, Label, verticalalignment = 'top', horizontalalignment = 'right', bbox=dict(boxstyle='round,pad=0.01', fc='white', alpha=0.7))
                                    else:
                                        ax.text(Sleep - 4/math.sqrt(2) - 0.5,Activity - 4/math.sqrt(2) - 0.5, Label, verticalalignment = 'bottom', horizontalalignment = 'right', bbox=dict(boxstyle='round,pad=0.01', fc='white', alpha=0.7))
                                else:
                                    if (Activity<50):                    
                                        ax.text(Sleep + 4/math.sqrt(2) + 0.5,Activity + 4/math.sqrt(2) + 0.5, Label, verticalalignment = 'top', horizontalalignment = 'left', bbox=dict(boxstyle='round,pad=0.01', fc='white', alpha=0.7))
                                    else:
                                        ax.text(Sleep + 4/math.sqrt(2) + 0.5,Activity - 4/math.sqrt(2) - 0.5, Label, verticalalignment = 'bottom', horizontalalignment = 'left', bbox=dict(boxstyle='round,pad=0.01', fc='white', alpha=0.7))
                        elif (linevars[0].upper()=="WM"):
                            if len(linevars)==6:
                                Sleep = int(linevars[1])
                                if (Sleep<0 or Sleep>100):
                                    messagebox.showerror("Error", "Sleep Ratio out of bounds!")
                                    break
                                Activity = int(linevars[2])
                                if (Activity<0 or Activity>100):
                                    messagebox.showerror("Error", "Activity Ratio out of bounds!")
                                    break
                                Radius = int(linevars[3])
                                Label = linevars[4]
                                Color = linevars[5].lower().strip();
                                plt.plot([Sleep], [Activity], 'k.', markersize=Radius*8.5 + 5, markeredgecolor='black', mew=3, markerfacecolor="None")
                                plt.plot([Sleep], [Activity], 'k.', markersize=Radius*8.5, markeredgecolor='white', mew=3, markerfacecolor="None")
                                if (Sleep>50):
                                    if (Activity<50):                    
                                        ax.text(Sleep - (Radius*8.5)/(9*math.sqrt(2)) - 1, Activity + (Radius*8.5)/(9*math.sqrt(2)) + 1, Label, color = Color, verticalalignment = 'top', horizontalalignment = 'right')
                                    else:
                                        ax.text(Sleep - (Radius*8.5)/(9*math.sqrt(2)) - 1, Activity - (Radius*8.5)/(9*math.sqrt(2)) - 1, Label, color = Color, verticalalignment = 'bottom', horizontalalignment = 'right')
                                else:
                                    if (Activity<50):                    
                                        ax.text(Sleep + (Radius*8.5)/(9*math.sqrt(2)) + 1, Activity + (Radius*8.5)/(9*math.sqrt(2)) + 1, Label, color = Color, verticalalignment = 'top', horizontalalignment = 'left')
                                    else:
                                        ax.text(Sleep + (Radius*8.5)/(9*math.sqrt(2)) + 1, Activity - (Radius*8.5)/(9*math.sqrt(2)) - 1, Label, color = Color, verticalalignment = 'bottom', horizontalalignment = 'left')
                            else:
                                Sleep = int(linevars[1])
                                if (Sleep<0 or Sleep>100):
                                    messagebox.showerror("Error", "Sleep Ratio out of bounds!")
                                    break
                                Activity = int(linevars[2])
                                if (Activity<0 or Activity>100):
                                    messagebox.showerror("Error", "Activity Ratio out of bounds!")
                                    break
                                Radius = int(linevars[3])
                                Label = linevars[4].strip()
                                plt.plot([Sleep], [Activity], 'k.', markersize=Radius*8.5 + 5, markeredgecolor='black', mew=3, markerfacecolor="None")
                                plt.plot([Sleep], [Activity], 'k.', markersize=Radius*8.5, markeredgecolor='white', mew=3, markerfacecolor="None")
                                if (Sleep>50):
                                    if (Activity<50):                    
                                        ax.text(Sleep - (Radius*8.5)/(9*math.sqrt(2)) - 1, Activity + (Radius*8.5)/(9*math.sqrt(2)) + 1, Label, color = Color, verticalalignment = 'top', horizontalalignment = 'right')
                                    else:
                                        ax.text(Sleep - (Radius*8.5)/(9*math.sqrt(2)) - 1, Activity - (Radius*8.5)/(9*math.sqrt(2)) - 1, Label, color = Color, verticalalignment = 'bottom', horizontalalignment = 'right')
                                else:
                                    if (Activity<50):                    
                                        ax.text(Sleep + (Radius*8.5)/(9*math.sqrt(2)) + 1, Activity + (Radius*8.5)/(9*math.sqrt(2)) + 1, Label, color = Color, verticalalignment = 'top', horizontalalignment = 'left')
                                    else:
                                        ax.text(Sleep + (Radius*8.5)/(9*math.sqrt(2)) + 1, Activity - (Radius*8.5)/(9*math.sqrt(2)) - 1, Label, color = Color, verticalalignment = 'bottom', horizontalalignment = 'left')
                        elif (linevars[0][0]=="#"):
                            continue;
                        elif (len(linevars[0].strip())==0):
                            continue;
                        else:
                            messagebox.showerror("Error", "Marker specifier incorrect!")

            # Make sure this comparison makes sense (i.e., different process nodes)
            # Get Names
            if snapshot_label is not None and utils.snapshot_reasonable(entry1, entry2):
                filename, label = utils.snapshot_gather(entry1, entry2)
                if not os.path.exists(path_to_output_directory + "Snapshots"):
                    os.makedirs(path_to_output_directory + "Snapshots")

                with open(path_to_output_directory + "Snapshots/"+snapshot_label+"_Desktop_" + filename + ".csv", "a") as desktop_file:
                    desktop_value = arr[17][77]
                    desktop_file.write(label + "," + str(desktop_value) + "\n")
                with open(path_to_output_directory + "Snapshots/"+snapshot_label+"_Server_" + filename + ".csv", "a") as server_file:
                    server_value = arr[30][5]
                    server_file.write(label + "," + str(server_value) + "\n")
                with open(path_to_output_directory + "Snapshots/"+snapshot_label+"_HPC_" + filename + ".csv", "a") as hpc_file:
                    hpc_value = arr[95][5]
                    hpc_file.write(label + "," + str(hpc_value) + "\n")
                with open(path_to_output_directory + "Snapshots/"+snapshot_label+"_Mobile_" + filename + ".csv", "a") as mobile_file:
                    mobile_value = arr[90][92]
                    mobile_file.write(label + "," + str(mobile_value) + "\n") 

            # want a more natural, table-like display
            ax.invert_yaxis()
            ax.xaxis.tick_top()
            ax.axis('tight')

            first_ipc = "{0:.2f}".format(first_entry['IPC'])
            second_ipc = "{0:.2f}".format(second_entry['IPC'])

            first_mpki = "{0:.2f}".format(first_entry['MPKI'])
            second_mpki = "{0:.2f}".format(second_entry['MPKI'])

            fig.text(0.95, 0.01, 'IPC: ' + first_ipc + ',' + second_ipc,
                     verticalalignment='bottom', horizontalalignment='left',
                     color='brown', fontsize=15)

            fig.text(0.95, 0.01, 'MPKI: ' + first_mpki + ',' + second_mpki,
                     verticalalignment='top', horizontalalignment='right',
                     color='brown', fontsize=15)

            # ax.set_xticklabels(column_labels, minor=False)
            # ax.set_yticklabels(row_labels, minor=False)
            # plt.colorbar(heatbar2)
            cbar = plt.colorbar(heatbar2, pad=0.05, ticks=[4015, 8030, 12045, 16060, 20075, 24090, 28105, 32120, 36000])
            cbar.ax.set_yticklabels(['11', '22', '33', '44', '55', '66', '77', '88', '99'])
            cbar.ax.tick_params(labelsize=fontSize)
            cbar.set_label('Years', rotation=360, size=axisLabelSize, labelpad=-30, y=1.08)
            # plt.colorbar(heatbar)
            cbar2 = plt.colorbar(heatbar, pad = 0.1)
            cbar2.ax.tick_params(labelsize=fontSize)
            # cbar.ax.set_yticklabels(labelsize=10)
            cbar2.set_label('Days', rotation=360, size=axisLabelSize, labelpad=-37.5, y=1.08)
            plt.xlabel('xlabel', fontsize=axisLabelSize)
            plt.ylabel('ylabel', fontsize=axisLabelSize)
            ax.set_xlabel('Percent Sleep')
            ax.xaxis.set_label_position('top')
            ax.xaxis.labelpad = 16;
            plt.ylabel('Activity Ratio')
            # plt.title(''.join([utils.rename(self.entry1, False), ' vs. ', utils.rename(self.entry2, False)]), y=1.08)

            image_file_name = path_to_output_directory + utils.rename(entry1, True) + "_vs_" + utils.rename(
                entry2, True) + ".pdf"

            plt.savefig(image_file_name, bbox_inches='tight')

            plt.clf()
            plt.close()

        else:
            messagebox.showinfo("Library Missing!", "Missing matplotlib, cannot plot in python!")

    @staticmethod
    def perform_greenchip_analysis(res):
        if settingsConfig.nativePlotting:
            res_keys = sorted(res.keys())

            data = []

            for key in res_keys:
                innerres = res[key]
                inner_keys = sorted(innerres.keys())
                inner_data = []
                for inner_key in inner_keys:
                    inner_data.append(innerres[inner_key])
                data.append(np.asarray(inner_data))
            arr = np.asarray(data).T
            return arr
        else: #Much less efficient to not use numpy, so only do it if it is not installed
            res_keys = sorted(res.keys())

            Matrix = []
            for x in range(0, len(res[1].keys())):
                Matrix.append([])
                for y in range(0, len(res_keys)):
                    Matrix[x].append(0)

            for key in res_keys:
                innerres = res[key]
                inner_keys = sorted(innerres.keys())
                for inner_key in inner_keys:
                    Matrix[inner_key][key] = innerres[inner_key]

            return Matrix

    @staticmethod
    def export_single_data(first_entry, second_entry, res, exportFile):
        if first_entry is None or second_entry is None:
            return
        arr = utils.perform_greenchip_analysis(res)

        with open(exportFile, "a") as out_file:
            for a in arr:
                for b in a[0]:
                    out_file.write(str(a)+","+str(b)+","+","+str(arr[a][b])+"\n")

    def average_gradient(Radius, Sleep, Activity, Orig, Mod):
        numofpoints = 0
        totaldifference = 0
        for x in range(Sleep - Radius, Sleep + Radius + 1):
            for y in range(Activity - Radius, Activity + Radius + 1):
                if ((x + y)<=Radius + Activity + Sleep and (x + y)>=Radius + Activity + Sleep ):
                    numofpoints = numofpoints + 1
                    totaldifference = totaldifference + Orig[x][y] - Mod[x][y]
        averagedifference = totaldifference/numofpoints           
        return averagedifference


    
    def partial_average(Radius, Sleep, Activity, Orig):
        numofpoints = 0
        total = 0
        for x in range(Sleep - Radius, Sleep + Radius + 1):
            for y in range(Activity - Radius, Activity + Radius + 1):
                if ((x + y)<=Radius + Activity + Sleep and (x + y)>=Radius + Activity + Sleep ):
                    numofpoints = numofpoints + 1
                    total = total + Orig[x][y]
        average = total/numofpoints           
        return average      

    def average_analysis(self, config1, config2, Sleep, Activity, Radius):
        config_dicts = []
        config_dicts.append(config1)
        config_dicts.append(config2) 
        if ((Radius > Sleep) or (Radius > Activity) or (Radius + Activity >= 100) or (Radius + Sleep >= 100)):
            messagebox.showinfo("Error", "Radius results in out of bounds points.")
            return
        difference = [0,0,0,0,0]
        original = chip_breakeven_IPC(config_dicts, False)['upgradeDays']
        old = config2['chipArea']
        config2['chipArea'] = config2['chipArea'] - (.01 * config2['chipArea'])
        mod = chip_breakeven_IPC(config_dicts, False)['upgradeDays']
        difference[0] = self.average_gradient(Radius, Sleep, Activity, original, mod)
        config2['chipArea'] = old

        old = config2['dynamicPower']
        config2['dynamicPower'] = config2['dynamicPower'] - (.01 * config2['dynamicPower'])
        mod = chip_breakeven_IPC(config_dicts, False)['upgradeDays']
        difference[1] = self.average_gradient(Radius, Sleep, Activity, original, mod)
        config2['dynamicPower'] = old

        old = config2['staticPower']
        config2['staticPower'] = config2['staticPower'] - (.01 * config2['staticPower'])
        mod = chip_breakeven_IPC(config_dicts, False)['upgradeDays']
        difference[2] = self.average_gradient(Radius, Sleep, Activity, original, mod)
        config2['staticPower'] = old

        old = config2['dynamicMemory']
        config2['dynamicMemory'] = config2['dynamicMemory'] - (.01 * config2['dynamicMemory'])
        mod = chip_breakeven_IPC(config_dicts, False)['upgradeDays']
        difference[3] = self.average_gradient(Radius, Sleep, Activity, original, mod)
        config2['dynamicMemory'] = old
        
        old = config2['staticMemory']
        config2['staticMemory'] = config2['staticMemory'] - (.01 * config2['staticMemory'])
        mod = chip_breakeven_IPC(config_dicts, False)['upgradeDays']
        difference[4] = self.average_gradient(Radius, Sleep, Activity, original, mod)
        config2['staticMemory'] = old
        
        total = difference[0] + difference[1] + difference[2] + difference[3] + difference[4]
        difference[0] = 100 * difference[0]/total
        difference[1] = 100 * difference[1]/total
        difference[2] = 100 * difference[2]/total
        difference[3] = 100 * difference[3]/total
        difference[4] = 100 * difference[4]/total

        messagebox.showinfo("Importance", "Current Average Number of Days to Breakeven: " + str(round(self.partial_average(Radius, Sleep, Activity, original),2))
            + "\nChip Area: " + str(round(difference[0],2)) + "%\nDynamic Power(Processor + Cache): "
            + str(round(difference[1],2)) + "%\nStatic Power(Processor + Cache): " + str(round(difference[2],2)) + "%\nDynamic Power(Memory): "
            + str(round(difference[3],2)) + "%\nStatic Power(Memory): " + str(round(difference[4],2)) + "%")
    

    def single_point_analysis(config1, config2, Sleep, Activity):
        config_dicts = []
        config_dicts.append(config1)
        config_dicts.append(config2) 
        if (Sleep < 0 or Activity < 0 or Sleep>=100 or Activity>=100): # Checks to see if the point is in bounds
            messagebox.showinfo("Error", "The values inputted are out of bounds")
            return
        difference = [0,0,0,0,0]
        orig = chip_breakeven_IPC(config_dicts, False)['upgradeDays'][Sleep][Activity]
        old = config2['chipArea']
        config2['chipArea'] = config2['chipArea'] - (.01 * config2['chipArea'])
        difference[0] = orig - chip_breakeven_IPC(config_dicts, False)['upgradeDays'][Sleep][Activity] # Measures gradient by using a 1% shift
        config2['chipArea'] = old

        old = config2['dynamicPower']
        config2['dynamicPower'] = config2['dynamicPower'] - (.01 * config2['dynamicPower'])
        difference[1] = orig - chip_breakeven_IPC(config_dicts, False)['upgradeDays'][Sleep][Activity] # Measures gradient by using a 1% shift
        config2['dynamicPower'] = old

        old = config2['staticPower']
        config2['staticPower'] = config2['staticPower'] - (.01 * config2['staticPower'])
        difference[2] = orig - chip_breakeven_IPC(config_dicts, False)['upgradeDays'][Sleep][Activity] # Measures gradient by using a 1% shift
        config2['staticPower'] = old

        old = config2['dynamicMemory']
        config2['dynamicMemory'] = config2['dynamicMemory'] - (.01 * config2['dynamicMemory'])
        difference[3] = orig - chip_breakeven_IPC(config_dicts, False)['upgradeDays'][Sleep][Activity] # Measures gradient by using a 1% shift
        config2['dynamicMemory'] = old
        
        old = config2['staticMemory']
        config2['staticMemory'] = config2['staticMemory'] - (.01 * config2['staticMemory'])
        difference[4] = orig - chip_breakeven_IPC(config_dicts, False)['upgradeDays'][Sleep][Activity] # Measures gradient by using a 1% shift
        config2['staticMemory'] = old
        
        total = difference[0] + difference[1] + difference[2] + difference[3] + difference[4]   # Scales gradients to percentages
        difference[0] = 100 * difference[0]/total
        difference[1] = 100 * difference[1]/total
        difference[2] = 100 * difference[2]/total
        difference[3] = 100 * difference[3]/total
        difference[4] = 100 * difference[4]/total

        messagebox.showinfo("Importance", "Current Number of Days to Breakeven: " + str(round(orig,2)) + "\nChip Area: " + str(round(difference[0],2)) + "%\nDynamic Power(Processor + Cache): "
            + str(round(difference[1],2)) + "%\nStatic Power(Processor + Cache): " + str(round(difference[2],2)) + "%\nDynamic Power(Memory): "
            + str(round(difference[3],2)) + "%\nStatic Power(Memory): " + str(round(difference[4],2)) + "%") # Displays a message box showing the percentages    

    @staticmethod
    def make_single_plot(self, first_entry, second_entry, title1, title2, res, plot_title):
        if settingsConfig.nativePlotting:

            initialFontSize = 13
            initialAxisLabelSize = 16
            initialTitleLabelSize = 20

            matplotlib.rc('xtick', labelsize=initialFontSize)
            matplotlib.rc('ytick', labelsize=initialFontSize)

            if first_entry is None or second_entry is None:
                return

            settingsFile = settingsConfig.advancedSettingsFile
            arr = utils.perform_greenchip_analysis(res)

            fig, ax = plt.subplots(figsize=(8,6.25))

            cdict2 = OurConstants.get_cdict2()

            cdict1 = OurConstants.get_cdict1()           

            numMarkers = 20

            markers = [None]*numMarkers*2
            markerSizes = [None]*numMarkers*2
            
            annotations = [None]*numMarkers
            xPosition = [None]*numMarkers
            yPosition = [None]*numMarkers

            marker_number = 0
            annotation_number = 0

            customgray = LinearSegmentedColormap('customgray', cdict1)
            customspectrum = LinearSegmentedColormap('customspectrum', cdict2)
            c = (0, 0, 0, 0)
            my_cmap = plt.get_cmap(customspectrum)
            my_cmap.set_under(color='white')
            second_cmap = plt.get_cmap(customgray)
            second_cmap.set_under(color=c)

            heatmap = ax.pcolormesh(arr, cmap=my_cmap, vmax=3650, vmin=0)
            heatbar = heatmap
            heatmap = ax.pcolormesh(arr, cmap=second_cmap, vmax=36000, vmin=4000)
            heatbar2 = heatmap

            def format_coord(x, y):
                col = int(x+0.5)
                row = int(y+0.5)
                if col>=0 and col<100 and row>=0 and row<100:
                    z = arr[row,col]
                    if (z<3500):
                        return 'Sleep=%1.4f%%, Activity=%1.4f%%, Days=%1.4f'%(x, y, z)
                    else:
                        return 'Sleep=%1.4f%%, Activity=%1.4f%%, Years=%1.4f'%(x, y, z/365)  
                else:
                    return 'Sleep=%1.4f, y=%1.4f'%(x, y)
            
            ax.format_coord = format_coord

           # def Clicked(event, int sleep, int activity):
            #    print(sleep)

            if settingsFile is None:
                marker_number = 0
                # Desktop
                #markers[0] = plt.plot([77], [17], 'k.', markersize=35.0, markeredgecolor='black', mew=3, markerfacecolor="None")
                #markers[1] = plt.plot([77], [17], 'k.', markersize=30.0, markeredgecolor='white', mew=3, markerfacecolor="None")
                #markerSizes[0] = 35.0
                #markerSizes[1] = 30.0
                #annotations[0] = plt.annotate('Desktop',[77+5,17+5], bbox=dict(boxstyle='round,pad=0.01', fc='white', alpha=0.7))
                #xPosition[0] = 77
                #yPosition[0] = 17

                # Server
                #markers[2] = plt.plot([5], [30], 'k.', markersize=35.0, markeredgecolor='black', mew=3, markerfacecolor="None")
                #markers[3] = plt.plot([5], [30], 'k.', markersize=30.0, markeredgecolor='white', mew=3, markerfacecolor="None")
                #markerSizes[2] = 35.0
                #markerSizes[3] = 30.0
                #annotations[1] = plt.annotate('Server',[5+5,30+5], bbox=dict(boxstyle='round,pad=0.01', fc='white', alpha=0.7))
                #xPosition[1] = 5
                #yPosition[1] = 30
				
                # HPC
                #markers[4] = plt.plot([5], [95], 'k.', markersize=35.0, markeredgecolor='black', mew=3, markerfacecolor="None")
                #markers[5] = plt.plot([5], [95], 'k.', markersize=30.0, markeredgecolor='white', mew=3, markerfacecolor="None")
                #markerSizes[4] = 35.0
                #markerSizes[5] = 30.0
                #annotations[2] = plt.annotate('HPC',[5+5,95+5], bbox=dict(boxstyle='round,pad=0.01', fc='white', alpha=0.7))
                #xPosition[2] = 5
                #yPosition[2] = 95
				
                # Cell Phone
                #markers[6] = plt.plot([92], [90], 'k.', markersize=35.0, markeredgecolor='black', mew=3, markerfacecolor="None")
                #markers[7] = plt.plot([92], [90], 'k.', markersize=30.0, markeredgecolor='white', mew=3, markerfacecolor="None")
                #markerSizes[6] = 35.0
                #markerSizes[7] = 30.0
                #annotations[3] = plt.annotate('Cellular',[92+5,90+5], bbox=dict(boxstyle='round,pad=0.01', fc='white', alpha=0.7))
                #xPosition[3] = 92
                #yPosition[3] = 90
				
                #marker_number = 8
                #annotation_number = 4
                
            else:

                with open(settingsFile, "r") as settingsObject:
                    for line in settingsObject:
                        linevars = line.split(" ");
                        if (linevars[0].upper()=="M"):
                            if len(linevars)==5:
                                Sleep = int(linevars[1])
                                if (Sleep<0 or Sleep>100):
                                    messagebox.showerror("Error", "Sleep Ratio out of bounds!")
                                    break
                                Activity = int(linevars[2])
                                if (Activity<0 or Activity>100):
                                    messagebox.showerror("Error", "Activity Ratio out of bounds!")
                                    break
                                Label = linevars[3]
                                Color = linevars[4].lower().strip();
                                markers[marker_number] = plt.plot([Sleep], [Activity], 'k.', markersize=35.0, markeredgecolor='black', mew=3, markerfacecolor="None")
                                markers[marker_number + 1] = plt.plot([Sleep], [Activity], 'k.', markersize=30.0, markeredgecolor='white', mew=3, markerfacecolor="None")
                                markerSizes[marker_number] = 35.0;
                                markerSizes[marker_number + 1] = 30.0;
                                marker_number = marker_number + 2;
                                xPosition[annotation_number] = Sleep;
                                yPosition[annotation_number] = Activity;
                                if (Sleep>50):
                                    if (Activity<50):                    
                                        annotations[annotation_number] = ax.text(xPosition[annotation_number] - 4/math.sqrt(2) - 0.5,yPosition[annotation_number] + 4/math.sqrt(2) + 0.5, Label, color = Color, verticalalignment = 'top', horizontalalignment = 'right')
                                    else:
                                        annotations[annotation_number] = ax.text(xPosition[annotation_number] - 4/math.sqrt(2) - 0.5,yPosition[annotation_number] - 4/math.sqrt(2) - 0.5, Label, color = Color, verticalalignment = 'bottom', horizontalalignment = 'right')
                                else:
                                    if (Activity<50):                    
                                        annotations[annotation_number] = ax.text(xPosition[annotation_number] + 4/math.sqrt(2) + 0.5,yPosition[annotation_number] + 4/math.sqrt(2) + 0.5, Label, color = Color, verticalalignment = 'top', horizontalalignment = 'left')
                                    else:
                                        annotations[annotation_number] = ax.text(xPosition[annotation_number] + 4/math.sqrt(2) + 0.5,yPosition[annotation_number] - 4/math.sqrt(2) - 0.5, Label, color = Color, verticalalignment = 'bottom', horizontalalignment = 'left')
                                annotation_number = annotation_number+1
                            else:
                                Sleep = int(linevars[1])
                                if (Sleep<0 or Sleep>100):
                                    messagebox.showerror("Error", "Sleep Ratio out of bounds!")
                                    break
                                Activity = int(linevars[2])
                                if (Activity<0 or Activity>100):
                                    messagebox.showerror("Error", "Activity Ratio out of bounds!")
                                    break
                                Label = linevars[3].strip()
                                markers[marker_number] = plt.plot([Sleep], [Activity], 'k.', markersize=35.0, markeredgecolor='black', mew=3, markerfacecolor="None")
                                markers[marker_number + 1] = plt.plot([Sleep], [Activity], 'k.', markersize=30.0, markeredgecolor='white', mew=3, markerfacecolor="None")
                                markerSizes[marker_number] = 35.0
                                markerSizes[marker_number + 1] = 30.0
                                marker_number = marker_number + 2
                                xPosition[annotation_number] = Sleep
                                yPosition[annotation_number] = Activity
                                if (Sleep>50):
                                    if (Activity<50):                    
                                        annotations[annotation_number] = ax.text(xPosition[annotation_number] - 4/math.sqrt(2) - 0.5,yPosition[annotation_number] + 4/math.sqrt(2) + 0.5, Label, verticalalignment = 'top', horizontalalignment = 'right', bbox=dict(boxstyle='round,pad=0.01', fc='white', alpha=0.7))
                                    else:
                                        annotations[annotation_number] = ax.text(xPosition[annotation_number] - 4/math.sqrt(2) - 0.5,yPosition[annotation_number] - 4/math.sqrt(2) - 0.5, Label, verticalalignment = 'bottom', horizontalalignment = 'right', bbox=dict(boxstyle='round,pad=0.01', fc='white', alpha=0.7))
                                else:
                                    if (Activity<50):                    
                                        annotations[annotation_number] = ax.text(xPosition[annotation_number] + 4/math.sqrt(2) + 0.5,yPosition[annotation_number] + 4/math.sqrt(2) + 0.5, Label, verticalalignment = 'top', horizontalalignment = 'left', bbox=dict(boxstyle='round,pad=0.01', fc='white', alpha=0.7))
                                    else:
                                        annotations[annotation_number] = ax.text(xPosition[annotation_number] + 4/math.sqrt(2) + 0.5,yPosition[annotation_number] - 4/math.sqrt(2) - 0.5, Label, verticalalignment = 'bottom', horizontalalignment = 'left', bbox=dict(boxstyle='round,pad=0.01', fc='white', alpha=0.7))
                                annotation_number = annotation_number+1
                        elif (linevars[0].upper()=="WM"):
                            if len(linevars)==6:
                                Sleep = int(linevars[1])
                                if (Sleep<0 or Sleep>100):
                                    messagebox.showerror("Error", "Sleep Ratio out of bounds!")
                                    break
                                Activity = int(linevars[2])
                                if (Activity<0 or Activity>100):
                                    messagebox.showerror("Error", "Activity Ratio out of bounds!")
                                    break
                                Radius = int(linevars[3])
                                Label = linevars[4]
                                Color = linevars[5].lower().strip();
                                markers[marker_number] = plt.plot([Sleep], [Activity], 'k.', markersize=Radius*8.5 + 5, markeredgecolor='black', mew=3, markerfacecolor="None")
                                markers[marker_number + 1] = plt.plot([Sleep], [Activity], 'k.', markersize=Radius*8.5, markeredgecolor='white', mew=3, markerfacecolor="None")
                                markerSizes[marker_number] = Radius*8.5 + 5;
                                markerSizes[marker_number + 1] = Radius*8.5;
                                marker_number = marker_number + 2;
                                if (Sleep>50):
                                    if (Activity<50):                    
                                        annotations[annotation_number] = ax.text(5, 5, Label, color = Color, verticalalignment = 'top', horizontalalignment = 'right')
                                    else:
                                        annotations[annotation_number] = ax.text(5, 5, Label, color = Color, verticalalignment = 'bottom', horizontalalignment = 'right')
                                else:
                                    if (Activity<50):                    
                                        annotations[annotation_number] = ax.text(5, 5, Label, color = Color, verticalalignment = 'top', horizontalalignment = 'left')
                                    else:
                                        annotations[annotation_number] = ax.text(5, 5, Label, color = Color, verticalalignment = 'bottom', horizontalalignment = 'left')
                                xPosition[annotation_number] = Sleep;
                                yPosition[annotation_number] = Activity;
                                annotation_number = annotation_number+1;
                            else:
                                Sleep = int(linevars[1])
                                if (Sleep<0 or Sleep>100):
                                    messagebox.showerror("Error", "Sleep Ratio out of bounds!")
                                    break
                                Activity = int(linevars[2])
                                if (Activity<0 or Activity>100):
                                    messagebox.showerror("Error", "Activity Ratio out of bounds!")
                                    break
                                Radius = int(linevars[3])
                                Label = linevars[4].strip()
                                markers[marker_number] = plt.plot([Sleep], [Activity], 'k.', markersize=Radius*8.5 + 5, markeredgecolor='black', mew=3, markerfacecolor="None")
                                markers[marker_number + 1] = plt.plot([Sleep], [Activity], 'k.', markersize=Radius*8.5, markeredgecolor='white', mew=3, markerfacecolor="None")
                                markerSizes[marker_number] = Radius*8.5 + 5;
                                markerSizes[marker_number + 1] = Radius*8.5;
                                marker_number = marker_number + 2;
                                if (Sleep>50):
                                    if (Activity<50):                    
                                        annotations[annotation_number] = ax.text(5, 5, Label, verticalalignment = 'top', horizontalalignment = 'right', bbox=dict(boxstyle='round,pad=0.01', fc='white', alpha=0.7))
                                    else:
                                        annotations[annotation_number] = ax.text(5, 5, Label, verticalalignment = 'bottom', horizontalalignment = 'right', bbox=dict(boxstyle='round,pad=0.01', fc='white', alpha=0.7))
                                else:
                                    if (Activity<50):                    
                                        annotations[annotation_number] = ax.text(5, 5, Label, verticalalignment = 'top', horizontalalignment = 'left', bbox=dict(boxstyle='round,pad=0.01', fc='white', alpha=0.7))
                                    else:
                                        annotations[annotation_number] = ax.text(5, 5, Label, verticalalignment = 'bottom', horizontalalignment = 'left', bbox=dict(boxstyle='round,pad=0.01', fc='white', alpha=0.7))
                                xPosition[annotation_number] = Sleep;
                                yPosition[annotation_number] = Activity;
                                annotation_number = annotation_number+1;
                        elif (linevars[0][0]=="#"):
                            continue;
                        elif (len(linevars[0].strip())==0):
                            continue;
                        else:
                            messagebox.showerror("Error", "Marker specifier incorrect!")
                        
                        #if "point" in line or "Point" in line:
                        #    tmp = line.split(":")[1].strip()
                        #    active = int(tmp.split(",")[0].strip())
                        #    sleep = int(tmp.split(",")[1].strip())
                        #    plt.plot([active], [sleep], 'k.', markersize=35.0, markeredgecolor='black', mew=3, markerfacecolor="None")
                        #    plt.plot([active], [sleep], 'k.', markersize=30.0, markeredgecolor='white', mew=3, markerfacecolor="None")

            # want a more natural, table-like display
            ax.invert_yaxis()
            ax.xaxis.tick_top()
            ax.axis('tight')

            first_ipc = "{0:.2f}".format(first_entry['IPC'])
            second_ipc = "{0:.2f}".format(second_entry['IPC'])

            ipc = fig.text(0.9, 0.11, 'IPC: ' + first_ipc + ',' + second_ipc,
                     verticalalignment='bottom', horizontalalignment='left',
                     color='brown', fontsize=initialFontSize, rotation = -90)

            # ax.set_xticklabels(column_labels, minor=False)
            # ax.set_yticklabels(row_labels, minor=False)
            # plt.colorbar(heatbar2)
            cbar = plt.colorbar(heatbar2, pad=0.05, ticks=[4015, 8030, 12045, 16060, 20075, 24090, 28105, 32120, 36000])
            cbar.ax.set_yticklabels(['11', '22', '33', '44', '55', '66', '77', '88', '99'])
            cbar.ax.tick_params(labelsize=initialFontSize)
            cbar.set_label('Years', rotation=360, size=initialAxisLabelSize, labelpad=-30, y=1.08)
            # plt.colorbar(heatbar)
            cbar2 = plt.colorbar(heatbar, pad = 0.1)
            cbar2.ax.tick_params(labelsize=initialFontSize)
            # cbar.ax.set_yticklabels(labelsize=10)
            cbar2.set_label('Days', rotation=360, size=initialAxisLabelSize, labelpad=-37.5, y=1.08)
            plt.xlabel('xlabel', fontsize=initialAxisLabelSize)
            plt.ylabel('ylabel', fontsize=initialAxisLabelSize)
            ax.set_xlabel('Percent Sleep')
            ax.xaxis.set_label_position('top')
            ax.xaxis.labelpad = 16;
            plt.ylabel('Activity Ratio')
            ax.set_title(label=plot_title, fontsize=initialTitleLabelSize, pad=12)
            
            widthScalingFactor = 2
            lengthScalingFactor = 1.3
            initialSize = min(fig.get_size_inches()[0]/widthScalingFactor,fig.get_size_inches()[1]/lengthScalingFactor)

            ax.set_aspect('equal', adjustable = None)
            
            def on_resize(event):
                nonlocal bmarker
                Size = min(fig.get_size_inches()[0]/widthScalingFactor,fig.get_size_inches()[1]/lengthScalingFactor)
                for i in range(marker_number):
                    markers[i][0].set_markersize(markerSizes[i]*Size/initialSize)
                for i in range(annotation_number):
                    if (Size/initialSize<1.5):
                        annotations[i].set_fontsize(10*Size/initialSize)
                    else:
                        annotations[i].set_fontsize(15)
                    if markerSizes[i*2]==35.0:
                        if (xPosition[i]>50):
                            if (yPosition[i]<50):                    
                                annotations[i].set_x(xPosition[i] - 4/math.sqrt(2) - 0.5/(Size/initialSize))
                                annotations[i].set_y(yPosition[i] + 4/math.sqrt(2) + 0.5/(Size/initialSize))
                            else:
                                annotations[i].set_x(xPosition[i] - 4/math.sqrt(2) - 0.5/(Size/initialSize))
                                annotations[i].set_y(yPosition[i] - 4/math.sqrt(2) - 0.5/(Size/initialSize))
                        else:
                            if (yPosition[i]<50):                    
                                annotations[i].set_x(xPosition[i] + 4/math.sqrt(2) + 0.5/(Size/initialSize))
                                annotations[i].set_y(yPosition[i] + 4/math.sqrt(2) + 0.5/(Size/initialSize))
                            else:
                                annotations[i].set_x(xPosition[i] + 4/math.sqrt(2) + 0.5/(Size/initialSize))
                                annotations[i].set_y(yPosition[i] - 4/math.sqrt(2) - 0.5/(Size/initialSize))
                    else:
                        if (xPosition[i]>50):
                            if (yPosition[i]<50):                    
                                annotations[i].set_x(xPosition[i] - (markerSizes[i*2 + 1])/(9*math.sqrt(2)) - 1/(Size/initialSize))
                                annotations[i].set_y(yPosition[i] + (markerSizes[i*2 + 1])/(9*math.sqrt(2)) + 1/(Size/initialSize))
                            else:
                                annotations[i].set_x(xPosition[i] - (markerSizes[i*2 + 1])/(9*math.sqrt(2)) - 1/(Size/initialSize))
                                annotations[i].set_y(yPosition[i] - (markerSizes[i*2 + 1])/(9*math.sqrt(2)) - 1/(Size/initialSize))
                        else:
                            if (yPosition[i]<50):                                        
                                annotations[i].set_x(xPosition[i] + (markerSizes[i*2 + 1])/(9*math.sqrt(2)) + 1/(Size/initialSize))
                                annotations[i].set_y(yPosition[i] + (markerSizes[i*2 + 1])/(9*math.sqrt(2)) + 1/(Size/initialSize))
                            else:
                                annotations[i].set_x(xPosition[i] + (markerSizes[i*2 + 1])/(9*math.sqrt(2)) + 1/(Size/initialSize))
                                annotations[i].set_y(yPosition[i] - (markerSizes[i*2 + 1])/(9*math.sqrt(2)) - 1/(Size/initialSize))

                if (Size<initialSize):
                    ax.tick_params(axis = 'both', labelsize = initialFontSize*Size/initialSize)
                    ax.xaxis.label.set_size(initialAxisLabelSize*Size/initialSize)
                    ax.yaxis.label.set_size(initialAxisLabelSize*Size/initialSize)
                    ax.xaxis.labelpad = 16*Size/initialSize
                    ax.yaxis.labelpad = 16*Size/initialSize - 8
                    ax.set_title(label=plot_title, fontsize=initialTitleLabelSize*Size/initialSize, pad=12*Size/initialSize)
                    cbar.ax.tick_params(labelsize=initialFontSize*(Size/initialSize)*math.sqrt(Size/initialSize))
                    cbar2.ax.tick_params(labelsize=initialFontSize*Size/initialSize*math.sqrt(Size/initialSize))
                    cbar.set_label('Years', rotation=360, size=initialAxisLabelSize*Size/initialSize, labelpad=-30*Size/initialSize, y=1.08)            
                    cbar2.set_label('Days', rotation=360, size=initialAxisLabelSize*Size/initialSize, labelpad=-37.5*Size/initialSize, y=1.08)
                else:
                    ax.tick_params(axis = 'both', labelsize = initialFontSize)
                    ax.xaxis.label.set_size(initialAxisLabelSize)
                    ax.yaxis.label.set_size(initialAxisLabelSize)
                    ax.xaxis.labelpad = 16;
                    ax.yaxis.labelpad = 8;
                    cbar.ax.tick_params(labelsize=initialFontSize)
                    cbar2.ax.tick_params(labelsize=initialFontSize)
                    cbar.set_label('Years', rotation=360, size=initialAxisLabelSize, labelpad=-30, y=1.08)            
                    cbar2.set_label('Days', rotation=360, size=initialAxisLabelSize, labelpad=-37.5, y=1.08)
                    
                bmarker.label.set_fontsize(10*Size/initialSize)
                bigmarker.label.set_fontsize(10*Size/initialSize)
                ipc.set_fontsize(initialFontSize*Size/initialSize)
                    
            
            def PlaceNewMarker(event):
                nonlocal annotation_number
                nonlocal marker_number
                Sleep = int(simpledialog.askstring("Sleep","Please enter the Marker's Sleep Ratio:")) # Prompts user for the sleep ratio at which the point is at
                Activity = int(simpledialog.askstring("Activity","Please enter the Marker's Activity Ratio:")) # Prompts user for the activity ratio at which the point is at
                Label = str(simpledialog.askstring("Label","Please enter the Marker's Label. The next window will ask for the label's color."))
                my_color = colorchooser.askcolor() #Ask the user for a color
                
                Size = min(fig.get_size_inches()[0]/widthScalingFactor,fig.get_size_inches()[1]/lengthScalingFactor)                
                xPosition[annotation_number] = Sleep;
                yPosition[annotation_number] = Activity;
                if (Sleep>50):
                    if (Activity<50):                    
                        annotations[annotation_number] = ax.text(xPosition[annotation_number] - 4/math.sqrt(2) - 0.5/(Size/initialSize),yPosition[annotation_number] + 4/math.sqrt(2) + 0.5/(Size/initialSize), Label, color = my_color[1], verticalalignment = 'top', horizontalalignment = 'right')
                    else:
                        annotations[annotation_number] = ax.text(xPosition[annotation_number] - 4/math.sqrt(2) - 0.5/(Size/initialSize),yPosition[annotation_number] - 4/math.sqrt(2) - 0.5/(Size/initialSize), Label, color = my_color[1], verticalalignment = 'bottom', horizontalalignment = 'right')
                else:
                    if (Activity<50):                    
                        annotations[annotation_number] = ax.text(xPosition[annotation_number] + 4/math.sqrt(2) + 0.5/(Size/initialSize),yPosition[annotation_number] + 4/math.sqrt(2) + 0.5/(Size/initialSize), Label, color = my_color[1], verticalalignment = 'top', horizontalalignment = 'left')
                    else:
                        annotations[annotation_number] = ax.text(xPosition[annotation_number] + 4/math.sqrt(2) + 0.5/(Size/initialSize),yPosition[annotation_number] - 4/math.sqrt(2) - 0.5/(Size/initialSize), Label, color = my_color[1], verticalalignment = 'bottom', horizontalalignment = 'left')
                
                markerSizes[marker_number] = 35.0;
                markerSizes[marker_number + 1] = 30.0;
                markers[marker_number] = ax.plot([Sleep], [Activity], 'k.', markersize=35.0*Size/initialSize, markeredgecolor='black', mew=3, markerfacecolor="None")
                markers[marker_number + 1] = ax.plot([Sleep], [Activity], 'k.', markersize=30.0*Size/initialSize, markeredgecolor='white', mew=3, markerfacecolor="None")
                marker_number = marker_number + 2
                annotation_number = annotation_number + 1
                if event.inaxes is not None:
                    event.inaxes.figure.canvas.draw_idle()

            def PlaceNewWideMarker(event):
                nonlocal annotation_number
                nonlocal marker_number                
                Sleep = int(simpledialog.askstring("Sleep","Please enter the Marker's Sleep Ratio:")) # Prompts user for the sleep ratio at which the point is at
                Activity = int(simpledialog.askstring("Activity","Please enter the Marker's Activity Ratio:")) # Prompts user for the activity ratio at which the point is at
                Radius = int(simpledialog.askstring("Radius","Please enter the Marker's Radius:"))
                Label = str(simpledialog.askstring("Label","Please enter the Marker's Label. The next window will ask for the label's color."))
                my_color = colorchooser.askcolor() #Ask the user for a color
                
                Size = min(fig.get_size_inches()[0]/widthScalingFactor,fig.get_size_inches()[1]/lengthScalingFactor)
                markerSizes[marker_number] = Radius*8.5 + 5
                markerSizes[marker_number + 1] = Radius*8.5
                markers[marker_number] = ax.plot([Sleep], [Activity], 'k.', markersize=(Radius*8.5 + 5)*Size/initialSize, markeredgecolor='black', mew=3, markerfacecolor="None")
                markers[marker_number + 1] = ax.plot([Sleep], [Activity], 'k.', markersize=Radius*8.5*Size/initialSize, markeredgecolor='white', mew=3, markerfacecolor="None")
                                
                xPosition[annotation_number] = Sleep
                yPosition[annotation_number] = Activity

                if (Sleep>50):
                    if (Activity<50):                    
                        annotations[annotation_number] = ax.text(5, 5, Label, color = my_color[1], verticalalignment = 'top', horizontalalignment = 'right')
                        annotations[annotation_number].set_x(xPosition[annotation_number] - (markerSizes[annotation_number*2 + 1])/(9*math.sqrt(2)) - 1/(Size/initialSize))
                        annotations[annotation_number].set_y(yPosition[annotation_number] + (markerSizes[annotation_number*2 + 1])/(9*math.sqrt(2)) + 1/(Size/initialSize))
                    else:
                        annotations[annotation_number] = ax.text(5, 5, Label, color = my_color[1], verticalalignment = 'bottom', horizontalalignment = 'right')
                        annotations[annotation_number].set_x(xPosition[annotation_number] - (markerSizes[annotation_number*2 + 1])/(9*math.sqrt(2)) - 1/(Size/initialSize))
                        annotations[annotation_number].set_y(yPosition[annotation_number] - (markerSizes[annotation_number*2 + 1])/(9*math.sqrt(2)) - 1/(Size/initialSize))
                else:
                    if (Activity<50):                    
                        annotations[annotation_number] = ax.text(5, 5, Label, color = my_color[1], verticalalignment = 'top', horizontalalignment = 'left')
                        annotations[annotation_number].set_x(xPosition[annotation_number] + (markerSizes[annotation_number*2 + 1])/(9*math.sqrt(2)) + 1/(Size/initialSize))
                        annotations[annotation_number].set_y(yPosition[annotation_number] + (markerSizes[annotation_number*2 + 1])/(9*math.sqrt(2)) + 1/(Size/initialSize))
                    else:
                        annotations[annotation_number] = ax.text(5, 5, Label, color = my_color[1], verticalalignment = 'bottom', horizontalalignment = 'left')
                        annotations[annotation_number].set_x(xPosition[annotation_number] + (markerSizes[annotation_number*2 + 1])/(9*math.sqrt(2)) + 1/(Size/initialSize))
                        annotations[annotation_number].set_y(yPosition[annotation_number] - (markerSizes[annotation_number*2 + 1])/(9*math.sqrt(2)) - 1/(Size/initialSize))

                        
                marker_number = marker_number + 2
                annotation_number = annotation_number + 1
                if event.inaxes is not None:
                    event.inaxes.figure.canvas.draw_idle()               



            markerax = plt.axes([0.51, .01, 0.3, 0.075])
            bmarker = Button(markerax, 'Place New Marker')
            bmarker.on_clicked(PlaceNewMarker)

            bigmarkerax = plt.axes([0.13, .01, 0.35, 0.075])
            bigmarker = Button(bigmarkerax, 'Place New Wide Marker')
            bigmarker.on_clicked(PlaceNewWideMarker)

            # plt.title(''.join([utils.rename(self.entry1, False), ' vs. ', utils.rename(self.entry2, False)]), y=1.08)

            #image_file_name = path_to_output_directory + title1 + "_vs_" + title2 + ".pdf"
            
            fig.canvas.mpl_connect('resize_event', on_resize)
            #fig.tight_layout()
            plt.show(block=False)
            #plt.savefig(image_file_name, bbox_inches='tight')
            #plt.clf()
            #plt.close()
        elif sys.platform.startswith("win"):
            try:
                breakeven_export_name = filedialog.asksaveasfilename(defaultextension=".csv")
                with open(breakeven_export_name, "w") as indiff_writer:
                    for a in range(0, len(res)):
                        for b in range(0, len(res[0])):
                            indiff_writer.write(str(a)+","+str(b)+","+str(res[a][b])+"\n")
                #Assumes matlab is in the current directory
                dir_path = os.path.dirname(os.path.realpath(__file__))
                subprocess.call('matlab -nodesktop -nosplash /r "addpath '+str(dir_path)+';greenchip_plotter(\''+str(breakeven_export_name)+'\');"', shell = True)
            except:
                messagebox.showinfo("Library Missing!", "Missing matplotlib, and no matlab found to take its place!")
                for bbb in range(0, len(sys.exc_info())):
                    print(sys.exc_info()[bbb])
                #print(sys.exc_info()[0])
        else:
            messagebox.showinfo("Library Missing!", "Missing matplotlib, cannot plot natively in python!")
    
    # The points are done once to determine the maximum x axis location in order to plot the background colors.     
    #For some reason the background color overlay the plot points but they do not overlay the labels     
    #Func is called second time to plot the points over the background of color in order fot the points to be visible 
    @staticmethod
    def make_single_plot_carbon_points(self, first_entry, second_entry):        
        # Plotting location manufacturing phase Carbon for CPU
        sep = 4 # Separation between plotted point and label
        plt.plot([first_entry['Total CPU Carbon']], [first_entry['processSizeNum']], 'b', marker='o', markersize=10.0, markeredgecolor='blue', mew=3, markerfacecolor="blue", alpha=1.0)
        plt.plot([second_entry['Total CPU Carbon']], [second_entry['processSizeNum']], 'w', marker='o', markersize=10.0, markeredgecolor='black', mew=3, markerfacecolor="black", alpha=1.0)
        
        # Plotting location manufacturing phase Carbon for DRAM      
        plt.plot([first_entry['Total DRAM Carbon']], [first_entry['processSizeDramNum']], 'y', marker='o', markersize=10.0, markeredgecolor='yellow', mew=3, markerfacecolor="yellow", alpha=1.0)
        plt.plot([second_entry['Total DRAM Carbon']], [second_entry['processSizeDramNum']], 'm', marker='o', markersize=10.0, markeredgecolor='magenta', mew=3, markerfacecolor="magenta", alpha=1.0)
        
        #Plotting location usage phase Carbon
        plt.plot([first_entry['CPU Hourly Usage Carbon']], [first_entry['processSizeNum']], 'purple', marker='o', markersize=10.0, markeredgecolor='purple', mew=3, markerfacecolor="purple", alpha=1.0)  
        plt.plot([second_entry['CPU Hourly Usage Carbon']], [second_entry['processSizeNum']], 'brown', marker='o', markersize=10.0, markeredgecolor='brown', mew=3, markerfacecolor="brown", alpha=1.0) 
        plt.plot([first_entry['DRAM Hourly Usage Carbon']], [first_entry['processSizeDramNum']], 'orange', marker='o', markersize=10.0, markeredgecolor='orange', mew=3, markerfacecolor="orange", alpha=1.0)
        plt.plot([second_entry['DRAM Hourly Usage Carbon']], [second_entry['processSizeDramNum']], 'cyan', marker='o', markersize=10.0, markeredgecolor='cyan', mew=3, markerfacecolor="cyan", alpha=1.0)
    
    @staticmethod
    def make_single_plot_carbon(self, first_entry, second_entry, title1, title2, res):
        leftColor='lime' #green
        rightColor='red' #red
        
        if settingsConfig.nativePlotting:
            matplotlib.rc('xtick', labelsize=16)
            matplotlib.rc('ytick', labelsize=16)


            if first_entry is None or second_entry is None:
                return

            settingsFile = settingsConfig.advancedSettingsFile
            #arr controls the heatmap coloring
            #arr = utils.perform_greenchip_analysis(res)
        
            fig, ax = plt.subplots()
            
            cdict2 = OurConstants.get_cdict2()

            cdict1 = OurConstants.get_cdict1()

            customgray = LinearSegmentedColormap('customgray', cdict1)
            customspectrum = LinearSegmentedColormap('customspectrum', cdict2)
            c = (0, 0, 0, 0)
            my_cmap = plt.get_cmap(customspectrum)
            my_cmap.set_under(color='white')
            second_cmap = plt.get_cmap(customgray)
            second_cmap.set_under(color=c)
            ''' 
            heatmap = ax.pcolormesh(arr, cmap=my_cmap, vmax=3650, vmin=0)
            heatbar = heatmap
            heatmap = ax.pcolormesh(arr, cmap=second_cmap, vmax=36000, vmin=4000)
            heatbar2 = heatmap
            '''

            if settingsFile is None:
                '''    
                # Desktop
                plt.plot([77], [17], 'k.', markersize=35.0, markeredgecolor='black', mew=3, markerfacecolor="None")
                plt.plot([77], [17], 'k.', markersize=30.0, markeredgecolor='white', mew=3, markerfacecolor="None")
                plt.annotate('Desktop',[77+5,17+5])

                # Server
                plt.plot([5], [30], 'k.', markersize=35.0, markeredgecolor='black', mew=3, markerfacecolor="None")
                plt.plot([5], [30], 'k.', markersize=30.0, markeredgecolor='white', mew=3, markerfacecolor="None")
                plt.annotate('Server',[5+5,30+5])

                # HPC
                plt.plot([5], [95], 'k.', markersize=35.0, markeredgecolor='black', mew=3, markerfacecolor="None")
                plt.plot([5], [95], 'k.', markersize=30.0, markeredgecolor='white', mew=3, markerfacecolor="None")
                plt.annotate('HPC',[5+5,95+5])
                
                # Cell Phone
                plt.plot([92], [90], 'k.', markersize=35.0, markeredgecolor='black', mew=3, markerfacecolor="None")
                plt.plot([92], [90], 'k.', markersize=30.0, markeredgecolor='white', mew=3, markerfacecolor="None")
                plt.annotate('Cellular',[92+5,90+5])
                '''
                utils.make_single_plot_carbon_points(self,first_entry,second_entry)    
                
            else:

                with open(settingsFile, "r") as settingsObject:
                    for line in settingsObject:
                        if "point" in line or "Point" in line:
                            tmp = line.split(":")[1].strip()
                            carbonEm = int(tmp.split(",")[0].strip())
                            techNodenm = int(tmp.split(",")[1].strip())
                            plt.plot([carbonEm], [techNodenm], 'k.', markersize=35.0, markeredgecolor='black', mew=3, markerfacecolor="None")
                            plt.plot([carbonEm], [techNodenm], 'k.', markersize=30.0, markeredgecolor='white', mew=3, markerfacecolor="None")

            # want a more natural, table-like display
            ax.invert_yaxis()
            ax.xaxis.tick_top()
            ax.axis('tight')

            '''first_ipc = "{0:.2f}".format(first_entry['IPC'])
            second_ipc = "{0:.2f}".format(second_entry['IPC'])

            fig.text(0.95, 0.01, 'IPC: ' + first_ipc + ',' + second_ipc,
                     verticalalignment='bottom', horizontalalignment='left',
                     color='brown', fontsize=15)
                     '''

            # ax.set_xticklabels(column_labels, minor=False)
            # ax.set_yticklabels(row_labels, minor=False)
            # plt.colorbar(heatbar2)
            '''
            cbar = plt.colorbar(heatbar2, pad=0.05)
            cbar.ax.set_yticklabels(['11', '22', '33', '44', '55', '66', '77', '88', '99'])
            cbar.ax.tick_params(labelsize=16)
            cbar.set_label('Carbon Value', rotation=360, size=20, labelpad=-30, y=1.08)
            '''
            # plt.colorbar(heatbar)
            #cbar2 = plt.colorbar(heatbar)
            #cbar2.ax.tick_params(labelsize=16)
            # cbar.ax.set_yticklabels(labelsize=10)
            '''
            cbar2.set_label('days', rotation=360, size=20, labelpad=-37.5, y=1.08)
            '''
            plt.xlabel('xlabel', fontsize=16)
            plt.ylabel('ylabel', fontsize=16)
            plt.title(label='Carbon Generated from Manufacturing and Hourly Usage', fontsize='20', pad='20')
            # plt.xlabel('Percent Sleep')
            ax.set_xlabel('Carbon Emission (gCO2)')
            ax.xaxis.set_label_position('top')
            plt.ylabel('Technology Node (nm)')
            # plt.title(''.join([utils.rename(self.entry1, False), ' vs. ', utils.rename(self.entry2, False)]), y=1.08)

            #image_file_name = path_to_output_directory + title1 + "_vs_" + title2 + ".pdf"
            
            axes = plt.gca()
            n = int(axes.get_xlim()[1])
            
            for x in range(n+1):
                ax.axvline(x, color=colorFader(leftColor, rightColor, x/n), linewidth=6, alpha=1.0) 
            
            utils.make_single_plot_carbon_points(self, first_entry, second_entry)
            blue_patch=mpatches.Patch(color='blue', label='CPU Manufacturing - ' + first_entry['LocationManu CPU'])
            black_patch=mpatches.Patch(color='black', label='CPU Manufacturing - ' + second_entry['LocationManu CPU'])
            yellow_patch=mpatches.Patch(color='yellow', label='DRAM Manufacturing - ' + first_entry['LocationManu DRAM'])
            magenta_patch=mpatches.Patch(color='magenta', label='DRAM Manufacturing - ' + second_entry['LocationManu DRAM'])
            purple_patch=mpatches.Patch(color='purple', label='CPU Use/Hour - ' + first_entry['Carbon Use Phase Loc'])
            brown_patch=mpatches.Patch(color='brown', label='CPU Use/Hour - ' + second_entry['Carbon Use Phase Loc'])
            orange_patch=mpatches.Patch(color='orange', label='DRAM Use/Hour - ' + first_entry['Carbon Use Phase Loc'])
            cyan_patch=mpatches.Patch(color='cyan', label='DRAM Use/Hour - ' + second_entry['Carbon Use Phase Loc'])
            
            plt.legend(handles=[blue_patch, black_patch, yellow_patch, magenta_patch, purple_patch, brown_patch, orange_patch, cyan_patch], loc='center left', bbox_to_anchor=(1, 0.5), fancybox=True, shadow=True)
            #plt.figure().subplots_adjust(bottom=0.5)
            fig.tight_layout()       #try if other things are not working   
            
            plt.show()
            #plt.savefig(image_file_name, bbox_inches='tight')
            #plt.clf()
            #plt.close()
        elif sys.platform.startswith("win"):
            try:
                breakeven_export_name = filedialog.asksaveasfilename(defaultextension=".csv")
                with open(breakeven_export_name, "w") as indiff_writer:
                    for a in range(0, len(res)):
                        for b in range(0, len(res[0])):
                            indiff_writer.write(str(a)+","+str(b)+","+str(res[a][b])+"\n")
                #Assumes matlab is in the current directory
                dir_path = os.path.dirname(os.path.realpath(__file__))
                subprocess.call('matlab -nodesktop -nosplash /r "addpath '+str(dir_path)+';greenchip_plotter(\''+str(breakeven_export_name)+'\');"', shell = True)
            except:
                messagebox.showinfo("Library Missing!", "Missing matplotlib, and no matlab found to take its place!")
                for bbb in range(0, len(sys.exc_info())):
                    print(sys.exc_info()[bbb])
                #print(sys.exc_info()[0])
        else:
            messagebox.showinfo("Library Missing!", "Missing matplotlib, cannot plot natively in python!")

class OurConstants(object):


    @staticmethod
    def get_cdict2():
        return {'red': ((0.0, 0.0, 0.0),  # black
                          (0.13, 1.0, 1.0),  # purple
                          (0.26, 0.0, 0.0),  # blue
                          (0.39, 0.0, 0.0),  #teal
                          (0.52, 0.0, 0.0),  # green
                          (0.65, 1.0, 1.0),  # yellow
                          (0.78, 1.0, 1.0),  # orange
                          (0.9, 1.0, 1.0),  # red
                          (1.0, 0.3, 0.3)),  # gray

                  'green': ((0.0, 0.0, 0.0),
                            (0.13, 0.0, 0.0),  # purple
                            (0.26, 0.0, 0.0),  # blue
                            (0.39, 0.5, 0.5),  #teal
                            (0.52, 1.0, 1.0),  # green
                            (0.65, 1.0, 1.0),  # yellow
                            (0.78, 0.5, 0.5),  # orange
                            (0.9, 0.0, 0.0),  # red
                            (1.0, 0.3, 0.3)),  # gray


                  'blue': ((0.0, 0.0, 0.0),
                           (0.13, 1.0, 1.0),  # purple
                           (0.26, 1.0, 1.0),  # blue
                           (0.39, 0.5, 0.5),  #teal
                           (0.52, 0.0, 0.0),  # green
                           (0.65, 0.0, 0.0),  # yellow
                           (0.78, 0.0, 0.0),  # orange
                           (0.9, 0.0, 0.0),  # red
                           (1.0, 0.3, 0.3)),}  # gray

    @staticmethod
    def get_cdict1():
        return {'red': ((0.0, 0.3, 0.3),
                          (0.05, 0.4, 0.4),
                          (0.1, 0.5, 0.5),
                          (0.2, 0.6, 0.6),
                          (1.0, 1.0, 1.0)),

                  'green': ((0.0, 0.3, 0.3),
                            (0.05, 0.4, 0.4),
                            (0.1, 0.5, 0.5),
                            (0.2, 0.6, 0.6),
                            (1.0, 1.0, 1.0)),

                  'blue': ((0.0, 0.3, 0.3),
                           (0.05, 0.4, 0.4),
                           (0.1, 0.5, 0.5),
                           (0.2, 0.6, 0.6),
                           (1.0, 1.0, 1.0)),}

import csv
from enum import Enum
import time

from rich import print
from rich.pretty import pprint
from rich.progress import track, Progress

import Joist_and_Plank as jp
import pandas as pd
from O86 import O86_20 as O86
from Section import Section

class Units(Enum):
    Metric = 0
    Imperial = 1

units = Units.Imperial
if units == Units.Imperial:
    pressure_factor = 1/20.885 #psf to kPa
    udl_factor = 1/68.54 #plf to kN/m
    load_factor = 4.448222/1000 #lb to kN
    length_factor = 1000/3.28 #ft in mm
else:
    pressure_factor = 1
    load_factor = 1
    length_factor = 1
    
csv_filename = 'Joist_and_Plank.csv'
jp_dict = {}
species_list = []
with open(csv_filename, mode ='r')as file:
    csvFile = csv.DictReader(file)
    for lines in csvFile:
        temp = {}
        for key, value in lines.items():
            try:
                x = float(value)
            except:
                x = value
            temp[key] = x
        new_jp = jp.Joist_and_Plank(**temp)
        species_list.append(new_jp.name) 
        jp_dict[new_jp.name] = new_jp
        
        jp_df = pd.read_csv(csv_filename, index_col="Species")
        
def Sum_Loads(n_floors: int):
    i = 0
    floors = {}
    dl = 0
    ll = 0
    sl = 0
    while i < n_floors:
        if i == 0:
            dl = (roof_dead * wall_roof_trib+wall_sw * wall_heights[i])*udl_factor
            ll = 0*udl_factor
            sl = (roof_snow * wall_roof_trib)*udl_factor
        else:
            dl = ((floor_dead + partitions) * wall_floor_trib+wall_sw * wall_heights[i])*udl_factor
            ll = (floor_live * wall_floor_trib)*udl_factor
            sl = 0*udl_factor
        floors[n_floors-i] = {
            'H': wall_heights[i],
            'DL': dl,
            'LL': ll,
            'SL': sl
        }
        i += 1
    floor_df =pd.DataFrame(floors).transpose()
    new_df = floor_df.cumsum().drop(['H'], axis=1)
    return new_df

def Combo(df):
    combo_dict = {}
    combo_dict['1.4DL'] = df['DL'] * 1.4
    combo_dict['1.25DL+1.5LL+1.0SL'] = df['DL'] * 1.25 + df['LL'] * 1.5 + df['SL'] * 1.0
    combo_dict['1.25DL+1.5SL+1.0LL'] = df['DL'] * 1.25 + df['SL'] * 1.5 + df['LL'] * 1.0
    combo_dict['1.25DL+1.5LL'] = df['DL'] * 1.25 + df['LL'] * 1.5 
    combo_dict['1.25DL+1.5SL'] = df['DL'] * 1.25 + df['SL'] * 1.5 
    combo_df = pd.DataFrame(combo_dict)
    return combo_df

def Size_Studs(stud: Section, spacing: float, combo: str, load: float, load_dict: dict):
    #get long term and short term loads on stud
    if combo == '1.4DL':
        duration = 'Long'
        long = 0
        short = 0
    elif combo == '1.25DL+1.5LL+1.0SL':
        duration = 'Standard'
        long = load_dict['DL']
        short = load_dict['LL'] + 0.5* load_dict['SL']
    elif combo == '1.25DL+1.5SL+1.0LL':
        duration = 'Standard'
        long = load_dict['DL']
        short = load_dict['SL'] + 0.5* load_dict['LL']
    elif combo == '1.25DL+1.5LL':
        duration = 'Standard'
        long = load_dict['DL']
        short = load_dict['LL']
    elif combo == '1.25DL+1.5SL':
        duration = 'Standard'
        long = load_dict['DL']
        short = load_dict['SL']
    #get factored axial load on stud
    Pf = load * spacing / 1000
    Pl = long * spacing / 1000
    Ps = short * spacing / 1000
    #determine k factors
    k_factors = {
        "Kd": O86.CL5_3_2_2(duration,Pl, Ps), 
        "Kh": 1.0, 
        "Kse": 1.0, 
        "Ksc": 1.0, 
        "Kt": 1.0
    }
    #determine axial capacity of stud in eah direction
    Pr = {
        'Width': O86.CL6_5_6_2_3(stud,stud.Lu['Width'],**k_factors),
        'Depth': O86.CL6_5_6_2_3(stud,stud.Lu['Depth'],**k_factors)
    }
    #determine the DC ratio in each direction
    DC = {
        'Width': Pf/(Pr['Width']['Pr']/1000),
        'Depth': Pf/(Pr['Depth']['Pr']/1000)
    }
    #determine governing DC ratio
    DC = max(DC['Width'], DC['Depth'])
    
    return {'Pf': Pf, 'Pr': Pr, 'DC': DC, "k_factors": k_factors}

#set wall tribs and heights
wall_roof_trib = 2 #ft
wall_floor_trib = 11 #ft
wall_heights = [10,10,10,10,12] #ft
n_floors = len(wall_heights)
#set allowable spacings
spacings = [406,305,203] #mm
#create stud objects for various stud sizes to be used
s_2x4 = Section(38,89, jp_dict['SPF No1/No2'])
s_2x6 = Section(38,140, jp_dict['SPF No1/No2'])
s_2x8 = Section(38, 184, jp_dict['SPF No1/No2'])
#create list of stub objects
studs = [s_2x4, s_2x6, s_2x8]
#define base roof and floor loads
roof_dead = 22 #psf
roof_snow = 69 #psf
floor_dead = 35 #psf
floor_live = 40 #psf
partitions = 20 #psf
wall_sw = 12 #psf
#sum loads doen thorugh levels
loads_df = Sum_Loads(n_floors)
#print(f"Wall Load Summary\n{loads_df}\n")
#determine factorded load combinations for all floors
combo_df = Combo(loads_df) #.drop(['DL','LL','SL'], axis = 1)
#print(f"Load Combintation Summary\n{combo_df}\n")
#set governing DC ratio
DC_max = 1.0
results = []
results_dict = {}
final_results_dict ={}       
i = 0 #spacing iterator
k = 0 #stud section iterator

#print dataframes with full load and combos:
print("\n[bold blue]Unfactored Total Loads per floor[/bold blue]")
pprint(loads_df)
print("\n[bold blue]Factored Loads Combos per floor[/bold blue]")
pprint(combo_df)

with Progress() as progress:
    #loop over floors (wall heights)
    for level in range(n_floors,0, -1):
        task1 = progress.add_task(f"[bold red]Processing....{level}", total = 100)
        #set initial strud size to 2x4
        stud = studs[0]
        #set initial stud spacing
        spacing = spacings[0] 
        #set heaigh to hiehgt of current level
        h = wall_heights[n_floors - level] * length_factor #convert to m
        #set unsupported lengths in each direction
        stud.Lu['Width'] = 0.152 #nail spacing 
        stud.Lu['Depth'] = h #wall height
        #get dictoinary of all load combos at current level
        load_dict = loads_df.loc[level].to_dict()
        load_combo_dict = combo_df.loc[level].to_dict()
        #output what is happening to terminal
        print(f"\n[bold red]Running Design Checks for Level {level}[/bold red]")
        #print(f"Height = {round(h,3)}")
        # print(f"Loads: \n{load_dict}")
        # print(f"Combos: \n{load_combo_dict}")
        #loop through all load combination at current level
        for combo, load in load_combo_dict.items():
            #if combo == '1.25DL+1.5LL':  break
            results_dict[combo] = Size_Studs(stud, spacing, combo, load, load_dict)
            DC = results_dict[combo]['DC']
            while DC >= DC_max:
                stud.Plys += 1 # increase plys
                results_dict[combo] = Size_Studs(stud, spacing, combo, load, load_dict)
                if stud.Plys > 3: # if max number of plys is reached (3) reset plys and spacing and use next stud size
                    stud.Plys = 1 # reset plys
                    i += 1
                    spacing = spacings[i]
                    results_dict[combo] = Size_Studs(stud, spacing, combo, load, load_dict)
                if i > len(spacings)-1: # if min spacing (200) is reached reset to 400 and increase number of plys
                    i = 0 # reset spacing
                    k += 1 # increase stud size
                    stud = studs[k]
                    results_dict[combo] = Size_Studs(stud, spacing, combo, load, load_dict)
                if k > 3: # nothing works reset all values and display error message
                    break
                DC = results_dict[combo]['DC']
            results_dict[combo]['spacing'] = spacing
            results_dict[combo]['stud'] = stud   

        for combo, load in load_combo_dict.items():
            final_results_dict[combo] = Size_Studs(stud, spacing, combo, load, load_dict)
            final_results_dict[combo]['spacing'] = spacing
            final_results_dict[combo]['stud'] = stud 

        dc_list = []
        for combo in final_results_dict:
            result = final_results_dict[combo]
            dc_list.append(result['DC'])
            governing_dc = max(dc_list)
            if result['DC'] == governing_dc:
                governing_lc = combo

        while not progress.finished:
            progress.update(task1, advance = 20)
            time.sleep(0.2)

        if progress.finished:

        # for combo in results_dict:
        #     result = results_dict[combo]        
        #     print(f"\n[bold green]Results for {combo}[/bold green]")
        #     print(f"({result['stud'].Plys})-{result['stud'].Name} @ {result['spacing']} o/c")
        #     print(f"Pf = {result['Pf']}")
        #     print(f"Pr = {min(result['Pr']['Width']['Pr'],result['Pr']['Depth']['Pr']) / 1000}")
        #     print(f"DC = {result['DC']}")
            print("---------------------------------------------------------")  
            print(f"[bold red]Final Results for {level}[/bold red]")  
            for combo in final_results_dict:
                result = final_results_dict[combo]        
                print(f"[bold green]Results for {combo}[/bold green]")
                print(f"({result['stud'].Plys})-{result['stud'].Name} @ {result['spacing']} o/c")
                print(f"Pf = {result['Pf']}")
                print(f"Pr = {min(result['Pr']['Width']['Pr'],result['Pr']['Depth']['Pr']) / 1000}")
                print(f"DC = {result['DC']}")
            print("---------------------------------------------------------\n") 
            print("[bold red]Results for Govnerning Load Combo[/bold red]")
            print(f"[bold green]Governing Combo: {governing_lc}[/bold green]")
            result = final_results_dict[governing_lc]        
            print(f"({result['stud'].Plys})-{result['stud'].Name} {result['stud'].Material.name} @ {result['spacing']} o/c")
            print(f"Pf = {result['Pf']}")
            print(f"Pr = {min(result['Pr']['Width']['Pr'],result['Pr']['Depth']['Pr']) / 1000}")
            print(f"DC = {result['DC']}") 
            print("---------------------------------------------------------\n")      
#output as text file
# for i, floor in enumerate(results):
#     print("-----------------------------------------------")
#     print(f"Results for Floor {n_floors - i}")
#     for key, value in floor.items():
#         print(f"Load Combination: {key}")
#         print(f"({floor[key]['Stud'].Plys})-{floor[key]['Stud'].Name} @ {floor[key]['Spacing']}")
#         print(f"Pf = {round(floor[key]['Pf'],2)} kN Pr = {round(min(floor[key]['Pr']['Width']['Pr'], floor[key]['Pr']['Depth']['Pr'])/1000,2)} kN DC = {round(floor[key]['DC'],2)}")
#     print("-----------------------------------------------\n")

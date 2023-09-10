import matplotlib as mpl
import matplotlib.pyplot as plt
from pathlib import Path
import matplotlib.font_manager as fm
from matplotlib.colors import LinearSegmentedColormap
from mpl_toolkits.basemap import Basemap as Bp
import seaborn as sns
import numpy as np

global fontscale
fontscale = 0.8

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class fontsize:
    title = 30
    subtitle = 24
    label = 20
    clabel = 12
    sublabel = 12
    ticklabel = 16
    colorbarlabel = 18
    colorbarticklabel = 14
    legend = 16
    text = 16


theme = 'default'

def set_theme(theme_name):
    global theme
    theme = theme_name
    print(f'[HINT] Theme has been set to {theme}.')


# 色票(顏色選用優先級)
def colorlist(index):
    if type(index) == list:
        # 判斷是否所有元素都in
        if all(i in ['bg', 'bg1', 'bg2', 'fg', '1', '2', '3', '4', 'rfg'] for i in index):
            return [colorseries[i] for i in index]
        else:
            return index
    else:
        str(index)
        if index in ['bg', 'bg1', 'bg2', 'fg', '1', '2', '3', '4', 'rfg']:
            try:    
                if theme == 'default':
                    colorseries = {'bg': '#D9EEFD',
                                'bg1': '#D9EEFD',
                                'bg2': '#F7DCD1',
                                'rfg': '#F5F5F5',
                                'fg': '#111111',
                                '1': '#0A9CCF',
                                '2': '#AC005A',
                                '3': '#A19253',
                                '4': '#A43713'}
                    return colorseries[index]
                                
                elif theme == 'dark_background':
                    colorseries = {'bg': '#122D64',
                                'bg1': '#122D64',
                                'bg2': '#122D64',
                                'rfg': '#080808',
                                'fg': '#EEEEEE',
                                '1': '#0A9CCF',
                                '2': '#AC005A',
                                '3': '#A19253',
                                '4': '#A43713'}
                    return colorseries[index]
            except: # NameError: name 'theme' is not defined
                raise Exception(bcolors.WARNING+'Please run initplot() first.'+bcolors.ENDC)
                
        else:
            return index











# 獲取當前檔案位址
currentfilepath = __file__

# 刪去__file__中最後面自"\"開始的字串(刪除檔名)
motherpath = currentfilepath[:-len(currentfilepath.split('\\')[-1])]+'\\resources'
try: # assert if font files are in the directory
    assert Path(motherpath+"\\futura medium bt.ttf").is_file() and Path(motherpath+"\\Futura Heavy font.ttf").is_file() and Path(motherpath+"\\Futura Extra Black font.ttf").is_file(), f'[FATAL ERROR] Failed to find font files in {motherpath}.\nFailed to activate fontfiles clone.\nPlease install Futura fonts in the same directory as this file.\ninstall font-packages: https://dwl.freefontsfamily.com/download/futura/;\n Moving the font file to installed module folder{motherpath}.'
except:
    import os
    # go to motherpath
    motherpath = currentfilepath[:-len(currentfilepath.split('\\')[-1])]
    os.chdir(motherpath)
    # check if resources exists
    if os.path.exists(f'{motherpath}\\resources'):
        print(f'[HINT] Font files have been installed in {motherpath} already.')
    else:
    # clone github respository
        os.system(f'git clone https://github.com/VVVICTORZHOU/resources.git')
        print(f'[HINT] Try to clone github font respository into {motherpath}.')
        print(f'[HINT] Make sure the font files are in the directory:\n\t 1. {motherpath}\\resources\\futura medium bt.ttf\n\t 2. {motherpath}\\resources\\Futura Heavy font.ttf\n\t 3. {motherpath}\\resources\\Futura Extra Black font.ttf')
        print(f'\033[93m [HINT] If no, please install Futura fonts in the same directory as this file.\ninstall font-packages: https://dwl.freefontsfamily.com/download/futura/;\n Moving the font file to installed module folder: {motherpath}. \033[0m')
    try: # assert if font files are in the directory
        motherpath = currentfilepath[:-len(currentfilepath.split('\\')[-1])]+'\\resources'
        assert Path(motherpath+"\\futura medium bt.ttf").is_file() and Path(motherpath+"\\Futura Heavy font.ttf").is_file() and Path(motherpath+"\\Futura Extra Black font.ttf").is_file(), f'[FATAL ERROR] Failed to find font files in {motherpath}.\nFailed to activate fontfiles clone.\nPlease install Futura fonts in the same directory as this file.\ninstall font-packages: https://dwl.freefontsfamily.com/download/futura/;\n Moving the font file to installed module folder{motherpath}.'
    except:
        motherpath = currentfilepath[:-len(currentfilepath.split('\\')[-1])]+'\\resources'
        raise Exception(bcolors.FAIL+f'[FATAL ERROR] Failed to find font files in {motherpath}.\nFailed to activate fontfiles clone.\nPlease install Futura fonts in the same directory as this file.\ninstall font-packages: https://dwl.freefontsfamily.com/download/futura/;\n Moving the font file to installed module folder{motherpath}.'+bcolors.ENDC)

global fontpath, fontpath_bold, fontpath_black
fontpath = Path(mpl.get_data_path(), motherpath+"\\futura medium bt.ttf")
fontpath_bold = Path(mpl.get_data_path(), motherpath+"\Futura Heavy font.ttf")
fontpath_black = Path(mpl.get_data_path(), motherpath+"\Futura Extra Black font.ttf")


 

class SkewT_plot():
    def __init__(self, pressure, temperature, dewpoint, windspeed=False, winddirection=False, Uwind=False, Vwind=False, title='SKEW-T DIAGRAM', lefttitle=None, righttitle=None, xlabel='Temperature [°C]', ylabel='Pressure [hPa]'):
        '''
        This function is used to plot SkewT diagram.
        Input:
            pressure: pressure data [hPa]
            temperature: temperature data [degC]
            dewpoint: dewpoint data [degC]
            windspeed: windspeed data [m/s]
            winddirection: winddirection data [deg]
            Uwind: Uwind data [m/s]
            Vwind: Vwind data [m/s]
        Output:
            SkewT diagram
        '''

        from metpy.plots import SkewT
        from metpy.units import units
        import metpy.calc as mpcalc

        # Set up plot
        fig = plt.figure(figsize=(9, 9))
        skew = SkewT(fig, rotation=45)

        # set background color of skewT
        skew.ax.set_facecolor(colorlist('bg'))

        # set variables unit
        pressure = pressure *units('hPa')
        temperature = temperature *units('degC')
        dewpoint = dewpoint *units('degC')
        

        # Plot the data using normal plotting functions, in this case using
        # log scaling in Y, as dictated by the typical meteorological plot
        skew.plot(pressure, temperature, linewidth=2.5,color=colorlist('2'),label='Temperature')
        skew.plot(pressure, dewpoint, linewidth=2.5, color=colorlist('1'),label='Dewpoint')
        
        # create an axis for wind barbs and set its position at right side of the plot
        box = skew.ax.get_position()
        ax2 = fig.add_axes([box.x1*1.0515,box.y0*0.999,0,box.y0+box.height*0.835])
        ax2.set_xticks([])
        ax2.set_yticks([])
        

        # Add wind barbs, if winddirection and windspeed are provided, transform them to Uwind and Vwind, then plot
        if winddirection.all()!=False and windspeed.all()!=False:
            Uwind, Vwind = mpcalc.wind_components(windspeed*units('m/s'), winddirection*units('deg'))
            # plot wind barbs
            skew.plot_barbs(pressure, Uwind, Vwind, xloc=1.06)
        elif Uwind.all()!=False and Vwind.all()!=False:
            skew.plot_barbs(pressure, Uwind, Vwind, xloc=1.06)
        else: pass

        # Calculate LCL height and plot as black dot
        lcl_pressure, lcl_temperature = mpcalc.lcl(pressure[0], temperature[0], dewpoint[0])
        skew.plot(lcl_pressure, lcl_temperature, 'ko', markerfacecolor='black')

        # Calculate full parcel profile and add to plot as black line
        prof = mpcalc.parcel_profile(pressure, temperature[0], dewpoint[0]).to('degC')
        skew.plot(pressure, prof, colorlist('fg'), linewidth=2, label='Parcel Profile')

        # Shade areas of CAPE and CIN
        skew.shade_cin(pressure, temperature, prof, color=colorlist('3'), alpha=0.3, label='CIN')
        skew.shade_cape(pressure, temperature, prof, color=colorlist('4'), alpha=0.3, label='CAPE')

        # An example of a slanted line at constant T -- in this case the 0
        # isotherm
        #skew.ax.axvline(0, color='c', linestyle='--', linewidth=2)

        # Add the relevant special lines
        skew.plot_dry_adiabats()
        skew.plot_moist_adiabats()
        skew.plot_mixing_lines()

        # Add some keyvalue: CAPE[J/kg], CIN[J/kg], TLCL[degC], LCL[hPa], LFC[hPa], EL[hPa], PWAT[mm]
        CAPE, CIN = mpcalc.cape_cin(pressure, temperature, dewpoint, prof)
        CAPE = CAPE.magnitude
        CIN = CIN.magnitude
        TLCL = mpcalc.lcl(pressure[0], temperature[0], dewpoint[0])[1].magnitude
        LCL = mpcalc.lcl(pressure[0], temperature[0], dewpoint[0])[0].magnitude
        LFC = mpcalc.lfc(pressure, temperature, dewpoint)[0].magnitude
        EL = mpcalc.el(pressure, temperature, dewpoint)[0].magnitude
        PWAT = mpcalc.precipitable_water(pressure, dewpoint).magnitude
        labelcolor='fg'
        frameon=True
        framealpha=1
        facecolor='rfg'
        edgecolor='fg'
        edgewidth=2
        roundedge=False

        self.CAPE = CAPE
        self.CIN = CIN
        self.TLCL = TLCL
        self.LCL = LCL
        self.LFC = LFC
        self.EL = EL
        self.PWAT = PWAT



        skew.ax.text(0.02, 0.98, 'CAPE = {:.0f} [J/kg]\nCIN = {:.0f} [J/kg]\nTLCL = {:.0f} [°C]\nLCL = {:.0f} [hPa]\nLFC = {:.0f} [hPa]\nEL = {:.0f} [hPa]\nPWAT = {:.0f} [mm]'.format(CAPE, CIN, TLCL, LCL, LFC, EL, PWAT), transform=skew.ax.transAxes, fontsize=12, verticalalignment='top', bbox=dict(facecolor=colorlist(facecolor), edgecolor=colorlist(edgecolor), alpha=framealpha), fontproperties=fm.FontProperties(fname=fontpath, size=fontsize.text))

        LG = skew.ax.legend(loc='best', fontsize='x-large', labelcolor=colorlist(labelcolor), frameon=frameon, framealpha=framealpha, facecolor=colorlist(facecolor), edgecolor=colorlist(edgecolor),prop=fm.FontProperties(fname=fontpath, size=fontsize.legend))
        if roundedge == False:
            LG.get_frame().set_boxstyle('Round', pad=0.2, rounding_size=-0.01)
        LG.get_frame().set_linewidth(edgewidth)
        skew.ax.set_xlabel(xlabel, fontproperties=fm.FontProperties(fname=fontpath, size=fontsize.ticklabel))
        skew.ax.set_ylabel(ylabel, fontproperties=fm.FontProperties(fname=fontpath, size=fontsize.ticklabel))
        skew.ax.set_title(title, color=colorlist('fg'), fontproperties=fm.FontProperties(fname=fontpath, size=fontsize.title))
        if lefttitle != None:
            skew.ax.set_title(lefttitle, color=colorlist('1'), loc='left', fontproperties=fm.FontProperties(fname=fontpath_bold, size=fontsize.subtitle*0.7))
        if righttitle != None:
            skew.ax.set_title(righttitle, color=colorlist('2'), loc='right', fontproperties=fm.FontProperties(fname=fontpath_bold, size=fontsize.subtitle*0.7))

        skew.ax.spines['top'].set_visible(True)
        skew.ax.spines['right'].set_visible(True)
        skew.ax.spines['bottom'].set_visible(True)
        skew.ax.spines['left'].set_visible(True)
        skew.ax.spines['top'].set_linewidth(3)
        skew.ax.spines['right'].set_linewidth(3)
        skew.ax.spines['bottom'].set_linewidth(3)
        skew.ax.spines['left'].set_linewidth(3)
        skew.ax.tick_params(axis='both', which='major', width=3, length=5)
        skew.ax.tick_params(axis='both', which='minor', width=3, length=5)
        skew.ax.set_yticks(np.arange(1000, 99, -100),np.arange(1000, 99, -100), fontproperties=fm.FontProperties(fname=fontpath, size=fontsize.ticklabel))
        skew.ax.set_xticks(np.arange(-100, 51, 10),np.arange(-100, 51, 10), fontproperties=fm.FontProperties(fname=fontpath, size=fontsize.ticklabel))
        skew.ax.set_ylim(1000, 100)
        skew.ax.set_xlim(-40, 50)

    def __getitem__(self):
        return self
    
    def get_CAPE(self):
        return self.CAPE

    def get_CIN(self):
        return self.CIN
    
    def get_TLCL(self):
        return self.TLCL
    
    def get_LCL(self):
        return self.LCL
    
    def get_LFC(self):
        return self.LFC
    
    def get_EL(self):
        return self.EL
    
    def get_PWAT(self):
        return self.PWAT


class SurfaceAnalysis_plot():
    def __init__(self, lon, lat, data, title='Surface Analysis', lefttitle=None, righttitle=None, xlabel='Longitude', ylabel='Latitude', cmap='jet', vmin=None, vmax=None, cbarlabel='Surface Analysis', cbarlabelsize=fontsize.colorbarlabel, cbarlabelcolor='fg', cbarlabelweight='normal', cbarlabelrotation=0, cbarlabelpad=10, cbarlabelcolorbar=False, cbarlabelcolorbarlabel='[°C]', cbarlabelcolorbarlabelsize=fontsize.colorbarlabel, cbarlabelcolorbarlabelcolor='fg', cbarlabelcolorbarlabelweight='normal', cbarlabelcolorbarlabelrotation=0, cbarlabelcolorbarlabelpad=10, cbarlabelcolorbarlabelcolorbar=False, cbarlabelcolorbarlabelcolorbarlabel='[°C]', cbarlabelcolorbarlabelcolorbarlabelsize=fontsize.colorbarlabel, cbarlabelcolorbarlabelcolorbarlabelcolor='fg', cbarlabelcolorbarlabelcolorbarlabelweight='normal', cbarlabelcolorbarlabelcolorbarlabelrotation=0, cbarlabelcolorbarlabelcolorbarlabelpad=10, cbarlabelcolorbarlabelcolorbarlabelcolorbar=False, cbarlabelcolorbarlabelcolorbarlabelcolorbarlabel='[°C]', cbarlabelcolorbarlabelcolorbarlabelcolorbarlabelsize=fontsize.colorbarlabel, cbarlabelcolorbarlabelcolorbarlabelcolorbarlabelcolor='fg', cbarlabelcolorbarlabelcolorbarlabelcolorbarlabelweight='normal', cbarlabelcolorbarlabelcolorbarlabelcolorbarlabelrotation=0, cbarlabelcolorbarlabelcolorbarlabelcolorbarlabelpad=10):
        '''
        This function is used to plot Surface Analysis.
        Input:
            lon: longitude data [deg]
            lat: latitude data [deg]
            data: data to be plotted
        Output:
            Surface Analysis
        '''
        from metpy.plots import (
            ColdFront, WarmFront, ScallopedStroke, ColdFrontogenesis, WarmFrontogenesis, StationPlot, ColdFrontolysis, WarmFrontolysis, OccludedFront, OccludedFrontolysis, OccludedFrontogenesis, RidgeAxis, Squall, StationaryFront, StationaryFrontogenesis, StationaryFrontolysis
            )
        import cartopy.crs as ccrs
        import cartopy.feature as cfeature

        pass

    def __getitem__(self):
        return self
# SuperCap Aging Assistant Documentation

***Installer for current build can be found in the "Releases" tab to the right -->***
<br/>

## *File Requirements*
 
- **Aging Data**: .csv file generated from Landt Instruments V7.4 software[^1], columns for test time (units: seconds), voltage (units: volts), current (units: microamps), cycle number,
  and status (expected: CCD, CCC, and CVC)
- **Cyclic Voltammograms**: .txt files generated from BioLogic's EC-Lab software[^2], columns for time (units: seconds), voltage (units: volts), current (units: milliamps), and cycle number
- **Electrochemical Impedance Spectra**: .txt files generated from BioLogic's EC-Lab software, columns for frequency (units: hertz), real impedance (Re(Z), units: ohms), and imaginary
  impedance (-Im(Z), units: ohms)  

*Demo files for the current build are included for reference in the application's home directory that was created by the installer* 
<br/>
<br/>

## *Accelerated Aging of Supercapacitor Electrodes*

This application automates the processing and visualiation of data generated during acclerated electrochemical aging experiments performed on supercapacitors.[^3] A general aging experiment
proceeds as follows: (1) Pre-aging electrochemical characterization using cyclic voltammetry (CV) and electrochemical impedance spectroscopy (EIS), (2) An extended aging procedure of repeated "aging cycles" consisting of galvanostatic cycling and constant voltage floating (example in image below), and (3) Post-aging electrochemical characterization again using CV and EIS.
  
*Note: It is not required to fill in all of the file import fields, feel free to pick and choose the sections that are applicable for you.*
  
<img ref here>
Example of an electrochemical "aging cycle".[^4]
<br/>
<br/>

## *Calculations Performed*

The primary calculations performed by the application are the following:
  
Aging Data:
- Capacitance Fade:  
For every aging cycle, linear fitting is performed for both the charge and discharge branches of the galvanostatic cycle defined by the user (default is the sixth cycle). The slope of the fit line is used to determine capacitance (in F/g) according to the following equation:
<p align=center>Capacitance (F/g) = (<i>2 * i</i>) / (<i>slope * mass</i>) (<i>eq.</i> 1)</p>

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;where, *i* is the applied current and mass is the electrode mass.  

- IR Drop Increase:  
For every aging cycle, the IR drop is recorded for the galvanostatic cycle defined by the user (default is the sixth cycle). The IR drop (in ohm*cm^2) is calculated from the difference between the last point of with the following equation:
<p align=center>IR Drop (ohm * cm^2) = (<i>V<sub>C</sub> - V<sub>D</sub></i>) / (<i>i * area</i>) (<i>eq.</i> 2)</p>

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;where, *V<sub>C</sub>* is the last voltage value recorded during the charge branch of the cycle, *V<sub>D</sub>* is the first voltage value recorded during the 
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;discharge branch of the cycle, *i* is the applied current, and area is the electrode area.

- Q<sub>*irr*</sub>:  
The irrversible charge loss (Q<sub>*irr*</sub>) for each aging cycle is calculated by first taking the cumulative integral of the current versus time across the whole aging experiment then averaging the charge for the galvanostatic cycle defined by the user (default is the sixth cycle).
<br/>
<br/>

## *References and External Links*

[^1]: [Landt Instruments Battery Testing Software](https://www.landtinst.com/download/)
[^2]: [BioLogic EC-Lab](https://www.biologic.net/support-software/ec-lab-software/)
[^3]: [Understanding of carbon-based supercapacitors ageing mechanisms by electrochemical and analytical methods](https://www.sciencedirect.com/science/article/pii/S0378775317311370)
[^4]: [Supplementary Information from ref. 3](https://www.sciencedirect.com/science/article/pii/S0378775317311370)

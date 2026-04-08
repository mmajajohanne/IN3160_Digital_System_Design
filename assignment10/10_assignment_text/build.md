# Build and program the processor system using Vitis

Now that the hardware platform is exported, we can import this into the Vitis integrated development environment (Vitis).
This will allow us to program the Zynq processor and use its AXI peripherals which we in turn has connected to our PWM or PDM system. 

> [!NOTE]
> When communicating with the ARM processor core (Zynq processor), the USB "UART" is used, in addition to the USB "PROG" which still is used to program the FPGA.
>
> Check that both USB plugs are attached to the board.
> _Do not wiggle them if they are connected_, they are fragile.

* Open Vitis   

`vitis &`

When Vitis launces, you will have to select a workspace for your project builds. 
We reccomend using the top folder for this assignment, or any dedicated subfolder if you have decided on creating that. 

* Click _Open Workspace_ 
* Select your assignment folder

This will be your workspace for the rest of this assignment. 

The next step is to select what type of Development you will do. 
Before creating and running any application, we need to build a platform that can be used in Vitis. 
To create the project platform you will use the exported hardware platform created in Vivado. 

## Platform Component
* Select _Create Platform component_[^1].

[^1]: From vitis component tab, Embedded Development or System Development or File->New Component->Platform. 

### Name and Location
This opens the Create platform component wizard. 
* Change the Component name to ´GPIO_platform´.
* Leave the location unchanged
  
The component will then be created in the folder _workspace/GPIO_platform_.

* Click _Next_

### Flow
In the Flow part, you will have to browse to the exported hardware from Vivado. 

Leave the Hardware Design selected (Default).  

* Click _Browse_ for Hardware Design (XSA)
  * Navigate to O10-platform
  * Select O10_block_design_wrapper.xsa
  * Click _Open_

The other Flow options can be left unchanged. 
* Click _Next_

### OS and Processor
Here the Operating system is by default standalone and ps7_cortexa9_0 selected, along with "Generate boot artifacts".

> [!Note]
> You can note that there are two processor options, because the Zynq FPGA has two arm cores.
> For this project, We will only use the default ps7_cortexa9_0 

* Leave this part unchanged and click _Next_.
 
### Summary
Read the summary and check that it seems correct. 
* Click _Finish_

Now Vitis will work for 5-30 seconds to create the files needed to build the platform. 

* In the Flow pane, click _Build_

> [!Note]
> The Build icon may suggest that it is working (spinning circle) before it has started.
> If you click on it once and the Build Hammer icon occurs, click _Build_ again. 

When building the console output will report the progress in building. 

* Click File-> _Save All_ to ensure everything is saved after completion. 

Before creating the application, you can browse the files in the platform. 
* In the Vitis components tab, expand the GPIO platform
  * Expand further Output->hw->sdt
  * Click on the _O10_block_design_wrapper_

In the Right hand window you can now see the Hardware Platform Specification and the Address Map for the processor. 
Here you can see that your AXI_GPIO_0 module has reserved a base address and a high address and an S_AXI slave interface. 

Using this information you can check that you may access to the peripherals we have added. 
You can also check the addresses if there was trouble generating the correct header files in the application. 

If this seems correct we can proceed to the next step, creating the application. 


## Embedded Application

In Vitis, select your assignment workspace (if not already chosen). 
* click File-> New Component -> _Application_

This opens a Create Application Component Wizard:

### Name and location
* Change the component name to `PID_component`

The location can be unchanged, so the component will be put in the _workspace/PID_component_ folder.
* Click _Next_

### Hardware
* Select the _GPIO_Platform_

To select this, the GPIO platform has to be built correctly in the previous step. 
  
* Click _Next_

### Domain
The domain should be the standalone_ps7_cortexa9_0. 
Normally this is selected already. 
* Click _Next_

### Summary
* Read the summary and check that the information seems correct.
* Click _Finish_ 

In a few seconds, you may now start working on the software component.

* In the Vitis Components tab, Collapse the GPIO platform (if expanded)
* Expand the PID component
  * Further expland the Sources
  * _Right click on the src folder_
  * Import->Files...
  * Navigate to your project source folder
  * Select the `GPIO PID control.c` file
  * Click _Open_
 
* In the Flow tab, click _Build_

> [!NOTE]
> Before building, if browsed to the source .c file, errors will be displayed, such as `xgpio.h` not found.
> This seems to be a result of the build and compile order, so building the project should still work.
>
> _Saving all_ should clear the errors displayed; if the build completes. 

Check the console if the _build finished successfully_. 

* Click File-> _Save All_

If the build has completed successfully you can now run the application. 
Since the application uses serial communication you will need to open the _serial monitor_ in Vitis, or start _screen_ from a linux terminal.  

### Serial monitoring

* To enable the Vitis serial monitor, follow this guide: 
  [Cookbook: Serial Monitor in Vitis](https://github.uio.no/in3160/cookbook/wiki/7-Vitis#using-the-serial-monitor)

* Screen can be started from a linux terminal: ```screen /dev/ttyACM0 115200```

In both cases, 115200 baud is used for communication with the Zynq processor. 

## Running the finished application

Once serial monotoring is set up...
* In Vitis, Flow tab, PID_component, click _run_

If everything is set up correctly, messages will show how well the motor runs with the PID settings applied. 

> [!NOTE]
> The motor will perform differently depending on board, PWM frequency (FPGA) and PID settings (C program).
> It is expected that duty cycles below 50% may not be enough to drive the motor at all.
> 
> Lower PWM frequencies (~100-400 Hz) will drive the motor better on low duty cycles than high base frequencies. 
> 
> When the full PID is applied any frequency within the range of 100Hz to 6kHz should be able to drive the motor at all setpoints.  

> [!IMPORTANT]
> Demonstrate your system running to the lab supervisors.  

##  Extra (optional):
### Experiment with the PID values
* Add or change some runs at the end of the test, using your own PID values.
  * more iterations can be added to make the run longer (useful when experimenting) 

* What PID values works best with your setup? 
* Which PWM base frequency did you use? (or minimum PDM pulse length)?

### Using switches as input to the Zynq processor
> [!WARNING]
> This part implies rebuilding the FPGA fabric, and all the steps that follows.
>
> To avoid getting stranded with a project that does not run,
> it may be wise to create a new/duplicate the workspace, or demonstrate your system to a lab supervisor before making changes.  

* Modify the block design to be able to read (SW 0-7).
  * This can be done adding another AXI_GPIO module that connects to the switches.
* Modify the C code to run the PID routine continuously after the initial direction test, using the switches as velocity setpoint.
  (The direction test must be performed first).
  The setpoint should be between -40 and +40 using the eight switches (SW0-7) on the Zedboard.

[Back](./readme.md)

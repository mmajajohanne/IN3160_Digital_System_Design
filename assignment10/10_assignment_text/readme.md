# System on Chip integration - Combining a software PID controller with PWM in FPGA fabric
IN3160/4160
Version 2025-1

## Overview ##
> [!NOTE]
> Read all the task documents before starting the task.

### Task documents ###
* [Introduction](intro.md)
* [PID-control](theory.md)
* [VHDL modifications](vhdl.md)
* [IP creation](IP_creation.md)
* [Block design](blockdesign.md)
* [Build and run](build.md)

### External sources ###
This task was partly built using the AMD/ Xilinx tutorials on Vivado and Vitis. 
These tutorials can be good help if you are stuck or wonder why certain steps were used. 
The general links to these tutorials are 
[2023.1 Zynq-7000 Embedded Design tutorials](https://xilinx.github.io/Embedded-Design-Tutorials/docs/2023.1/build/html/docs/Introduction/Zynq7000-EDT/Zynq7000-EDT.html) 
and
[Vitis Tutorials](https://github.com/Xilinx/Vitis-Tutorials). 

The main relevant parts are described in these parts:  
* [Getting started with Zynq7000](https://xilinx.github.io/Embedded-Design-Tutorials/docs/2023.1/build/html/docs/Introduction/Zynq7000-EDT/1-introduction.html)
* [Using the Zynq SoC Processing System](https://xilinx.github.io/Embedded-Design-Tutorials/docs/2023.1/build/html/docs/Introduction/Zynq7000-EDT/2-using-zynq.html)
* [Using the GP Port in Zynq Devices](https://xilinx.github.io/Embedded-Design-Tutorials/docs/2023.1/build/html/docs/Introduction/Zynq7000-EDT/5-using-gp-port-zynq.html)
* [Vitis 2024.1 Embedded Software Tutorial](https://github.com/Xilinx/Vitis-Tutorials/tree/2024.1/Embedded_Software/Getting_Started)

If building the system fails, try read up in these tutorials. 
> [!NOTE]
> In case of version conflicts, note that a list of different releases is listed in the bottom of the tutorials main menu.

## Approval

> [!IMPORTANT]
> **All systems shall be demonstrated for a lab supervisor.**
> The system shall run and demonstrate that
> * Serial communication with the Zynq processor works (required to verify the next step)
> * The motor can run correctly using the PID control.

> [!CAUTION]
> **Prepare well ahead of the due date**
> 
> Everyone can not expect to use the last lab hour before deadline to demonstrate the task.
> If you cannot finish earlier, you will have to negotiate an appointment to demonstrate your system before the deadline runs out[^1].
>
> _The lab supervisors are generally not at work outside lab hours._ 
> It is OK to send email requests before the last lab session, not later[^2].
>
> **Lab supervisors _may_ accept video delivery in cases where it is difficult or impossible to find a reasonable time for appointment.**
> * The video must then verify
>    * that you are running your module (from programming in Vitis)
>    * that the PID system works
>    * that serial data is transferred to the PC during operation
>
> **Video delivery is an exception.**
> 
> Care must be made to avoid excess storage.
> (Canvas has upper limits on this, so this cannot be used broadly).
> 10 FPS is fine, but on-screen text must be readable. 

[^1]: The time for demonstrating can be as specified by the lab supervisor, as long as the appointment is approved by the lab supervisor within the deadline.
[^2]: Normal ifi guidelines for permissions, such as sick leave, still applies.   

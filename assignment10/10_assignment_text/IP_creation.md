## 1: Create your ‘IP’ that can be connected to other IPs ##
To enable the use of your module together with other IPs (Intellectual Property – here other pre-made modules and the Zynq processor) in Vivado, you will make IP-package for your project. 
Read the introduction to understand what goes in your IP (the FPGA system).

* Create or modify your top layer to enable connections to the AXI_GPIO IPs ([VHDL modifications section](./vhdl.md)). 

When Vivado creates a package it will essentially create an database file (.xml) with description of information Xilinx uses when connecting IPs. 
It may also generate a wrapper HDL entity, to ensure names are understood by the tool used later. 

> [!NOTE]
> For this part it is useful to note that vivado will make a copy of your source files, wherever they are sourced from.
> This means that editing them later means they will require to replace the files copied into the project.
> Alternatively when editing in Vivado, your source origin will remain untouched.  

Follow these steps to **create an IP from your project** (Oblig 8) files, using your new top layer:
* Create a new folder or folder structure for this assignment.
   * Make a subfolder for all your sources vhdl and the c application from the task [src](./src/) folder.
      * _The tools will create a number of new folders and files, so try avoid mixing them with _your_ src folder_.    
* Create a new project in vivado called “oblig10_IP”, using your updated top module.
   * Project type
      * _Default settings is OK_ (RTL-project, no boxes checked)
   * Add sources
      * _Include all the VHDL modules you will use_. 
      * Target language and Simulator language can be VHDL (mixed may work too)
   * _Skip adding constraints_.
   * Default part
      * Select Boards-> _Zedboard Zynq Evaluation and Development Kit 1.4 avnet.com Board rev d_  (Refresh/Download if required)
   * Project summary
      * _Finish_ (Check that it seems right, no actions required)
   * Project manager
     * Manually change all the source files to VHDL 2008
       * Once all has been changed, there should be no more syntax errors in the Design sources.
          * You _may_ get no errors before making the change, but each file must be set individually to ensure no errors showing up later. 
   * Make sure no constraints are listed (_Pins should not be bound at this stage_). 
*	_Run synthesis_
*	Select _Open Synthesized Design_ when synthesis is complete.
*	Verify that synthesis has completed without critical warnings or errors
   *	If there are critical warnings or errors, correct them before continuing. 
*	From the “Tools” menu select “Create and package New IP”
   *	Next
   *	Select _Package your current project_
      * This may result in a "Create Directory error"	since default is one step above your UIO-user folder. 
   * Select a location for your IP
      *	the Oblig10_IP folder can be used in this context[^1].
   *	Next/Finish
     
[^1]: In a company, you would probably have a specific library location to put the IPs created, but this is a one-time only use, so the Vivado project folder is fine. 

> [!NOTE]
> The packager will give critical warning:
> "[IP_Flow 19-5655] Packaging a component with a VHDL-2008 top file is not fully supported. Please refer to UG1118 'Creating and Packaging Custom IP'.
>
> However, as we are not re-synthesizing the design, these warnings can be ignored at this point.
> 
> This also means that from this point, we should not make changes in our VHDL code without starting over from the top.

* _Make sure there are no other critical warnings_, and press OK.   
*	Review the “Package IP” tab, 
   *	Check that the names make sense for your IP.
      Vivado will create names according to the VHDL entity name, so it should be recognizable.
    	Consider if that name is a good one if you were about to re-use this design in a different setting and make changes if that makes sense to you.
   *	Browse through the _Packaging steps_ from _Identification_ to _Customization GUI_. No changes should be required.
   *	Click **Review and Package** then _Package IP_ 
   *	Click “OK” when Finished packaging your IP
*	Close the project to avoid making changes that would induce re-synthesizing of the package. (File -> Close project…)

At this point, the IP should be ready to fetch and use in a block-design, which is the [next step](./blockdesign.md). 

[Back](./readme.md)

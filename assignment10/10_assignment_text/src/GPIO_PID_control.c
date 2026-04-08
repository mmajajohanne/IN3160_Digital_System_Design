/*
 * GPIO PID control for Vitis 2024.1 by Yngve Hafting, UIO
 *
 * PS7 UART (Zynq) is not initialized by this application, since
 * bootrom/bsp configures it to baud rate 115200
 *
 * Changes since 2019 version:
 * xil_printf.h changed to using only stdio.h 
 * ie xil_printf("..") changed to printf("")
 * platform.h and platform.c from hello_world example removed along with
 * init_platform();    // which does nothing with default of 115200 baud.
 * cleanup_platform(); // which does nothing with default of 115200 baud.
 *
 * This version uses delays (sleep) rather than interrups for timing the control loop. 
 * Using delays is not reccomended for control loops due to inaccurate timing. 
 * However, for the DC motor setup in IN3160/4160, these inaccuracies are small and negligible.  
 * 
 */

#include <stdio.h>        // for Zynq to PC communication using printf. 
#include <xgpio.h>        // Axi GPIO library (Zynq to FPGA fabric communication)
#include <xparameters.h>  // Addresses for GPIO and other peripherals
#include "sleep.h"        // Sleep timer library
#include <stdbool.h>      // Allow for bool (=> better readability)

#define OUT_PORT 1     // must correspond to the AXI-GPIO configuration in vivado
#define IN_PORT 2      // must correspond to the AXI-GPIO configuration in vivado
#define GPIO_MASK 0xFF // corresponds to the number of useful bits (8) for both directions in the AXI-GPIO 
#define MY_GPIO_ID XPAR_AXI_GPIO_0_BASEADDR  // GPIO port 0 base address from xparameters.h
#define VELOCITY_TO_SETPOINT_SCALE 320       // 1024*40/128 (40 is assumed speed at 100% duty cycle, +-128 is +-100%).
#define MS 1000        // one ms in microseconds (uS)
#define SEC 1000*MS    // one sec in uS

// AXI_GPIO setup
XGpio myGPIOport;       //Our bidirectional AXI-GPIO port reference
XGpio_Config *cfg_ptr;  //Pointer used for configuring GPIO

// Identify motor direction to adjust for motor -output and/or
// -readout having and arbitrary direction. See findDirection()
bool reverseDirection = false;  // Motor direction setting  

//PID variables will be maintained by myPid()
int currentError  = 0;
int previousError = 0;
int sumError      = 0;
int deltaError    = 0;

// read velocity from GPIO-port
int readVelocity(bool reverse){
    int velocity;
    velocity = XGpio_DiscreteRead(&myGPIOport, IN_PORT);  // read velocity
    if (velocity > 128) velocity = velocity -256; // correct for negative values
    if (reverse) return -velocity; // correct for reverse operation.
    return velocity;
}

// print velocity to UART (usually /dev/ttyACM0)
void printVelocity(){
    int velocity=0;
    velocity = readVelocity(reverseDirection);
    printf("Velocity = %d rotations per 10s \n\r", velocity);
}

// myPID calculates an 8 bit signed setpoint value [-128 to +127] for pulse width modulation
// Setpoint should be in the range of -40 to +40
int myPID(int mySetPoint, int myKp, int myKi, int myKd){
    int velocity;
    int P, I, D;  // Constants should be in the range of +-2*VELOCITY_TO_SETPOINT_SCALE
    int PID;
    // error calculations, all scaled up by SETPOINT_SCALE
    previousError = currentError;
    velocity = readVelocity(reverseDirection);
    currentError = mySetPoint - velocity;
    sumError = sumError + currentError;
    deltaError = currentError - previousError;

    // Calculate P,I,D
    P = myKp*currentError;
    I = myKi*sumError;
    D = myKd*deltaError;
    PID = (P+I+D)/VELOCITY_TO_SETPOINT_SCALE;

    // truncate to legal values
    if (PID > 127) {
        printf("PID Value > 127:  %d, P: %d, I: %d D: %d \n\r", PID, P, I, D);
        PID = 127;
    }
    if (PID < -128) {
        printf("PID Value < -128:  %d  P: %d, I: %d D: %d \n\r", PID, P, I, D);
        PID = -128;
    }
    return PID;
}

// set the setpoint using the GPIO port
void setGPIO(int mySetPoint){
    u32 maskedSetPoint = mySetPoint;
    maskedSetPoint &= GPIO_MASK;
    XGpio_DiscreteWrite(&myGPIOport, OUT_PORT, maskedSetPoint);
    usleep(50*MS); // 50 ms delay
}

void stopMotor(){
    setGPIO(0); // order a stop
    usleep(300*MS); // 300 ms delay
}

// Run PID loop 
void runPID(int setPoint, int P, int I, int D, int iterations){
    int it=0;
    int set = setPoint;
    printf("setpoint:  %d, P: %d, I: %d D: %d   \n\r", set, P, I, D);
    while(it < iterations){
        setGPIO(myPID(set,P, I, D));
        it++;
        if (it%20 == 0) printVelocity(); // display velocity some times
    }
    stopMotor();
    readVelocity(reverseDirection);
}

// Set the pulse width value directly and check direction
bool runDirect(int pulseWidth, int iterations){
    int it = 0;
    bool reverse = false;
    printf("pulse width value:  %d, range [-128,128> \n\r", pulseWidth);
    while (it< iterations){
        setGPIO(pulseWidth);
        it++;
        if (it%20 == 0) printVelocity(); // display velocity some times
        // check for reverse operation at 30 iterations
        if (it == 30){
            if (readVelocity(false) > 0){
                if (pulseWidth < 0) reverse = true;
            } else {
                if (pulseWidth > 0) reverse = true;
            }
        }
    }
    stopMotor();
    readVelocity(false);
    return reverse;
}

// Find which way the motor runs compared to speed readout
void findDirection(){
    print("*** 100% duty cycle (full power) *** \n\r");
    reverseDirection = runDirect(127, 100); // 100 iterations of 50 us

    if (reverseDirection){
    	print ("Reversed operation detected \n\r");
    	print ("Speed readout will be reversed \n\r");
    } else {
    	print ("Forward operation detected\n\r");
    }
    print(" \n\r");
	print("IF the motor has not engaged yet, please revise the system setup...\n\r");
	print(" \n\r");
}

int main(){
    print("Serial communication established...\n\r");

    // 2025 Initialize communication from Zynq to AXI-GPIO 
    cfg_ptr = XGpio_LookupConfig(MY_GPIO_ID);
    XGpio_CfgInitialize(&myGPIOport, cfg_ptr, cfg_ptr->BaseAddress);
    print("GPIO ports configured...\n\r");

    // Launch the show..!
    print(" \n\r");
    print("********************* \n\r");
    print("* PWM and PID test  * \n\r");
    print("********************* \n\r");
    print("*  max speed = 40   * \n\r");
    print("* rounds per 10s at * \n\r");
    print("*  100% duty cycle  * \n\r");
    print("********************* \n\r");
    print(" \n\r");

    print("STEP0: Deciding direction... \n\r");
    print(" \n\r");
    findDirection();
    print(" \n\r");
    usleep(SEC*1);

    print("STEP1: PWM set directly\n\r");
    print(" \n\r");
    print("*** 50% duty cycle (1/2 power) *** \n\r");
    runDirect(64, 100); // 100 iterations (each 50 us)

    print(" \n\r");
    print("*** 12,5% duty cycle (1/8 power) ***\n\r");
    runDirect(16, 100); // 128/8 = 16

    print(" \n\r");
    print("*** 3% duty cycle (1/32 power) ***\n\r");
    runDirect(4, 100);

    print(" \n\r");
    print("--- PWM test finished ---  \n\r");
    usleep(SEC*1);

    print(" \n\r");
    print(" \n\r");
    print("STEP2: Speed constant, testing PID parameters... \n\r");
    print(" \n\r");
    print("*** 50% speed, only P   *** \n\r");
    print("*** setpoint = 20 r/10s ***\n\r");
    runPID(20, 800, 0, 0, 100);

    print(" \n\r");
    print(" \n\r");
    usleep(SEC*1);

    print("*** 50% speed, P + I    ***\n\r");
    print("*** setpoint = 20 r/10s ***\n\r");
    runPID(20, 800, 50, 0, 100);

    print(" \n\r");
    print(" \n\r");
    usleep(SEC*1);

    print("*** 50% speed, P I D    ***\n\r");
    print("*** setpoint = 20 r/10s ***\n\r");
    runPID(20, 800, 50, 130, 100); // Half speed, P+I+D

    print(" \n\r");
    print(" \n\r");
    usleep(SEC*1);

    print("STEP3: PID testing PID at different speed\n\r");
    print(" \n\r");
    print("*** 12,5% speed, P I D ***\n\r");
    print("*** setpoint = 5 r/10s ***\n\r");
    runPID(5, 800, 50, 130, 100); // 1/8 of max speed , PID

    print(" \n\r");
    print("*** -75% speed, P I D                    ***\n\r");
    print("*** setpoint = -30 rounds per 10 seconds ***\n\r");
    runPID(-30, 800, 50, 130, 100);

    print(" \n\r");
    print("*** -5% speed, P I D                    ***\n\r");
    print("*** setpoint = -2 rounds per 10 seconds ***\n\r");
    runPID(-2, 800, 50, 130, 100);

    print(" \n\r");
    print("***              FINISHED              ***\n\r");
    print("***      If you are using screen,      ***\n\r");
    print("*** press Ctrl-A then k then y to quit ***\n\r");
    print("***                 --                 ***\n\r");
    print("***  press Ctrl-A then ESC to enable   ***\n\r");
    print("***     scrolling using arrow keys     ***\n\r");
    print(" \n\r");
    return 0;
}

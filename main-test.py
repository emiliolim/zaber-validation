from zaber_cli import ZaberCLI
from zaber_motion import Units
from pathlib import Path
from datetime import datetime
from time import sleep
from futek_cli import FUTEKDeviceCLI
import xlsxwriter
import numpy as np


"""
Performs a test to validate the Zaber stage making sure of the following criteria:
 -  Pressure from downward moving loadcell is evenly distributed between the 
    2 loadcells reading from the bottom of the stage 
 -  Graph of each load cell should be a step wise function where each step is
    1/2 Newtons force difference
 -  Entire test stops when 20 Newtons is read from atleast 1 loadcell (prevent overload)

Outputs:
 -  Excel files for force over time of all 3 loadcells (time should be synched) 
"""

####################
# TESTING PARAMETERS
####################
SPEED = 1 # mm/s
STEP_SIZE_NEWTONS = 1
STEP_SIZE_MS = 5000
UPPER_LIMIT_NEWTONS = 32
SAVE_PATH = "./data/"

TEST_MODE = 0

####################
# TEST FUNCTION
####################
def test():
   """
   Test the zaber stage to move downwards and stop when it reads 20 from an array
   """
   # Initialize futek connection
   if TEST_MODE:
      dataA = np.linspace(0, 40, 140)
      dataB = np.linspace(0, 40, 120)
      dataC = np.linspace(0, 40, 160)
   else:
      print("Running real test")
      futek = FUTEKDeviceCLI()
      load_cell_a_serial = futek.SerialNumber_A
      load_cell_b_serial = futek.SerialNumber_B if futek.SerialNumber_B else "N/A"
      load_cell_c_serial = futek.SerialNumber_C if futek.SerialNumber_C else "N/A"
      

   # Initialize zaber connection
   zaber = ZaberCLI()
   connection = zaber.connect(comport="COM4")
   if connection == 0: # this should be handled in the CLI in the future
      print("Cannot Connect to Zaber comport")
      return 
   
   if zaber.axis.is_parked():
      zaber.axis.unpark()
   currentPosition = zaber.axis.get_position()
   # Extract = 10
   # zaber.axis.move_relative((Extract), Units.LENGTH_MILLIMETRES)
   # Initial variables
   readings_arrA = [0] * 18000
   readings_arrB = [0] * 18000
   readings_arrC = [0] * 18000
   init_time = datetime.now()
   init_seconds = init_time.second + init_time.microsecond / 1e6
   init_flag = True # Flag for the first iteration of the loop
   init_val_A = 0 # initial value for pressure
   init_val_B = 0
   init_val_C = 0
   force_idx = 0
   last_step_force = 0

   user = input("Type anything to begin or -1 to leave: ")
   if user == "-1":
      print("Exiting Early")
      return
   
   file_name = input("Enter file name for this run: ")
   if file_name == "":
      file_name = "Run"

   # Check if load cells are flipped and adjust polarity accordingly
   query_A = input(f"Is Load Cell {load_cell_a_serial} flipped? (y/n): ")
   if query_A.lower() == "y":
      pol_A = -1
   else:
      pol_A = 1
   query_B = input(f"Is Load Cell {load_cell_b_serial} flipped? (y/n): ")
   if query_B.lower() == "y":
      pol_B = -1
   else:
      pol_B = 1
   query_C = input(f"Is Load Cell {load_cell_c_serial} flipped? (y/n): ")
   if query_C.lower() == "y":
      pol_C = -1
   else:
      pol_C = 1

   print("Beginning Validation Test: Moving loadcell downwards")
   zaber.axis.move_velocity(SPEED*0.1, Units.VELOCITY_MILLIMETRES_PER_SECOND)
   while True:
      if TEST_MODE:
         sleep(1)
         reading_A = dataA[force_idx]
         reading_B = dataB[force_idx]
         reading_C = dataC[force_idx]
      else:
         reading_A = futek.getNormalData_A() # Read force value
         reading_A = reading_A * (4.44822 * pol_A) # convert pounds to Newtons and change polarity
         reading_B = futek.getNormalData_B() # Read force value
         reading_B = reading_B * (4.44822 * pol_B) # convert pounds to Newtons and change polarity
         #reading_C = 0 # placeholder for top loadcell reading since we don't have a 3rd loadcell yet
         reading_C = futek.getNormalData_C() # Read force value
         reading_C = reading_C * (4.44822 * pol_C) # convert pounds to Newtons and change polarity

      if init_flag:
         init_val_A = reading_A
         init_val_B = reading_B
         init_val_C = reading_C
         init_flag = False

      # Log the residual of current - initial force
      stage_force_A = reading_A - init_val_A
      stage_force_B = reading_B - init_val_B
      stage_force_C = reading_C - init_val_C

      readings_arrA[force_idx] = stage_force_A
      readings_arrB[force_idx] = stage_force_B
      readings_arrC[force_idx] = stage_force_C
      force_idx = force_idx + 1
      print("Force Value for LC A: " + str(stage_force_A))

      # Pause at each step increment
      current_step = int(stage_force_A / STEP_SIZE_NEWTONS)
      if current_step > last_step_force:
         zaber.axis.stop()
         pause_start = datetime.now()
         while (datetime.now() - pause_start).total_seconds() * 1000 < STEP_SIZE_MS:
            if TEST_MODE:
               sleep(0.1)
               reading_A = dataA[force_idx] if force_idx < len(dataA) else dataA[-1]
               reading_B = dataB[force_idx] if force_idx < len(dataB) else dataB[-1]
               reading_C = dataC[force_idx] if force_idx < len(dataC) else dataC[-1]
            else:
               reading_A = futek.getNormalData_A() # Read force value
               reading_A = reading_A * (4.44822 * pol_A) # convert pounds to Newtons and change polarity
               reading_B = futek.getNormalData_B() # Read force value
               reading_B = reading_B * (4.44822 * pol_B) # convert pounds to Newtons and change polarity
               #reading_C = 0 # placeholder for top loadcell reading since we don't have a 3rd loadcell yet
               reading_C = futek.getNormalData_C() # Read force value
               reading_C = reading_C * (4.44822 * pol_C) # convert pounds to Newtons and change polarity
               
            stage_force_A = reading_A - init_val_A
            stage_force_B = reading_B - init_val_B
            stage_force_C = reading_C - init_val_C
            readings_arrA[force_idx] = stage_force_A
            readings_arrB[force_idx] = stage_force_B
            readings_arrC[force_idx] = stage_force_C
            force_idx = force_idx + 1
         zaber.axis.move_velocity(SPEED*0.1, Units.VELOCITY_MILLIMETRES_PER_SECOND)
         last_step_force = current_step

      # Once sample is hit, stop the axis
      if stage_force_A >= UPPER_LIMIT_NEWTONS or stage_force_B >= UPPER_LIMIT_NEWTONS or stage_force_C >= UPPER_LIMIT_NEWTONS:
         zaber.axis.stop()
         break
   
   print("Newton Limit Reached: Moving loadcell back up")
   zaber.axis.move_velocity(-SPEED*2, Units.VELOCITY_MILLIMETRES_PER_SECOND)
   while True:
      if TEST_MODE:
         reading_A = 0
         reading_B = 0
         reading_C = 0
      else:
         reading_A = futek.getNormalData_A() # Read force value
         reading_A = reading_A * (4.44822 * pol_A) # convert pounds to Newtons and change polarity
         reading_B = futek.getNormalData_B() # Read force value
         reading_B = reading_B * (4.44822 * pol_B) # convert pounds to Newtons and change polarity
         #reading_C = 0 # placeholder for top loadcell reading since we don't have a 3rd loadcell yet
         reading_C = futek.getNormalData_C() # Read force value
         reading_C = reading_C * (4.44822 * pol_C) # convert pounds to Newtons and change polarity

      # Log the residual of current - initial force
      stage_force_A = reading_A - init_val_A
      stage_force_B = reading_B - init_val_B
      stage_force_C = reading_C - init_val_C

      readings_arrA[force_idx] = stage_force_A
      readings_arrB[force_idx] = stage_force_B
      readings_arrC[force_idx] = stage_force_C
      force_idx = force_idx + 1
      # print("Force Value: " + str(stage_force))

      # Grab current position
      curr_pos = zaber.axis.get_position()
      last_position = (curr_pos*0.047625)/1000 # to mm
      if last_position <= (currentPosition*0.047625)/1000:
         zaber.axis.stop()
         break
   
   print("Testing complete: Saving data to xlsx sheet")
   if zaber.axis.is_parked():
      zaber.axis.unpark()
   
   zaber.axis.move_absolute(17, Units.LENGTH_MILLIMETRES)
   path = Path(SAVE_PATH)
   file_name = file_name + ".xlsx" # create file name
   path = path / file_name
   workbook = xlsxwriter.Workbook(path)
   worksheet = workbook.add_worksheet("Run")

   # Create Column headers
   worksheet.write('A1', 'Index')
   worksheet.write('B1', f'Load Cell {load_cell_a_serial}')
   worksheet.write('C1', f'Load Cell {load_cell_b_serial}')
   worksheet.write('D1', f'Load Cell {load_cell_c_serial}')
   worksheet.write('E1', 'Time')

   # Time Array
   time = np.linspace(init_seconds, 
               (len(readings_arrA)- 1) * 0.016 + init_seconds,
               len(readings_arrA))
   
   # Save data arrays to file
   for index in range(len(readings_arrA)):
      worksheet.write(index+1, 0, index + 1)
      worksheet.write(index+1, 1, readings_arrA[index])
      worksheet.write(index+1, 2, readings_arrB[index])
      worksheet.write(index+1, 3, readings_arrC[index])
      worksheet.write(index+1, 4, time[index])
   workbook.close()


   futek.stop()
   futek.exit()
   zaber.disconnect()


   
      


test()


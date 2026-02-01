# import nidaqmx
import bge # type: ignore
# import os
# from collections import OrderedDict
# from nidaqmx.constants import AcquisitionType
# import time
# import math
# from obislaser import LaserController


class Component(bge.types.KX_PythonComponent):
    # Put your arguments here of the format ("key", default_value).
    # These values are exposed to the UI.
    # args = OrderedDict([
    # ])
    
    def cleanup(self):
        """ Clean up the scene and any remaining objects. """
        try:
            # Get the current scene
            scene = bge.logic.getCurrentScene()
            
            # Clean up any physics objects
            for obj in scene.objects:
                if obj.getPhysicsId():
                    obj.suspendDynamics()
                    obj.endObject()
            
            # Clean up any remaining game objects
            for obj in scene.objects:
                if not obj.invalid:
                    obj.endObject()
                    
        except Exception as e:
            print(f"Error during scene cleanup: {e}")

        """ Stop the nidaqmx tasks and close the connections. """
        # if self.laser is not None:
        #     print(self.laser.set_power_mw(0))
        #     print(self.laser.turn_off())
        #     self.laser.close()
        #     del self.laser
        
        # if not self.object["mouse_debug"]:
        #     try:
        #         # turn off cameras
        #         self.task_do_camera.write(False)

        #         # turn off laser
        #         self.task_do_laser.write(False)
                
        #         # close nidaqmx task
        #         # self.task_ao.close()
        #         self.task_ai_airball.stop()
        #         self.task_ai_airball.close()
        #         self.task_do_camera.close()
        #     except:
        #         pass
        #     finally:
        #         # del self.task_ao
        #         del self.task_ai_airball
        #         del self.task_do_camera
        #         del self.task_do_laser
        print("cleanup")

    def start(self, args):
        """
        Initialize the zero offset and threshold values for the voltage readings.
        Then select the experiment and set up the save path.
        Finally, start the nidaqmx tasks and set the start time.
        """
        print(f"Script is running via component on object: {self.object.name}")
        # self.COMPUTERNAME = os.environ["COMPUTERNAME"]
        # self.V_ZERO_OFFSET = { "X": 2.48, "Y": 2.48, "Z": 2.48 }
        # self.YDIR = 1
        # if self.COMPUTERNAME == "LRI-110045":
        #     self.V_ZERO_OFFSET = { "X": 2.59, "Y": 2.60, "Z": 2.62 }
        # elif self.COMPUTERNAME == "LRI-110117":
        #     self.YDIR = -1
        # else:
        #     print("Warning: voltage offsets not configured for this computer.")
        # print(f"COMPUTERNAME={self.COMPUTERNAME}")

        # self.task_ai_airball = None
        # self.task_do_camera = None
        # self.task_do_laser = None
        # self.simulated = False
        # self.abort = False

        # self.laser = LaserController()
        # if not self.laser.open():
        #     print("Failed to open laser serial port.")
        #     del self.laser
        #     self.laser = None
        #     # self.abort = True
        #     # return
        # else:
        #     print(self.laser.set_power_mw(0))
        #     print(self.laser.turn_on())
        #     time.sleep(10)

        # self.laser_process = False
        # self.laser_powered = False

        
        # # File Start Time
        # self.start_time_formatted = time.strftime("%Y-%m-%d %H-%M-%S", time.localtime(time.time()))


        # # Set up the save path
        # self.experimentSelect()
        # if self.abort:
        #     bge.logic.endGame()
        # else:
        #     print(f"Start Time: {self.start_time_formatted}")

        #     # Save Path
        #     self.save_path = os.path.join("I:\\data\\", self.COMPUTERNAME,
        #         time.strftime("%b%y", time.localtime(time.time())),
        #         time.strftime("%m%d%y", time.localtime(time.time())))
            
        #     # Create the save path if it does not exist
        #     if not os.path.exists(self.save_path):
        #         try:
        #             os.makedirs(self.save_path)
        #         except:
        #             print(f"Could not create directory {self.save_path}")
        #             self.abort = True
        #             self.object["save_data"] = False

        #     # Start the nidaqmx tasks
        #     if not self.object["mouse_debug"]:
        #         self.startNidaq()

        #     # Start Time
        #     self.start_time = time.time()
        print("start")

    def update(self):
        """ Check for the escape key, elapsed time, or abort flag. Process mouse movement. """
        # Check for window close event
        if bge.logic.KX_INPUT_ACTIVE in bge.logic.window.inputs:
            if bge.logic.window.inputs[bge.logic.KX_INPUT_ACTIVE].values[0]:
                self.cleanup()
                bge.logic.endGame()
                return

        # Check for escape key
        if bge.logic.keyboard.inputs[bge.events.ESCKEY].values[0]:
            self.cleanup()
            bge.logic.endGame()
            return

        print("update")

    # def process_movement(self):
    #     """ Process the mouse movement by reading the nidaqmx data. """
    #     if self.simulated:
    #         # read simulation data
    #         if self.simulation_index >= len(self.simulation_data):
    #             self.abort = True
    #             return
    #         sample = self.simulation_data[self.simulation_index]
    #         if len(sample) > 3:
    #             sample[0] = sample[1]
    #             sample[1] = sample[2]
    #             sample[2] = sample[3]
    #         self.simulation_index += 1
    #     elif self.object["use_keyboard"] or self.object["mouse_debug"]:
    #         # read keyboard inputs
    #         inputs = bge.logic.keyboard.inputs
    #         sample = [self.V_ZERO_OFFSET["X"], self.V_ZERO_OFFSET["Y"], self.V_ZERO_OFFSET["Z"]]
    #         if inputs[bge.events.WKEY].values[0]:
    #             sample[1] += self.V_ZERO_OFFSET["X"] * 0.5
    #         if inputs[bge.events.SKEY].values[0]:
    #             sample[1] += self.V_ZERO_OFFSET["X"] * -0.5
    #         if inputs[bge.events.AKEY].values[0]:
    #             sample[2] += self.V_ZERO_OFFSET["Z"] * 0.5
    #         if inputs[bge.events.DKEY].values[0]:
    #             sample[2] += self.V_ZERO_OFFSET["Z"] * -0.5
    #     else:
    #         # read nidaqmx data
    #         raw_sample = self.task_ai_airball.read(number_of_samples_per_channel=1)
    #         sample = [raw_sample[0][0], raw_sample[1][0], raw_sample[2][0]]

    #     # process movement
    #     movement = [self.elapsed_time, sample[0], sample[1], sample[2]]
    #     x = (movement[3] - self.V_ZERO_OFFSET["X"]) / self.V_ZERO_OFFSET["X"]
    #     y = (movement[2] - self.V_ZERO_OFFSET["Y"]) / self.V_ZERO_OFFSET["Y"]
    #     z = (movement[1] - self.V_ZERO_OFFSET["Z"]) / self.V_ZERO_OFFSET["Z"]
    #     threshold = 0.1
    #     if abs(x) < threshold:
    #         x = 0
    #     if abs(y) < threshold:
    #         y = 0
    #     if abs(z) < threshold:
    #         z = 0
    #     z = z * 2.9
    #     x = x * 1.4 # 2.1 # originally 1.4. changed on 1/17/25
    #     apply_offset = [x * 0.5 * self.YDIR, y * -0.5, z * 0.01]
    #     self.object.applyMovement((0, apply_offset[0], 0), True)
    #     self.object.applyRotation((0, 0, apply_offset[2]), True)

    #     # update the data
    #     self.postion.append([   self.elapsed_time,
    #                             self.object.worldPosition[0],
    #                             self.object.worldPosition[1],
    #                             (self.object.worldOrientation.to_euler()[2] + (math.pi * 2)) % (math.pi * 2),
    #                             1 if self.laser_powered else 0
    #                         ])
    #     self.movement.append(movement)

    # def startNidaq(self):
    #     """ Start the nidaqmx tasks for reading the analog input and writing the digital output. """
    #     # self.task_ao = nidaqmx.Task()
    #     self.task_ai_airball = nidaqmx.Task()
    #     self.task_do_camera = nidaqmx.Task()
    #     self.task_do_laser = nidaqmx.Task()
    #     # self.ao3 = self.task_ao.ao_channels.add_ao_voltage_chan("Dev1/ao3") # to process reward
    #     self.task_ai_airball.ai_channels.add_ai_voltage_chan("Dev1/ai0")
    #     self.task_ai_airball.ai_channels.add_ai_voltage_chan("Dev1/ai1")
    #     self.task_ai_airball.ai_channels.add_ai_voltage_chan("Dev1/ai2")
    #     self.task_do_camera.do_channels.add_do_chan("Dev1/port0/line1")
    #     self.task_do_laser.do_channels.add_do_chan("Dev1/port0/line3")

    #     self.task_ai_airball.timing.cfg_samp_clk_timing(rate=60,
    #                                             sample_mode=AcquisitionType.CONTINUOUS,
    #                                             samps_per_chan=1)
    #     self.task_ai_airball.start()
    #     self.task_do_camera.write(True)
    #     self.task_do_laser.write(False)

    # def save_data(self):  
    #     """ Save the data to csv files. """
    #     if self.object["save_data"]:
    #         tgt_file = os.path.join(self.save_path, f"Mouse {self.mouse_no} {self.start_time_formatted}.tgt.csv")
    #         with open(f"{tgt_file}", "w") as f:
    #             for target in self.targets:
    #                 f.write(",".join(map(str, target)) + "\n")
    #         mov_file = os.path.join(self.save_path, f"Mouse {self.mouse_no} {self.start_time_formatted}.mov.csv")
    #         with open(f"{mov_file}", "w") as f:
    #             for movement in self.movement:
    #                 f.write(",".join(map(str, movement)) + "\n")
    #         pos_file = os.path.join(self.save_path, f"Mouse {self.mouse_no} {self.start_time_formatted}.pos.csv")
    #         with open(f"{pos_file}", "w") as f:
    #             for position in self.postion:
    #                 f.write(",".join(map(str, position)) + "\n")
    #         print(f"Saving data to {self.save_path}")

    # def experimentSelect(self):
    #     """ Select the experiment and set up the targets. """
    #     prompt = "//===============================================\n"\
    #            + "||        Select an experiment                   \n"\
    #            + "||===============================================\n"\
    #            + "||  0.  Quit                                     \n"\
    #            + "||  1.  Linear Track (Not Yet Available)         \n"\
    #            + "||  2.  One-Object                               \n"\
    #            + "||  3.  Two-Object Same                          \n"\
    #            + "||  4.  Two-Object Horizontal Stripes            \n"\
    #            + "||  5.  Two-Object Dots                          \n"\
    #            + "||  6.  Two-Object Squares                       \n"\
    #            + "||  7.  Two-Object Triangles                     \n"\
    #            + "||  99. Simulation from File                     \n"\
    #            + "\\===============================================\n"
    #     prompt2 = prompt.replace("||  1.  Linear Track (Not Yet Available)         \n", "")
    #     prompt2 = prompt2.replace("||  99. Simulation from File                     \n", "")
    #     user_input = ""
    #     while (user_input not in ["0", "2", "3", "4", "5", "6", "7", "99"]):
    #         print(prompt)
    #         user_input = input().strip()
            
    #     # Set the positions of the novel objects
    #     scene_name = self.object.scene.name
    #     if scene_name == "Scene":
    #         novelObject = ["CVert", "CVert2", "CHoriz", "CDots", "CSq", "CTri"]
    #         OFamiliar = "OFamiliar"
    #         ONovel = "ONovel"
    #         ArenaCircle = "ArenaCircle"
    #     else:
    #         novelObject = ["CVert.001", "CVert2.001", "CHoriz.001", "CDots.001", "CSq.001", "CTri.001"]
    #         OFamiliar = "OFamiliar.001"
    #         ONovel = "ONovel.001"
    #     for obj in novelObject:
    #         try:
    #             self.object.scene.objects.get(obj).worldPosition[2] = (-2) * self.object.scene.objects.get(obj).worldScale[2]
    #         except:
    #             print(f"Object {obj} not found in scene {scene_name}.")
            
    #     # Set the positions of the familiar and novel objects
    #     try:
    #         self.oFamiliar = self.object.scene.objects.get(OFamiliar)
    #         self.oNovel = self.object.scene.objects.get(ONovel)
    #     except:
    #         print(f"Objects {OFamiliar} or {ONovel} not found in scene {scene_name}.")
    #         self.abort = True
    #         return
    #     self.mouse_no = ""
    #     self.duration = 0.0
        
    #     try:
    #         fPosition = (self.oFamiliar.worldPosition[0], self.oFamiliar.worldPosition[1], self.oFamiliar.worldPosition[2])
    #         fScale = (self.oFamiliar.worldScale[0], self.oFamiliar.worldScale[1], self.oFamiliar.worldScale[2])
    #         nPosition = (self.oNovel.worldPosition[0], self.oNovel.worldPosition[1], self.oNovel.worldPosition[2])
    #         nScale = (self.oNovel.worldScale[0], self.oNovel.worldScale[1], self.oNovel.worldScale[2])
    #     except:
    #         print(f"Objects {OFamiliar} or {ONovel} not found in scene {scene_name}.")
    #         self.abort = True
    #         return
            
    #     if user_input in ["0", "1"]:
    #         self.abort = True
    #     else:            
    #         if user_input == "99":
    #             file_path = self.validate_simulation_file()
    #             if file_path is None:
    #                 self.abort = True
    #                 return
    #             else:
    #                 self.load_simulation_data(file_path)
    #                 self.simulated = True
                    
    #                 while (user_input not in ["0", "2", "3", "4", "5", "6", "7"]):
    #                     print(prompt2)
    #                     user_input = input().strip()

    #         if user_input == "0":
    #             self.abort = True
    #         else:
    #             self.targets = [
    #                 ["world", "environment", "datetime", "radius"],
    #                 ["error", "blender", self.start_time_formatted, self.object.scene.objects.get(ArenaCircle).worldScale[0] if scene_name == "Scene" else 0],
    #                 ["spawned", "x", "y", "radius"]
    #                 ]

    #             self.movement = [
    #                 ["elapsed", "orbital", "lateral", "forward"],
    #             ]

    #             self.postion = [
    #                 ["elapsed", "x", "y", "d", "laser"],
    #             ]
    #             self.object.scene.objects.get(novelObject[0]).worldPosition = fPosition
    #             self.object.scene.objects.get(novelObject[0]).worldScale = fScale
                
    #             if user_input == "2":
    #                 self.targets[1][0] = "oneObject"
    #                 self.targets.append([0, fPosition[0], fPosition[1], fScale[0]])
    #             else:
    #                 do_swap = input("Swap familiar and novel objects? (y/[n]): ")
    #                 rStr = ""
    #                 if len(do_swap) > 0 and do_swap[0].lower() == "y":
    #                     tempPosition,   tempScale   = fPosition,    fScale
    #                     fPosition,      fScale      = nPosition,    nScale
    #                     nPosition,      nScale      = tempPosition, tempScale
    #                     rStr = "Swapped"
    #                 self.targets.append([0, fPosition[0], fPosition[1], fScale[0]])
    #                 self.targets.append([0, nPosition[0], nPosition[1], nScale[0]])
    #                 if user_input == "3":
    #                     self.targets[1][0] = "twoObjectSame"
    #                     self.object.scene.objects.get(novelObject[1]).worldPosition = nPosition
    #                     self.object.scene.objects.get(novelObject[1]).worldScale = nScale
    #                 elif user_input == "4":
    #                     self.targets[1][0] = "twoObjectHorizontal"
    #                     self.object.scene.objects.get(novelObject[2]).worldPosition = nPosition
    #                     self.object.scene.objects.get(novelObject[2]).worldScale = nScale
    #                 elif user_input == "5":
    #                     self.targets[1][0] = "twoObjectDots"
    #                     self.object.scene.objects.get(novelObject[3]).worldPosition = nPosition
    #                     self.object.scene.objects.get(novelObject[3]).worldScale = nScale
    #                 elif user_input == "6":
    #                     self.targets[1][0] = "twoObjectSquares"
    #                     self.object.scene.objects.get(novelObject[4]).worldPosition = nPosition
    #                     self.object.scene.objects.get(novelObject[4]).worldScale = nScale
    #                 elif user_input == "7":
    #                     self.targets[1][0] = "twoObjectTriangles"
    #                     self.object.scene.objects.get(novelObject[5]).worldPosition = nPosition
    #                     self.object.scene.objects.get(novelObject[5]).worldScale = nScale
            
    #             # Get the mouse number
    #             while (not (self.mouse_no is None)) and (len(self.filePathSafe(self.mouse_no)) == 0):
    #                 self.mouse_no = self.filePathSafe(input("Enter mouse number: "))
                
    #             # Get the duration of the experiment (not applicable for simulation)
    #             if not self.simulated:
    #                 getDuration = "not_numeric"
    #                 while (not getDuration.isnumeric()):
    #                     try:
    #                         getDuration = input("Enter duration (default 300): ")
    #                     except:
    #                         getDuration = ""
    #                     if len(getDuration) == 0:
    #                         getDuration = "300"
    #                 print (f"Starting experiment {self.mouse_no} for {getDuration} seconds.")
    #                 self.duration = int(getDuration)
        
    # def filePathSafe(self, input):
    #     return "".join([c for c in input if c.isalpha() or c.isdigit() or c in [' ', '.', '_', '-']]).strip().replace(" ", "_")

    # def validate_simulation_file(self):
    #     """ Prompt the user for a valid CSV file with 4 columns and no missing data. """
    #     import csv

    #     while True:
    #         file_path = input("Enter the path to the simulation CSV file: ").strip().replace("\"","")
    #         if file_path == "":
    #             return None
            
    #         if not os.path.exists(file_path):
    #             print("File does not exist. Please try again.")
    #             continue

    #         try:
    #             with open(file_path, 'r') as f:
    #                 reader = csv.reader(f)
    #                 rows = list(reader)

    #                 # Validate header or first row
    #                 len_header = len(rows[0])
    #                 if len(rows) < 2 or len_header not in [3, 4]:
    #                     raise ValueError("CSV must have exactly 3 or 4 columns: [elapsed,] orbital, lateral, forward.")
                    

    #                 # Validate all rows are rectangular
    #                 for row in rows[1:]:
    #                     if len(row) != len_header:
    #                         raise ValueError("CSV contains missing or extra data in some rows.")

    #             print(f"File '{file_path}' is valid.")
    #             return file_path

    #         except Exception as e:
    #             print(f"Invalid file format: {e}. Please try again.")

    # def load_simulation_data(self, file_path):
    #     """ Load movement data from a validated CSV file into memory. """
    #     import csv
    #     with open(file_path, 'r') as f:
    #         reader = csv.reader(f)
    #         next(reader)  # Skip the header
    #         self.simulation_data = [list(map(float, row)) for row in reader]
    #         self.simulation_index = 0
    #         print(f"Loaded {len(self.simulation_data)} lines of simulation data.")

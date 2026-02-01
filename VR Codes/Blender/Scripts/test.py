import nidaqmx
import bge # type: ignore
import os
from collections import OrderedDict
from nidaqmx.constants import AcquisitionType
import time
import math

V_ZERO_OFFSET = 2.48
V_THRESHOLD = 0.02

class Component(bge.types.KX_PythonComponent):
    # Put your arguments here of the format ("key", default_value).
    # These values are exposed to the UI.
    args = OrderedDict([
    ])
    
    def cleanup(self):
        if not self.object["mouse_debug"]:
            try:
                # turn off cameras
                self.task_do.write(False)
                # close nidaqmx task
                self.task_ai.stop()
                self.task_ai.close()
                self.task_do.close()
                # self.task_ao.close()
            except:
                pass
            finally:
                del self.task_ai
                del self.task_do
                # del self.task_ao

    def start(self, args):
        self.task_ai = None
        self.task_do = None
        self.abort = False
        
        self.experimentSelect()
        if not self.abort:
            self.startNidaq()
            
            self.start_time = time.time()
            self.start_time_formatted = time.strftime("%Y-%m-%d %H-%M-%S", time.localtime(self.start_time))
            self.elapsed_time = 0
            
            self.save_path = os.path.join("I:\\data\\", os.environ["COMPUTERNAME"], time.strftime("%b%y", time.localtime(self.start_time)), time.strftime("%m%d%y", time.localtime(self.start_time)))
            
            if not os.path.exists(self.save_path):
                try:
                    os.makedirs(self.save_path)
                except:
                    print(f"Could not create directory {self.save_path}")
                    self.abort = True
        
        if self.abort:
            # end game
            self.cleanup()
            bge.logic.endGame()

    def update(self):
        self.elapsed_time = (time.time() - self.start_time)
        if (bge.logic.keyboard.inputs[bge.events.ESCKEY].values[0]) or (self.elapsed_time > self.duration):
            if self.object["save_data"]:
                # write csv files for targets, movement, and position
                tgt_file = os.path.join(self.save_path, f"Mouse {self.mouse_no} {self.start_time_formatted}.tgt.csv")
                with open(f"{tgt_file}", "w") as f:
                    for target in self.targets:
                        f.write(",".join(map(str, target)) + "\n")
                mov_file = os.path.join(self.save_path, f"Mouse {self.mouse_no} {self.start_time_formatted}.mov.csv")
                with open(f"{mov_file}", "w") as f:
                    for movement in self.movement:
                        f.write(",".join(map(str, movement)) + "\n")
                pos_file = os.path.join(self.save_path, f"Mouse {self.mouse_no} {self.start_time_formatted}.pos.csv")
                with open(f"{pos_file}", "w") as f:
                    for position in self.postion:
                        f.write(",".join(map(str, position)) + "\n")
                print(f"Saving data to {self.save_path}")
            # end game
            self.cleanup()
            bge.logic.endGame()
        else:
            if self.object["use_keyboard"] or self.object["mouse_debug"]:
                inputs = bge.logic.keyboard.inputs
                movement = [self.elapsed_time, 0, 0, 0]
                if inputs[bge.events.WKEY].values[0]:
                    self.object.applyMovement((0, 0.4, 0), True)
                    movement[2] = 1
                if inputs[bge.events.SKEY].values[0]:
                    self.object.applyMovement((0, -0.4, 0), True)
                    movement[2] = -1
                if inputs[bge.events.AKEY].values[0]:
                    self.object.applyRotation((0, 0, 0.05), True)
                    movement[3] = 1
                if inputs[bge.events.DKEY].values[0]:
                    self.object.applyRotation((0, 0, -0.05), True)
                    movement[3] = -1
            else:
                # read nidaqmx data
                sample = self.task_ai.read(number_of_samples_per_channel=1)
                movement = [self.elapsed_time, sample[0][0], sample[1][0], sample[2][0]]
                x = (movement[3] - V_ZERO_OFFSET) / V_ZERO_OFFSET
                y = (movement[2] - V_ZERO_OFFSET) / V_ZERO_OFFSET
                z = (movement[1] - V_ZERO_OFFSET) / V_ZERO_OFFSET
                if abs(x) < V_THRESHOLD:
                    x = 0
                if abs(y) < V_THRESHOLD:
                    y = 0
                if abs(z) < V_THRESHOLD:
                    z = 0
                apply_offset = [x * -0.5, y * -0.5, z * 0.01]
                self.object.applyMovement((0, apply_offset[0], 0), True)
                self.object.applyRotation((0, 0, apply_offset[2]), True)

            self.postion.append([self.elapsed_time, self.object.worldPosition[0], self.object.worldPosition[1], (self.object.worldOrientation.to_euler()[2] + (math.pi * 2)) % (math.pi * 2)])
            self.movement.append(movement)
            
    def startNidaq(self):
        # Put your initialization code here, args stores the values from the UI.
        # self.object is the owner object of this component.
        # self.object.scene is the main scene.       
        self.task_ai = nidaqmx.Task() if not self.object["mouse_debug"] else None
        self.task_do = nidaqmx.Task() if not self.object["mouse_debug"] else None
        if not self.object["mouse_debug"]:
            # self.task_ao = nidaqmx.Task()
            self.ai0 = self.task_ai.ai_channels.add_ai_voltage_chan("Dev1/ai0") # rotation
            self.ai1 = self.task_ai.ai_channels.add_ai_voltage_chan("Dev1/ai1") # x-axis
            self.ai2 = self.task_ai.ai_channels.add_ai_voltage_chan("Dev1/ai2") # y-axis
            # self.ao3 = self.task_ao.ao_channels.add_ao_voltage_chan("Dev1/ao3") # to process reward
            self.do1 = self.task_do.do_channels.add_do_chan("Dev1/port0/line1") # To turn on cameras
            
            
            self.task_ai.timing.cfg_samp_clk_timing(rate=60,
                                                sample_mode=AcquisitionType.CONTINUOUS,
                                                samps_per_chan=1)
        
            # Turn on cameras
            self.task_do.write(True)
            self.task_ai.start()
        
                
    def experimentSelect(self):
        self.targets = [
            ["world", "environment", "unused", "radius"],
            ["error", "blender", 0, self.object.scene.objects.get("ArenaCircle").worldScale[0]],
            ["spawned", "x", "y", "radius"]
            ]

        self.movement = [
            ["elapsed", "orbital", "lateral", "forward"],
        ]

        self.postion = [
            ["elapsed", "x", "y", "d"],
        ]
        
        
        novelObject = ["CVert", "CVert2", "CHoriz", "CDots", "CSq", "CTri"]
        for obj in novelObject:
            self.object.scene.objects.get(obj).worldPosition[2] = (-2) * self.object.scene.objects.get(obj).worldScale[2]
        
        prompt = "//===============================================\n"\
               + "||        Select an experiment                   \n"\
               + "||===============================================\n"\
               + "||  0.  Quit                                     \n"\
               + "||  1.  Linear Track (Not Yet Available)         \n"\
               + "||  2.  One-Object                               \n"\
               + "||  3.  Two-Object Same                          \n"\
               + "||  4.  Two-Object Horizontal Stripes            \n"\
               + "||  5.  Two-Object Dots                          \n"\
               + "||  6.  Two-Object Squares                       \n"\
               + "||  7.  Two-Object Triangles                     \n"\
               + "\\===============================================\n"
        user_input = ""
        while (user_input.strip() not in ["0", "2", "3", "4", "5", "6", "7"]):
            print(prompt)
            user_input = input()
            
        self.oFamiliar = self.object.scene.objects.get("OFamiliar")
        self.oNovel = self.object.scene.objects.get("ONovel")
        self.mouse_no = ""
        self.duration = ""
        
        fPosition = (self.oFamiliar.worldPosition[0], self.oFamiliar.worldPosition[1], self.oFamiliar.worldPosition[2])
        fScale = (self.oFamiliar.worldScale[0], self.oFamiliar.worldScale[1], self.oFamiliar.worldScale[2])
        nPosition = (self.oNovel.worldPosition[0], self.oNovel.worldPosition[1], self.oNovel.worldPosition[2])
        nScale = (self.oNovel.worldScale[0], self.oNovel.worldScale[1], self.oNovel.worldScale[2])
            
        if user_input == "0":
            self.abort = True
        else:
            if user_input == "1":
                pass
            else:                
                self.object.scene.objects.get("CVert").worldPosition = fPosition
                self.object.scene.objects.get("CVert").worldScale = fScale
                self.targets.append([0, fPosition[0], fPosition[1], fScale[0]])
                
                if user_input == "2":
                    self.targets[1] = ["oneObject", "blender", 0, 100]
                else:
                    do_swap = input("Swap familiar and novel objects? (y/[n]): ")
                    rStr = ""
                    if len(do_swap) > 0 and do_swap[0].lower() == "y":
                        tempPosition = fPosition
                        tempScale = fScale
                        fPosition = nPosition
                        fScale = nScale
                        nPosition = tempPosition
                        nScale = tempScale
                        rStr = "Swapped"
                    self.targets.append([0, nPosition[0], nPosition[1], nScale[0]])
                    if user_input == "3":
                        self.targets[1] = ["twoObjectSame", "blender", 0, 100]
                        self.object.scene.objects.get("CVert2").worldPosition = nPosition
                        self.object.scene.objects.get("CVert2").worldScale = nScale
                    elif user_input == "4":
                        self.targets[1] = ["twoObjectHorizontal" + rStr, "blender", 0, 100]
                        self.object.scene.objects.get("CHoriz").worldPosition = nPosition
                        self.object.scene.objects.get("CHoriz").worldScale = nScale
                    elif user_input == "5":
                        self.targets[1] = ["twoObjectDots" + rStr, "blender", 0, 100]
                        self.object.scene.objects.get("CDots").worldPosition = nPosition
                        self.object.scene.objects.get("CDots").worldScale = nScale
                    elif user_input == "6":
                        self.targets[1] = ["twoObjectSquares" + rStr, "blender", 0, 100]
                        self.object.scene.objects.get("CSq").worldPosition = nPosition
                        self.object.scene.objects.get("CSq").worldScale = nScale
                    elif user_input == "7":
                        self.targets[1] = ["twoObjectTriangles" + rStr, "blender", 0, 100]
                        self.object.scene.objects.get("CTri").worldPosition = nPosition
                        self.object.scene.objects.get("CTri").worldScale = nScale
            
            while (not (self.mouse_no is None)) and (len(self.filePathSafe(self.mouse_no)) == 0):
                self.mouse_no = self.filePathSafe(input("Enter mouse number: "))

            while (not self.duration.isnumeric()):
                try:
                    self.duration = input("Enter duration (default 300s): ")
                except:
                    self.duration = ""
                if len(self.duration) == 0:
                    self.duration = "300"
            print (f"Starting experiment {self.mouse_no} for {self.duration} seconds.")
            self.duration = int(self.duration)
        
    def filePathSafe(self, input):
        return "".join([c for c in input if c.isalpha() or c.isdigit() or c in [' ', '.', '_', '-']]).strip().replace(" ", "_")

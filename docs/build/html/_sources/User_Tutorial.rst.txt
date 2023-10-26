User Tutorial
================

Contents 
------------------
Through this tutorial, you will learn how to optimize your tower design in SAP2000 using Autobuilder. This tutorial will also help to familiarize you with the program's basic functions and features.

The required materials and finished product of this tutorial can be found in <C:\Program Files (x86)\University of Toronto Seismic Design Team\Autobuilder\Example_beta> 

.. note::

    1. The SAP2000 model used in this tutorial is incomplete and only for demonstration purposes. See “Modelling in SAP2000” for an introductory SAP2000 modelling tutorial. 
    2. Save the Autobuilder file frequently throughout the tutorial if possible. 

This section describes the process of setting up a new Autobuilder model.

.. |gear| image:: images/Icons/gear.png
.. |disk| image:: images/Icons/disk.png
.. |folder-horizontal-open| image:: images/Icons/folder-horizontal-open.png
.. |arrow-090| image:: images/Icons/arrow-090.png 
.. |arrow-270| image:: images/Icons/arrow-270.png 
.. |flip| image:: images/Icons/flip.png
.. |Bracing-24x24| image:: images/Icons/Bracing-24x24.png
.. |plus| image:: images/Icons/plus.png
.. |minus| image:: images/Icons/minus.png
.. |Floorplane-24x24| image:: images/Icons/Floor_Plan-24x24.png
.. |panel-24x24| image:: images/Icons/Panel-24x24.png
.. |pencil| image:: images/Icons/pencil.png
.. |pencil_plus| image:: images/Icons/pencil_plus.png
.. |generatetower-24x24| image:: images/Icons/GenerateTower-24x24.png
.. |runtower-24x24| image:: images/Icons/RunTower-24x24.png

1. Initializing a New Model
------------------------------------

1.1 Initialize the Model
~~~~~~~~~~~~~~~~~~~~~~~~~
* To start, go to *Settings -> Project Settings /* click |gear|
* The *Project Settings* dialog shown below will appear. 
.. image:: images/Project-Settings.png
* Enter the following 
    * Floor Elevations
        * 0.0, 6.0, 9.0, 12.0, 15.0, 18.0, 21.0, 24.0, 27.0, 30.0, 33.0, 36.0, 39.0, 42.0, 45.0,
        48.0, 51.0, 54.0, 57.0, 60.0
        Note: Always include the elevations of the ground floor and the roof
    * Section Properties
        * 1: FSEC1
        * 2: BALSA_0.1875x0.1875
    * Analysis options
        * Ground motion: uncheck "Run"
            * Note: To obtain the complete set of performance metrics, including roof
            accelerations, displacements and base shear, check “Run”. Please
            ensure the ground motion is correctly defined in the SAP2000 model.
        * Analysis type: "Time history analysis"
        * SAP2000 model: “C:\Program Files (x86)\University of Toronto Seismic Design
        Team\Autobuilder\Example_beta\SAP Model\2022.sdb”
    * Render settings   
        * x: 12.0
        * y: 12.0
        * z: 60.0
        * Note: The input values should correspond to the maximum dimensions of your
        tower
* Press OK to return to the main window. 

2. Main Window
------------------------------------
This section describes the basic controls in the main window.

2.1 Save File
~~~~~~~~~~~~~~~~~~~~~~~~~
* To start, go to *File -> Save File.../* click |disk|
* The *Save File* dialog shown below will appear.
.. image:: images/save-file.png
* Save your current model
    * Directory: "C:\Users\<Your Name>\Downloads" (Or any other folder)
    * Name: “Tutorial 1.ab”

2.2 Open File
~~~~~~~~~~~~~~~~~~~~~~~~~
* To start, go to *File -> Open File.../* click  |folder-horizontal-open|
* The *Open File* dialog shown below will appear.
.. image:: images/Open-file.png

* Open your previously saved model

2.3 Section View
~~~~~~~~~~~~~~~~~~~~~~~~~
The left portion of the main window consists of the section view of the tower as seen below. 
.. image:: images/section-view.png

* Click |arrow-090| or |arrow-270| to move up or down a floor. “Z= X.X” represents the current floor elevation and will change accordingly.    
* |flip| changes the orientation of the panels


2.4 3-D View
~~~~~~~~~~~~~~~~~~~~~~~~~
The right portion of the main window consists of the 3-D view of the tower as seen below.
.. image:: images/3-D-view.png 

* Click |arrow-090|  or |arrow-270| to shift up or down.
* Scroll up or down to zoom in or out.
* Doublc click to resume to the original zoom level.

3. Bracing Schemes
------------------------------------
This section details the steps to define bracing schemes. By default, there will be one pre-defined bracing scheme.

3.1 Create Bracing Schemes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
* To start, go to *Edit -> Bracing Scheme/* click |Bracing-24x24|
* The *Bracing Scheme* dialog shown below will appear. 
.. image:: images/bracing-scheme.png    
* Click |plus| at the left side of the dialog to create a new bracing scheme.
* Rename "New Bracing 1" to "double_x".
* Enter the following coordinates and the material of each member in the table shown below.
.. image:: images/define-bracing.png
* Click |plus| to add a new row.
* Select one or multiple rows and click |minus| to delete. 
* (Note: The following mathematical operations are allowed: +, -, *, /.)
* Repeat the steps above for the “x” bracing scheme.
* Press OK to return to the main window.

4. Floor Plans
------------------------------------
This section details the steps to define floor plans. By default, there will be ten pre-defined floor plans.

4.1 Create/Edit Floor Plans
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
* To start, go to *Edit -> Floor Plan/* click |Floorplane-24x24|.
* The *Floor* Plan dialog shown below will appear. 

.. image:: images/floor-plan.png

* Select all the existing floor plans click |minus| to delete.
* Create a new floor plan by clicking |plus| next to "Edit Floor Plan" and rename it to “Floor_1_7”.
* Enter the following information in the new floor plan:
  
  * X Y Coordinates

    +-------+-------+--------+--------+
    |   X   |   Y   | Bottom |  Top   |
    +=======+=======+========+========+
    |   0   |   0   |   1    |   1    |
    +-------+-------+--------+--------+
    |  12   |   0   |   2    |   2    |
    +-------+-------+--------+--------+
    |  12   |  12   |   3    |   3    |
    +-------+-------+--------+--------+
    |   0   |  12   |   4    |   4    |
    +-------+-------+--------+--------+
    |   3   |   3   |   6    |   6    |
    +-------+-------+--------+--------+
    |   9   |   9   |   7    |   7    |
    +-------+-------+--------+--------+
    |   3   |   9   |   8    |   8    |
    +-------+-------+--------+--------+
    
  * Members

    +-------+-----+
    | Start | End |
    +=======+=====+
    |   1   |  2  |
    +-------+-----+
    |   2   |  3  |
    +-------+-----+
    |   3   |  4  |
    +-------+-----+
    |   4   |  1  |
    +-------+-----+
    |   5   |  6  |
    +-------+-----+
    |   6   |  7  |
    +-------+-----+
    |   7   |  8  |
    +-------+-----+
    |   8   |  5  |
    +-------+-----+


* Repeat the steps above for the rest of floor plans:
    * Floor plan name: Floor_8_10_16_19
        * X Y Coordinates 

          +-------+-------+--------+--------+
          |   X   |   Y   | Bottom |  Top   |
          +=======+=======+========+========+
          |   0   |   0   |   1    |   1    |
          +-------+-------+--------+--------+
          |  12   |   0   |   2    |   2    |
          +-------+-------+--------+--------+
          |  12   |  12   |   3    |   3    |
          +-------+-------+--------+--------+
          |   0   |  12   |   4    |   4    |
          +-------+-------+--------+--------+
        * Members

          +-------+-----+
          | Start | End |
          +=======+=====+
          |   1   |  2  |
          +-------+-----+
          |   2   |  3  |
          +-------+-----+
          |   3   |  4  |
          +-------+-----+
          |   4   |  1  |
          +-------+-----+


    * Floor plan name: Floor_11_15
        * X Y Coordinates 

          +---------+---------+--------+--------+
          |   X     |   Y     | Bottom |  Top   |
          +=========+=========+========+========+
          |  3.25   |  3.25   |   1    |   1    |
          +---------+---------+--------+--------+
          |  8.75   |  3.25   |   2    |   2    |
          +---------+---------+--------+--------+
          |  8.75   |  8.75   |   3    |   3    |
          +---------+---------+--------+--------+
          |  3.25   |  8.75   |   4    |   4    |
          +---------+---------+--------+--------+


4.2 Assign Floor Plans to Elevation 
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
* To start, go to *Assign Elevation.*
* The table shown below will appear.
.. image:: images/floor-plan-2.png
* Enter the name of th floor plans to their corresponding elevations

  +------------+------------------+-----------------------+
  | Elevation  |   1st Layer      |   2nd Layer           |
  +============+==================+=======================+
  |    0.0     | Floor_1_7        |                       |
  +------------+------------------+-----------------------+
  |    6.0     | Floor_1_7        |                       |
  +------------+------------------+-----------------------+
  |    9.0     | Floor_1_7        |                       |
  +------------+------------------+-----------------------+
  |    12.0    | Floor_1_7        |                       |
  +------------+------------------+-----------------------+
  |    15.0    | Floor_1_7        |                       |
  +------------+------------------+-----------------------+
  |    18.0    | Floor_1_7        |                       |
  +------------+------------------+-----------------------+
  |    21.0    | Floor_1_7        | Floor_8_10_16_19      |
  +------------+------------------+-----------------------+
  |    24.0    | Floor_8_10_16_19 |                       |
  +------------+------------------+-----------------------+
  |    27.0    | Floor_8_10_16_19 |                       |
  +------------+------------------+-----------------------+
  |    30.0    | Floor_11_15      |                       |
  +------------+------------------+-----------------------+
  |    33.0    | Floor_11_15      |                       |
  +------------+------------------+-----------------------+
  |    36.0    | Floor_11_15      |                       |
  +------------+------------------+-----------------------+
  |    39.0    | Floor_11_15      |                       |
  +------------+------------------+-----------------------+
  |    42.0    | Floor_11_15      |                       |
  +------------+------------------+-----------------------+
  |    45.0    | Floor_11_15      |                       |
  +------------+------------------+-----------------------+
  |    48.0    | Floor_11_15      |                       |
  +------------+------------------+-----------------------+
  |    51.0    | Floor_8_10_16_19 |                       |
  +------------+------------------+-----------------------+
  |    54.0    | Floor_8_10_16_19 |                       |
  +------------+------------------+-----------------------+
  |    57.0    | Floor_8_10_16_19 |                       |
  +------------+------------------+-----------------------+
  |    60.0    | Floor_8_10_16_19 |                       |
  +------------+------------------+-----------------------+

    
* 1st Layer: Primary floor plan
* 2nd Layer: Secondary floor plan which is directly on top of the 1st Layer
* Note: The nearest floor plans will be connected. For instance, Floor_8_10_16_19 at
elevation 21.0 will be connected to Floor_8_10_16_19 at elevation 24.0, while Floor_1_7 at elevation 21.0 will be connected to Floor_1_7 at elevation 18.0.

4.3 Define Location of the Centre of Mass (COM)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
The locations of the COMs are important for the center of rigidity calculation, which is used to evaluate the performances of towers with asymmetrical floor plans.

* To start, go to *Centre of Mass.*
* The table shown below will appear.
.. image:: images/floor-plan-3.png
* Enter the followings:

  +------------+-----+-----+
  | Elevation  |  X  |  Y  |
  +============+=====+=====+
  |    0.0     | 6.0 | 6.0 |
  +------------+-----+-----+
  |    6.0     | 6.0 | 6.0 |
  +------------+-----+-----+
  |    9.0     | 6.0 | 6.0 |
  +------------+-----+-----+
  |    12.0    | 6.0 | 6.0 |
  +------------+-----+-----+
  |    15.0    | 6.0 | 6.0 |
  +------------+-----+-----+
  |    18.0    | 6.0 | 6.0 |
  +------------+-----+-----+
  |    21.0    | 6.0 | 6.0 |
  +------------+-----+-----+
  |    24.0    | 6.0 | 6.0 |
  +------------+-----+-----+
  |    27.0    | 6.0 | 6.0 |
  +------------+-----+-----+
  |    30.0    | 6.0 | 6.0 |
  +------------+-----+-----+
  |    33.0    | 6.0 | 6.0 |
  +------------+-----+-----+
  |    36.0    | 6.0 | 6.0 |
  +------------+-----+-----+
  |    39.0    | 6.0 | 6.0 |
  +------------+-----+-----+
  |    42.0    | 6.0 | 6.0 |
  +------------+-----+-----+
  |    45.0    | 6.0 | 6.0 |
  +------------+-----+-----+
  |    48.0    | 6.0 | 6.0 |
  +------------+-----+-----+
  |    51.0    | 6.0 | 6.0 |
  +------------+-----+-----+
  |    54.0    | 6.0 | 6.0 |
  +------------+-----+-----+
  |    57.0    | 6.0 | 6.0 |
  +------------+-----+-----+
  |    60.0    | 6.0 | 6.0 |
  +------------+-----+-----+
    
* Press OK to return to the main window 

5. Panels
------------------------------------
This section details the steps to create and edit panels. Panels are boxes/quadrilaterals that define the design locations of the braces.

5.1 Generate Panels from Floor Plans
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
* Go to *Edit -> Generate Panel -> with Floor Plan*
* The generated panels will be shown in the section view. 
.. image:: images/section-view-2.png

5.2 Edit Panels
~~~~~~~~~~~~~~~~~~~~~~~~~
* To start, go to *Edit -> Panel/* click |panel-24x24|.
* The *Panel* dialog shown below will appear.
.. image:: images/panel.png
* Click and select a panel in the table on the left. The selected panel will be shown in the 3D viewer.
.. image:: images/panel-2.png
* Other tips:
    * Give the panel a name with meaning (e.g. “Floor_1_East”). This will help later when we
    assign the panels to the bracing groups.
    * Change the coordinates of existing panels or create new panels for bracings that are
    designed to span multiple floors.
* Press OK to return to the main window.

6. Design Variables
------------------------------------
This section details the steps to create and edit design variable groups, including bracings and member sections.

6.1 Define Bracing Group
~~~~~~~~~~~~~~~~~~~~~~~~~
* Go to *Edit -> Design Variable/* click |pencil|.
* The Design Variables dialog shown below will appear.

.. image:: images/design-variable.png

* Click |plus| above the left column to create a new bracing group and rename it to “x_double_x”.
* Click |plus| above the right column to create a new variable. Select “double_x” from the drop- down.
* Create another variable and select “x”.

6.2 Define Section Group
~~~~~~~~~~~~~~~~~~~~~~~~~
* Click the “Section Group” tab.
* Repeat the same steps for the new section group.
    * Section Group Name: “0.1875_FSEC1”
    * Variable:
        * FSEC1
        * BALSA_0.1875x0.1875
* Press OK to return to the main window.

7. Variable Assignment 
------------------------------------
This section details the steps to assign the bracing and member section design variable groups.

7.1 Assign Bracing Design to Panel
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
* Go to *Edit -> Variable Assignment/* click |pencil_plus|.
* The *Variable Assignment* dialog shown below will appear.
.. image:: images/variable-assignment.png

* Click |plus|.
* Select “x_double_x” in the drop-down for Panel “1”.
* Alternatively, click “Import .csv”.
* Select and import
    * Directory: “C:\Users\<Your Name>\Downloads” (or the folder which the model is saved
    in)
    * Name: “bracing_assignments.csv”
* Format of the import file for bracing assignment:
    * 1st column: Panel Name
    * 2nd column: Bracing Group Name

    .. image:: images/format-bracing-assignment.png
    * Note: No header required
* The *Bracing Assignment* table will be filled as seen below.
.. image:: images/bracing-assignment-table.png

7.2 Assign Member Section to Members
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
* Go to *Section Assignment*
* Click “Import .csv” and select
    * Directory: “C:\Users\<Your Name>\Downloads” (or the folder which the model is saved in)
    * Name: “section_assignments.csv”
* Format of the import file for section assignment:
    * 1st column: Member ID in SAP2000 model
        * Note: Need to obtain directly from SAP2000
    * 2nd column: Section Group Name
    .. image:: images/format-section-assignment.png
    
* In this tutorial, section assignment is not required. Thus, select all section assignments and click |minus| to delete.
* Press OK to return to the main window.

8. Generate Tower
------------------------------------
This section details the steps to generate tower designs.

8.1 Generate Towers
~~~~~~~~~~~~~~~~~~~~~~~~~
* Go to *Analysis -> Generate Towers/* click |generatetower-24x24|.
* The *Generate Tower* dialog shown below will appear.
.. image:: images/generate-tower.png
* Press OK to return to the main window.

8.2 Additional Information
~~~~~~~~~~~~~~~~~~~~~~~~~
* All possible tower designs will be generated based on the permutations of selected bracing designs/member sections and the associated panels/member IDs.
* In our case, there is one bracing group that contains two bracing designs, including “double_x” and “x”. This bracing group is assigned to all panels. Therefore, a total of two tower designs will be generated.
* Open the input table file in File Explorer.
    * Directory: “C:\Users\<Your Name>\Downloads” (or the folder which the model is saved
    in)
    * Name: “inputTable.csv”
* The following table should appear in Excel.
.. image:: images/format-input-table.png

* Format of input table:
    * towerNumber: the number ID of the tower.
    * Variable-<XXX>: the bracing design/member section in variable group XXX that was used
    in the tower.
    * Panel <X>: the bracing design that was assigned to panel X.

9. Run Tower
------------------------------------
This section details the steps to model and run analysis on all the tower designs in SAP2000.

9.1 Run Towers
~~~~~~~~~~~~~~~~~~~~~~~~~
* Go to *Analysis -> Run Towers/* click |runtower-24x24|.
* The *Run Towers* dialog shown below will appear.
  .. image:: images/run-towers.png
    
  * SAP2000 Path
      * Must match the SAP2000.exe installed on your computer.
  * Nodes to Analyze
      * Format: <ID1>,<ID2>,<ID2>...
      * Enter the IDs of nodes of interest, typically the roof nodes.
      * Maximum accelerations and displacements will be measured from these nodes.
      * Node IDs need to be obtained from the previously selected SAP2000 model.
      * Note: May be ignored if “Ground Motion” is unchecked in Project Settings.
  * Footprint (sq in)
      * Total footprint of the tower.
  * Total Height (in)
      * Total height of the tower.
  * Total Mass (kg)
      * Total mass/weights on the tower.
  * Ground Motion Identifier
      * Maximum acceleration, displacement and base shear are obtained when the
      tower is subjected to load combinations containing the identifier/keyword (e.g.
      D+GM1-NS)
      * Note: May be ignored if “Ground Motion” is unchecked in Project Settings.

* Verify if the SAP2000 Path is correct. Do not change other inputs.
* Click “Run Now”.
* The Build Towers dialog shown below will appear.
.. image:: images/build-towers.png
* After completing the analysis:
.. image:: images/build-towers-2.png
* Close the *Build Towers* dialog and open the plot of tower performances.
.. image:: images/tower-performances.png
    





EMAIL_MESSAGE = """
Hi Adriana,

I hope this message finds you well. I would like to bring to your attention a few critical points regarding the preparation of files for LION system upload and adherence to labor regulations at specific locations. 
•	No formula in files: Please ensure that all formulas and links are removed from the files. Such elements may lead to issues during the automatic upload to LION. Below are some guidelines for preparing the files:
o	No empty headers between columns.
o	Headers must be consistent and preferably in English, as they will be programmed.
o	Avoid formulas or links to other files; they may function on your laptop but not elsewhere.
•	Location code consistency: The location codes used in the movements must match those available in a separate locations file and be consistent with the codes in ROCS. Any discrepancies, such as using CDG_h when runtimes data utilizes CDG, will lead to errors.
•	Colocated movements: We need to decide on handling movements like "CDG_h -> CDG". Should these be included in the final output or omitted?
For your reference, I have placed the lion-minimum-data.xlsx file in the shared folder. It serves as an example of the desired final data format. Hovering over the headers will provide explanations for each column, and additional comments are available for further clarification. Feel free to contact me via Teams or email if you have any questions. 
Labor regulations in LION: Please note that LION considers the following labor regulations that may affect scheduling and planning: 
•	Maximum legal driving time per shift is 9 hours; working time is 12 hours.
•	Non-driving turn-around time of 15 minutes is required before departure, affecting the period of availability (POA). POA is used by the local authorities to assign the driver to other tasks outside LION schedule
•	Driving turn-around time of 10 minutes is allocated upon arrival, counted as driving time.
•	Drivers must wait at least 25 minutes between consecutive movements, termed turn-around time. This can vary per location
•	Each shift begins and ends with a 30-minute debriefing period, included in working time calculations.
•	Drivers must return to their base location after each shift; empty movements may be added to extend shifts cost-effectively and accommodate this requirement.
•	A 60-minute break is mandatory every 4.5 hours of driving, and a 30-minute break every 6 hours of working, unless a 60-minute break has been taken.
•	Breaks must occur at a location, with sufficient transfer time between movements to accommodate them.
Please let me know if you require further clarification. 
"""
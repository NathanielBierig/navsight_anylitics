# import pandas as pd
# def add_blank_values(row):
#     if 'FRAME_ACQUIRED' in row[1]:
#         commas = ', ' * 12
#         row = str(row) + commas
#
#     return row
# def temp_sped_func():
#     df = pd.read_csv('3GpsLog.csv')
#     df = df.apply(lambda row: add_blank_values(row), axis=1)
#     df.to_csv('3GpsLog.csv', index=False)
# import csv
#
# def add_commas_to_frame_acquired_rows(input_file, output_file):
#     with open(input_file, 'r') as infile, open(output_file, 'w', newline='') as outfile:
#         reader = csv.reader(infile)
#         writer = csv.writer(outfile)
#
#         for row in reader:
#             if not any("FRAME_ACQUIRED" in cell for cell in row):
#                 # Add 12 commas to rows containing "FRAME_AQUIRED"
#
#                 writer.writerow(row)
#
# input_csv_file = "3GpsLog.csv"  # Replace with your input CSV file name
# output_csv_file = "3GpsLogAVL.csv"  # Replace with your desired output CSV file name
#
# add_commas_to_frame_acquired_rows(input_csv_file, output_csv_file)
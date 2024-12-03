import pandas as pd
from datetime import datetime, time

def load(user):
    # Initialize an empty list to store attendance data
    attendance_data = []

    # Load the existing Excel file if it exists
    excel_file_path = 'attendance_example_with_datetime.xlsx'
    try:
        existing_df = pd.read_excel(excel_file_path)
        attendance_data = existing_df.to_dict('records')
    except FileNotFoundError:
        print('hello')
        pass

    # Load the existing list of names if it exists
    name_list = set()
    for entry in attendance_data:
        name_list.add(entry['Name'])

    # Get the current time
    current_time = datetime.now().time()

    # Loop to collect attendance data from the user
    name = user
    if name:
        if current_time <= time(10, 30):
            attendance = "Present"
        else:
            attendance = "Absent"
        name_list.add(name)
    else:
        attendance = "Absent"

    attendance_data.append({'Name': name, 'Attendance': attendance, 'DateTime': datetime.now()})

    # Create a DataFrame from the collected data
    df = pd.DataFrame(attendance_data)

    # Export DataFrame to Excel
    df.to_excel(excel_file_path, index=False)

    print(f"Excel file '{excel_file_path}' updated successfully.")
    
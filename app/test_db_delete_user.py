from db import delete_user

employee_number = "60002"

deleted = delete_user(employee_number)

if deleted:
    print(f"Deleted employee {employee_number}")
else:
    print(f"No employee found with employee number {employee_number}")
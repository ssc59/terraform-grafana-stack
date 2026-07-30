from worker import process_employee
from threading import Thread




def run_employee_worker(employee_number):
    thread = Thread(
        target=process_employee,
        args=(employee_number,),
        daemon=False,
        name=f"employee-{employee_number}",
    )

    thread.start()
    return thread

#run_employee_worker("60001")
run_employee_worker("60002")
#run_employee_worker("60003")



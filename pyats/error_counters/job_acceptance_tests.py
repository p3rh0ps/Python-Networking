import os
from genie.testbed import load

def main(runtime):

    # ----------------
    # Load the testbed
    # ----------------

    if not runtime.testbed:
        # If no testbed is provided, load the default one.
        # Load default location of testbed
        testbedfile = os.path.join('testbed.yml')
        testbed = load(testbedfile)
    else:
        # Use the one provided
        testbed = runtime.testbed

    # Find the location of the script in relation to the job file
    testscript = os.path.join(os.path.dirname(__file__), 'automation_acceptance_tests.py')

    # run script
    runtime.tasks.run(testscript=testscript, testbed=testbed)


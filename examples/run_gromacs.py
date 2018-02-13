
from __future__ import print_function

from time import sleep
import cerise_client.service as cc
import os

# Create a new service for user myuser, with given cluster credentials
env = os.environ
# srv = cc.require_managed_service(
#     'cerise-mdstudio-das5-myuser', 29593,
#     'mdstudio/cerise-mdstudio-das5:develop',
#     os.environ['CERISE_DAS5_USERNAME'],
#     os.environ['CERISE_DAS5_PASSWORD'])

srv = cc.require_managed_service(
    'cerise-mdstudio-gt-myuser', 29593,
    'mdstudio/cerise-mdstudio-gt:develop',
    os.environ['CERISE_GT_USERNAME'],
    os.environ['CERISE_GT_PASSWORD'])


cc.start_managed_service(srv)

sleep(10)
print(srv.get_log())

# Create a job and set workflow and inputs
print("Creating job")
job = srv.create_job('decompose_include')
job.set_workflow('protein_ligand.cwl')
job.add_input_file('protein_file', 'protein.pdb')
job.add_input_file('protein_top', 'protein.top')
job.add_input_file('ligand_file', 'compound.pdb')
job.add_input_file('topology_file', 'compound_ref.itp')
job.set_input('sim_time', 0.001)
job.set_input('residues', [28,29,65,73,74,75,76,78,80,81,82,83,84,85,86,87,88,89,90,91,92,93,94,100,103,104,107,108,111,115,128,156,159,160,161,162,163,164,165,166,167,168,170,171,172,176,183,184,185,186,187,188,189,190,191,192,193,194,195,196,197,198,199,200,201,204,219,220,221,223,224,225,226,227,228,230,231,250,275,276,277,278,279,280,281,282,283,284,285,286,287,288,289,290,291,292,293,294,295,339,342,343,346,347,348,349,350,351,352,353,354,355,374,375,376,377,378,379,382,415,416,417,418,419,420,422,423,424,425,426,427,428,429,430,431,432,433,434,435,438,460,461,462,463,464,465,466,467,468,470,481])


# Secondary files
job.add_secondary_file('protein_top', 'ref_conf_1-posre.itp')
job.add_secondary_file('protein_top', 'attype.itp')
job.add_secondary_file('topology_file', 'compound_ref-posre.itp')

# Start it
print("Running job")
job.run()

# Give the service a chance to stage things
print("Waiting")
while job.state == 'Waiting':
    sleep(1)

# store this somewhere, in a database
persisted_srv = cc.service_to_dict(srv)
persisted_job_id = job.id          # this as well

# # Stop the service
# cc.stop_managed_service(srv)

# # Here, you would quit Python, shut down the computer, etc.
# # To resume where we left off
# srv = cc.service_from_dict(persisted_srv)
# if not cc.managed_service_is_running(srv):
#     cc.start_managed_service(srv)

# job = srv.get_job_by_id(persisted_job_id)

# Wait for job to finish
while job.is_running():
    sleep(3)

# Process output
# Process output
if job.state == 'Success':
    file_formats = {
        "gromitout": "{}.out",
        "gromiterr": "{}.err",
        "gromacslog2": "{}.out",
        "gromacslog3": "{}.out",
        "gromacslog4": "{}.out",
        "gromacslog5": "{}.out",
        "gromacslog6": "{}.out",
        "gromacslog7": "{}.out",
        "gromacslog8": "{}.out",
        "gromacslog9": "{}.out",
        "energy_edr":  "{}.edr",
        "energy_dataframe": "{}.ene",
        "energyout": "{}.out",
        "energyerr": "{}.err",
        "decompose_dataframe": "{}.ene",
        "decompose_err": "{}.err",
        "decompose_out": "{}.out"}

    # Save all data about the simulation
    outputs = job.outputs
    for key, fmt in file_formats.items():
        if key in outputs:
            file_object = outputs[key]
            file_object.save_as(fmt.format(key))
else:
    print('There was an error: ' + job.state)
    print(job.log)

# Clean up the job and the service
srv.destroy_job(job)
cc.destroy_managed_service(srv)

from __future__ import print_function

from time import sleep
import os

import cerise_client.service as cc


# Create a new service for user myuser, with given cluster credentials
srv = cc.require_managed_service(
        'cerise-mdstudio-das5-myuser', 29593,
        'mdstudio/cerise-mdstudio-das5:develop',
        os.environ['CERISE_DAS5_USERNAME'],
        os.environ['CERISE_DAS5_PASSWORD'])
cc.start_managed_service(srv)

# Create a job and set workflow and inputs
print("Creating job")
job = srv.create_job('example_job')
job.set_workflow('md_workflow.cwl')
job.add_input_file('protein_pdb', 'CYP19A1vs.pdb')
job.add_input_file('protein_top', 'CYP19A1vs.top')
job.add_input_file('protein_itp', 'CYP19A1vs-posre.itp')
job.add_input_file('ligand_pdb', 'BHC89.pdb')
job.add_input_file('ligand_top', 'BHC89.itp')
job.add_input_file('ligand_itp', 'BHC89-posre.itp')
job.add_input_file('include_itp', 'attype.itp')
job.set_input('force_field', 'amber99SB')
job.set_input('sim_time', 0.001)

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

# Stop the service
cc.stop_managed_service(srv)

# Here, you would quit Python, shut down the computer, etc.
# To resume where we left off
srv = cc.service_from_dict(persisted_srv)
if not cc.managed_service_is_running(srv):
    cc.start_managed_service(srv)

job = srv.get_job_by_id(persisted_job_id)

# Wait for job to finish
while job.is_running():
    sleep(3)

# Process output
if job.state == 'Success':
    job.outputs['trajectory'].save_as('CYP19A1vs_BHC89.trr')
    job.outputs['energy'].save_as('energy.out')
else:
    print('There was an error: ' + job.state)
    print(job.log)
    job.outputs['energyout'].save_as('energy.out')
    job.outputs['energyerr'].save_as('energy.err')

# Clean up the job and the service
srv.destroy_job(job)
cc.destroy_managed_service(srv)

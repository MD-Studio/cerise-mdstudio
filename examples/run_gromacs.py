from __future__ import print_function

from time import sleep
import cerise_client.service as cc
import os

# Create a new service for user myuser, with given cluster credentials
env = os.environ
srv = cc.require_managed_service(
        'cerise-mdstudio-das5-myuser', 29593,
        'mdstudio/cerise-mdstudio-das5:develop',
        os.environ['CERISE_DAS5_USERNAME'],
        os.environ['CERISE_DAS5_PASSWORD'])
cc.start_managed_service(srv)

# Create a job and set workflow and inputs
print("Creating job")
job = srv.create_job('decompose_include')
job.set_workflow('md_workflow.cwl')
job.add_input_file('protein_pdb', 'protein.pdb')
job.add_input_file('protein_top', 'protein.top')
job.add_input_file('ligand_pdb', 'compound.pdb')
job.add_input_file('ligand_top', 'compound_ref.itp')
job.set_input('sim_time', 0.001)
job.set_input('residues', "28,29,65,73")
job.set_input('force_field', 'amber99SB')

# Secondary files
job.add_secondary_file('protein_top', 'ref_conf_1-posre.itp')
job.add_secondary_file('protein_top', 'attype.itp')
job.add_secondary_file('ligand_top', 'compound_ref-posre.itp')

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
    job.outputs['trajectory'].save_as('protein.trr')
    job.outputs['energy'].save_as('protein.edr')
    job.outputs['energy_dataframe'].save_as('energy.ene')
    job.outputs['decompose_dataframe'].save_as('decompose.ene')
else:
    print('There was an error: ' + job.state)
    print(job.log)

# Clean up the job and the service
srv.destroy_job(job)
cc.destroy_managed_service(srv)


from __future__ import print_function

from time import sleep
import cerise_client.service as cc
import os

# Create a new service for user myuser, with given cluster credentials
env = os.environ
srv = cc.require_managed_service(
    'scientist_das5', 29593,
    # 'mdstudio/cerise-mdstudio-das5:develop',
    'cerise-das5:test',
    os.environ['CERISE_DAS5_USERNAME'],
    os.environ['CERISE_DAS5_PASSWORD'])

# srv = cc.require_managed_service(
#     'scientist_binac', 29593,
#     'mdstudio/cerise-mdstudio-binac:develop',
#     os.environ['CERISE_BINAC_USERNAME'],
#     os.environ['CERISE_BINAC_PASSWORD'])

# srv = cc.require_managed_service(
#     'scientist_gt', 29593,
#     'mdstudio/cerise-mdstudio-gt:develop',
#     os.environ['CERISE_GT_USERNAME'],
#     os.environ['CERISE_GT_PASSWORD'])

# Start a new service
cc.start_managed_service(srv)

# Create a job and set workflow and inputs
print("Creating job")
job = srv.create_job('thermodynamic_int')
job.set_workflow('lambda_points.cwl')

files = {
    'min_mdp_file': 'data/em_steep_0.mdp',
    'min_gro_file': 'data/start.gro',
    'min_top_file': 'data/topo.top'}

for key, file_path in files.items():
    job.add_input_file(key, file_path)

job.set_input('openmp_thread', 1)
# Secondary files
# job.add_secondary_file('protein_top', 'ref_conf_1-posre.itp')

# Start it
print("Running job")
job.run()

# Give the service a chance to stage things
print("Waiting")
print(srv.get_log())
while job.state == 'Waiting':
    sleep(1)

# # store this somewhere, in a database
# persisted_srv = cc.service_to_dict(srv)
# persisted_job_id = job.id          # this as well

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
if job.state == 'Success':
    print("good")
    # file_formats = {
    #     "decompose_err": "{}.err",
    #     "decompose_out": "{}.out"}

    # # Save all data about the simulation
    # outputs = job.outputs
    # for key, fmt in file_formats.items():
    #     if key in outputs:
    #         file_object = outputs[key]
    #         file_object.save_as(fmt.format(key))
else:
    print('There was an error: ' + job.state)
    print(job.log)

# Clean up the job and the service
srv.destroy_job(job)
cc.destroy_managed_service(srv)

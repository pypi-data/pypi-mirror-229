import json
import re
import zipfile
import os
import sys
import certifi
import urllib3.request
import requests

job_server = os.environ.get('JOB_SERVER_URL')

def get_launch_args():
    """
    Method to return job_type_id and job_id from the parameters used to launch a script from the command line.
   
    Returns
    ---------
    out: job_type_id, job_id
        Returns a tuple that contains the job_type_id and job_id
   
    """

    if(len(sys.argv) < 2):
        raise Exception("Expecting at least two launch args, including one with a comma delimitted job_type_id and job_id")

    parts = sys.argv[1].split(',')

    if(len(parts) != 2):
        raise Exception("Launch argument must be a comma delimitted string that include job type id and job id")

    return parts[0], parts[1]

def set_job_status(job_type_id: str, job_id: str, status: str):
    """
    Set job to current status, this will also post a push notification
    to send updates to any subscribed clients.

    Parameters
    ----------
    job_type_id : string
       The job type id to update the status, for jobs running reports this is the report id

    job_id: string
        The job id to update the percentage completion for the job that is being executed.
    
    """

    if(job_server is None):
        raise Exception("Missing environment variable [JOB_SERVER_URL]")
    
    status_url = '%s/api/job/%s/%s/%s' % (job_server, job_type_id, job_id, status)
    print(status_url)
    r = requests.get(status_url)
    if(r.status_code > 299):
        raise Exception("Error setting job status %s - Http Code %d (%s)" % (status, r.status_code, r.content))

def set_job_progress(job_type_id, job_id, percent_complete):
    """
    Update job the job progress percent, this will also post a push
    notification to sned updates to any subscribed clients.

    Parameters
    ----------
    job_type_id: string
       The job_type_id to update the percentage completed for reports this is the report id

    job_id: string
        The job_id to update the percentage completion for the job that is being executed.
    """

    if(job_server is None):
        raise Exception("Missing environment variable [JOB_SERVER_URL]")

    r = requests.get('%s/api/job/%s/%s/progress/%d' % (job_server, job_type_id, job_id, percent_complete))
    if(r.status_code > 299):
       raise Exception("Error setting job error message: Http Response Code: %d" % r.status_code)

def add_job_error(job_type_id, job_id, error_message):
    """
    Called when a job has an error, will log that error on the server and notify the user
   
    Parameters
    ----------
    job_type_id: string
       The job_type_id to update the percentage completed for reports this is the report id

    job_id: string
        The job_id to update the percentage completion for the job that is being executed.
   
    error_message: string
        Error message to be logged and reported to the user
    """

    output = {
        "jobTypeId": job_type_id,
        "jobId": job_id,
        "success": False,
        "error": error_message
    }

    if(job_server is None):
        raise Exception("Missing environment variable [JOB_SERVER_URL]")

    r = requests.post('%s/api/job/failed' % job_server, json=output)   
    if(r.status_code > 299):
       raise Exception("Error writing job error Http Error Code %d" % r.status_code)
    
def complete_job(job_type_id, job_id, artifactType, artifactUrl, artifactId, executionTimeSeconds):
    """
    Called when a job has an error, will log that error on the server and notify the user
   
    Parameters
    ----------
    job_type_id: string
       The job_type_id to update the percentage completed for reports this is the report id

    job_id: string
        The job_id to update the percentage completion for the job that is being executed.
   
    artifactType: string
        Type of artifact

    artifactUrl: string
        URL of the output artifactt

    artifactId: string
        id of the outtput artifact

    executionTimeSeconds
        Time taken to run the job
    """

    output = {
        "jobTypeId": job_type_id,
        "jobId": job_id,
        "success": True,
        "executionTimeSeconds": executionTimeSeconds,
        "artifactType": artifactType,
        "artifactUrl": artifactUrl,
        "artifactId": artifactId
    }

    if(job_server is None):
        raise Exception("Missing environment variable [JOB_SERVER_URL]")

    r = requests.post('%s/api/job/completed' % job_server, json=output)   
    if(r.status_code > 299):
       raise Exception("Error writing job error Http Error Code %d" % r.status_code)
   
def get_job(job_type_id: str, job_id: str):
    """
    Download a job, a job consists of the information necessary to build a report or process data
    
    Parameters
    ----------
    job_type_id: string
        The job_type_id is the defintion of what needs to be done for this job.

    job_id: string
        The job_id is the instance of the job that should be executed.
   
    Returns
    ----------
    out : job, parameters
        Tuple to include a job and the parmaters that can be used for the execution of the job.
    """

    set_job_status(job_type_id, job_id, "Running")

    if(job_server is None):
        raise Exception("Missing environment variable [JOB_SERVER_URL]")

    getJobUri = job_server + '/api/job/' + job_type_id + '/' + job_id
   
    r = requests.get(getJobUri)
    if(r.status_code > 299):
        raise Exception("Could not get job details for job type id=%s and job id=%s" % (job_type_id, job_id))

    job = json.loads(r.text)
    reportParameters = json.loads(job["payload"])
    return job, reportParameters


def get_script_file(output_dir, script_id, revision_id):
    """
    Get a script file, or collection of files that make up the scripts necessry to execute
    a job or a report.  If the script is a collection of files it will be downloaded as a zip
    file an extracted in the directory provided.

    If a zip file is downloaded, the file that has the method start_job will be returned.

    If the directory already exists, it will use the existing script file.

    Parameters
    ---------

    output_dir:
        Base directory of where the file(s) should be downloaded.

    script_id: string
        ID of the script that will be downloaded

    revision_id: string;
        Revision of the report to be downloade

    Returns
    ---------
    out: string
        Returns the name of the script file that can be loaded and executed
    
    """
    if os.path.exists(output_dir):
        print("Script directory %s exists, checking it for module with start_job." % output_dir)
        sys.path.append(output_dir)

        files = os.listdir(output_dir)
        for file in files:
            script_file_name, file_extension = os.path.splitext(file)
            if(file_extension.lower() == ".py"):
                module = __import__(script_file_name)
                if(callable(getattr(module, "start_job", None))):
                    return script_file_name

        sys.path.remove(output_dir)

        print("Could not find script file that implements start_job")

        raise Exception("Could not find script file that implements start_job")
 
    print("Script directory doesn't exist, downloading now.")

    # If we made it here, that means the file doesn't exists locally so download it.

    path = "/api/report/%s/runtime/%s" % (script_id, revision_id)

    url = "%s%s" % (job_server, path)
    print("Downloading script %s" % url)

    http = urllib3.PoolManager(cert_reqs='CERT_REQUIRED', ca_certs=certifi.where())
    r = http.request("GET", url, preload_content=False)

    if r.status > 299:
        print('Failed http %d url: %s' % (r.status, url))
        print('--------------------------------------------------------------------------------')
        print()
        r.release_conn()
        return None

    print("Downloaded script %s" % url)
    
    m = re.search('filename=?([\w\.\-]*)',r.headers['Content-Disposition'])
    fileName = m.group(1)
    fullOutput = "%s/%s" % (output_dir, fileName)

    print("Script file name %s" % fileName)
    print("Full output for file %s" % fullOutput)

    os.makedirs(output_dir)
    with open(fullOutput, 'wb') as out:
        while True:
            data = r.read(65535)
            if not data:
                break
        
            out.write(data)
    r.release_conn()

    if r.headers["Content-Type"] == "application/zip":
        with zipfile.ZipFile(fullOutput, 'r') as zip_ref:
            zip_ref.extractall(output_dir)

        os.remove(fullOutput)
        
        # add the output directory so we can attempt to load all the files
        # via __import__
        sys.path.append(output_dir)

        files = os.listdir(output_dir)
        for file in files:
            script_file_name, file_extension = os.path.splitext(file)
            if(file_extension.lower() == ".py"):
                module = __import__(script_file_name)
                if(callable(getattr(module, "start_job", None))):
                    # we found the file so now remove it the path, it will get added
                    # back in later.
                    sys.path.remove(output_dir)
                    fullScriptFileName = "%s/%s" % (output_dir, file)
                    revisionFileName = "%s/%s.py" % (output_dir, revision_id)

                    os.rename(fullScriptFileName, revisionFileName)
                    
                    return revision_id

        
        sys.path.remove(output_dir)

        raise Exception("Could not find script file that implements start_job")
    else:
        script_file_name, file_extension = os.path.splitext(fileName)
        fullScriptFileName = "%s/%s" % (output_dir, fileName)
        revisionFileName = "%s/%s.py" % (output_dir, revision_id)

        os.rename(fullScriptFileName, revisionFileName)
              
        return revision_id
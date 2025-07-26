import os
import tempfile
from celery import shared_task
from .models import Submission, Problem
import subprocess

LANGUAGE_CONFIG = {
    'python': {
        'image': 'python:3.10-slim',
        'run_cmd': 'python /code/user_code.py',
        'file_name': 'user_code.py',
    },
    'cpp': {
        'image': 'gcc:latest',
        'run_cmd': 'g++ /code/user_code.cpp -o /code/a.out && /code/a.out',
        'file_name': 'user_code.cpp',
    },
    'java': {
        'image': 'openjdk:latest',
        'run_cmd': 'javac /code/UserCode.java && java -cp /code UserCode',
        'file_name': 'UserCode.java',
    },
}

@shared_task
def run_code_job(language, code, stdin, shared_dir):
    """
    Hybrid code execution that can switch between subprocess and Kubernetes
    based on USE_KUBERNETES environment variable
    """
    # Check if we should use Kubernetes execution
    use_kubernetes = os.environ.get('USE_KUBERNETES', 'false').lower() == 'true'
    
    if use_kubernetes:
        return run_code_job_kubernetes(language, code, stdin, shared_dir)
    else:
        return run_code_job_subprocess(language, code, stdin, shared_dir)

def run_code_job_subprocess(language, code, stdin, shared_dir):
    """
    Execute code using subprocess (for Render, local development, etc.)
    """
    config_obj = LANGUAGE_CONFIG.get(language.lower())
    if not config_obj:
        return {'error': 'Unsupported language'}
    
    try:
        # Create temporary directory for code execution
        with tempfile.TemporaryDirectory() as temp_dir:
            code_path = os.path.join(temp_dir, config_obj['file_name'])
            with open(code_path, 'w') as f:
                f.write(code)
            
            input_path = os.path.join(temp_dir, 'input.txt')
            with open(input_path, 'w') as f:
                f.write(stdin)
            
            # Execute code based on language
            if language.lower() == 'python':
                result = subprocess.run(
                    ['python', code_path],
                    input=stdin,
                    capture_output=True,
                    text=True,
                    timeout=10,
                    cwd=temp_dir
                )
            elif language.lower() == 'cpp':
                # Compile C++ code
                compile_result = subprocess.run(
                    ['g++', code_path, '-o', os.path.join(temp_dir, 'a.out')],
                    capture_output=True,
                    text=True,
                    timeout=10,
                    cwd=temp_dir
                )
                if compile_result.returncode != 0:
                    return {'error': f'Compilation error: {compile_result.stderr}'}
                
                # Run compiled code
                result = subprocess.run(
                    [os.path.join(temp_dir, 'a.out')],
                    input=stdin,
                    capture_output=True,
                    text=True,
                    timeout=10,
                    cwd=temp_dir
                )
            elif language.lower() == 'java':
                # Compile Java code
                compile_result = subprocess.run(
                    ['javac', code_path],
                    capture_output=True,
                    text=True,
                    timeout=10,
                    cwd=temp_dir
                )
                if compile_result.returncode != 0:
                    return {'error': f'Compilation error: {compile_result.stderr}'}
                
                # Run compiled Java code
                class_name = config_obj['file_name'].replace('.java', '')
                result = subprocess.run(
                    ['java', class_name],
                    input=stdin,
                    capture_output=True,
                    text=True,
                    timeout=10,
                    cwd=temp_dir
                )
            else:
                return {'error': 'Unsupported language'}
            
            # Return results
            if result.returncode == 0:
                return {'output': result.stdout}
            else:
                return {'error': f'Runtime error: {result.stderr}'}
                
    except subprocess.TimeoutExpired:
        return {'error': 'Time limit exceeded'}
    except Exception as e:
        return {'error': f'Execution error: {str(e)}'}

def run_code_job_kubernetes(language, code, stdin, shared_dir):
    """
    Execute code using Kubernetes pods (for production, GKE, etc.)
    """
    try:
        # Import Kubernetes libraries only when needed
        from kubernetes import client, config
        import time
    except ImportError:
        return {'error': 'Kubernetes libraries not installed. Install with: pip install kubernetes'}
    
    config_obj = LANGUAGE_CONFIG.get(language.lower())
    if not config_obj:
        return {'error': 'Unsupported language'}
    
    try:
        # Create shared directory
        os.makedirs(shared_dir, exist_ok=True)
        code_path = os.path.join(shared_dir, config_obj['file_name'])
        with open(code_path, 'w') as f:
            f.write(code)
        input_path = os.path.join(shared_dir, 'input.txt')
        with open(input_path, 'w') as f:
            f.write(stdin)
        
        # Load Kubernetes config
        try:
            config.load_kube_config()
        except Exception:
            try:
                config.load_incluster_config()
            except Exception as e:
                return {'error': f'Kubernetes config error: {str(e)}'}
        
        batch_v1 = client.BatchV1Api()
        job_name = f"oj-job-{int(time.time()*1000)}"
        
        # Security context for the container
        security_context = client.V1SecurityContext(
            run_as_user=1000,
            run_as_group=3000,
            allow_privilege_escalation=False,
            capabilities=client.V1Capabilities(drop=["ALL"]),
            read_only_root_filesystem=True
        )
        
        run_cmd = config_obj['run_cmd']
        container = client.V1Container(
            name="runner",
            image=config_obj['image'],
            command=["/bin/sh", "-c", run_cmd],
            resources=client.V1ResourceRequirements(
                limits={"cpu": "1", "memory": "256Mi"},
                requests={"cpu": "0.2", "memory": "128Mi"}
            ),
            volume_mounts=[client.V1VolumeMount(
                mount_path="/code",
                name="code-volume"
            )],
            security_context=security_context,
            stdin=True,
            tty=False
        )
        
        volume = client.V1Volume(
            name="code-volume",
            host_path=client.V1HostPathVolumeSource(
                path=shared_dir
            )
        )
        
        pod_spec = client.V1PodSpec(
            containers=[container],
            restart_policy="Never",
            volumes=[volume],
            security_context=client.V1PodSecurityContext(
                run_as_non_root=True,
                seccomp_profile=client.V1SeccompProfile(type="RuntimeDefault")
            )
        )
        
        template = client.V1PodTemplateSpec(
            metadata=client.V1ObjectMeta(labels={"job-name": job_name}),
            spec=pod_spec
        )
        
        job_spec = client.V1JobSpec(
            template=template,
            backoff_limit=0,
            active_deadline_seconds=10
        )
        
        job = client.V1Job(
            api_version="batch/v1",
            kind="Job",
            metadata=client.V1ObjectMeta(name=job_name),
            spec=job_spec
        )
        
        # Create the job
        batch_v1.create_namespaced_job(
            body=job,
            namespace="default"
        )
        
        core_v1 = client.CoreV1Api()
        pod_name = None
        
        # Wait for pod to be created
        for _ in range(30):
            pods = core_v1.list_namespaced_pod(
                namespace="default",
                label_selector=f"job-name={job_name}"
            )
            if pods.items:
                pod_name = pods.items[0].metadata.name
                pod_phase = pods.items[0].status.phase
                if pod_phase in ['Running', 'Succeeded', 'Failed']:
                    break
            time.sleep(1)
        
        if not pod_name:
            batch_v1.delete_namespaced_job(
                name=job_name,
                namespace="default",
                body=client.V1DeleteOptions(propagation_policy='Foreground')
            )
            return {'error': 'Pod not created'}
        
        # Wait for job completion
        for _ in range(15):
            job_status = batch_v1.read_namespaced_job_status(job_name, "default")
            pods = core_v1.list_namespaced_pod(
                namespace="default",
                label_selector=f"job-name={job_name}"
            )
            pod_phase = pods.items[0].status.phase if pods.items else None
            
            if job_status.status.succeeded:
                try:
                    logs = core_v1.read_namespaced_pod_log(
                        name=pod_name, namespace="default")
                except Exception:
                    logs = ''
                batch_v1.delete_namespaced_job(
                    name=job_name,
                    namespace="default",
                    body=client.V1DeleteOptions(propagation_policy='Foreground')
                )
                return {'output': logs}
            elif job_status.status.failed:
                try:
                    logs = core_v1.read_namespaced_pod_log(
                        name=pod_name, namespace="default")
                except Exception:
                    logs = ''
                batch_v1.delete_namespaced_job(
                    name=job_name,
                    namespace="default",
                    body=client.V1DeleteOptions(propagation_policy='Foreground')
                )
                return {'error': 'Runtime Error', 'logs': logs}
            time.sleep(1)
        
        batch_v1.delete_namespaced_job(
            name=job_name,
            namespace="default",
            body=client.V1DeleteOptions(propagation_policy='Foreground')
        )
        return {'error': 'Time Limit Exceeded'}
        
    except Exception as e:
        return {'error': f'Kubernetes execution error: {str(e)}'}
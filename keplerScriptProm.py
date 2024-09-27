import subprocess
import requests
import time

NAMESPACE = 'kepler'
POD_NAME = 'kepler-94mcm'
PORT = 9102

def port_forward_pod(namespace, pod_name, port):
    command = [
        'kubectl', 'port-forward',
        f'pod/{pod_name}', f'{port}:{port}', '-n', namespace
    ]
    return subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

def fetch_metrics(port):
    url = f'http://localhost:{port}/metrics'
    response = requests.get(url)
    response.raise_for_status()
    return response.text

def main():
    pf_process = port_forward_pod(NAMESPACE, POD_NAME, PORT)
    try:
        time.sleep(2)
        
        metrics = fetch_metrics(PORT)
        print(metrics)
        
        with open('kepler-metrics.txt', 'w') as file:
            file.write(metrics)
            
    except Exception as e:
        print(f'Error: {e}')
    finally:
        pf_process.terminate()

if __name__ == "__main__":
    main()
import json
import os
import requests
from kubernetes import client, config

def make_prometheus_request(query):
    params = {
        'query': query
    }
    return float(requests.get(PROMETHEUS_URL, params=params).json()['data']['result'][0]['value'][1])

folder = "prometheus_metrics_OB"
metricResults = "istio_total_metrics_TEST.json"
jsonOut = os.path.join(folder, metricResults)

# Load kubeconfig and initialize client
config.load_kube_config()
v1 = client.AppsV1Api()

# Specify the namespace
namespace = "online-boutique"

# List services in the specified namespace
services = v1.list_namespaced_deployment(namespace)

# Prometheus server URL
PROMETHEUS_URL = 'http://localhost:9090/api/v1/query'

results = []
servicesList = []
for svc in services.items:
    print(svc.metadata.name)
    servicesList.append(svc.metadata.name)

pairs = [(svc1, svc2) for i, svc1 in enumerate(servicesList) for svc2 in servicesList[i+1:]]

for svc1, svc2 in pairs:
    try:
        my_dest2 = f'{svc2}.online-boutique.svc.cluster.local'
        
        requestVolume = f'avg(increase(istio_requests_total{{app="{svc1}", destination_service="{my_dest2}", destination_service_namespace="{namespace}"}}[1m]))'
        responseRequestVolume = make_prometheus_request(requestVolume)

        requestDurationSum = f'avg(rate(istio_request_duration_milliseconds_sum{{app="{svc1}", destination_service="{my_dest2}", destination_service_namespace="{namespace}"}}[1m]))'
        responseRequestDurationSum = make_prometheus_request(requestDurationSum)

        requestDurationCount = f'avg(rate(istio_request_duration_milliseconds_count{{app="{svc1}", destination_service="{my_dest2}", destination_service_namespace="{namespace}"}}[1m]))'
        responseRequestDurationCount = make_prometheus_request(requestDurationCount)

        requestSizeSum = f'avg(rate(istio_request_bytes_sum{{app="{svc1}", destination_service="{my_dest2}", destination_service_namespace="{namespace}"}}[1m]))'
        responseRequestSizeSum = make_prometheus_request(requestSizeSum)

        requestSizeCount = f'avg(rate(istio_request_bytes_count{{app="{svc1}", destination_service="{my_dest2}", destination_service_namespace="{namespace}"}}[1m]))'
        responseRequestSizeCount = make_prometheus_request(requestSizeCount)

        requestThroughput = f'avg(rate(istio_requests_total{{app="{svc1}", destination_service="{my_dest2}", destination_service_namespace="{namespace}"}}[1m]))'
        responseRequestThroughput = make_prometheus_request(requestThroughput)

        responseSizeSum = f'avg(rate(istio_response_bytes_sum{{app="{svc1}", destination_service="{my_dest2}", destination_service_namespace="{namespace}"}}[1m]))'
        responseResponseSizeSum = make_prometheus_request(responseSizeSum)

        responseSizeCount = f'avg(rate(istio_response_bytes_count{{app="{svc1}", destination_service="{my_dest2}", destination_service_namespace="{namespace}"}}[1m]))'
        responseResponseSizeCount = make_prometheus_request(responseSizeCount)

        responseThroughput = f'avg(rate(istio_response_messages_total{{app="{svc1}", destination_service="{my_dest2}", destination_service_namespace="{namespace}"}}[1m]))'
        responseResponseThroughput = make_prometheus_request(responseThroughput)

        reqDuration = responseRequestDurationSum / responseRequestDurationCount
        reqSize = responseRequestSizeSum / responseRequestSizeCount
        resSize = responseResponseSizeSum / responseResponseSizeCount

        measurement = {"source": svc1, "destination": svc2, "requestVolume": responseRequestVolume, "requestDuration": reqDuration, "requestSize": reqSize, "requestThroughput": responseRequestThroughput, "responseSize": resSize, "responseThroughput": responseResponseThroughput}
        results.append(measurement)
        
    except IndexError:
        pass

for svc1, svc2 in pairs:
    try:
        my_dest1 = f'{svc1}.online-boutique.svc.cluster.local'

        requestVolume = f'avg(increase(istio_requests_total{{app="{svc2}", destination_service="{my_dest1}", destination_service_namespace="{namespace}"}}[1m]))'
        responseRequestVolume = make_prometheus_request(requestVolume)

        requestDurationSum = f'avg(rate(istio_request_duration_milliseconds_sum{{app="{svc2}", destination_service="{my_dest1}", destination_service_namespace="{namespace}"}}[1m]))'
        responseRequestDurationSum = make_prometheus_request(requestDurationSum)

        requestDurationCount = f'avg(rate(istio_request_duration_milliseconds_count{{app="{svc2}", destination_service="{my_dest1}", destination_service_namespace="{namespace}"}}[1m]))'
        responseRequestDurationCount = make_prometheus_request(requestDurationCount)

        requestSizeSum = f'avg(rate(istio_request_bytes_sum{{app="{svc2}", destination_service="{my_dest1}", destination_service_namespace="{namespace}"}}[1m]))'
        responseRequestSizeSum = make_prometheus_request(requestSizeSum)

        requestSizeCount = f'avg(rate(istio_request_bytes_count{{app="{svc2}", destination_service="{my_dest1}", destination_service_namespace="{namespace}"}}[1m]))'
        responseRequestSizeCount = make_prometheus_request(requestSizeCount)

        requestThroughput = f'avg(rate(istio_requests_total{{app="{svc2}", destination_service="{my_dest1}", destination_service_namespace="{namespace}"}}[1m]))'
        responseRequestThroughput = make_prometheus_request(requestThroughput)

        responseSizeSum = f'avg(rate(istio_response_bytes_sum{{app="{svc2}", destination_service="{my_dest1}", destination_service_namespace="{namespace}"}}[1m]))'
        responseResponseSizeSum = make_prometheus_request(responseSizeSum)

        responseSizeCount = f'avg(rate(istio_response_bytes_count{{app="{svc2}", destination_service="{my_dest1}", destination_service_namespace="{namespace}"}}[1m]))'
        responseResponseSizeCount = make_prometheus_request(responseSizeCount)

        responseThroughput = f'avg(rate(istio_response_messages_total{{app="{svc2}", destination_service="{my_dest1}", destination_service_namespace="{namespace}"}}[1m]))'
        responseResponseThroughput = make_prometheus_request(responseThroughput)

        reqDuration = responseRequestDurationSum / responseRequestDurationCount
        reqSize = responseRequestSizeSum / responseRequestSizeCount
        resSize = responseResponseSizeSum / responseResponseSizeCount

        measurement = {"source": svc2, "destination": svc1, "requestVolume": responseRequestVolume, "requestDuration": reqDuration, "requestSize": reqSize, "requestThroughput": responseRequestThroughput, "responseSize": resSize, "responseThroughput": responseResponseThroughput}
        results.append(measurement)

    except IndexError:
        pass

with open(jsonOut, 'w') as f:
    json.dump(results, f, indent=4)

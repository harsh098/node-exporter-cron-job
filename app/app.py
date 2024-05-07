from kubernetes import client, config
from dotenv import load_dotenv
import os, sys
import requests
from typing import List, Dict
import asyncio
import datetime
import logging


load_dotenv()
LOGS_DIR = os.path.join(os.curdir, "logs") 
ENV=os.environ.get("ENV", "cluster")
SERVICE_NAME=os.environ.get("SERVICE_NAME", "node-exporter")
NAMESPACE=os.environ.get("NAMESPACE", "default")
PORT=os.environ.get("PORT", "9100")
logging.basicConfig(level = logging.INFO)
logger=logging.getLogger(__name__)
logger.setLevel(logging.INFO)

if ENV=="dev":
    config.load_kube_config()
    logger.info(ENV)
    logger.info(SERVICE_NAME)
    logger.info(NAMESPACE)
    logger.info(f"KUBECONFIG={os.environ.get('KUBECONFIG', 'not set')}")
    if os.environ.get("KUBECONFIG", "") and os.path.exists(os.environ.get("KUBECONFIG")):
        logger.info("KUBECONFIG FOUND")
    else:
        logger.critical("Missing Kubeconfig")
else:
    config.load_incluster_config()


v1 = client.CoreV1Api()

def get_endpoint_info(service_name: str, namespace: str) -> List[Dict[str, str]]:
    """
    This function retrieves endpoint IP and nodeNames for a given Service Name.

    Args:
        service_name: The name of the Kubernetes service.

    Returns:
        A dictionary containing endpoint IP and corresponding node names.
    """

    endpoints = v1.read_namespaced_endpoints(service_name, namespace)
    endpoints_info = []
    for subset in endpoints.subsets:
        for address in subset.addresses:
            ip = address.ip
            nodeName = address.node_name
            endpoints_info.append({"ip": ip, "node_name": nodeName})
            logger.info(f"[INFO]Discovered {nodeName} at {ip}")
    
    return endpoints_info

def __get_logs_data(ip: str, port: str) -> str:
    """
    Makes a GET request to the provided URL (http://{ip}:{port}/metrics) and returns the response.

    Args:
        ip (str): The IP address of the Node-Exporter Pod.
        port (str): The port number on which the Node-Exporter Pod is listening.

    Returns:
        requests.Response: The response object from the GET request, or None if an error occurs.
    """

    url = f"http://{ip}:{port}/metrics"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching metrics: {e}")
        sys.exit(1)
        

def fetch_and_store_logs_data(ip: str, node_name: str, port: str) -> None:
    """
    Fetch Logs and Write data to log files
    Args:
        ip (str): IP Address of the Node-Exporter Pod
        node_name (str): Name of K8s node
        port (str): The port number on which the Node-Exporter Pod is listening.
    Returns:
        None
    """
    data = __get_logs_data(ip, port)
    time = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    try:
        filepath = os.path.join(LOGS_DIR, f"{node_name}-{time}.log")
        with open(filepath, "w+") as f:
            f.write(data)
    except:
        sys.exit(1)

async def pull_logs_data(endpoints_info: List[Dict[int, int]]):
    loop = asyncio.get_event_loop()
    tasks = []
    for endpoint in endpoints_info:
        tasks.append(loop.run_in_executor(None, fetch_and_store_logs_data, endpoint["ip"], endpoint["node_name"], PORT))
    await asyncio.gather(*tasks)

if __name__ == '__main__':
    try:
        endpoints = get_endpoint_info(service_name=SERVICE_NAME, namespace=NAMESPACE)
        asyncio.run(pull_logs_data(endpoints))
    except Exception as e:
        logger.fatal(f"Fatal Error Occured: {e}")
        sys.exit(1)
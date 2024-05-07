### Step -1 Install Prometheus Operator
This will install the prometheus-operator which is required to run the node-exporter.
```helm upgrade --install prometheus-operator prometheus-community/kube-prometheus-stack --namespace node-exporter --values operator-values.yml --create-namespace```
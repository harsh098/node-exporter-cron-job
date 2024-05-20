## Testing the code for Cron Job Before running on actual K8s Cluster

### Preflight Checks
Make sure the cluster you are trying to access is configured on your `~/.kube/config` file and the correct context is set using the
`kubectl config use-context <context name>`

### Step 1: Copy the `.env.example` file to `.env` as configure the vars as instructed

1. Copy the file
   ```
   cp .env.example .env
   ```
2. Edit the file parameters as shown
   ```
   vi .env
   ```

### Step 2: Run the docker compose file
```
docker compose up
```
On success the container will exit with `status code 0`

### Step 3: Destroy the containers

```
docker compose down
```

   

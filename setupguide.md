# Setup Guide

`git clone [szegedai/shunqa](https://github.com/szegedai/SHunQA.git)`
`git checkout dockerization`
`docker compose up`

## Elastic and Kibana

Copy the elastic container's ID:

```sh
docker container ls
```

Enter the docker container:

```shell
docker exec -it <CONTAINER_ID> bash
```

Generate and save password for 'elastic' user:

```shell
cd /opt/bitnami/elasticsearch/bin
elasticsearch-reset-password -u elastic
```

Copy the password to [.env](.env) -> `ELASTIC_PASSWORD`

Generate Service token for Kibana:

```shell
elasticsearch-service-tokens create elastic/kibana kibana-token
```

Copy the service token to [.env](.env) -> `KIBANA_ELASTICSEARCH_SERVICEACCOUNTTOKEN`.

Restart your Kibana container afterwards. You can generate an API Token with the Kibana UI.

```shell
docker container restart <CONTAINER_ID>
```

To avoid losing the current password do not down the containers.

## Frontend

1. Change the [.env](.env) `NUXT_APP_CDN_URL` variable into the URL that the site runs on. For example if you access the site at `https://ai.inf.u-szeged.hu/demo/qa/` it should be that.
2. The `FRONTEND_ELASTIC_TABLES` env variable should be parsed in however if it's not the case, change it in the `frontend/nuxt.config.ts`. In theory this should be more strings with , between them.
3. Change the `apiUrl` in the `frontend/nuxt.config.ts` to the `example/api` for example if you access the site at `https://ai.inf.u-szeged.hu/demo/qa/` it should be `https://ai.inf.u-szeged.hu/demo/qa/api`.
[Unit]
Description={{ item.name }}

[Install]
WantedBy=default.target

[Container]
Image=ghcr.io/warpstreamlabs/bento:1.15
ContainerName={{ item.name }}
Network=metabase.network
{% for env in item.envs -%}
Environment={{ env.name }}={{ env.value }}
{% endfor -%}
Environment=NATS_HOST={{ analytic_nats_host }}
Environment=NATS_STREAM={{ item.nats_stream }}
Volume=/etc/bento/{{ item.name }}.yml:/bento.yaml:ro,z

[Service]
Restart=on-failure

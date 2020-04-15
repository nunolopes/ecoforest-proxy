# ecoforest-proxy
proxy server for Ecoforest and Netflame stoves

## run
```
python ecoforest-proxy.py
```

## Docker compose
```
ecoforest-proxy:  
    build: ./ecoforest_proxy/
    container_name: ecoforest
    restart: always
    ports:
      - 8998:8998
```

## Home Assistant config

```
sensor:
  - platform: rest
    name: ecoforest
    resource: 'http://192.168.0.254:8998/ecoforest/fullstats'
    method: 'GET'
    scan_interval: 10
    force_update: true
    json_attributes:
      - temperatura
      - consigna_potencia
      - modo_func
      - modo_operacion
      - state
      - on_off
      - consigna_temperatura
      - estado
      - error_MODO_on_off
  - platform: template
    sensors:
      ecoforest_status:
        entity_id: sensor.ecoforest
        friendly_name: "Status"
        value_template: "{{ state_attr('sensor.ecoforest', 'state') }}"
      ecoforest_temp:
        entity_id: sensor.ecoforest
        friendly_name: "Temperature"
        unit_of_measurement: "°C"
        value_template: "{{ state_attr('sensor.ecoforest', 'consigna_temperatura') }}"
      ecoforest_potencia:
        entity_id: sensor.ecoforest
        friendly_name: "Power"
        value_template: "{{ state_attr('sensor.ecoforest', 'consigna_potencia') }}"
      ecoforest_room_temp:
        entity_id: sensor.ecoforest
        friendly_name: "Room Temperature"
        unit_of_measurement: "°C"
        value_template: "{{ state_attr('sensor.ecoforest', 'temperatura') }}"
```

# ecoforest-proxy
proxy server for Ecoforest and Netflame stoves

## run
```
ECOFOREST_HOST=http://10.0.0.0 ECOFOREST_PASSWORD=pwd ECOFOREST_USERNAME=user python ecoforest-proxy.py
```

## Docker compose
```
ecoforest-proxy:  
    build: ./ecoforest_proxy/
    container_name: ecoforest
    restart: always
    environment:
      ECOFOREST_HOST: http://10.0.0.0
      ECOFOREST_PASSWORD: pwd
      ECOFOREST_USERNAME: user
    ports:
      - 8998:8998
```

## Home Assistant config (configuration.yaml)

```
You need to install this custom button card at:
https://github.com/jcwillox/lovelace-paper-buttons-row
(example in pictures at the end)


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

    - platform: rest
      name: ecoforestother
      resource: 'http://192.168.0.254:8998/ecoforest/otherstats'
      method: 'GET'
      scan_interval: 9
      force_update: true
      json_attributes:
        - Th
        - Da
        - Tp
        - Nh
        - Ne
        - Pn
        - Pf
        - Es
        - Ex
        - Ni
        - Co
        - Tn

    - platform: template
      sensors:
        ecoforest_gastemp:
          friendly_name: "Gas Temperature"
          unit_of_measurement: "°C"
          value_template: "{{ state_attr('sensor.ecoforestother', 'Th') }}"
        ecoforest_depression:
          friendly_name: "Depression"
          unit_of_measurement: "Pa"
          value_template: "{{ state_attr('sensor.ecoforestother', 'Da') }}"
        ecoforest_cpu:
          friendly_name: "CPU Temperature"
          unit_of_measurement: "°C"
          value_template: "{{ state_attr('sensor.ecoforestother', 'Tp') }}"
        ecoforest_hours:
          friendly_name: "Working Hours"
          value_template: "{{ state_attr('sensor.ecoforestother', 'Nh') }}"
        ecoforest_ignitions:
          friendly_name: "Ignitions"
          value_template: "{{ state_attr('sensor.ecoforestother', 'Ne') }}"
        ecoforest_livepulse:
          friendly_name: "Live Pulse"
          unit_of_measurement: "s"
          value_template: "{{ state_attr('sensor.ecoforestother', 'Pn') }}"
        ecoforest_pulseoffset:
          friendly_name: "Pulse Offset"
          unit_of_measurement: "s"
          value_template: "{{ state_attr('sensor.ecoforestother', 'Pf') }}"
        ecoforest_wstate:
          friendly_name: "Working State"
          value_template: "{{ state_attr('sensor.ecoforestother', 'Es') }}"
        ecoforest_extractor:
          friendly_name: "Extractor"
          unit_of_measurement: "%"
          value_template: "{{ state_attr('sensor.ecoforestother', 'Ex') }}"
        ecoforest_level:
          friendly_name: "Working Level"
          value_template: "{{ state_attr('sensor.ecoforestother', 'Ni') }}"
        ecoforest_convector:
          friendly_name: "Convector Air Flow"
          unit_of_measurement: "%"
          value_template: "{{ state_attr('sensor.ecoforestother', 'Co') }}"
        ecoforest_ntc:
          friendly_name: "NTC Probe Temperature"
          unit_of_measurement: "°C"
          value_template: "{{ state_attr('sensor.ecoforestother', 'Tn') }}"


switch:        
  - platform: template
    switches:
      ecoforest_switch:
        friendly_name: "Ecoforest On/Off"
        value_template: "{{ (is_state('sensor.ecoforest_status', 'on')) or (is_state('sensor.ecoforest_status', 'starting')) }}"
        turn_on:
          service: rest_command.ecoforest_onoff
          data:
            status: "on"
        turn_off:
          service: rest_command.ecoforest_onoff
          data:
            status: "off"

rest_command:
  ecoforest_powerdown:
    url: http://your_ip_address:8998/ecoforest/set_power?power=down
    method: GET
  ecoforest_powerup:
    url: http://your_ip_address:8998/ecoforest/set_power?power=up
    method: GET
  ecoforest_onoff:
    url: http://your_ip_address:8998/ecoforest/set_status?status={{ status }}
    method: GET
```

## Home Assistant UI Lovelace (ui-lovelace.yaml)
```
      - type: vertical-stack
        title: Heating
        show_header_toggle: false
        cards:
          - type: entities
            state_color: on
            entities:
              - entity: sensor.ecoforest_status
                secondary_info: last-changed
                icon: 'mdi:power'
              - entity: sensor.ecoforest_gastemp
                secondary_info: last-changed
              - entity: sensor.ecoforest_livepulse
                secondary_info: last-changed
              - entity: sensor.ecoforest_extractor
                secondary_info: last-changed
              - entity: sensor.ecoforest_ntc
                secondary_info: last-changed
          - type: gauge
            entity: sensor.ecoforest_potencia
            name: 'power'
            min: 0
            max: 9
            severity:
              green: 0
              yellow: 4
              red: 7
          - type: "custom:paper-buttons-row"
            buttons:
              - icon: "mdi:chevron-up"
                #name: "up"
                tap_action:
                  action: call-service
                  service: rest_command.ecoforest_powerup
                style: # These are the default styles that can be overridden by state styles.
                  button:
                    border-radius: 10px
                    font-size: 16px
                    background-color: var(--table-row-alternative-background-color)
              - icon: "mdi:power"
                name: false
                entity: switch.ecoforest_switch
                style:
                  button:
                    background-color: var(--table-row-alternative-background-color)
                    border-radius: 10px
                    font-size: 1.2rem
                    padding: 8px
                  icon:
                    width: 40px # make the icon bigger.
                    height: auto
                state_styles:
                  "on":
                    button:
                      background-color: var(--table-row-alternative-background-color)
                    icon:
                      #color: var(--paper-item-icon-active-color)
                      color: green
                  "off": # define a state then provide a style object.
                    button:
                      background-color: var(--table-row-alternative-background-color)
                    icon:
                      color: red
              - icon: "mdi:chevron-down"
                #name: "down"
                tap_action:
                  action: call-service
                  service: rest_command.ecoforest_powerdown
                style: # These are the default styles that can be overridden by state styles.
                  button:
                    border-radius: 10px
                    font-size: 16px
                    background-color: var(--table-row-alternative-background-color)
          - type: entities
            state_color: on
            entities:
              - entity: sensor.ecoforest_room_temp
                secondary_info: last-changed
                name: Room Temperature

```
<img src="example.jpg" width="400"/>
<img src="example_shutdown.jpg" width="400" />

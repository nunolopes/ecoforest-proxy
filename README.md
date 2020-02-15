# ecoforest-proxy
proxy server for Ecoforest stoves

  ecoforest-proxy:  
    build: ./ecoforest_proxy/
    container_name: ecoforest
    restart: always
    ports:
      - 8998:8998

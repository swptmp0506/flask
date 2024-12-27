services:
  web:
    image: furniture_inventory_app
    ports:
      - "5000:5000"
    volumes:
      # Mount templates directory so changes are instant
      - ./templates:/flask-json-app/templates
      # Mount uploads directory so photos are accessible
      - ./uploads:/flask-json-app/uploads
      # Mount the JSON file so you can view and edit it directly
      - ./furniture_inventory.json:/flask-json-app/furniture_inventory.json
    restart: unless-stopped

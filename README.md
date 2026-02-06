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

source myenv/bin/activate

python3 massive_flood.py --url "http://10.0.0.1/client?page=dashboard" --duration 120000 --threads 200

python3 massive_flood.py --url "http://10.0.0.1/client?page=dashboard" --duration 120000 --threads 2000
--countdown 30

--countdown 30 # 30-second countdown
--countdown 0 # Start immediately
--countdown 5 # Quick 5-second countdown

python3 extreme_flood.py --url "http://10.0.0.1" --min 5000 --max 15000 --duration 600

python3 portal_flood.py --url "http://10.0.0.1/client?page=dashboard" --users 1000 --no-variants

python3 portal_flood.py --url "http://10.0.0.1/client?page=dashboard" --duration 300 --users 1000 --no-variants

import csv, random
with open("data/metrics.csv","w",newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["cpu_usage","ram_usage","disk_usage"])
    for i in range(1000):
        cpu = random.uniform(10,60)
        ram = random.uniform(30,70)
        disk = random.uniform(40,80)
        if random.random()<0.05:
            cpu = random.uniform(90,100)
            ram = random.uniform(90,100)
            disk = random.uniform(90,100)
        writer.writerow([cpu,ram,disk])

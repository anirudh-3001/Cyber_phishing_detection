import csv

input_file = "tranco_1m.csv"
output_file = "tranco.txt"

count = 0

with open(input_file, newline="", encoding="utf-8") as csvfile:
    reader = csv.reader(csvfile)
    next(reader)  # skip header

    with open(output_file, "w", encoding="utf-8") as f:
        for row in reader:
            domain = row[1].strip()
            url = "https://" + domain
            f.write(url + "\n")
            count += 1

print("Extracted legitimate URLs:", count)

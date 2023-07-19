import os
import re
import sys
from csv import DictReader, DictWriter, field_size_limit
import xlrd
import xlwt
import xlutils.copy

field_size_limit(sys.maxsize)

def write(data: list[dict], filename=None, headers=None):
    if len(data) < 1:
        return
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    _, ext = os.path.splitext(filename)
    if str.startswith(ext, '.xl'):
        if os.path.exists(filename):
            wb_in: xlrd.Book = xlrd.open_workbook(filename)
            wb: xlwt.Workbook = xlutils.copy.copy(wb_in)
        else:
            wb: xlwt.Workbook = xlwt.Workbook()
            wb.add_sheet('Sheet1')
        ws: xlwt.Worksheet = wb.get_sheet(0)
        headers = headers or []
        for entry in data:
            for key in entry.keys():
                if key not in headers:
                    headers.append(key)
        for i, header in enumerate(headers):    
            ws.write(0, i, header)
        for i, entry in enumerate(data):
            for j, header in enumerate(headers):
                ws.write(i + 1, j, str(entry.get(header, None)))
        wb.save(filename)
    else:
        with open(filename, "w") as f:
            writer = DictWriter(f, fieldnames=headers or data[0].keys(), extrasaction='ignore')
            writer.writeheader()
            writer.writerows(data)
    print(f"Wrote to {filename}")

def read(filename, headers=None):
    if not os.path.exists(filename):
        return
    data: list[dict] = []
    with open(filename, "r") as f:
        _, ext = os.path.splitext(filename)
        if str.startswith(ext, '.xl'):
            ws: xlrd.sheet.Sheet = xlrd.open_workbook(filename).sheet_by_index(0)
            ite = iter(ws.get_rows())
            headers = [element.value for element in next(ite)]
            for entry in ite:
                entry = dict(zip(headers, [element.value for element in entry]))
                # Convert floats to ints since XLRD is weird
                for key in entry:
                    if isinstance(entry[key], float) and entry[key].is_integer():
                        entry[key] = int(entry[key])
                data.append(entry)
        else:
            reader = DictReader(f, fieldnames=headers)
            data.extend([row for row in reader])
    print(f"Read from {filename}")
    return data

def freq_write(report, filename):
    freqs = {}
    for issue in report:
        matches = re.findall(r'\b\w+\b', issue['title'].lower())
        for match in matches:
            freqs[match] = freqs[match] + 1 if match in freqs else 1
    freqs = dict(sorted(freqs.items(), key=lambda item: item[1], reverse=True))
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, "w") as f:
        f.write(f'word,count\n')
        for key in freqs:
            f.writelines(f'{key},{freqs[key]}\n')

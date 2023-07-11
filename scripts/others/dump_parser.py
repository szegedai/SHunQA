import mwxml

dump = mwxml.Dump.from_file(open("../data.xml"))
print(dump.site_info.name, dump.site_info.dbname)

counter = 0

with open("../data.txt", "w") as f:
    f.write("-" * 200 + "\n")
    for page in dump:
        counter += 1
        for revision in page:
            f.write(revision.text + "\n")
            f.write("-" * 200 + "\n")
        if counter == 100:
            break


with open("3000-traditional-hanzi.tsv", encoding="utf8") as srcf, open("3000-traditional-hanzi-output.tsv", mode="w", encoding="utf8") as outf:
    for line in srcf:
        try:
            line_list = line.split("\t")
            character = line_list[0]
            pinyin = line_list[4]
            meaning = line_list[6]
            vocabulary = line_list[7]
            vocabulary_pinyin = line_list[8]
            outf.write(f"{character}\t{pinyin}\t{meaning}\t{vocabulary}\t{vocabulary_pinyin}\n")
        except:
            print(line)

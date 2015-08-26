#!/usr/bin/env python
#coding=utf-8
import os, sys, argparse, re

g_header = "| Word | Definition |\n"
g_column = "|--------|--------|\n"
g_separator = "######  \n"
g_MarkdownExten = '.md'

def genVocaDict(inFile):

    if 'readme.md' == inFile.lower() or 'example.md' == inFile.lower():
        print("Skip: {}".format(inFile))
        return (None, None, None)

    with open(inFile, 'r') as f:
        article = f.read()

    if not article:
        print("Skip empty file: {}".format(inFile))
        return (None, None, None)

    vocas = re.findall(r"\[[^\[]*\]\[\d+\]", article)
    lines = article.split('\n')

    area_index = [i for i, s in enumerate(lines) if g_separator.replace('\n','') in s]
    
    if len(area_index) == 1:
        #article and reference 
        article_lines=lines[:area_index[0]]
        ref_lines=lines[area_index[0]+1:]
    elif len(area_index) == 2:
        #article, reference, and dictionary
        article_lines=lines[:area_index[0]]
        ref_lines=lines[area_index[0]+1:area_index[1]]
    else:
        print("Format Error: {}".format(inFile))
        return (None, None, None)

    #print("area_index : {}".format(area_index))
    ref_lines=filter(None, ref_lines) #remove empty line

    # vocabulary dic = {index, [voca, url, definition]}
    voca_dict = {}
    for v in vocas:
        index = v.split('][')[1].replace(']','')
        word = v.split('][')[0].replace('[','')  
        voca_dict[index]=word

    for v in ref_lines:
        if v.startswith("["):
            index = re.findall(r'(?<=\[)(\d*)(?=\])',v)
            url = re.findall(r'https?:\/\/.*?(?=\s)',v)
            desc = re.findall(r'"(.*?)"',v)
            word_str = voca_dict[index[0]]
            voca_dict[index[0]]=[word_str, url[0], desc[0]]

    return (article_lines, ref_lines, voca_dict)

def saveFile(file_name, article, ref_lines, dict_table):
    file_text='\n'.join(article) +'\n' + g_separator + '\n' + '\n'.join(ref_lines)+ '\n' + g_separator + '\n'
    file_text+= g_header + g_column

    for key in range(1, len(dict_table)+1):
        word_list = dict_table[str(key)]
        file_text+='|['+word_list[0]+']('+word_list[1]+') | '+word_list[2]+'|\n'
    
    #update markdown file.  
    with open(file_name, "w") as f:
        f.write(file_text)
    print("done : {}".format(file_name))

def buildWB(file_path, title, dict_table):
    wb_text = '_' + file_path + '_  \n' + '__'+ title.replace('#','') + '__  \n\n'
    wb_text += g_header + g_column

    for key in range(1, len(dict_table)+1):
        word_list = dict_table[str(key)]
        wb_text+='|['+word_list[0]+']('+word_list[1]+') | '+word_list[2]+'|\n'

    wb_text+='\n'
    return wb_text

def saveWB(file_name, wb_table):
    if not file_name.endswith(g_MarkdownExten):
        file_name += g_MarkdownExten 

    with open(file_name, "w") as f:
        f.write(wb_table)

    print("Save word banks to : {}".format(file_name))

def getMarkdownlist(dirPath):
    flist=[]
    for root, directories, filenames in os.walk(dirPath):
        for filename in filenames:
            if filename.endswith('.md'):
                flist.append(os.path.join(root,filename))

    return flist

def main():
    #force using utf-8 
    reload(sys)
    sys.setdefaultencoding('utf-8')

    parser = argparse.ArgumentParser(description='The vocabulary builder for language learning.')
    parser.add_argument('-i', '--input', dest="input", help='Input a markdown file or a folder', default=None, required=True)
    parser.add_argument('-b', '--bank', dest="bank", help='Build word bank to a single file', default=None)
    args = parser.parse_args()

    if os.path.isfile(args.input):
        art, ref, tb = genVocaDict(args.input)
        if art and ref and tb:
            saveFile(args.input, art, ref, tb)
            if args.bank:
                dict_table = buildWB(args.input, art[0], tb)
                saveWB(args.bank, dict_table)

    elif os.path.isdir(args.input):
        mdflist = getMarkdownlist(args.input)
        dict_table=''
        for f in mdflist:
            art, ref, tb = genVocaDict(f)
            if art and ref and tb:
                saveFile(f, art, ref, tb)
                if args.bank:
                    dict_table += buildWB(f, art[0], tb)

        if args.bank:
            saveWB(args.bank, dict_table)

    else:
        parser.print_help()
        return None


if __name__ == '__main__':
    main()


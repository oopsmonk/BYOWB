#!/usr/bin/env python
#coding=utf-8
import os, sys, argparse, re

g_header = "| Word | Definition |  \n"
g_column = "|--------|--------|  \n"
g_separator = "######  \n"

def genVocaDic(inFile):

    if 'readme.md' == inFile.lower() or 'example.md' == inFile.lower():
        print("Skip: {}".format(inFile))
        return None

    with open(inFile, 'r') as f:
        article = f.read()

    if not article:
        print("Empty file: {}".format(inFile))
        return None

    vocas = re.findall(r"\[[^\[]*\]\[\d+\]", article)
    lines = article.split('\n')

    area_index = [i for i, s in enumerate(lines) if g_separator.replace('\n','') in s]
    
    if not area_index:
        print("Format Error")
        return None
    elif len(area_index) == 1:
        #article and reference 
        article_lines=lines[:area_index[0]]
        ref_lines=lines[area_index[0]+1:]
    elif len(area_index) <= 2:
        #article, reference, and dictionary
        article_lines=lines[:area_index[0]]
        ref_lines=lines[area_index[0]+1:area_index[1]]
    else:
        print("Format Error")
        return None

    #print("area_index : {}".format(area_index))
    ref_lines=filter(None, ref_lines) #remove empty line

    # vocabulary dic = {index, [voca, url, definition]}
    voca_dic = {}
    for v in vocas:
        index = v.split('][')[1].replace(']','')
        word = v.split('][')[0].replace('[','')  
        voca_dic[index]=word

    for v in ref_lines:
        if v.startswith("["):
            index = re.findall(r'(?<=\[)(\d*)(?=\])',v)
            url = re.findall(r'https?:\/\/.*?(?=\s)',v)
            desc = re.findall(r'"(.*?)"',v)
            word_str = voca_dic[index[0]]
            voca_dic[index[0]]=[word_str, url[0], desc[0]]

    #gen dic text
    voca_text='  \n'.join(article_lines) +'  \n' + g_separator + '\n' + '  \n'.join(ref_lines)+ '  \n' + g_separator + '\n'
    voca_text+= g_header + g_column

    for key in range(1, len(voca_dic)+1):
        word_list = voca_dic[str(key)]
        voca_text+='|['+word_list[0]+']('+word_list[1]+') | '+word_list[2]+'|  \n'
    
    #update markdown file.  
    with open(inFile, "w") as f:
        f.write(voca_text)

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

    parser = argparse.ArgumentParser(description='Vocabulary builder for language learning.')
    parser.add_argument('-i', '--input', dest="input", help='Input a markdown file or a folder', default='',required=True)
    args = parser.parse_args()
    if os.path.isfile(args.input):
        genVocaDic(args.input)
    elif os.path.isdir(args.input):
        mdflist = getMarkdownlist(args.input)
        for f in mdflist:
            genVocaDic(f)
    else:
        parser.print_help()
        return None


if __name__ == '__main__':
    main()


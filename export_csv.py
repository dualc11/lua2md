from mdutils.mdutils import MdUtils
import luadata, sys, json, re, csv, os
from enum import Enum 

REMOVE_SPECIAL_CHARACTER_REG_EX = '[^A-Za-z0-9]+'

class Tag():
    def __init__(self, tagDict):
        self.enumTag = Enum('tag', tagDict)

    def addTag(self, newkey, newValue):
        newDict = {}
        for v in self.enumTag:
            newDict[v.name] = v.value 
        newDict[newkey] = newValue
        self.enumTag =  Enum('tag', newDict)

class Book:
    def __init__(self, rawBook, tag):
        self.rawBook = rawBook
        self.bookChapter = {}
        self.tagClass = tag
        self.tag = self.tagClass.enumTag

    def addHighlight(self, highlight):
        if highlight[self.tag.CHAPTER.value] in self.bookChapter.keys():
            self.bookChapter[highlight[self.tag.CHAPTER.value]].append(highlight)
        else:
            self.bookChapter[highlight[self.tag.CHAPTER.value]] = [highlight]

    def createBookChapter(self):
        for page, listHighlight in self.rawBook[self.tag.HIGHLIGHT.value].items():
            if listHighlight is None: 
                continue
            if hasOneHighlightPage(listHighlight):
                highlight = listHighlight[0]
                highlight = self.addPageHighlight(highlight, page)
                self.addHighlight(highlight)
            else : 
                for highlight in listHighlight: 
                    highlight = self.addPageHighlight(highlight, page)
                    self.addHighlight(highlight)

    def addPageHighlight(self, highlight, page):
        highlight[self.tag.REALPAGE.value] = page
        return highlight

def hasOneHighlightPage(listHighlight):
    return len(listHighlight) == 1

def initMdFile(file_name, title):
    mdFile = MdUtils(file_name=file_name, title=title)
    return mdFile

if __name__ == '__main__':
    readDir = sys.argv[1]
    writeDir = sys.argv[2]
    bookNames = []
    for subdir, dirs, files in os.walk(readDir):
        bookNames.append(dirs)
    print(bookNames[0])
    for bookName in bookNames[0]:
        print("Processing file:" + bookName)
        readFile = readDir+'/'+bookName+'/metadata.epub.lua'
        rawBook = luadata.read(readFile, encoding="utf-8")
        bookTag = {'CHAPTER' : "chapter",
            'HIGHLIGHT' : "highlight",
            'REALPAGE' : "realPage",
            "STATS" : "stats",
            "TITLE" : "title",
            "TEXT" : "text",
            "REALPAGE" : "realPage",
            "DOC_PROPS": "doc_props",
            "AUTHORS": "authors"
        }
        tag = Tag(bookTag)
        book = Book(rawBook = rawBook, tag = tag)
        book.createBookChapter()
        
        title = book.rawBook["doc_props"]["title"]
        authors = book.rawBook["doc_props"]["authors"]

        header = ["Highlight","Title","Author","URL","Note","Location","Date"]
        with open(writeDir+'/'+title+'.csv', 'w', encoding='UTF8') as f:
            writer = csv.writer(f)

            # write the header
            writer.writerow(header)
            for ch, hl in book.bookChapter.items():
                #print(ch)
                for h in hl:
                    data = [h[book.tag.TEXT.value], title, authors, "", "","",""]
                    # write the data
                    writer.writerow(data)
                #print("End chapter")
                  




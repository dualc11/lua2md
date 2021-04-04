from mdutils.mdutils import MdUtils
import luadata, sys, json, re 
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
    path = sys.argv[1]
    print("Processing file:" + path)
    #path = 'note.lua.lua'
    rawBook = luadata.read(path, encoding="utf-8")
    d = {'CHAPTER' : "chapter",
        'HIGHLIGHT' : "highlight",
        'REALPAGE' : "realPage",
        "STATS" : "stats",
        "TITLE" : "title",
        "TEXT" : "text",
        "REALPAGE" : "realPage"
    }
    tag = Tag(d)
    book = Book(rawBook = rawBook, tag = tag)
    book.createBookChapter()
    
    fileName = re.sub(REMOVE_SPECIAL_CHARACTER_REG_EX, "", str(rawBook["stats"]["title"]))

    mdFile_ = initMdFile(file_name = fileName, title = "Bookmarks form " + rawBook["stats"]["title"])

    for chapter, chapterhighlights in book.bookChapter.items():
        print("Processing chapter: " + chapter)
        mdFile_.new_header(level=1, title=chapter)
        for highlight in chapterhighlights:
            mdFile_.new_paragraph(""+highlight[book.tag.TEXT.value] + " - Page: "+ str(highlight[book.tag.REALPAGE.value]))
        mdFile_.new_paragraph()
    mdFile_.create_md_file()
                  




import jpype
try:
    import urllib.request as urllib2
except ImportError:
    import urllib2
import socket
import charade
import threading

socket.setdefaulttimeout(15)
lock = threading.Lock()

InputSource        = jpype.JClass('org.xml.sax.InputSource')
StringReader       = jpype.JClass('java.io.StringReader')
HTMLHighlighter    = jpype.JClass('de.l3s.boilerpipe.sax.HTMLHighlighter')
BoilerpipeSAXInput = jpype.JClass('de.l3s.boilerpipe.sax.BoilerpipeSAXInput')

from functools import wraps

def thread_safe(method):
    @wraps(method)
    def _impl(self, *args, **kwargs):
        try:
            # make it thread safe, see jpype documentation for more info
            if threading.activeCount() > 1:
                if jpype.isThreadAttachedToJVM() is False:
                    jpype.attachThreadToJVM()
            #lock.acquire()
            return method(self, *args, **kwargs)
        finally:
            #lock.release()
            pass
    return _impl

class Extractor(object):
    """
    Extract text. Constructor takes 'extractor' as a keyword argument,
    being one of the boilerpipe extractors:
    - DefaultExtractor
    - ArticleExtractor
    - ArticleSentencesExtractor
    - KeepEverythingExtractor
    - KeepEverythingWithMinKWordsExtractor
    - LargestContentExtractor
    - NumWordsRulesExtractor
    - CanolaExtractor
    """
    extractor = None
    source    = None
    data      = None
    headers   = {'User-Agent': 'Mozilla/5.0'}
    
    @thread_safe
    def __init__(self, extractor='DefaultExtractor', **kwargs):
        if extractor == "KeepEverythingWithMinKWordsExtractor":
            kMin = kwargs.get("kMin", 1)  # set default to 1
            self.extractor = jpype.JClass(
                    "de.l3s.boilerpipe.extractors."+extractor)(kMin)
        else:
            self.extractor = jpype.JClass(
                "de.l3s.boilerpipe.extractors."+extractor).INSTANCE

    @thread_safe
    def get(self, url=None, html=None):
        return self._process(url=url, html=html)

    @thread_safe
    def getText(self, url=None, html=None):
        source, data = self._process(html=html, url=url)
        return source.getContent()

    @thread_safe
    def getTextBlocks(self, url=None, html=None):
        source, data = self._process(html=html, url=url)
        blocks = source.getTextBlocks()
        results = []
        for i in range(blocks.size()):
            if blocks[i].isContent():
                results.append(blocks[i].getText())
        return results

    @thread_safe
    def getHTML(self, url=None, html=None):
        highlighter = HTMLHighlighter.newExtractingInstance()
        source, data = self._process(self, url=url, html=html)
        return highlighter.process(source, data)


    def _process(self, **kwargs):
        if kwargs.get('url'):
            request     = urllib2.Request(kwargs['url'], headers=self.headers)
            connection  = urllib2.urlopen(request)
            data        = connection.read()
            encoding    = connection.headers['content-type'].lower().split('charset=')[-1]
            if encoding.lower() == 'text/html':
                encoding = charade.detect(data)['encoding']
            if encoding is None:
                encoding = 'utf-8'
            data = str(data, encoding)
        elif kwargs.get('html'):
            data = kwargs['html']
            if not isinstance(data, str):
                data = str(data, charade.detect(data)['encoding'])
        else:
            raise Exception('No text or url provided')

        reader = StringReader(data)
        source = BoilerpipeSAXInput(InputSource(reader)).getTextDocument()
        self.extractor.process(source)
        return source, data
    
    def getImages(self, source, data):
        extractor = jpype.JClass("de.l3s.boilerpipe.sax.ImageExtractor").INSTANCE
        images = extractor.process(source, data)
        jpype.java.util.Collections.sort(images)
        # list comprehension returns 
        #   TypeError: iter() returned non-iterator of type 'java.util.ArrayList$Itr'
        # so do it the old way:
        results = []
        for i in range(images.size()):
            img = images[i]
            results.append({
                'src'   : img.getSrc(),
                'width' : img.getWidth(),
                'height': img.getHeight(),
                'alt'   : img.getAlt(),
                'area'  : img.getArea()
            })
        return results

import jpype
import socket
import threading

from bs4 import UnicodeDammit
import requests

socket.setdefaulttimeout(15)
lock = threading.Lock()

InputSource = jpype.JClass('org.xml.sax.InputSource')
StringReader = jpype.JClass('java.io.StringReader')
HTMLHighlighter = jpype.JClass('de.l3s.boilerpipe.sax.HTMLHighlighter')
BoilerpipeSAXInput = jpype.JClass('de.l3s.boilerpipe.sax.BoilerpipeSAXInput')

from functools import wraps

# suppress warning for invalid SSL certificates
requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)

#: Headers passed with each request
_DEFAULT_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.89 Safari/537.36'}

EXTRACTORS = [
    'DefaultExtractor',
    'ArticleExtractor',
    'ArticleSentencesExtractor',
    'KeepEverythingWithMinKWordsExtractor',  # if used, don't forget to pass the kMin argument to its constructor
    'KeepEverythingExtractor',
    'LargestContentExtractor',
    'NumWordsRulesExtractor',
    'CanolaExtractor'
]


def thread_safe(method):
    @wraps(method)
    def _impl(self, *args, **kwargs):
        try:
            # make it thread safe, see jpype documentation for more info
            if threading.activeCount() > 1:
                if jpype.isThreadAttachedToJVM() is False:
                    jpype.attachThreadToJVM()
            # lock.acquire()
            return method(self, *args, **kwargs)
        finally:
            # lock.release()
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
    source = None
    data = None
    headers = {'User-Agent': 'Mozilla/5.0'}

    @thread_safe
    def __init__(self, extractor='DefaultExtractor', **kwargs):
        if extractor == "KeepEverythingWithMinKWordsExtractor":
            kMin = kwargs.get("kMin", 1)  # set default to 1
            self.extractor = jpype.JClass(
                "de.l3s.boilerpipe.extractors." + extractor)(kMin)
        else:
            self.extractor = jpype.JClass(
                "de.l3s.boilerpipe.extractors." + extractor).INSTANCE

    @thread_safe
    def get(self, url=None, html=None):
        return self._process(url=url, html=html)

    @thread_safe
    def getText(self, url=None, html=None, processed=None):
        source, data = self._process(html=html, url=url, processed=processed)
        return source.getContent()

    @thread_safe
    def getTextBlocks(self, url=None, html=None, processed=None):
        source, data = self._process(html=html, url=url, processed=processed)
        blocks = source.getTextBlocks()
        results = []
        for i in range(blocks.size()):
            if blocks[i].isContent():
                results.append(blocks[i].getText())
        return results

    @thread_safe
    def getHTML(self, url=None, html=None, processed=None):
        source, data = self._process(html=html, url=url, processed=processed)
        highlighter = HTMLHighlighter.newExtractingInstance()
        return highlighter.process(source, data)

    def getImages(self, url=None, html=None, processed=None):
        if processed is not None:
            source, data = processed
        else:
            source, data = self.get(url=url, html=html)

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
                'src': img.getSrc(),
                'width': img.getWidth(),
                'height': img.getHeight(),
                'alt': img.getAlt(),
                'area': img.getArea()
            })
        return results

    def _process(self, **kwargs):
        if kwargs.get('processed'):
            source, data = kwargs.get('processed')
            return source, data
        if kwargs.get('url'):
            resp = requests.get(kwargs['url'], verify=False, stream=True, headers=_DEFAULT_HEADERS)
            data = self._convert(resp.content)
        elif kwargs.get('html'):
            data = kwargs['html']
            if not isinstance(data, str):
                data = self._convert(data)
        else:
            raise Exception('No text or url provided')

        reader = StringReader(data)
        source = BoilerpipeSAXInput(InputSource(reader)).getTextDocument()
        self.extractor.process(source)
        return source, data

    def _convert(self, content):
        converted = UnicodeDammit(content)
        if not converted.unicode_markup:
            raise UnicodeDecodeError(
                "Failed to detect encoding, tried [%s]", ', '.join(converted.tried_encodings))
        # print converted.original_encoding
        return converted.unicode_markup

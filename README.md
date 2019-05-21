# boilerpipe3
Python interface to Boilerpipe, Boilerplate Removal and Fulltext Extraction from HTML pages

Installation
============
You can install this lib directly from github repository by execute these command
    
    pip install git+ssh://git@github.com/derlin/boilerpipe3@master


Usage
=====

Be sure to have set JAVA_HOME properly since jpype depends on this setting.

The constructor takes a keyword argment ``extractor``, being one of the available boilerpipe extractor types:

- DefaultExtractor
- ArticleExtractor
- ArticleSentencesExtractor
- KeepEverythingExtractor
- KeepEverythingWithMinKWordsExtractor
- LargestContentExtractor
- NumWordsRulesExtractor
- CanolaExtractor

If no extractor is passed the DefaultExtractor will be used by default.

    from boilerpipe.extract import Extractor
    extractor = Extractor(extractor='ArticleExtractor')

Once you get an extractor instance, extract relevant content using one of `getText`, `getHTML`, `getTextBlock`, `getImages`. Each one accepts one of the following arguments: 

- `url`: the url of the page
- `html`: an html string to parse
- `processed`: the `(source, data)` returned by the method `get`.


Example:

    extracted_text = extractor.getText(url=your_url)
	
    extracted_html = extractor.getHTML(url=your_url)
    
If you need multiple information, you can save some computation time by doing:

    processed = extractor.get(url=url) # download and process once
    
    text = extractor.getText(processed=processed)
    text_blocks = extractor.getTextBlocks(processed=processed)
    html = extractor.getHTML(processed=processed)
    images = extractor.getImages(processed=processed)


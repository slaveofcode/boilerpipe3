# boilerpipe3
Python interface to Boilerpipe, Boilerplate Removal and Fulltext Extraction from HTML pages

Installation
============
You can install this lib directly from github repository by execute these command
    
    pip install git+ssh://git@github.com/derlin/boilerpipe3@master

Or from official pypi 

    pip install boilerpipe3

Configuration
=============

Dependencies:
jpype, charade

The boilerpipe jar files will get fetched and included automatically when building the package.

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

Once you get an extractor instance, extract relevant content using one of `getText`, `getHTML`. Each one accepts one of the following arguments: 

- `url`: the url of the page
- `html`: an html string to parse

Example:

    extracted_text = extractor.getText(url=your_url)
	
    extracted_html = extractor.getHTML(url=your_url)

To extract images, first parse the page|html string using `get` (same arguments as above + returns the parsed source and metadata), then call `getImages`. Oneline:

    extracted_images = extractor.getImages(*extractor.get(url=url))

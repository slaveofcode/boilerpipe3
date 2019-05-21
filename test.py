from boilerpipe import Extractor

urls = [
    "https://stackoverflow.com/questions/20996639/why-does-setup-py-develop-not-work",
    "http://www.hyperkommunikation.ch/personen/mani_matter_texte.htm",
    "https://www.freevap.ch/fr/ustensiles-diy-flacons-vides/111-flacon-diy-10ml.html",
    "https://fr.wikipedia.org/wiki/Codage_des_caract%C3%A8res#Europe"
]

extractor = Extractor()

for url in urls:
    html = extractor.getHTML(url)
    processed = extractor.get(url)
    print('%s :  %d chars, html:%d=url:%d=proc:%d text blocks, %d images.' % (
        url,
        len(extractor.getText(processed=processed)),
        len(extractor.getTextBlocks(html=html)),
        len(extractor.getTextBlocks(url=url)),
        len(extractor.getTextBlocks(processed=processed)),
        len(extractor.getImages(processed=processed))
    ))


import os
from glob import glob
from warnings import warn

from lxml import etree

from . import type
from .model import CitationStylesElement
from ...util import DATA_PATH


SCHEMA_PATH = os.path.join(DATA_PATH, 'csl', 'schema', 'csl.rng')
LOCALES_PATH = os.path.join(DATA_PATH, 'csl', 'locales')
STYLES_PATH = os.path.join(DATA_PATH, 'csl', 'styles')


NAMES = ['author', 'collection_editor', 'composer', 'container_author',
         'editor', 'editorial_director', 'illustrator', 'interviewer',
         'original_author', 'recipient', 'translator']

DATES = ['accessed', 'container', 'event_date', 'issued', 'original_date',
         'submitted']

NUMBERS = ['chapter_number', 'collection_number', 'edition', 'issue', 'number',
           'number_of_pages', 'number_of_volumes', 'volume']

VARIABLES = (['abstract', 'annote', 'archive', 'archive_location',
              'archive_place', 'authority', 'call_number', 'citation_label'
              'citation_number', 'collection_title', 'container_title',
              'container_title_short', 'dimensions', 'doi', 'event',
              'event_place', 'first_reference_note_number', 'genre', 'isbn',
              'issn', 'jurisdiction', 'keyword', 'locator', 'medium', 'note',
              'original_publisher', 'original_publisher_place', 'original_title',
              'page', 'page_first', 'pmid', 'pmcid', 'publisher',
              'publisher_place', 'references', 'section', 'source', 'status',
              'title', 'title_short', 'URL', 'version', 'year_suffix'] +
             NAMES + DATES + NUMBERS)

LOCALES = [os.path.basename(path)[8:-4]
           for path in glob(os.path.join(LOCALES_PATH, 'locales-*.xml'))]


class CitationStylesXML(object):
    def __init__(self, f):
        lookup = etree.ElementNamespaceClassLookup()
        namespace = lookup.get_namespace('http://purl.org/net/xbiblio/csl')
        namespace[None] = CitationStylesElement
        namespace.update(dict([(cls.__name__.replace('_', '-').lower(), cls)
                               for cls in CitationStylesElement.__subclasses__()]))

        self.parser = etree.XMLParser(remove_comments=True, encoding='UTF-8',
                                      no_network=True)
        self.parser.set_element_class_lookup(lookup)
        self.schema = etree.RelaxNG(etree.parse(SCHEMA_PATH))
        self.xml = etree.parse(f, self.parser)#, base_url=".")
        if not self.schema.validate(self.xml):
            err = self.schema.error_log
            #raise Exception("XML file didn't pass schema validation:\n%s" % err)
            warn("XML file didn't pass schema validation:\n%s" % err)
            # TODO: proper error reporting
        self.root = self.xml.getroot()


class CitationStylesLocale(CitationStylesXML):
    def __init__(self, locale):
        locale_path = os.path.join(LOCALES_PATH, 'locales-{}.xml'.format(locale))
        try:
            super().__init__(locale_path)
        except IOError:
            raise ValueError("'{}' is not a known locale".format(style))


class CitationStylesStyle(CitationStylesXML):
    def __init__(self, style, locale='en-US'):
        try:
            if not os.path.exists(style):
                style = os.path.join(STYLES_PATH, '{}.csl'.format(style))
        except TypeError:
            pass
        try:
            super().__init__(style)
        except IOError:
            raise ValueError("'{}' is not a known style".format(style))
        self.root.set_locale_list(locale)

    def render_citation(self, reference, **options):
        return self.root.citation.render(reference)

    def render_bibliography(self, references, **options):
        return self.root.bibliography.render(references)


##class CitationStylesBibliographyFormatter(BibliographyFormatter):
##    def __init__(self, style, locale='en-US'):
##        self.style = Style(style).root
##        self.locale = Locale(locale)
##    READ "Locale Prioritization"
##    def format_citation(self, references):
##        try:
##            references = self.style.citation.sort(references)
##        except AttributeError:
##            pass
##
####        try:
####            index = self.bibliography.index(reference)
####            return StyledText('[{}]'.format(index + 1))
####        except:
####            return StyledText('[ERROR]')
##
##    def format_bibliography(self, target):
##        items = []
##        heading = Heading('References', style=acknowledgement_heading_style)
##        target.add_flowable(heading)
##        for i, ref in enumerate(self.bibliography):
##            authors = ['{} {}'.format(name.given_initials(), name.family)
##                       for name in ref.author]
##            authors = ', '.join(authors)
##            item = '[{}]&nbsp;{}, "{}", '.format(i + 1, authors, ref.title)
##            item += Emphasized(ref['container_title'])
##            item += ', {}'.format(ref.issued.year)
##            items.append(item)
##            paragraph = Paragraph(item, style=bibliographyStyle)
##            target.add_flowable(paragraph)
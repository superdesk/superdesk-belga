import logging
from .belga_newsml_1_2 import BelgaNewsMLOneFeedParser
from superdesk.io.registry import register_feed_parser
from superdesk.publish.formatters.newsml_g2_formatter import XML_LANG
from .base_belga_newsml_1_2 import SkipItemException
logger = logging.getLogger(__name__)


class BelgaTipNewsMLOneFeedParser(BelgaNewsMLOneFeedParser):
    """Feed Parser which can parse specific Belga News ML xml files."""

    NAME = 'belgatipnewsml12'

    label = 'Belga Tip News ML 1.2 Parser'

    SUPPORTED_ASSET_TYPES = ('TIP',)

    def parser_newsitem(self, newsitem_el):
        """
        Parse Newsitem element.

        Example:

         <NewsItem xml:lang="fr">
            <Identification>
                ....
            </Identification>
            <NewsManagement>
                ....
            </NewsManagement>
            <NewsComponent>
                ....
            </NewsComponent>
          </NewsItem>

        :param newsitem_el:
        :return:
        """
        # Identification
        self._item_seed.update(
            self.parser_identification(newsitem_el.find('Identification'))
        )

        # NewsManagement
        self._item_seed.update(
            self.parser_newsmanagement(newsitem_el.find('NewsManagement'))
        )

        # NewsComponent
        news_component_1 = newsitem_el.find('NewsComponent')
        if news_component_1 is not None:
            # Genre from NewsComponent 1st level
            for element in news_component_1.findall('DescriptiveMetadata/Genre'):
                if element.get('FormalName'):
                    # genre CV
                    self._item_seed.setdefault('subject', []).append({
                        "name": element.get('FormalName'),
                        "qcode": element.get('FormalName'),
                        "scheme": "genre"
                    })

            # NewsComponent 2nd level
            # NOTE: each NewsComponent of 2nd level is a separate item with unique GUID
            for news_component_2 in news_component_1.findall('NewsComponent'):
                # create an item
                item = {**self._item_seed, 'guid': self._item_seed.get("date_id")}

                # NewsComponent
                try:
                    self.parser_newscomponent(item, news_component_2)
                except SkipItemException:
                    continue

                # type
                self.populate_fields(item)

                self._items.append(item)

    def parser_newscomponent(self, item, newscomponent_el):
        """
        Parse NewsComponent in NewsItem element.

        Example:

        <NewsComponent>
          <NewsLines>
              <DateLine xml:lang="fr">Paris, 9 déc 2018 (AFP) -</DateLine>
            <HeadLine xml:lang="fr">Un an après, les fans de Johnny lui rendent hommage à Paris</HeadLine>
            <NewsLine>
              <NewsLineType FormalName="ProductLine"/>
              <NewsLineText xml:lang="fr">(Photo+Live Video+Video)</NewsLineText>
            </NewsLine>
          </NewsLines>
          <AdministrativeMetadata>
            <Provider>
              <Party FormalName="AFP"/>
            </Provider>
          </AdministrativeMetadata>
          <DescriptiveMetadata>
            ....
          </DescriptiveMetadata>
          <ContentItem>
            ....
          </ContentItem>
        </NewsComponent>

        :param item:
        :param component_el:
        :return:
        """
        # Role
        role = newscomponent_el.find('Role')
        if role is not None:
            role_name = role.attrib.get('FormalName')
            if not (role_name and role_name.upper() in self.SUPPORTED_ASSET_TYPES):
                logger.warning('NewsComponent/Role/FormalName is not supported: "{}". '
                               'Skiping an "{}" item.'.format(role_name, item['guid']))
                raise SkipItemException
        else:
            logger.warning('NewsComponent/Role was not found. Skiping an "{}" item.'.format(
                item['guid']
            ))
            raise SkipItemException

        # language
        item['language'] = newscomponent_el.attrib.get(XML_LANG)

        # NewsLines
        newslines_el = newscomponent_el.find('NewsLines')
        self.parser_newslines(item, newslines_el)

        # AdministrativeMetadata
        admin_el = newscomponent_el.find('AdministrativeMetadata')
        self.parser_administrativemetadata(item, admin_el)

        # DescriptiveMetadata
        descript_el = newscomponent_el.find('DescriptiveMetadata')
        self.parser_descriptivemetadata(item, descript_el)

        # get 3rd level NewsComponent
        # body_html, headline, abstract
        for formalname, item_key in (('Body', 'body_html'), ('Title', 'headline'), ('Lead', 'abstract')):
            role = newscomponent_el.find('NewsComponent/Role[@FormalName="{}"]'.format(formalname))
            if role is not None:
                newscomponent = role.getparent()
                datacontent = newscomponent.find('ContentItem/DataContent')
                _format = newscomponent.find('ContentItem/Format')

                if datacontent is not None and _format is not None:
                    if datacontent.text:
                        item[item_key] = datacontent.text.strip()

                        if item_key == 'body_html':
                            item[item_key] = self._plain_to_html(item[item_key])
                else:
                    logger.warning('Mimetype or DataContent was not found. Skiping an "{}" item.'.format(
                        item['guid']
                    ))
                    raise SkipItemException
        if not item.get('body_html'):
            item['body_html'] = item.get('headline')
        return item


register_feed_parser(BelgaTipNewsMLOneFeedParser.NAME, BelgaTipNewsMLOneFeedParser())

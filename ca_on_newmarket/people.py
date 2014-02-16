from pupa.scrape import Scraper

from utils import lxmlize, CanadianLegislator as Legislator, CONTACT_DETAIL_TYPE_MAP, CONTACT_DETAIL_NOTE_MAP

import re

COUNCIL_PAGE = 'http://www.newmarket.ca/en/townhall/contactinformationmayorandtowncouncil.asp'


class NewmarketPersonScraper(Scraper):

  def get_people(self):
    page = lxmlize(COUNCIL_PAGE)

    councillors = page.xpath('//div[@id="printArea"]//table//tr//td')[4:-1]
    for councillor in councillors:
      if councillor == councillors[0]:
        yield self.scrape_mayor(councillor)
        continue
      name = councillor.xpath('.//a/text()')[0]
      district = councillor.xpath('.//strong/text()')[1].replace('Councillor- ', '')
      district = district if not 'Regional' in district else 'Newmarket'
      role = councillor.xpath('.//strong/text()')[1].split('-')[0]  # @todo Mayor is not being set
      url = councillor.xpath('.//a/@href')[0]

      p = Legislator(name=name, post_id=district, role=role)
      p.add_source(COUNCIL_PAGE)
      p.add_source(url)

      p.image = councillor.xpath('.//img/@src')[0]

      page = lxmlize(url)
      info = page.xpath('//div[@id="printArea"]')[0]
      info = info.xpath('.//p[@class="heading"][2]/following-sibling::p')
      address = info.pop(0).text_content().strip()
      if not address:
        address = info.pop(0).text_content().strip()

      if 'Ward' in info[0].text_content():
        info.pop(0)

      numbers = info.pop(0).text_content().split(':')
      email = page.xpath('//a[contains(@href, "mailto:")]/text()')[0]
      p.add_contact('email', email, None)
      for i, contact in enumerate(numbers):
        if i == 0:
          continue
        if '@' in contact:
          continue  # executive assistant email
        else:
          number = re.findall(r'([0-9]{3}-[0-9]{3}-[0-9]{4})', contact)[0]
          ext = re.findall(r'(Ext\. [0-9]{3,4})', contact)
          if ext:
            number = number + ext[0].replace('Ext. ', ' x')
          contact_type = re.findall(r'[A-Za-z]+$', numbers[i - 1])[0]
        if 'Fax' in contact_type:
          p.add_contact('fax', number, 'legislature')
        elif 'Phone' in contact_type:
          p.add_contact('voice', number, 'legislature')
        else:
          p.add_contact(CONTACT_DETAIL_TYPE_MAP[contact_type], number, CONTACT_DETAIL_NOTE_MAP[contact_type])
      site = page.xpath('.//a[contains(text(), "http://")]')
      if site:
        p.add_link(site[0].text_content(), None)
      yield p

  def scrape_mayor(self, div):
    name = div.xpath('.//strong/text()')[0].replace(',', '')
    p = Legislator(name=name, post_id='Newmarket', role='Councillor')
    p.add_source(COUNCIL_PAGE)

    numbers = div.xpath('.//p/text()')
    for number in numbers:
      num_type, number = number.split(':')
      if 'Fax' in num_type:
        p.add_contact('fax', number, 'legislature')
      else:
        p.add_contact(CONTACT_DETAIL_TYPE_MAP[num_type], number, CONTACT_DETAIL_NOTE_MAP[num_type])
    email = div.xpath('.//a[contains(@href, "mailto:")]')[0].text_content()
    p.add_contact('email', email, None)
    return p

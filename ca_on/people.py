# coding: utf-8
from __future__ import unicode_literals
from utils import CanadianScraper, CanadianPerson as Person

COUNCIL_PAGE = 'http://www.ontla.on.ca/web/members/member_addresses.do'


class OntarioPersonScraper(CanadianScraper):

    def scrape(self):
        page = self.lxmlize(COUNCIL_PAGE)
        for block in page.xpath('//div[@class="addressblock"]'):
            name_elem = block.xpath('.//a[@class="mpp"]')[0]
            name = ' '.join(name_elem.text.split())

            riding = block.xpath('.//div[@class="riding"]//text()')[0].strip().replace('--', '\u2014')
            district = riding.replace('Chatham—Kent', 'Chatham-Kent')  # m-dash to hyphen
            email_node = block.xpath('.//div[@class="email"]')
            if email_node:
                email = self.get_email(email_node[0])
            phone = block.xpath('.//div[@class="phone"]//text()')[0]
            mpp_url = name_elem.attrib['href']

            mpp_page = self.lxmlize(mpp_url)

            assert riding in mpp_page.xpath('//h1/text()')[0], '{} not in ridings'.format(riding)

            image = mpp_page.xpath('//img[@class="mppimg"]/@src')
            party = mpp_page.xpath('//div[@class="mppinfoblock"]/p[last()]/text()')[0].strip()

            p = Person(primary_org='legislature', name=name, district=district, role='MPP', party=party)
            if image:
                p.image = image[0]
            p.add_source(COUNCIL_PAGE)
            p.add_source(mpp_url)
            if email:
                p.add_contact('email', email)
            p.add_contact('voice', phone, 'legislature')
            yield p

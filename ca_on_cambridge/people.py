from __future__ import unicode_literals
from utils import CanadianScraper, CanadianPerson as Person

import re

COUNCIL_PAGE = 'http://www.cambridge.ca/cs_mayor/wards_councillors.php?cpid=51&sid=57'
MAYOR_PAGE = 'http://www.cambridge.ca/article.php?ssid=167'


class CambridgePersonScraper(CanadianScraper):

    def scrape(self):
        regional_councillor_seat_number = 1

        yield self.mayor_info(MAYOR_PAGE)

        page = self.lxmlize(COUNCIL_PAGE)
        councillors = page.xpath('//div[@id="news"]//p')
        for councillor in councillors:
            district = councillor.xpath('./b')[0].text_content()
            district = re.findall('(?:W|R).*', district)[0]
            role = 'Councillor'
            if 'Regional' in district:
                role = 'Regional Councillor'
                district = 'Cambridge (seat {})'.format(regional_councillor_seat_number)
                regional_councillor_seat_number += 1
            name = councillor.xpath('.//a')[0].text_content()

            url = councillor.xpath('.//a')[0].attrib['href']
            page = self.lxmlize(url)

            image = page.xpath('//img[contains(@src, "councilImages")]/@src')[0]
            address = page.xpath('//*[contains(text(),"Address")]/ancestor::td')[-1].text_content().split(':')[-1].replace("\t", '')
            phone = page.xpath('//*[contains(text(),"Tel")]/ancestor::td')[-1].text_content().split(':')[-1].replace("\t", '')
            phone = phone.replace('(', '').replace(') ', '-')
            if page.xpath('//*[contains(text(),"Fax")]'):
                fax = page.xpath('//*[contains(text(),"Fax")]/ancestor::td')[-1].text_content().split(':')[-1].replace("\t", '')
                fax = fax.replace('(', '').replace(') ', '-')
            email = self.get_email(page)

            p = Person(primary_org='legislature', name=name, district=district, role=role)
            p.add_source(COUNCIL_PAGE)
            p.add_source(url)
            p.add_contact('address', address, 'legislature')
            p.add_contact('voice', phone, 'legislature')
            p.add_contact('fax', fax, 'legislature')
            p.add_contact('email', email)
            p.image = image
            yield p

    def mayor_info(self, url):
        page = self.lxmlize(url)
        name = page.xpath('//h3//text()')[0].split(',')[1]
        email = self.get_email(page)
        phone = page.xpath('//td//text()[contains(., "Tel:")]')[0].split(':')[1]

        addr_row = page.xpath('//td[text()="3): "]/parent::tr')
        addr_rows = addr_row + addr_row[0].xpath('./following-sibling::tr')[:3]
        addr = '\n'.join(row[2].text for row in addr_rows)

        photo_url = page.xpath('//center/img/@src')[0]

        p = Person(primary_org='legislature', name=name, district="Cambridge", role='Mayor', image=photo_url)
        p.add_source(url)
        p.add_contact('email', email)
        p.add_contact('voice', phone, 'legislature')
        p.add_contact('address', addr, 'legislature')
        return p

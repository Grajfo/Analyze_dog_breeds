import scrapy
from decimal import localcontext, Decimal, ROUND_HALF_UP


class DogBreedSpider(scrapy.Spider):
    name = "dog_breeds"
    allowed_domains = ['dogtime.com']
    start_urls = ['https://dogtime.com/dog-breeds/profiles/']

    def parse(self, response):
        vsa_dela = response.css('div.list-container')

        pasmePoCrkah = vsa_dela.css('div.article-crumbs div.list-item')

        for pasme in pasmePoCrkah:
            url = pasme.css('a.list-item-img::attr(href)').extract_first()
            #url = 'https://dogtime.com/dog-breeds/afador'
            yield scrapy.Request(url, callback=self.parse_dog_breed, priority=1)

    def parse_dog_breed(self, response):
        podatki = response.css('div.breeds-single-content')
        rezultati = {}

        name = podatki.css('h1::text').extract_first()
        rezultati['Name'] = podatki.css('h1::text').extract_first()

        tekst = podatki.css('div.breeds-single-intro p')
        all_tekst = tekst.css('p ::text').extract()
        url_slika = podatki.css('div.breeds-single-intro img::attr(src)').extract_first()

        besedilo = ''
        for words in list(all_tekst):
            if 'See below' in words:
                break
            else:
                besedilo += words + " "

        rezultati['About'] = " ".join(besedilo.split())
        rezultati['Url_image'] = url_slika

        karakteristike = podatki.css('div.breeds-single-details div.breed-characteristics-ratings-wrapper')
        breed_charac = ['Adaptability', 'All Around Friendliness', 'Health And Grooming Needs',
                        'Trainability', 'Physical Needs']

        for i, karakter in enumerate(karakteristike):
            seznam_char_imen = karakter.css('div.js-list-item div.characteristic-title::text').extract()
            seznam_char_ocen = karakter.css('div.js-list-item div.star::text').extract()
            ocena = 0
            for j in range(0, len(seznam_char_imen)):
                rezultati[seznam_char_imen[j]] = int(seznam_char_ocen[j])
                ocena += int(seznam_char_ocen[j])
            with localcontext() as ctx:
                ctx.rounding = ROUND_HALF_UP
                izracun = Decimal(ocena) / len(seznam_char_imen)
                rezultati[breed_charac[i]] = izracun.to_integral_value()

        stats_title = podatki.css('div.breed-vital-stats-wrapper div.vital-stat-title::text').extract()
        stats = podatki.css('div.breed-vital-stats-wrapper div.vital-stat-box::text').extract()
        for i in range(0, len(stats_title)):
            title = stats_title[i].replace(":", "")
            if i is 0:
                rezultati[title] = stats[i]
            elif i is 1:
                rez = stats[i].split()
                if 'Mutt' in name:
                    izracun_povprecja = (int(rez[0]) + int(rez[2])) / 2  # years
                    rezultati[title] = izracun_povprecja
                elif rez[0].isdigit() and rez[2].isdigit() and 'feet' not in rez:
                    izracun_povprecja = (int(rez[0]) + int(rez[2])) / 2  # visina
                    rezultati[title] = round(izracun_povprecja / 0.39370, 2)  # sprememba v centimetre
                elif rez[2].isdigit():
                    rezultati[title] = round(int(rez[2]) / 0.39370, 2)  # sprememba v centimetre
                else:
                    continue
            elif i is 2:
                rez = stats[i].split()
                if rez[0].isdigit() and rez[2].isdigit():
                    izracun_povprecja = (int(rez[0]) + int(rez[2])) / 2  # pounds
                    rezultati[title] = round(izracun_povprecja / 2.2046, 2)  # sprememba v kilograme
                elif rez[2].isdigit():
                    rezultati[title] = round(int(rez[2]) / 2.2046, 2)  # sprememba v kilograme
                else:
                    continue
            elif i is 3:
                rez = stats[i].split()
                if rez[0].isdigit() and rez[2].isdigit():
                    if '+' in rez[2]:
                        izracun_povprecja = (int(rez[0]) + int(rez[2].replace("+", ""))) / 2  # years
                        rezultati[title] = izracun_povprecja
                    else:
                        izracun_povprecja = (int(rez[0]) + int(rez[2])) / 2  # years
                        rezultati[title] = izracun_povprecja
                elif rez[2].isdigit():
                    rezultati[title] = int(rez[2])
                else:
                    continue

        yield rezultati

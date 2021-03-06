"""
 Bing (Videos)

 @website     https://www.bing.com/videos
 @provide-api yes (http://datamarket.azure.com/dataset/bing/search)

 @using-api   no
 @results     HTML
 @stable      no
 @parse       url, title, content, thumbnail
"""

from json import loads
from lxml import html
from searx.engines.xpath import extract_text
from searx.url_utils import urlencode


categories = ['videos']
paging = True
time_range_support = True
language_support = True
number_of_results = 35

search_url = 'https://www.bing.com/videos/asyncv2?{query}&async=content&'\
             'first={offset}&count={number_of_results}&CW=1366&CH=25&FORM=R5VR5'
time_range_string = '&qft=+filterui:videoage-lt{interval}'
time_range_dict = {'day': '1440',
                   'week': '10080',
                   'month': '43200',
                   'year': '525600'}


# do search-request
def request(query, params):
    offset = (params['pageno'] - 1) * 10 + 1

    if params['language'] != 'all' and params['language'] != 'zh':
        query = u'language:{} {}'.format(params['language'], query.decode('utf-8')).encode('utf-8')

    # query and paging
    params['url'] = search_url.format(query=urlencode({'q': query}),
                                      offset=offset,
                                      number_of_results=number_of_results)

    # time range
    if params['time_range'] in time_range_dict:
        params['url'] += time_range_string.format(interval=time_range_dict[params['time_range']])

    return params


# get response from search-request
def response(resp):
    results = []

    dom = html.fromstring(resp.text)

    for result in dom.xpath('//div[@class="dg_u"]'):
        link = result.xpath('./div[@class="mc_vtvc"]/a')[0]
        url = link.attrib.get('href')
        if url[0] == '/':
            url = 'https://bing.com' + url
        title = extract_text(result.xpath('.//div[@class="mc_vtvc_title"]/@title')[0])
        content = link.attrib.get('aria-label').replace(title, '')
        thumbnail = result.xpath('.//img[1]/@src')[0]

        results.append({'url': url,
                        'title': title,
                        'content': content,
                        'thumbnail': thumbnail,
                        'template': 'videos.html'})

        if len(results) >= number_of_results:
            break

    return results

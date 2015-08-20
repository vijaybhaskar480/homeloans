from scrapy.selector import Selector
import json
import sys
import requests
import threading
import time
import csv

final_dump = []


def fun(spec_url):

    """
    Extract information from each page. The XPATHs need to be validated and updated frequently 
    depending on the change in the site.

    Arguments:
    spec_url -- URL of the specific page to be scraped.

    Output:
    Dictionary containing the information of the listing / Project.

    """

    global count
    time.sleep(1)
    
    response = requests.get(spec_url).text
    html = Selector(text=response)
    
    obj = {}

    try:
        obj['url'] = spec_url
    except:
        obj['url'] = 'N/A'

    try:
        obj['Propertyname'] = html.xpath('//div[@class="fwn blk mt15"]/span[@itemprop="name"]/text()')[0].extract()
        
    except:
        try:
            obj['Propertyname'] = html.xpath('//div[@class="logo"]/a/@alt')[0].extract()
        except:
            try:
                obj['Propertyname'] = html.xpath('//div[@class="tWhite di mt20"]/h1/text()')[0].extract().strip().split(',')[0]
            except:
                obj['Propertyname'] = 'N/A'

    try:
        sale_properties = html.xpath('//h3[@class="b f16 blk"]/text()')[0].extract().split()[0]
        try:
            obj['Number of Sale Properties'] = str(int(sale_properties))
        except Exception as e:
            obj['Number of Sale Properties'] = 'N/A'
    except:
        obj['Number of Sale Properties'] = 'N/A'

    try:
        location = html.xpath('//div[@class="pdt5"]/text()')[0].extract().split(':')[1]
        if ',' in location:
            obj['Location'] = location.split(',')[0]
            obj['city'] = location.split(',')[1]
        else:
            obj['Location'] = 'N/A'
            obj['city'] = 'N/A'
    except:
        try:
            location = html.xpath('//div[@class="listDiv1"]/table/tbody/tr/td[1]/p[2]/text()')[0].extract()
            if ',' in location:
                obj['Location'] = location.split(',')[0]
                obj['city'] = location.split(',')[1]
        except:
            obj['Location'] = 'N/A'
            obj['city'] = 'N/A'

    try:
        obj['Number of views'] = html.xpath('//div[@class="vSimProp mt15"]/div/b/text()')[0].extract().split()[0]
    except:
        obj['Number of views'] = 'N/A'

    obj['about_builder'] = 'N/A'
    obj['by_builder'] = 'N/A'

    if obj['about_builder'] == 'N/A':
        try:
            builder_list = html.xpath('//div[@id="builderSection"]/div/a/div/text()')[0].extract()
            if 'About' in builder_list:
                builder_list = builder_list.replace("About", "")
            obj['about_builder'] = builder_list
        except:
            obj['about_builder'] = 'N/A'

    if obj['about_builder'] == 'N/A':
        i = 1
        while True:
            try:
                builder_name = html.xpath('//div[@class="nplistcntr floatl"]/div[' + str(i) + ']/div[1]/b/text()')[0].extract()
                if builder_name:
                    if 'Builder' in builder_name:
                        obj['about_builder'] = html.xpath('//div[@class="nplistcntr floatl"]/div[' + str(i) + ']/div[1]/text()')[2].extract().strip()
                        break
                    i += 1
                else:
                    break
            except:
                count = 0
                break

    if obj['by_builder'] == 'N/A':
        try:
            obj['by_builder'] = html.xpath('//span[@itemprop="manufacturer"]/span[@itemprop="name"]/text()')[0].extract()
        except:
            obj['by_builder'] = 'N/A'

    try:
        obj['Price'] = html.xpath('//div[@class="lf ml20 mt15"]/span/text()')[1].extract()
    except:
        try:
            obj['Price'] = html.xpath('//div[@class="listDiv1"]/table/tbody/tr/td[2]/p[2]/text()')[0].extract()
        except:
            obj['Price'] = 'N/A'

    try:
        obj['Property Type'] = html.xpath('//div[@class="listDiv1"]/table/tbody/tr/td[1]/p[1]/text()')[0].extract()
    except:
        obj['Property Type'] = 'N/A'

    try:
        floor_plan_no = html.xpath('//ul[@class="imBlock cpointer"]/li/div[@class="mt5"]/text()')[0].extract()
        if 'Floor Plans' in floor_plan_no:
            obj['Number of Floor Plans'] = floor_plan_no.split()[0]
        else:
            if 'Floor Plans' in html.xpath('//ul[@class="imBlock cpointer"]/li[2]/div[@class="mt5"]/text()')[0].extract():
                obj['Number of Floor Plans'] = html.xpath('//ul[@class="imBlock cpointer"]/li[2]/div[@class="mt5"]/text()')[0].extract().split()[0]
            else:
                obj['Number of Floor Plans'] = 'N/A'
    except:
        obj['Number of Floor Plans'] = 'N/A'

    try:
        obj['Area'] = 'N/A'
        obj['Unit_Type'] = 'N/A'
        obj['possession_date'] = 'N/A'
        property_details = html.xpath(
            '//span[@class="f13 grey3"]/text()')[0].extract().strip()
        if property_details:
            for i in range(0, 3):
                try:
                    property_details1 = property_details.split('|')[i]
                    if property_details.split('|')[i].strip().split(':')[0] == 'Size':
                        obj['Area'] = property_details.split(
                            '|')[i].strip().split(':')[1]
                    if property_details.split('|')[i].strip().split(':')[0] == 'Plans':
                        obj['Unit_Type'] = property_details.split(
                            '|')[i].strip().split(':')[1]
                    if property_details.split('|')[i].strip().split(':')[0] == 'Possession':
                        obj['possession_date'] = property_details.split(
                            '|')[i].strip().split(':')[1]
                except Exception as e:
                    str(e)
    except:
        obj['Area'] = 'N/A'
        obj['Unit_Type'] = 'N/A'
        obj['possession_date'] = 'N/A'

    if obj['Area'] == 'N/A':
        try:
            field_name = html.xpath('//div[@class="listDiv1"]/table/tbody/tr/td[1]/p[3]/strong/text()')[0].extract()
            if 'Area' in field_name:
                area_field = html.xpath('//div[@class="listDiv1"]/table/tbody/tr/td[1]/p[3]/text()').extract()
                if len(area_field) > 1:
                    obj['Area'] = str(" ".join(area_field))
                else:
                    obj['Area'] = area_field[0]
        except:
            obj['Area'] = 'N/A'

    if obj['Unit_Type'] == 'N/A':
        try:
            obj['Unit_Type'] = html.xpath('//div[@class="listDiv1"]/table/tbody/tr/td[2]/p[1]/text()')[0].extract()
        except:
            obj['Unit_Type'] = 'N/A'

    if obj['possession_date'] == 'N/A':
        try:
            obj['possession_date'] = html.xpath('//div[@class="listDiv1"]/table/tbody/tr/td[2]/p[3]/text()')[0].extract()
        except:
            obj['possession_date'] = 'N/A'

    if obj['possession_date'] == 'N/A':
        try:
            chk_poss = html.xpath('//div[@class="contBox"]/div[1]/div/text()')[0].extract()
            if 'Possession' in chk_poss:
                poss_date = str(html.xpath('//div[@class="contBox"]/div[1]/div[2]/div[2]/text()')[0].extract()) + ' ' + str(html.xpath(
                        '//div[@class="contBox"]/div[1]/div[2]/div[1]/text()')[0].extract())
            
            obj['possession_date'] = poss_date
        except:
            obj['possession_date'] = 'N/A'

    if obj['Unit_Type'] == 'N/A':
        i = 1
        prop_details = []
        while True:
            try:
                prop_details.append(str(html.xpath('//div[@class="oviewRange npsrp"]/table/tbody/tr[' + str(i) + ']/td[@class="10%"]/nobr/text()')[0].extract()))
                i += 1
            except:
                break
        if prop_details:
            obj['Unit_Type'] = ",".join(prop_details)
        else:
            obj['Unit_Type'] = 'N/A'

    if obj['Price'] == 'N/A':
        i = 1
        price_details = []
        while True:
            try:
                price_details.append(str(html.xpath('//div[@class="oviewRange npsrp"]/table/tbody/tr[' + str(i) + ']/td[4]/text()')[0].extract()))
                i += 1
            except:
                break
        if price_details:
            obj['Price'] = ",".join(price_details)
        else:
            obj['Price'] = 'N/A'

    if obj['Area'] == 'N/A':
        i = 1
        area_details = []
        while True:
            try:
                area_details.append(str(html.xpath('//div[@class="oviewRange npsrp"]/table/tbody/tr[' + str(i) + ']/td[3]/text()')[0].extract()))
                i += 1
            except:
                break
        if area_details:
            obj['Area'] = ",".join(area_details)
        else:
            obj['Area'] = 'N/A'

    obj['Number of Towers'] = 'N/A'
    obj['Number of Floors'] = 'N/A'
    obj['Number of Units'] = 'N/A'
    obj['Project Area'] = 'N/A'

    try:
        proj_details = html.xpath('//div[@class="lf mt15"]/div[@class="mt10"]/div[2]/div[2]/b[1]/text()')[0].extract()
        if 'project details' in proj_details.lower():
            details_list = html.xpath('//div[@class="lf mt15"]/div[@class="mt10"]/div[2]/div[2]/text()').extract()
            for i in range(0, len(details_list)):
                if ':' in details_list[i]:
                    split_char = ':'
                if '-' in details_list[i]:
                    split_char = '-'

                if 'number of towers' in details_list[i].lower() or 'no. of towers' in details_list[i].lower() or 'total blocks' in details_list[i].lower() or 'no of blocks' in details_list[i].lower() or 'no of towers' in details_list[i].lower():
                    obj['Number of Towers'] = str(
                        details_list[i].split(split_char)[1])
                if 'number of floors' in details_list[i].lower() or 'total floors' in details_list[i].lower() or 'no. of floors' in details_list[i].lower() or 'no of floors' in details_list[i].lower():
                    obj['Number of Floors'] = str(
                        details_list[i].split(split_char)[1])
                if 'number of units' in details_list[i].lower() or 'no. of units' in details_list[i].lower() or 'no of units' in details_list[i].lower() or 'total units' in details_list[i].lower():
                    obj['Number of Units'] = str(
                        details_list[i].split(split_char)[1])
                if 'total area' in details_list[i].lower():
                    obj['Project Area'] = str(
                        details_list[i].split(split_char)[1])
    except:
        try:
            proj_details = html.xpath('//div[@class="descTxt ml15"]/div[2]/text()')[1].extract()
            if 'project details' in proj_details.lower():
                details_list = html.xpath('//div[@class="descTxt ml15"]/div[2]/text()').extract()
                for i in range(0, len(details_list)):
                    if ':' in details_list[i]:
                        split_char = ':'
                    if '-' in details_list[i]:
                        split_char = '-'

                    if 'number of towers' in details_list[i].lower() or 'no. of towers' in details_list[i].lower() or 'total blocks' in details_list[i].lower() or 'no of blocks' in details_list[i].lower() or 'no of towers' in details_list[i].lower():
                        obj['Number of Towers'] = str(
                            details_list[i].split(split_char)[1])
                    if 'number of floors' in details_list[i].lower() or 'total floors' in details_list[i].lower() or 'no. of floors' in details_list[i].lower() or 'no of floors' in details_list[i].lower():
                        obj['Number of Floors'] = str(
                            details_list[i].split(split_char)[1])
                    if 'number of units' in details_list[i].lower() or 'no. of units' in details_list[i].lower() or 'no of units' in details_list[i].lower() or 'total units' in details_list[i].lower():
                        obj['Number of Units'] = str(
                            details_list[i].split(split_char)[1])
                    if 'total area' in details_list[i].lower():
                        obj['Project Area'] = str(
                            details_list[i].split(split_char)[1])
        except:
            try:
                proj_details = html.xpath(
                    '//div[@class="lf mt15"]/div[@class="mt10"]/div[2]/div[2]/text()')[1].extract()
                if 'project details' in proj_details.lower():
                    details_list = html.xpath(
                        '//div[@class="lf mt15"]/div[@class="mt10"]/div[2]/div[2]/text()').extract()
                    for i in range(0, len(details_list)):
                        if ':' in details_list[i]:
                            split_char = ':'
                        if '-' in details_list[i]:
                            split_char = '-'

                        if 'number of towers' in details_list[i].lower() or 'no. of towers' in details_list[i].lower() or 'total blocks' in details_list[i].lower() or 'no of blocks' in details_list[i].lower() or 'no of towers' in details_list[i].lower():
                            obj['Number of Towers'] = str(
                                details_list[i].split(split_char)[1])
                        if 'number of floors' in details_list[i].lower() or 'total floors' in details_list[i].lower() or 'no. of floors' in details_list[i].lower() or 'no of floors' in details_list[i].lower():
                            obj['Number of Floors'] = str(
                                details_list[i].split(split_char)[1])
                        if 'number of units' in details_list[i].lower() or 'no. of units' in details_list[i].lower() or 'no of units' in details_list[i].lower() or 'total units' in details_list[i].lower():
                            obj['Number of Units'] = str(
                                details_list[i].split(split_char)[1])
                        if 'total area' in details_list[i].lower():
                            obj['Project Area'] = str(
                                details_list[i].split(split_char)[1])
            except:
                try:
                    proj_details = html.xpath(
                        '//div[@class="lf mt15"]/div[@class="mt10"]/div[2]/div[1]/b[1]/text()')[0].extract()
                    if 'project details' in proj_details.lower():
                        details_list = html.xpath(
                            '//div[@class="lf mt15"]/div[@class="mt10"]/div[2]/div[1]/text()').extract()
                        for i in range(0, len(details_list)):
                            if ':' in details_list[i]:
                                split_char = ':'
                            if '-' in details_list[i]:
                                split_char = '-'

                            if 'number of towers' in details_list[i].lower() or 'no. of towers' in details_list[i].lower() or 'total blocks' in details_list[i].lower() or 'no of blocks' in details_list[i].lower() or 'no of towers' in details_list[i].lower():
                                obj['Number of Towers'] = str(
                                    details_list[i].split(split_char)[1])
                            if 'number of floors' in details_list[i].lower() or 'total floors' in details_list[i].lower() or 'no. of floors' in details_list[i].lower() or 'no of floors' in details_list[i].lower():
                                obj['Number of Floors'] = str(
                                    details_list[i].split(split_char)[1])
                            if 'number of units' in details_list[i].lower() or 'no. of units' in details_list[i].lower() or 'no of units' in details_list[i].lower() or 'total units' in details_list[i].lower():
                                obj['Number of Units'] = str(
                                    details_list[i].split(split_char)[1])
                            if 'total area' in details_list[i].lower():
                                obj['Project Area'] = str(
                                    details_list[i].split(split_char)[1])
                except:
                    obj['Number of Towers'] = 'N/A'
                    obj['Number of Floors'] = 'N/A'
                    obj['Number of Units'] = 'N/A'
                    obj['Project Area'] = 'N/A'

    if len(obj) != 18:
        print obj
    return obj


def dump_page(start_url, filename):

    """

    Storing the data(json) extracted from each individual page to the list final_dump.
    Extracts the URL of each projects and calls the extraction function (fun) on that URL.

    """

    global final_dump
    try:
        response = requests.get(start_url).text
    except Exception as e1:
        print e1

    html = Selector(text=response)
    properties = html.xpath('//div[@class="npsrp npsrp_size rel cpointer"]')
    print start_url
    print len(properties)
    for p_detail in properties:
        try:
            obj = fun(p_detail.xpath('.//div[@class="npt_titl b f16"]/a/@href')[0].extract())
            final_dump.append(obj)
        except Exception as e:
            print e
            pass


def number_of_pages(start_url):

    """ Identify the Number of pages to scrape. Currently being entered directly into the variable 'pages' """

    try:
        response = requests.get(start_url + '1').text
        html = Selector(text=response)
        # pages = int(html.xpath('//div[@class="sRTabs"]/a[2]/text()')[0].extract().split()[0]) / 30
        pages = 20
        print pages
        return pages
    except:
        return 0


def dump_pages(start_url, filename, annex):

    """
    Page-Iteration, Threading and Writing the final output to the target file.

    """

    global final_dump
    final_dump = []
    pages = number_of_pages(start_url + "1")
    threads = []
    for page in range(1, pages + 1):
        threads.append(
            threading.Thread(target=dump_page, args=[start_url + str(page) + annex, filename]))
    concurrent = 1
    size = len(threads) / concurrent + 1
    print size
    for i in range(size):
        todo = threads[i * concurrent:(i + 1) * concurrent]
        for t in todo:
            t.start()
        for t in todo:
            t.join()

    f = open(filename, 'w')
    f.write(json_csv(final_dump))
    f.close()


def json_csv(data):

    """ Convert a JSON object to csv data """

    keys = []
    csv_data = ''
    for item in data:
        for key in item:
            keys.append(key.encode('utf-8'))
    keys = list(set(keys))
    csv_data += '"%s"\n' % '","'.join(keys)
    for row in data:
        values = []
        for key in keys:
            value_temp = row.get(key.decode('utf-8'))
            if type(value_temp) is list:
                value_temp = str(";".join(value_temp))
            values.append((value_temp or "N/A").encode('utf-8'))

        csv_data += '"%s"\n' % '","'.join(values)
    return csv_data



def main():

    """
    Loops over the cities for which data has to be extracted. 
    Cities to be input from a separate csv file.

    """

    city_list = []
    ip = open('99_tier2_cities.txt','r')
    reader = ip.read().split('\n')
    for row in reader:
        city = row.lower().strip()
        if len(city)>0:
            city_list.append(city)
    print city_list
    
    for city_name in city_list:
        print city_name

        start_url = "http://www.99acres.com/new-projects-in-" + str(city_name) +"-ffid-page-"
        annex = "?search_type=QS&search_location=CP32&lstAcn=CP_R&lstAcnId=32&src=CLUSTER&selected_tab=1&isvoicesearch=N&keyword=" +str(city_name)+"&np_search_type=NP%2CNL&strEntityMap=IiI%3D&refine_results=Y&Refine_Localities=Refine%20Localities&action=%2Fdo%2Fquicksearch%2Fsearch"

        dump_file_name = '99acres_june_' + str(city_name) + '.csv'
        dump_pages(start_url, dump_file_name, annex)

main()


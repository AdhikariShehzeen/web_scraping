import requests
import json
import pandas as pd

"""
zip code
studio url
studio name
address
phone number
instructor name

"""
base_url = 'https://www.mindbodyonline.com/explore/locations/'

headers = {
    "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0"
}

def clean_datas(data):
    clean_data = []
    for d in data:
        clean_d = {}
        clean_d['Location_Code'] = d['requested_location_id']
        clean_d['Zip_Code'] = d['attributes']['postalCode']
        clean_d['Studio_Name'] = d['attributes']['slug']
        clean_d['Studio_url'] = d['studio_url']
        try:
            address = d['attributes']['address'] + ', ' +  d['attributes']['city'] + ', ' + d['attributes']['state'] + ', ' + d['attributes']['postalCode']
        except:
            address = d['attributes']['address']
        clean_d['Address'] = address
        clean_d['Phone_Number'] = d['attributes']['phone']
        clean_d['instructor_Name'] = d['instructors']    
        clean_data.append(clean_d)
    
    return clean_data

def collect_instructor(slug):
    url_instructor = 'https://prod-mkt-gateway.mindbody.io/v1/search/instructors'
    payload = {"filter":{"locationSlugs":[slug]}}
    r = requests.post(url_instructor, headers = headers, data = json.dumps(payload)).json()
    instructor_names = []
    for instructor in r['data']:
        instructor_names.append(instructor['attributes']['name'])
    return {'instructors' : instructor_names, 'studio_url' : base_url+ slug}
    
    
def collect_data(lat, lon, i):
    data = []
    page = 1
    while True:
        print(page)
        payload = {"sort":"-_score,distance","page":{"size":10,"number":page},"filter":{"categories":[],"radius":-1,"term":"","cmMembershipBookable":"any","latitude":lat,"longitude":lon,"categoryTypes":["Fitness"]}}    
        url = "https://prod-mkt-gateway.mindbody.io/v1/search/locations"
        r = requests.post(url, headers = headers, data=json.dumps(payload)).json()
        print(r['meta'])
        for d in r['data']:
            if d not in data:
                d['requested_location_id'] = i
                d.update(collect_instructor(d['attributes']['slug']))
                data.append(d)
        page += 1
#        if page > r['meta']['found']//100 + 1:
#            break
        if page > 12:
            break
        
    return data

ids = [90001, 90089, 90506, 91010, 91335, 91617, 90002]
ids = [str(i) for i in ids]

clean_data = []
for i in ids:
    print('###########Started For:::', i)
    url_location = 'https://prod-mkt-gateway.mindbody.io/v1/geolocate?filter.q={}'.format(i)
    r = requests.get(url_location)
    lat, lon = json.loads(r.text)['data']['latitude'], json.loads(r.text)['data']['longitude']    
    data = (collect_data(lat, lon, i))
    clean_data.extend(clean_datas(data))
    
clean_data = pd.DataFrame(clean_data)
clean_data.to_csv('mindBody.csv', index = False)
    
    
    

import re
import time
import TheSilent.puppy_requests as puppy_requests

def kitten_crawler(init_host,delay=0):
    host = init_host.rstrip("/")
    host_list = [host + "/"]
    try:
        sitemap_list = []
        data = puppy_requests.text(init_host + "/sitemap.xml")
        data = data.replace("<","\n<")
        data = re.findall("<loc>(http\S+)",data)
        for _ in data:
            _ = _.split("<")[0]
            if "sitemap" in _:
                sitemap_list.append(_)

            else:
                host_list.append(_)

    except:
        pass

    if len(sitemap_list) > 0:
        for _ in sitemap_list:
            time.sleep(delay)
            try:
                data = puppy_requests.text(_)
                data = data.replace("<","\n<")
                data = re.findall("<loc>(http\S+)",data)
                for __ in data:
                    host_list.append(__)

            except:
                pass

    _ = -1
    while True:
        _ += 1
        try:
            print(host_list[_])
            time.sleep(delay)
            host_list = list(dict.fromkeys(host_list[:]))
            data = puppy_requests.text(host_list[_])

            href = re.findall("href\s?=\s?[\"\'](\S+)[\"\']",data)
            href = list(set(href[:]))
            for __ in href:
                if __.startswith("/"):
                    __ = __.rstrip('"')
                    __ = __.rstrip("'")
                    host_list.append(init_host + __)

        except IndexError:
            break

        except:
            continue

    host_list = list(dict.fromkeys(host_list[:]))
    return host_list

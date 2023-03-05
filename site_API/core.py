from settings import SiteSettings
from site_API.utils.site_api_handler import SiteApiInterface

site = SiteSettings()

# HTTP заголовок запроса
headers = {
    "X-RapidAPI-Key": site.api_key.get_secret_value(),
    "X-RapidAPI-Host": site.host_api
}

# URL запроса
url = 'https://' + site.host_api
# Параметры запроса
params = {"limit": "5", "offset": "0"}

site_api = SiteApiInterface()

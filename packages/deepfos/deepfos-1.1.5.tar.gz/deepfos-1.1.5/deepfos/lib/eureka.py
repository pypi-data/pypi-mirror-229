from xml.etree import ElementTree
from deepfos.lib.httpcli import AioHttpCli, SyncHttpCli
from deepfos.lib.utils import concat_url
from cachetools import TTLCache
from deepfos.options import OPTION


__all__ = ['Eureka']


class EurekaClient:
    def __init__(self):
        self.xml_cache = TTLCache(maxsize=1, ttl=600)
        self.xml_key = "__xml__"
        self.server_cache = TTLCache(maxsize=1024, ttl=120)

    async def get_url(self, server_name):
        server_name = server_name.upper()
        if server_name in self.server_cache:
            return self.server_cache[server_name]

        url = await self._find_url(server_name)
        self.server_cache[server_name] = url
        return url

    def sync_get_url(self, server_name):
        server_name = server_name.upper()
        if server_name in self.server_cache:
            return self.server_cache[server_name]

        url = self._sync_find_url(server_name)
        self.server_cache[server_name] = url
        return url

    async def _get_xml(self):
        if self.xml_key in self.xml_cache:
            return self.xml_cache[self.xml_key]
        resp = await AioHttpCli.get(concat_url(OPTION.server.eureka, 'apps'))
        raw_xml = await resp.text()
        return self._add_to_cache(raw_xml)

    def _sync_get_xml(self):
        if self.xml_key in self.xml_cache:
            return self.xml_cache[self.xml_key]
        resp = SyncHttpCli.get(concat_url(OPTION.server.eureka, 'apps'))
        raw_xml = resp.text
        return self._add_to_cache(raw_xml)

    async def _find_url(self, server_name):
        xml = await self._get_xml()
        return self._walk_apps(xml, server_name)

    def _sync_find_url(self, server_name):
        xml = self._sync_get_xml()
        return self._walk_apps(xml, server_name)

    def _add_to_cache(self, raw_xml):
        xml = ElementTree.fromstring(raw_xml)
        self.xml_cache[self.xml_key] = xml
        return xml

    @staticmethod
    def _walk_apps(xml, server_name):
        for app in xml.iter('application'):
            app_name = app.find('name').text

            if app_name != server_name:
                continue

            instance = app.find('instance')
            status = instance.find('status')
            if status.text != "UP":
                continue
            port = instance.find('port')
            port_enable = port.get('enabled').lower() == "true"

            secure_port = instance.find('securePort')
            secure_port_enable = secure_port.get('enabled').lower() == "true"
            if port_enable:
                valid_port = port.text
                proto = "http://"
            elif secure_port_enable:
                valid_port = secure_port.text
                proto = "https://"
            else:
                continue

            ip = instance.find('ipAddr').text
            return f"{proto}{ip}:{valid_port}"

        raise RuntimeError(f"Cannot find instance for server: {server_name}")


Eureka = EurekaClient()

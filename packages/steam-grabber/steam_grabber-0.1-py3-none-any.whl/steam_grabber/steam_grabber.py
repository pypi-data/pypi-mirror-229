import aiohttp
import rsa
import base64
import time
from yarl import URL
from bs4 import BeautifulSoup
from enum import Enum
from datetime import datetime
import re

class SteamUrls(Enum):
    Community = "https://steamcommunity.com"
    Store = "https://store.steampowered.com"


class Client:
    def __init__(self, username: str, password: str, proxy: str = None, proxy_username: str = None, proxy_password: str = None):
        self.username = username
        self.password = password

        if proxy and proxy_username and proxy_password:
            proxy = f"http://{proxy_username}:{proxy_password}@{proxy}"
        
        connector = aiohttp.TCPConnector(proxy=proxy) if proxy else None
        self.session = aiohttp.ClientSession(connector=connector)
        
        self._repeats = 0
        self.logged_in = False

    async def test_login(self):
        async with self.session.get(SteamUrls.Community.value) as resp:
            self.logged_in = self.username in await resp.text()
            return self.logged_in

    async def do_login(self):
        login_request = await self.send_login()
        if login_request.get('captcha_needed'):
            raise ValueError("Captcha required for login")
        
        if not login_request['success']:
            raise ValueError(f"Invalid Credentials: {login_request.get('message', 'Unknown error')}")

        await self.do_redirect(login_request)
        self.update_cookies()
        
        if not await self.test_login():
            self.logged_in = False
            raise ConnectionError('Login Failed')
        
        self.logged_in = True
        return self.session

    def update_cookies(self):
        community_domain = SteamUrls.Community.value[8:]
        store_domain = SteamUrls.Store.value[8:]
        prev_cookies = self.session.cookie_jar.filter_cookies(store_domain)
        
        for cookie in prev_cookies:
            cookie['domain'] = community_domain
        
        self.session.cookie_jar.update_cookies(prev_cookies, URL(SteamUrls.Community.value))

    async def get_rsa(self):
        url = f"{SteamUrls.Community.value}/login/getrsakey/?username={self.username}"
        async with self.session.post(url) as resp:
            data = await resp.json()
            mod = int(data.get('publickey_mod', '0'), 16)
            exp = int(data.get('publickey_exp', '0'), 16)
            timestamp = data.get('timestamp')
            
            if not mod or not exp or not timestamp:
                if self._repeats < 10:
                    self._repeats += 1
                    return await self.get_rsa()
                else:
                    raise ValueError("Unable to obtain RSA keys")
            
            return {'rsa_key': rsa.PublicKey(mod, exp), 'rsa_timestamp': timestamp}

    async def send_login(self):
        rsa_keys = await self.get_rsa()
        encrypted_pass = base64.b64encode(rsa.encrypt(self.password.encode(), rsa_keys['rsa_key'])).decode()
        
        payload = {
            'password': encrypted_pass,
            'username': self.username,
            'rsatimestamp': rsa_keys['rsa_timestamp'],
            'emailauth': '',
            'loginfriendlyname': '',
            'captchagid': '-1',
            'captcha_text': '',
            'emailsteamid': '',
            'remember_login': 'false',
            'donotcache': str(int(time.time() * 1000))
        }
        
        url = f"{SteamUrls.Community.value}/login/dologin/?username={self.username}"
        async with self.session.post(url, data=payload) as resp:
            return await resp.json()

    async def do_redirect(self, resp_json):
        transfer_params = resp_json.get('transfer_parameters')
        if not transfer_params:
            raise Exception('transfer_parameters not found. Steam might be having issues.')
        
        for url in resp_json.get('transfer_urls', []):
            async with self.session.post(url, data=transfer_params):
                pass

    async def get_all_account_info(self, apikey: str):
        account_info_url = "https://store.steampowered.com/account/"
        result_dict = {}
        csgo = {}
        async with self.session.get(account_info_url) as response:
            if response.status == 200:
                soup = BeautifulSoup(await response.text(), 'html.parser')
                
                result_dict['balance'] = soup.select_one(".accountData.price a").text.split(" ")[0]
                result_dict['currency'] = soup.select_one(".accountData.price a").text.split(" ")[1]
                result_dict['country'] = soup.select_one(".country_settings p .account_data_field").text
                result_dict['steam_id'] = soup.select_one(".youraccount_steamid").text.replace("Steam ID: ", "")
                result_dict['email'] = soup.select_one("span.account_manage_label + span.account_data_field").text

        join_url = f"http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key={apikey}&steamids={result_dict['steam_id']}&format=json/"
        async with self.session.get(join_url) as response:
            if response.status == 200:
                res = await response.json()
                time_created_unix_time = res['response']['players'][0]['timecreated']
                time_created_dt_object = datetime.fromtimestamp(time_created_unix_time)
                time_created_ormalised_time = time_created_dt_object.strftime('%Y-%m-%d')

                last_online_unix_time = res['response']['players'][0]['lastlogoff']
                last_online_dt_object = datetime.fromtimestamp(last_online_unix_time)
                last_online_ormalised_time = last_online_dt_object.strftime('%Y-%m-%d')

                result_dict['created_at'] = time_created_ormalised_time
                result_dict['last_online'] = last_online_ormalised_time

        account_vac_bans_url = "https://help.steampowered.com/ru/wizard/VacBans"
        async with self.session.get(account_vac_bans_url) as response:
            if response.status == 200:
                soup = BeautifulSoup(await response.text(), 'html.parser')
                vac_box = soup.select_one(".refund_info_box")
                if vac_box:
                    vac_list = [div.span.text for div in soup.select_one(".refund_info_box").find_all('div') if div.span]
                else:
                    vac_list = []
                result_dict['vac_bans'] = vac_list

        games_url = f"http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key={apikey}&steamid={result_dict['steam_id']}&include_appinfo=true&include_played_free_games=true&format=json/"
        async with self.session.get(games_url) as response:
            if response.status == 200:
                res = await response.json()
                game_count = res['response']['game_count']
                games = {game['name']: round(game['playtime_forever'] / 60) for game in res['response']['games']}
                result_dict['game_count'] = game_count
                result_dict['games'] = games

        csgo_exp_rank_url = f"https://steamcommunity.com/my/gcpd/730?l=english"
        async with self.session.get(csgo_exp_rank_url) as response:
            if response.status == 200:
                soup = BeautifulSoup(await response.text(), 'html.parser')
                for div in soup.find_all('div', class_='generic_kv_line'):
                    if "CS:GO Profile Rank: " in div.text:
                        rank = int(div.text.split("CS:GO Profile Rank: ")[1])
                csgo['csgo_exp_rank'] = rank
        
        csgo_matchmaking_url = f"https://steamcommunity.com/my/gcpd/730?l=english&tab=matchmaking"
        async with self.session.get(csgo_matchmaking_url) as response:
            if response.status == 200:
                soup = BeautifulSoup(await response.text(), 'html.parser')
                table = soup.find('table', class_='generic_kv_table')
                rows = table.find_all('tr')[1:]
                data = {}
                for row in rows:
                    columns = row.find_all('td')
                    mode = columns[0].text.strip()
                    if mode in ["Competitive", "Wingman"]:
                        wins = int(columns[1].text.strip()) if columns[1].text.strip().isdigit() else None
                        skill_group = int(columns[4].text.strip()) if columns[4].text.strip().isdigit() else None
                        last_match = columns[5].text.strip()
                        
                        data[mode] = {
                            "Wins": wins,
                            "Skill Group": skill_group,
                            "Last Match": last_match
                        }
                csgo['matchmaking'] = data
        
        csgo_inventory_url = f"https://steamcommunity.com/profiles/{result_dict['steam_id']}/inventory/json/730/2"
        async with self.session.get(csgo_inventory_url) as response:
            if response.status == 200:
                res = await response.json()
                pattern = re.compile(r'^\d+_\d+$')
                market_names = [description['market_name'] for key, description in res['rgDescriptions'].items() if pattern.match(key)]
                csgo['inventory'] = market_names
                result_dict['csgo'] = csgo

        return result_dict

    async def get_balance(self):
        account_info_url = "https://store.steampowered.com/account/"
        async with self.session.get(account_info_url) as response:
            if response.status == 200:
                soup = BeautifulSoup(await response.text(), 'html.parser')
                return soup.select_one(".accountData.price a").text.split(" ")[0]

    async def get_currency(self):
        account_info_url = "https://store.steampowered.com/account/"
        async with self.session.get(account_info_url) as response:
            if response.status == 200:
                soup = BeautifulSoup(await response.text(), 'html.parser')
                return soup.select_one(".accountData.price a").text.split(" ")[1]

    async def get_country(self):
        account_info_url = "https://store.steampowered.com/account/"
        async with self.session.get(account_info_url) as response:
            if response.status == 200:
                soup = BeautifulSoup(await response.text(), 'html.parser')
                return soup.select_one(".country_settings p .account_data_field").text

    async def get_steamid(self):
        account_info_url = "https://store.steampowered.com/account/"
        async with self.session.get(account_info_url) as response:
            if response.status == 200:
                soup = BeautifulSoup(await response.text(), 'html.parser')
                return soup.select_one(".youraccount_steamid").text.replace("Steam ID: ", "")

    async def get_email(self):
        account_info_url = "https://store.steampowered.com/account/"
        async with self.session.get(account_info_url) as response:
            if response.status == 200:
                soup = BeautifulSoup(await response.text(), 'html.parser')
                return soup.select_one("span.account_manage_label + span.account_data_field").text

    async def get_time_created(self, apikey: str):
        steam_id = await self.get_steamid()
        join_url = f"http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key={apikey}&steamids={steam_id}&format=json/"
        async with self.session.get(join_url) as response:
            if response.status == 200:
                res = await response.json()
                time_created_unix_time = res['response']['players'][0]['timecreated']
                time_created_dt_object = datetime.fromtimestamp(time_created_unix_time)
                return time_created_dt_object.strftime('%Y-%m-%d')

    async def get_last_online(self, apikey: str):
        steam_id = await self.get_steamid()
        join_url = f"http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key={apikey}&steamids={steam_id}&format=json/"
        async with self.session.get(join_url) as response:
            if response.status == 200:
                res = await response.json()
                last_online_unix_time = res['response']['players'][0]['lastlogoff']
                last_online_dt_object = datetime.fromtimestamp(last_online_unix_time)
                return last_online_dt_object.strftime('%Y-%m-%d')

    async def get_vac_bans(self):
        account_vac_bans_url = "https://help.steampowered.com/ru/wizard/VacBans"
        async with self.session.get(account_vac_bans_url) as response:
            if response.status == 200:
                soup = BeautifulSoup(await response.text(), 'html.parser')
                vac_box = soup.select_one(".refund_info_box")
                if vac_box:
                    vac_list = [div.span.text for div in soup.select_one(".refund_info_box").find_all('div') if div.span]
                else:
                    vac_list = []
                return vac_list
    
    async def get_games(self, apikey: str):
        steam_id = await self.get_steamid()
        games_url = f"http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key={apikey}&steamid={steam_id}&include_appinfo=true&include_played_free_games=true&format=json/"
        async with self.session.get(games_url) as response:
            if response.status == 200:
                res = await response.json()
                games = {game['name']: round(game['playtime_forever'] / 60) for game in res['response']['games']}
                return games

    async def get_games_count(self, apikey: str):
        steam_id = await self.get_steamid()
        games_url = f"http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key={apikey}&steamid={steam_id}&include_appinfo=true&include_played_free_games=true&format=json/"
        async with self.session.get(games_url) as response:
            if response.status == 200:
                res = await response.json()
                game_count = res['response']['game_count']
                return game_count
    
    async def get_csgo_exp_rank(self):
        csgo_exp_rank_url = f"https://steamcommunity.com/my/gcpd/730?l=english"
        async with self.session.get(csgo_exp_rank_url) as response:
            if response.status == 200:
                soup = BeautifulSoup(await response.text(), 'html.parser')
                for div in soup.find_all('div', class_='generic_kv_line'):
                    if "CS:GO Profile Rank: " in div.text:
                        rank = int(div.text.split("CS:GO Profile Rank: ")[1])
                return rank
    
    async def get_csgo_matchmaking_ranks(self):
        csgo_matchmaking_url = f"https://steamcommunity.com/my/gcpd/730?l=english&tab=matchmaking"
        async with self.session.get(csgo_matchmaking_url) as response:
            if response.status == 200:
                soup = BeautifulSoup(await response.text(), 'html.parser')
                table = soup.find('table', class_='generic_kv_table')
                rows = table.find_all('tr')[1:]
                data = {}
                for row in rows:
                    columns = row.find_all('td')
                    mode = columns[0].text.strip()
                    if mode in ["Competitive", "Wingman"]:
                        wins = int(columns[1].text.strip()) if columns[1].text.strip().isdigit() else None
                        skill_group = int(columns[4].text.strip()) if columns[4].text.strip().isdigit() else None
                        last_match = columns[5].text.strip()
                        
                        data[mode] = {
                            "Wins": wins,
                            "Skill Group": skill_group,
                            "Last Match": last_match
                        }
                return data
    
    async def get_csgo_inventory(self):
        steam_id = await self.get_steamid()
        csgo_inventory_url = f"https://steamcommunity.com/profiles/{steam_id}/inventory/json/730/2"
        async with self.session.get(csgo_inventory_url) as response:
            if response.status == 200:
                res = await response.json()
                pattern = re.compile(r'^\d+_\d+$')
                market_names = [description['market_name'] for key, description in res['rgDescriptions'].items() if pattern.match(key)]
                return market_names
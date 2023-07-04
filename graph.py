""" Mastodon users followig and followers graph visualization"""
import os.path
import re

from mastodon import Mastodon
from pyvis.network import Network

import config # local config.py file with credentials username and password

CLIENT_CRED_PATH = 'client_cred.secret'
USER_CRED_PATH = 'user_cred.secret'

if not os.path.exists(CLIENT_CRED_PATH):
    print("Creating app")
    Mastodon.create_app(
        client_name =  config.CLIENT_NAME,
        api_base_url = config.API_BASE_URL,
        to_file = CLIENT_CRED_PATH
    )

if not os.path.exists(USER_CRED_PATH):
    print("Creating user login")
    mastodon = Mastodon(client_id = CLIENT_CRED_PATH,)
    mastodon.log_in(
        username = config.USERNAME,
        password = config.PASSWORD,
        to_file = USER_CRED_PATH
    )

mastodon = Mastodon(access_token = USER_CRED_PATH)

accounts_data = {}
def recursive_traverse(user_id, depth=0):
    """
    Go recursively through all users and write their related ones
    """
    account_info = mastodon.account(user_id)

    followers = mastodon.account_followers(id=user_id, limit=10) # Limited at 10 followers (max=80)
    # TODO continious fetch
    # use following functions to fetch all
    # mastodon.fetch_next mastodon.fetch_remaining
    # TODO add following accounts
    # use mastodon.account_following()
    # + use sets instead of lists

    print("Doing: " + str(user_id) + " " + account_info["acct"])
    if not user_id in accounts_data:
        accounts_data[user_id] = {
            'title' : account_info["acct"],
            'value' : account_info["followers_count"],
            'followers' : [],
            'url' : account_info["url"],
        }

    for follower in followers:
        follower_id = follower["id"]
        if not follower_id in accounts_data:
            accounts_data[follower_id] = {
                'title' : follower["acct"],
                'value' : follower["followers_count"],
                'followers' : [],
                'url' : follower["url"],
            }

        accounts_data[user_id]["followers"].append(follower_id)
        if depth > 0:
            recursive_traverse(follower_id, depth - 1)

net = Network()
def draw_graph():
    """Draw graph from accounts_data"""

    # Add all nodes from data
    for account_id, account in accounts_data.items():
        # Get domain from url to use it in nodo group for coloring
        url = account["url"]
        pattern = r"https?://([\w.-]+)/"
        match = re.search(pattern, url)
        domain = match.group(1) if match else None

        net.add_node(account_id,
                     label=str(account_id),
                     group=domain,
                     title=account["title"],
                     value=account["value"])

    # Add all edges from data
    for account_id, account in accounts_data.items():
        for follower_id in account["followers"]:
            net.add_edge(account_id, follower_id)

recursive_traverse(mastodon.me()["id"], 1)
draw_graph()

net.toggle_physics(False)
net.show('graph.html', notebook=False)

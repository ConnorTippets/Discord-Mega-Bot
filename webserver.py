from quart import *
from discord.ext import ipc
from properties import ipc_key

app = Quart(__name__)
ipc_client = ipc.Client(
    secret_key=ipc_key
)  # secret_key must be the same as your server


@app.route("/")
async def index():
    users = await ipc_client.request("get_users")
    guilds = await ipc_client.request("get_guilds")
    return f"Guilds: {guilds}</br>Users: {users:,}"

@app.route("/api/stats")
async def stats():
    users = await ipc_client.request("get_users")
    guilds = await ipc_client.request("get_guilds")
    return jsonify({"guilds": str(guilds), "users": f"{users:,}"})

@app.route("/api/get_member_count")
async def member_count():
    count = await ipc_client.request("get_member_count", guild_id=int(request.args.get("guild_id")))
    return str(count)

app.run()

import json

import quart
import quart_cors
from quart import request

# Note: Setting CORS to allow chat.openapi.com is required for ChatGPT to access your plugin
app = quart_cors.cors(quart.Quart(__name__), allow_origin="https://chat.openai.com")

_SKILLS = {}


@app.post("/skills/<string:username>")
async def add_skill(username):
    request = await quart.request.get_json(force=True)
    if username not in _SKILLS:
        _SKILLS[username] = []
    _SKILLS[username].append(request["skill"])
    return quart.Response(response='OK', status=200)

@app.post("/setskills/<string:username>")
async def set_skills(username):
    request = await quart.request.get_json(force=True)
    _SKILLS[username] = request["skills"]
    return quart.Response(response='OK', status=200)

@app.get("/skills/<string:username>")
async def get_skills(username):
    return quart.Response(response=json.dumps(_SKILLS.get(username, [])), status=200)


@app.delete("/skills/<string:username>")
async def delete_skill(username):
    request = await quart.request.get_json(force=True)
    skill_idx = request["skill_idx"]
    if 0 <= skill_idx < len(_SKILLS[username]):
        _SKILLS[username].pop(skill_idx)
    return quart.Response(response='OK', status=200)


@app.get("/logo.png")
async def plugin_logo():
    filename = 'static/logo.png'
    return await quart.send_file(filename, mimetype='image/png')


@app.get("/.well-known/ai-plugin.json")
async def plugin_manifest():
    host = request.headers['Host']
    with open("ai-plugin.json") as f:
        text = f.read()
        # This is a trick we do to populate the PLUGIN_HOSTNAME constant in the manifest
        text = text.replace("PLUGIN_HOSTNAME", f"https://{host}")
        return quart.Response(text, mimetype="text/json")


@app.get("/openapi.yaml")
async def openapi_spec():
    host = request.headers['Host']
    with open("openapi.yaml") as f:
        text = f.read()
        # This is a trick we do to populate the PLUGIN_HOSTNAME constant in the OpenAPI spec
        text = text.replace("PLUGIN_HOSTNAME", f"https://{host}")
        return quart.Response(text, mimetype="text/yaml")


def main():
    app.run(debug=True, host="0.0.0.0", port=5003, certfile='secret/localhost.crt', keyfile='secret/localhost.key')


if __name__ == "__main__":
    main()
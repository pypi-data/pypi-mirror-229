# Qlik SDK

Qlik's Python SDK allows you to leverage the APIs of Qlik Cloud platform from the comfort of python.

---

- [qlik-sdk-python](#qlik-sdk-python)
  - [Install](#install)
  - [Getting started](#getting-started)
  - [Authentication options](#authentication-options)
    - [API keys](#api-keys)
  - [Changelog](#changelog)
  - [Contributing](#contributing)
    - [Bugs](#bugs)
    - [Features](#features)
    - [Developing](#developing)
  - [Examples](#examples)
    - [apps_items.py](#apps_itemspy)
    - [flask_oauth.py](#flask_oauthpy)
    - [import_export.py](#import_exportpy)
    - [rpc basics example_custom_type.py](#rpc-basics-example_custom_typepy)
    - [rpc basics lists app_object_list app_object_list.py](#rpc-basics-lists-app_object_list-app_object_listpy)
    - [rpc basics lists field_list field_list.py](#rpc-basics-lists-field_list-field_listpy)
    - [rpc basics lists variable_list variable_list.py](#rpc-basics-lists-variable_list-variable_listpy)
    - [rpc data hypercubes pivot hypercube_pivot.py](#rpc-data-hypercubes-pivot-hypercube_pivotpy)
    - [rpc data hypercubes stacked hypercube_stacked.py](#rpc-data-hypercubes-stacked-hypercube_stackedpy)
    - [rpc data hypercubes straight hypercube_straight.py](#rpc-data-hypercubes-straight-hypercube_straightpy)
    - [rpc rpc.py](#rpc-rpcpy)

---

## Install

```bash
python3 -m pip install --upgrade qlik-sdk
```

## Getting started

The lowest supported python version is `3.8`.
A good place to start is our [examples](./examples/). Take a look and learn how to authorize and use our REST and RPC clients to access the APIs. If you're in a real hurry, the essence of our examples is shown below.

```python
from qlik_sdk import Auth, AuthType, Config

api_key = "<MY_API_KEY>"
base_url = "<URL_TO_MY_TENANT>" # E.g. https://foo.qlikcloud.eu.com

q = Qlik(config=Config(host=base_url, auth_type=AuthType.APIKey, api_key=api_key))

user = q.users.get_me()
print("Logged in as: " + user.name)
# For REST calls: auth.rest
# For RPC calls: auth.rpc
```

## Authentication options

### API keys

An API key is a token representing a user in your tenant. Anyone may interact with the platform programmatically using the API key. The token contains the user context, respecting the access control privileges the user has in your tenant. More info can be found on [Qlik Dev Portal](https://qlik.dev/basics/authentication-options#api-keys).

For a step-by-step guide on how to get an API key for your tenant, check this [tutorial](https://qlik.dev/tutorials/generate-your-first-api-key).

### OAuth2

OAuth is a standard security protocol for authorization and delegation. It allows third party applications to access API resources without disclosing the end-user credentials.

For a step-by-step guide on how to create an OAuth client for your tenant, check [Creating and managing OAuth clients](https://help.qlik.com/en-US/cloud-services/Subsystems/Hub/Content/Sense_Hub/Admin/mc-create-oauth-client.htm)

```py
# Authorization
  # Create auth object
  config = Config(
        host='my-tenant.qlikcloud.com',
        auth_type=AuthType.OAuth2,
        client_id='<clientId>',
        client_secret='<clientSecret>',
        redirect_url='<redirectUrl>',
        scope='<scopes>',
    )
  auth = Auth(config=config)

  # for login redirect to authorization uri for OAuth exchange token flow
  # which will call callback endpoint with credentials
  redirect(auth.generate_authorization_url(), code=301)

  # on callback endpoint (redirectUri), exachange the creadentials with token
  auth.authorize(request.full_path)

  # fetch a resource
  user = auth.rest(path="/users/me")

  # refreshing token
  auth.refresh_token()

  # deauthorization
  auth.deauthorize()
```

## Examples

### apps_items.py

```py

import os
import uuid
from dataclasses import asdict

from dotenv import dotenv_values

from qlik_sdk import (
    AppAttributes,
    AppUpdateAttributes,
    AuthType,
    Config,
    CreateApp,
    Qlik,
    UpdateApp,
)

# get QCS_SERVER and QCS_API_KEY from .env file in the same folder as this script
file_dir = os.path.dirname(os.path.abspath(__file__))
dotenv_path = os.path.join(file_dir, ".env")
if not os.path.exists(dotenv_path):
    print("Missing .env file: " + dotenv_path)
env_values = dotenv_values(dotenv_path=dotenv_path)
host = env_values.get("QCS_SERVER", False)
api_key = env_values.get("QCS_API_KEY", False)

config = Config(host=host, auth_type=AuthType.APIKey, api_key=api_key)
q = Qlik(config=config)

user = q.users.get_me()
print("Logged in as: " + user.name)


def log_req(req):
    print("request:", req.method, req.url)
    return req


def log_res(res):
    print("response:", res.request.method, res.request.url, "->", res.status_code)
    return res


q.apps.auth.rest.interceptors["response"].use(log_res)
q.apps.auth.rest.interceptors["request"].use(log_req)

# The body parameter can be either an object or a dict
# The recommended way is to use an object

# create apps - 2 methods - dict body or obj body
# create app - dict body
random_app_name1 = str(uuid.uuid1())
app_dict_body = q.apps.create(data={"attributes": {"name": random_app_name1}})
app_dict_body.delete()

# create app - obj body
random_app_name2 = str(uuid.uuid1())
app = q.apps.create(
    data=CreateApp(
        attributes=AppAttributes(name=random_app_name2, description="desc", spaceId="")
    ),
)

# Convert app object to dict
app_asdict = asdict(app)

# set load script, reload and evaluate expression
with app.open():
    script = "Load RecNo() as N autogenerate(200);"
    app.set_script(script)
    app.do_reload()
    eval = app.evaluate("SUM([N])")
    print(eval)


# Set attribute
# body: dict
app.set(data={"attributes": {"name": "set-name-dict"}})
# body: obj
update_name = str(uuid.uuid1())
app.set(
    UpdateApp(
        attributes=AppUpdateAttributes(description="new description", name=update_name)
    )
)


# items list - query param name
items0 = q.items.get_items(name=update_name)
app.delete()
items1 = q.items.get_items(name=update_name)
# get_items using an app name query param, result-length before and after delete
print(
    f"found items matching: {update_name}, before and after delete: {len(items0)}, {len(items1)}"
)


items = q.items.get_items()
first_100_item_names = []
for item in items.pagination:
    if len(first_100_item_names) < 100:
        first_100_item_names.append(item.name)
    else:
        break

```

### flask_oauth.py

```py

import os
import random

from dotenv import dotenv_values
from flask import Flask, redirect, render_template, request

# src. should be removed when example is public
from src.qlik_sdk import Auth, AuthType, Config

# get QCS_SERVER and QCS_API_KEY from .env file in the same folder as this script
file_dir = os.path.dirname(os.path.abspath(__file__))
dotenv_path = os.path.join(file_dir, ".env")
if not os.path.exists(dotenv_path):
    print("Missing .env file: " + dotenv_path)
env_values = dotenv_values(dotenv_path=dotenv_path)
host = env_values.get("QCS_SERVER_OAUTH", False)
client_id = env_values.get("CLIENT_ID_WEB", False)
client_secret = env_values.get("CLIENT_SECRET_WEB", False)
redirect_url = "http://localhost:3000/login/callback"


config = Config(
    host=host,
    auth_type=AuthType.OAuth2,
    client_id=client_id,
    client_secret=client_secret,
    redirect_url=redirect_url,
    scope=["offline_access"],
)
auth = Auth(config=config)

app = Flask(__name__)

template_data = {"is_logged_in": False, "user": "", "eval_result": ""}


@app.route("/")
def index():
    try:
        user = auth.rest(path="/users/me")
        user = user.json()
        template_data["is_logged_in"] = True
        template_data["user"] = f"User: {user['name']} is logged in"
    except Exception:
        template_data["is_logged_in"] = False
        template_data["user"] = ""
    return render_template("index.html", template_data=template_data)


@app.route("/login")
def login():
    return redirect(auth.generate_authorization_url(), code=301)


@app.route("/login/callback")
def callback():
    auth.authorize(request.full_path)
    return redirect("/", code=301)


@app.route("/logout")
def logout():
    auth.deauthorize()
    template_data["is_logged_in"] = False
    template_data["user"] = ""
    return redirect("/", code=301)


@app.route("/refresh")
def refresh():
    auth.refresh_token()
    return redirect("/", code=301)


@app.route("/websocket")
def websocket():
    random_id = random.randint(1, 1000)
    app_id = f"SessionApp_{random_id}"
    try:
        # Open a websocket for a session app using RpcClient
        rpc_session = auth.rpc(app_id)
        try:
            rpc_session.open()
            app_handle = (rpc_session.send("GetActiveDoc", -1))["qReturn"]["qHandle"]
            rpc_session.send(
                "SetScript",
                app_handle,
                "Load RecNo() as N autogenerate(10)",
            )
            rpc_session.send("DoReload", app_handle)
            eval_result = rpc_session.send("Evaluate", app_handle, "SUM([N])")
            template_data["is_logged_in"] = True
            template_data["eval_result"] = eval_result["qReturn"]
        except Exception as err:
            print(f"rpc_session error occured: {err}")
            return redirect("/", code=500)
        finally:
            rpc_session.close()
            print("rpc_connection closed")
    except Exception as err:
        print(f"error occured while setting up auth: {err}")
        return redirect("/", code=500)
    return redirect("/", code=301)


if __name__ == "__main__":
    app.run(host="localhost", port=3000, debug=True)

```

### import_export.py

```py

import json
import os
import shutil
import uuid

from dotenv import dotenv_values

from qlik_sdk import AuthType, Config, Qlik

# get QCS_SERVER and QCS_API_KEY from .env file in the same folder as this script
file_dir = os.path.dirname(os.path.abspath(__file__))
dotenv_path = os.path.join(file_dir, ".env")
if not os.path.exists(dotenv_path):
    print("Missing .env file: " + dotenv_path)
env_values = dotenv_values(dotenv_path=dotenv_path)
host = env_values.get("QCS_SERVER", False)
api_key = env_values.get("QCS_API_KEY", False)

with open(os.path.join(file_dir, "sheetListDef.json")) as json_file:
    sheet_list_def = json.load(json_file)


config = Config(host=host, auth_type=AuthType.APIKey, api_key=api_key)
q = Qlik(config=config)

# Print user name
user = q.users.get_me()
print("Logged in as: " + user.name)

# Create a managed space
space_name = "publish-apps-sdk-test" + str(uuid.uuid1())
shared_space = q.spaces.create(
    {
        "name": space_name,
        "description": "space used for testing",
        "type": "managed",
    }
)
print(f"created space with name {space_name} and id {shared_space.id}")

# Import app - (app with multiple sheets)
qvf_file = os.path.join(file_dir, "two-sheets.qvf")
app_name = "import-test" + str(uuid.uuid1())
with open(qvf_file, "rb") as qvf_data:
    imported_app = q.apps.import_app(data=qvf_data, name=app_name)

print(f"imported app with name {app_name} and id {imported_app.attributes.id}")

# Publish each sheet
print(f"open app with id {imported_app.attributes.id} and publish all sheets")
with imported_app.open():
    session_obj = imported_app.create_session_object(sheet_list_def)
    sheet_list_layout = session_obj.get_layout()
    sheet_id_list = [q.qInfo.qId for q in sheet_list_layout.qAppObjectList.qItems]
    for sheet_id in sheet_id_list:
        print(f"publishing sheet with id {sheet_id}")
        sheet_obj = imported_app.get_object(sheet_id)
        sheet_obj.publish()

# Publish the app
print(
    f"publish app with id {imported_app.attributes.id} to space with id {shared_space.id}"
)
published_app = imported_app.publish({"spaceId": shared_space.id})
print(f"published app id {published_app.attributes.id}")

# export app
local_filename = f"exported{uuid.uuid1()}.qvf"
temp_contents_url = imported_app.export()
# download app streaming to file
with q.auth.rest(path=temp_contents_url, method="get", stream=True) as r:
    with open(local_filename, "wb") as f:
        shutil.copyfileobj(r.raw, f)
print(f"Exported {published_app.attributes.name} to {local_filename}")

ext_file_path = env_values.get("EXTENSION_ZIP_PATH", False)
# Upload extension
with open(ext_file_path, "rb") as ext_file:
    ext = q.extensions.create(file=ext_file)


# TODO
# set properties - change sheet name
# upload theme
# apply themes on the app
# import datafiles

# Delete everything created
print("cleaning up")
ext.delete()
imported_app.delete()
published_app.delete()
shared_space.delete()
os.remove(local_filename)

```

### rpc basics example_custom_type.py

```py

import os
import sys
import uuid

from dotenv import dotenv_values

from qlik_sdk import Apps, Auth, AuthType, Config

# get QCS_SERVER and QCS_API_KEY from .env file in the same folder as this script
file_dir = os.path.dirname(os.path.abspath(__file__))
dotenv_path = os.path.join(file_dir, "../../.env")
if not os.path.exists(dotenv_path):
    print("Missing .env file: " + dotenv_path)
env_values = dotenv_values(dotenv_path=dotenv_path)
host = env_values.get("QCS_SERVER", False)
api_key = env_values.get("QCS_API_KEY", False)

config = Config(host=host, auth_type=AuthType.APIKey, api_key=api_key)


auth = Auth(config)
apps = Apps(config)

session_app_id = "SessionApp_" + str(uuid.uuid1())
session_app = apps.create_session_app(session_app_id)
with session_app.open():
    # create a generic object of a custom type
    properties = {
        "qInfo": {"qType": "custom-object"},
    }

    obj = session_app.create_session_object(properties)

    # set a custom property i.e. a property not defined in GenericObjectProperties
    properties["CustomProperty"] = "custom-property-value"
    obj.set_properties(properties)

    # fetch the properties and validate that the custom property is returned
    new_props = obj.get_properties()
    if new_props.qInfo.qType != "custom-object":
        sys.exit(1)
    if new_props.CustomProperty != "custom-property-value":
        sys.exit(1)

```

### rpc basics lists app_object_list app_object_list.py

```py

import os
import sys
import uuid

from dotenv import dotenv_values

from src.qlik_sdk import Apps, AuthType, Config, GenericObjectProperties
from src.qlik_sdk.apis.Apps import JsonObject
from src.qlik_sdk.apis.Qix import AppObjectListDef, NxInfo


class CustomObjectProperties(GenericObjectProperties):
    meta: dict[str, str] = None


def list_app_objects():
    # get QCS_SERVER and QCS_API_KEY from .env file in the same folder as this script
    file_dir = os.path.abspath("")
    dotenv_path = os.path.join(file_dir + "/examples", ".env")
    if not os.path.exists(dotenv_path):
        print("Missing .env file: " + dotenv_path)
    env_values = dotenv_values(dotenv_path=dotenv_path)
    host = env_values.get("QCS_SERVER", False)
    api_key = env_values.get("QCS_API_KEY", False)

    config = Config(host=host, auth_type=AuthType.APIKey, api_key=api_key)
    apps = Apps(config)

    session_app_id = "SessionApp_" + str(uuid.uuid1())
    session_app = apps.create_session_app(session_app_id)

    with session_app.open():
        for i in range(10):
            properties = CustomObjectProperties(
                qInfo=NxInfo(qType="my-object"),
                meta=dict({"title": f"my-object-{i}"}),
            )
            session_app.create_object(properties)
        list_properties = GenericObjectProperties(
            qInfo=NxInfo(qType="my-list"),
            qAppObjectListDef=AppObjectListDef(
                qType="my-object", qData=JsonObject(title="/meta/title")
            ),
        )
        try:
            object = session_app.create_object(qProp=list_properties)
            layout = object.get_layout()
            return layout.qAppObjectList.qItems.__len__()
        except ValueError as e:
            print(e.__class__)


if list_app_objects() != 10:
    print("Error in number of objects .....")
    sys.exit(1)

```

### rpc basics lists field_list field_list.py

```py

import os
import sys
import uuid

from dotenv import dotenv_values

from src.qlik_sdk import Apps, AuthType, Config, GenericObjectProperties
from src.qlik_sdk.apis.Qix import FieldListDef, NxInfo

script = """
TempTable:
Load
RecNo() as Field1,
Rand() as Field2,
Rand() as Field3
AutoGenerate 100
"""


# get QCS_SERVER and QCS_API_KEY from .env file in the same folder as this script
file_dir = os.path.abspath("")
dotenv_path = os.path.join(file_dir + "/examples", ".env")
if not os.path.exists(dotenv_path):
    print("Missing .env file: " + dotenv_path)
env_values = dotenv_values(dotenv_path=dotenv_path)
host = env_values.get("QCS_SERVER", False)
api_key = env_values.get("QCS_API_KEY", False)

config = Config(host=host, auth_type=AuthType.APIKey, api_key=api_key)
apps = Apps(config)

session_app_id = "SessionApp_" + str(uuid.uuid1())
session_app = apps.create_session_app(session_app_id)

with session_app.open():
    # Load in some data into the session document:
    session_app.set_script(script)
    session_app.do_reload()

    # Create a field list using qFieldListDef and list all fields available in the document.

    object = session_app.create_session_object(
        GenericObjectProperties(
            qInfo=NxInfo(qType="my-field-list"),
            qFieldListDef=FieldListDef(),
        )
    )
    layout = object.get_layout()
    print("field-list ", layout.qFieldList.qItems)
    items = layout.qFieldList.qItems
    if (
        items.__len__() != 3
        or items[0].qName != "Field1"
        or items[1].qName != "Field2"
        or items[2].qName != "Field3"
    ):
        print("Error generated qFieldsLists ......")
        sys.exit(1)

```

### rpc basics lists variable_list variable_list.py

```py

import os
import sys
import uuid

from dotenv import dotenv_values

from src.qlik_sdk import Apps, AuthType, Config, GenericObjectProperties
from src.qlik_sdk.apis.Apps import JsonObject
from src.qlik_sdk.apis.Qix import NxInfo, VariableListDef

script = """
TempTable:
Load
RecNo() as Field1,
Rand() as Field2,
Rand() as Field3
AutoGenerate 100
"""


# get QCS_SERVER and QCS_API_KEY from .env file in the same folder as this script
file_dir = os.path.abspath("")
dotenv_path = os.path.join(file_dir + "/examples", ".env")
if not os.path.exists(dotenv_path):
    print("Missing .env file: " + dotenv_path)
env_values = dotenv_values(dotenv_path=dotenv_path)
host = env_values.get("QCS_SERVER", False)
api_key = env_values.get("QCS_API_KEY", False)

config = Config(host=host, auth_type=AuthType.APIKey, api_key=api_key)
apps = Apps(config)

session_app_id = "SessionApp_" + str(uuid.uuid1())
session_app = apps.create_session_app(session_app_id)

with session_app.open():
    # Load in some data into the session document:
    session_app.set_script(script)
    session_app.do_reload()
    session_app.create_variable_ex(
        GenericObjectProperties(
            qInfo=NxInfo(qType="variable"),
            qComment="sample comment",
            qDefinition="=Count(Field1)",
            qName="vVariableName",
        )
    )
    variable = session_app.get_variable_by_id("vVariableName")
    object = session_app.create_session_object(
        GenericObjectProperties(
            qInfo=NxInfo(qType="VariableList"),
            qVariableListDef=VariableListDef(
                qType="variable",
                qData=JsonObject(tags="/tags"),
                qShowSession=True,
                qShowConfig=True,
                qShowReserved=True,
            ),
        )
    )
    layout = object.get_layout()
    layout.qVariableList.qItems
    print("variable-list: ", layout.qVariableList.qItems)
    for item in layout.qVariableList.qItems:
        if item.qName == "vVariableName":
            sys.exit(0)
    sys.exit(1)

```

### rpc data hypercubes pivot hypercube_pivot.py

```py

import os
import sys
import uuid

from dotenv import dotenv_values

from src.qlik_sdk import Apps, AuthType, Config
from src.qlik_sdk.apis.Qix import (
    GenericObjectProperties,
    HyperCubeDef,
    NxDimension,
    NxInfo,
    NxInlineDimensionDef,
    NxInlineMeasureDef,
    NxMeasure,
    NxPage,
    NxSelectionCell,
)

script = """
TempTable:
Load
RecNo() as ID,
RecNo()+1 as ID2,
Rand() as Value
AutoGenerate 100
"""

# get QCS_SERVER and QCS_API_KEY from .env file
file_dir = os.path.dirname(os.path.abspath(__file__))
dotenv_path = os.path.join(file_dir, "../../../../.env")
if not os.path.exists(dotenv_path):
    print("Missing .env file: " + dotenv_path)
env_values = dotenv_values(dotenv_path=dotenv_path)
host = env_values.get("QCS_SERVER", False)
api_key = env_values.get("QCS_API_KEY", False)

config = Config(host=host, auth_type=AuthType.APIKey, api_key=api_key)
apps = Apps(config)

session_app_id = "SessionApp_" + str(uuid.uuid1())
session_app = apps.create_session_app(session_app_id)
with session_app.open():
    # Load in some data into the session document:
    session_app.set_script(script)
    session_app.do_reload()

    obj = session_app.create_object(
        GenericObjectProperties(
            qInfo=NxInfo(qType="my-pivot-hypercube"),
            qHyperCubeDef=HyperCubeDef(
                qDimensions=[
                    NxDimension(qDef=NxInlineDimensionDef(qFieldDefs=["ID"])),
                    NxDimension(qDef=NxInlineDimensionDef(qFieldDefs=["ID2"])),
                ],
                qMeasures=[
                    NxMeasure(
                        qDef=NxInlineMeasureDef(
                            qDef="Sum(Value)",
                        )
                    )
                ],
                qMode="EQ_DATA_MODE_PIVOT",
                qAlwaysFullyExpanded=True,
            ),
        )
    )
    data = obj.get_hyper_cube_pivot_data(
        "/qHyperCubeDef",
        [
            NxPage(
                qHeight=5,
                qLeft=0,
                qTop=0,
                qWidth=2,
            )
        ],
    )

    print("HyperCude object data: ", data)

    obj.select_pivot_cells(
        "/qHyperCubeDef", [NxSelectionCell(qType="D", qRow=1, qCol=0)], False, False
    )

    data = obj.get_hyper_cube_pivot_data(
        "/qHyperCubeDef",
        [
            NxPage(
                qHeight=5,
                qLeft=0,
                qTop=0,
                qWidth=2,
            )
        ],
    )

    print("Hypercube data pages after selection: ", data)
    if not (
        len(data) == 1
        and len(data[0].qData) == 1
        and len(data[0].qTop) == 1
        and data[0].qTop[0].qText == "Sum(Value)"
    ):
        print("Error in generated stack pages ......")
        sys.exit(1)

```

### rpc data hypercubes stacked hypercube_stacked.py

```py

import os
import sys
import uuid

from dotenv import dotenv_values

from src.qlik_sdk import Apps, AuthType, Config
from src.qlik_sdk.apis.Qix import (
    GenericObjectProperties,
    HyperCubeDef,
    NxDimension,
    NxInfo,
    NxInlineDimensionDef,
    NxInlineMeasureDef,
    NxMeasure,
    NxPage,
    NxSelectionCell,
)

script = """
TempTable:
Load
RecNo() as ID,
RecNo()+1 as ID2,
Rand() as Value
AutoGenerate 100
"""

# get QCS_SERVER and QCS_API_KEY from .env file
file_dir = os.path.dirname(os.path.abspath(__file__))
dotenv_path = os.path.join(file_dir, "../../../../.env")
if not os.path.exists(dotenv_path):
    print("Missing .env file: " + dotenv_path)
env_values = dotenv_values(dotenv_path=dotenv_path)
host = env_values.get("QCS_SERVER", False)
api_key = env_values.get("QCS_API_KEY", False)

config = Config(host=host, auth_type=AuthType.APIKey, api_key=api_key)
apps = Apps(config)

session_app_id = "SessionApp_" + str(uuid.uuid1())
session_app = apps.create_session_app(session_app_id)
with session_app.open():
    # Load in some data into the session document:
    session_app.set_script(script)
    session_app.do_reload()

    obj = session_app.create_object(
        GenericObjectProperties(
            qInfo=NxInfo(
                qType="my-stacked-hypercube",
            ),
            qHyperCubeDef=HyperCubeDef(
                qDimensions=[
                    NxDimension(qDef=NxInlineDimensionDef(qFieldDefs=["ID"])),
                    NxDimension(qDef=NxInlineDimensionDef(qFieldDefs=["ID2"])),
                ],
                qMeasures=[
                    NxMeasure(
                        qDef=NxInlineMeasureDef(
                            qDef="Sum(Value)",
                        )
                    )
                ],
                qMode="EQ_DATA_MODE_PIVOT_STACK",
                qAlwaysFullyExpanded=True,
            ),
        )
    )
    data = obj.get_hyper_cube_stack_data(
        "/qHyperCubeDef",
        [
            NxPage(
                qHeight=5,
                qLeft=0,
                qTop=0,
                qWidth=2,
            )
        ],
        10000,
    )

    print("HyperCude stack data: ", data)

    obj.select_pivot_cells(
        "/qHyperCubeDef",
        [
            NxSelectionCell(
                qType="D",
                qRow=1,
                qCol=0,
            )
        ],
        False,
        False,
    )

    data = obj.get_hyper_cube_stack_data(
        "/qHyperCubeDef",
        [
            NxPage(
                qHeight=5,
                qLeft=0,
                qTop=0,
                qWidth=2,
            )
        ],
        10000,
    )
    print("Hypercube stack data pages after selection: ", data)
    if not (
        len(data) == 1
        and len(data[0].qData) == 1
        and len(data[0].qData[0].qSubNodes) == 1
        and len(data[0].qData[0].qSubNodes[0].qSubNodes) == 1
    ):
        print("Error in generated stack pages ......")
        sys.exit(1)

```

### rpc data hypercubes straight hypercube_straight.py

```py

import os
import sys
import uuid

from dotenv import dotenv_values

from src.qlik_sdk import Apps, AuthType, Config
from src.qlik_sdk.apis.Qix import (
    GenericObjectProperties,
    HyperCubeDef,
    NxDimension,
    NxInfo,
    NxInlineDimensionDef,
    NxInlineMeasureDef,
    NxMeasure,
    NxPage,
)

script = """
TempTable:
Load
RecNo() as ID,
Rand() as Value
AutoGenerate 100
"""

# get QCS_SERVER and QCS_API_KEY from .env file
file_dir = os.path.dirname(os.path.abspath(__file__))
dotenv_path = os.path.join(file_dir, "../../../../.env")
if not os.path.exists(dotenv_path):
    print("Missing .env file: " + dotenv_path)
env_values = dotenv_values(dotenv_path=dotenv_path)
host = env_values.get("QCS_SERVER", False)
api_key = env_values.get("QCS_API_KEY", False)

config = Config(host=host, auth_type=AuthType.APIKey, api_key=api_key)
apps = Apps(config)

session_app_id = "SessionApp_" + str(uuid.uuid1())
session_app = apps.create_session_app(session_app_id)
with session_app.open():
    # Load in some data into the session document:
    session_app.set_script(script)
    session_app.do_reload()
    obj = session_app.create_object(
        GenericObjectProperties(
            qInfo=NxInfo(
                qType="my-straight-hypercube",
            ),
            qHyperCubeDef=HyperCubeDef(
                qDimensions=[NxDimension(qDef=NxInlineDimensionDef(qFieldDefs=["ID"]))],
                qMeasures=[
                    NxMeasure(
                        qDef=NxInlineMeasureDef(
                            qDef="=Sum(Value)",
                        )
                    )
                ],
                qInitialDataFetch=[NxPage(qHeight=5, qWidth=2)],
            ),
        )
    )
    layout = obj.get_layout()
    print("Hypercube data pages: ", layout)
    data = obj.select_hyper_cube_cells("/qHyperCubeDef", [0, 2, 4], [0], False, False)
    print("After selection (notice the `qState` values)")
    print("HyperCude object data: ", data)
    layout = obj.get_layout()
    print(layout)
    if not (
        len(layout.qHyperCube.qDimensionInfo[0].qGroupFieldDefs) == 1
        and layout.qHyperCube.qDimensionInfo[0].qGroupFieldDefs[0] == "ID"
        and layout.qInfo.qType == "my-straight-hypercube"
    ):
        print("Error in generated layout ......")
        sys.exit(1)

```

### rpc rpc.py

```py

import os
import uuid

from dotenv import dotenv_values

from qlik_sdk import Auth, AuthType, Config, Qlik
from qlik_sdk.rpc import RequestObject

# get QCS_SERVER and QCS_API_KEY from .env file in the same folder as this script
file_dir = os.path.dirname(os.path.abspath(__file__))
dotenv_path = os.path.join(file_dir, "../.env")
if not os.path.exists(dotenv_path):
    print("Missing .env file: " + dotenv_path)
env_values = dotenv_values(dotenv_path=dotenv_path)
host = env_values.get("QCS_SERVER", False)
api_key = env_values.get("QCS_API_KEY", False)

auth = Auth(Config(host=host, auth_type=AuthType.APIKey, api_key=api_key))
q = Qlik(Config(host=host, auth_type=AuthType.APIKey, api_key=api_key))


def log_request_interceptor(request: RequestObject) -> RequestObject:
    print("request: " + str(request))
    return request


def log_qreturn_response_interceptor(response):
    if "result" in response and "qReturn" in response["result"]:
        qreturn = str(response["result"]["qReturn"])
        print(f"qReturn: {qreturn}")
    return response


# register interceptors
auth.rpc.interceptors["request"].use(log_request_interceptor)
auth.rpc.interceptors["response"].use(log_qreturn_response_interceptor)

session_app_id = "SessionApp_" + str(uuid.uuid1())
rpc_session = auth.rpc(app_id=session_app_id)

with rpc_session.open() as rpc_client:
    app = rpc_client.send("OpenDoc", -1, session_app_id)
    handle = app["qReturn"]["qHandle"]
    script = "Load RecNo() as N autogenerate(200);"
    # set load script and reload
    rpc_client.send("SetScript", handle, script)
    rpc_client.send("DoReload", handle)

    # parameters can be passed without name which will be sent positional in an array
    count_expr = "COUNT([N])"
    positional_eval = rpc_client.send("Evaluate", handle, count_expr)
    print(f"Evaluate {count_expr} = {positional_eval}")

    # parameters can also be passed with name which will be sent as an object
    sum_expr = "SUM([N])"
    keyword_eval = rpc_client.send("Evaluate", handle, qExpression=sum_expr)
    print(f"Evaluate {sum_expr} = {keyword_eval}")

```

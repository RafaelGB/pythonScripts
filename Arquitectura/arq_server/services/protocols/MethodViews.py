from flask import request, make_response, jsonify
from flask.views import MethodView

class InventoryItemApi(MethodView):
        """ /api/inventory/<item_name> """
        inventory = {
            "apple": {
                "description": "Crunchy and delicious",
                "qty": 30
            },
            "cherry": {
                "description": "Red and juicy",
                "qty": 500
            },
            "mango": {
                "description": "Red and juicy",
                "qty": 500
            }
        }

        error = {
            "itemNotFound": {
                "errorCode": "itemNotFound",
                "errorMessage": "Item not found"
            },
            "itemAlreadyExists": {
                "errorCode": "itemAlreadyExists",
                "errorMessage": "Could not create item. Item already exists"
            }
        }

        def get(self, item_name):
            """ Get an item """
            if not self.inventory.get(item_name, None):
                return make_response(jsonify(self.error["itemNotFound"]), 400)
            return make_response(jsonify(self.inventory[item_name]), 200)

        def post(self, item_name):
            """ Create an item """
            if self.inventory.get(item_name, None):
                return make_response(jsonify(self.error["itemAlreadyExists"]), 400)
            body = request.get_json()
            self.inventory[item_name] = {"description": body.get("description", None), "qty": body.get("qty", None)}
            return make_response(jsonify(self.inventory[item_name]))

        def put(self, item_name):
            """ Update/replace an item """
            body = request.get_json()
            self.inventory[item_name] = {"description": body.get("description", None), "qty": body.get("qty", None)}
            return make_response(jsonify(self.inventory[item_name]))

        def patch(self, item_name):
            """ Update/modify an item """
            if not self.inventory.get(item_name, None):
                return make_response(jsonify(self.error["itemNotFound"]), 400)
            body = request.get_json()
            self.inventory[item_name].update({"description": body.get("description", None), "qty": body.get("qty", None)})
            return make_response(jsonify(self.inventory[item_name]))

        def delete(self, item_name):
            """ Delete an item """
            if not self.inventory.get(item_name, None):
                return make_response(jsonify(self.error["itemNotFound"]), 400)
            del self.inventory[item_name]
            return make_response(jsonify({}), 200)


methodViewDict = {
    "inventory_item_api": InventoryItemApi
}

def selectMethod(alias):
    if alias in methodViewDict:
        return methodViewDict[alias]
    else:
        return None
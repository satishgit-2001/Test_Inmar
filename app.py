from flask import Flask, Response, request
import json
from bson import json_util,ObjectId
from pymongo import MongoClient


MONGO_URL = "mongodb://localhost:27017/sst_test_database"
client = MongoClient(MONGO_URL, connect=False, maxPoolSize=3, maxIdleTimeMS=30000)
db_handle = client['sst_test_database']

app = Flask(__name__)


@app.route("/test", methods=['GET'])
def test_flask():
    print("hello")
    return "Hello Falsk"
    

@app.route("/api/v1/add_location", methods=['POST'])
def add_location():
    """
        json_payload: {location_name: "SAS", location_description: "region belongs to metro"}

    """
    try:
        json_data = request.get_json(force=True)
        loc_name = json_data.get('location_name')
        loc_desc = json_data.get('location_description')
        res = db_handle['locations'].insert({
            'location_name' : loc_name,
            'location_description': loc_desc
        })
        if res:
            response = {'status':True, 'message':"location added"}
        else:
            response = {'status':False, 'message':"location {} was not added".format(loc_name)}
    except Exception as e:
        response = {'status':False, 'message':"service error {}".format(str(e))}
    return Response(json.dumps(response, default=json_util.default), mimetype="application/json")


@app.route("/api/v1/all_locations", methods=['GET'])
def list_all_locations():
    """
        Get list of all locations
    """
    try:
        locs = db_handle['locations'].find({})
        if locs.count()>0:
            loc_list= list()
            for loc in locs:
                loc_list.append({'location_id':loc.get('_id'), 'location_name':loc.get('location_name'), 'location_description':loc.get('location_description')})
            if loc_list:
                response = {'status': True, "locations": loc_list}
            else:
                response = {'status': False}
    except Exception as e:
        response = {'status':False, 'message':"service error {}".format(str(e))}
    return Response(json.dumps(response, default=json_util.default), mimetype="application/json")


@app.route("/api/v1/location/<location_id>", methods=['GET'])
def get_location_details(location_id):
    """
        Get location details
    """
    try:
        res = db_handle['locations'].find_one({'_id' : ObjectId(location_id)})
        if res:
            response = {'status':True, 'data':res}
        else:
            response = {'status':False, 'message':"location {} was not found".format(location_id)}
    except Exception as e:
        response = {'status':False, 'message':"service error {}".format(str(e))}
    return Response(json.dumps(response, default=json_util.default), mimetype="application/json")


@app.route("/api/v1/location/<location_id>", methods=['PUT'])
def update_location(location_id):
    """
        payload : {"location_name": "Center_costa", "location_description": "banglore"}
    """
    try:
        json_data = request.get_json(force=True)
        upd_items = dict()
        if json_data.get('location_name'):
            upd_items['location_name'] = json_data.get('location_name')
        if json_data.get('location_description'):
            upd_items['location_description'] = json_data.get('location_description') 
        upd_res = db_handle['locations'].update_one({'_id':ObjectId(location_id)}, {"$set": upd_items})
        if upd_res:
            response = {'status':True, 'message': "location updated"}
        else:
            response = {'status':False, 'message':"location {} was not updated".format(location_id)}
    except Exception as e:
        response = {'status':False, 'message':"service error {}".format(str(e))}
    return Response(json.dumps(response, default=json_util.default), mimetype="application/json")


@app.route("/api/v1/location/<location_id>", methods=['DELETE'])
def delete_location(location_id):
    """
        Deletes the location
    """
    try:
        del_res = db_handle['locations'].delete_one({ '_id':ObjectId(location_id)})
        if del_res.deleted_count == 1:
            response = {'status':True, 'message': "location deleted"}
        else:
            response = {'status':False, 'message':"location {} was not deleted".format(location_id)}
    except Exception as e:
        response = {'status':False, 'message':"service error {}".format(str(e))}
    return Response(json.dumps(response, default=json_util.default), mimetype="application/json")


@app.route("/api/v1/<location_id>/add_department", methods=['POST'])
def add_department(location_id):
    """
        json_payload: {"department_name": "BAKERY", "department_type": "Food"}

    """
    try:
        json_data = request.get_json(force=True)
        department_name = json_data.get('department_name')
        department_type = json_data.get('department_type')
        res = db_handle['departments'].insert({
            'location_id' : ObjectId(location_id),
            'department_name': department_name,
            'department_type': department_type
        })
        if res:
            response = {'status':True, 'message':"department added"}
        else:
            response = {'status':False, 'message':"department {} was not added".format(department_name)}
    except Exception as e:
        response = {'status':False, 'message':"service error {}".format(str(e))}
    return Response(json.dumps(response, default=json_util.default), mimetype="application/json")


@app.route("/api/v1/<location_id>/all_departments", methods=['GET'])
def list_departments_of_location(location_id):
    """
        Get departments of a location
    """
    try:
        depts= list()
        dep_data = db_handle['departments'].find({'location_id' : ObjectId(location_id)})
        if dep_data.count()>0:
            for dep in dep_data:
                depts.append({'_id':dep.get('_id'), 'department_name':dep.get('department_name'), 'department_type':dep.get('department_type')})                
            response = {'status':True, 'data': depts}
        else:
            response = {'status':False, 'message':"departments were not found for location{}".format(location_id)}
    except Exception as e:
        response = {'status':False, 'message':"service error {}".format(str(e))}
    return Response(json.dumps(response, default=json_util.default), mimetype="application/json")


@app.route("/api/v1/<location_id>/department/<department_id>", methods=['GET'])
def get_department_details(location_id,department_id):
    """
        Get the details of a department
    """
    try:
        dep_details = db_handle['departments'].find_one({ '_id': ObjectId(department_id), 'location_id' : ObjectId(location_id) })
        if dep_details:
            response = {'status':True, 'data': dep_details}
        else:
            response = {'status':False, 'message':"department details not found{}".format(department_id)}
    except Exception as e:
        response = {'status':False, 'message':"service error {}".format(str(e))}
    return Response(json.dumps(response, default=json_util.default), mimetype="application/json")


@app.route("/api/v1/<location_id>/department/<department_id>", methods=['PUT'])
def update_department(location_id,department_id):
    """
        payload : {"department_name": "BAKERY", "department_type": "Bake Food"}
    """
    try:
        json_data = request.get_json(force=True)
        upd_items = dict()
        if json_data.get('department_name'):
            upd_items['department_name'] = json_data.get('department_name')
        if json_data.get('department_type'):
            upd_items['department_type'] = json_data.get('department_type') 
        upd_res = db_handle['departments'].update_one({'_id':ObjectId(department_id),'location_id' : ObjectId(location_id)}, {"$set": upd_items})        
        if upd_res:
            response = {'status':True, 'message': "department udpated"}
        else:
            response = {'status':False, 'message':"department {} was not updated".format(department_id)}
    except Exception as e:
        response = {'status':False, 'message':"service error {}".format(str(e))}
    return Response(json.dumps(response, default=json_util.default), mimetype="application/json")


@app.route("/api/v1/department/<department_id>", methods=['DELETE'])
def delete_department(department_id):
    """
        Deletes the department
    """
    try:
        del_res = db_handle['departments'].delete_one({ '_id':ObjectId(department_id)})
        if del_res.deleted_count == 1:
            response = {'status':True, 'message': "department deleted"}
        else:
            response = {'status':False, 'message':"department {} was not deleted".format(department_id)}
    except Exception as e:
        response = {'status':False, 'message':"service error {}".format(str(e))}
    return Response(json.dumps(response, default=json_util.default), mimetype="application/json")


@app.route("/api/v1/<location_id>/<department_id>/add_category", methods=['POST'])
def add_category(location_id, department_id):
    """
        json_payload: {"category_name": "Bakery Bread", "category_description": "Bread cooked"}

    """
    try:
        json_data = request.get_json(force=True)
        category_name = json_data.get('category_name')
        category_description = json_data.get('category_description')
        res = db_handle['categories'].insert({
            'department_id' : ObjectId(department_id),
            'category_name': category_name,
            'category_description': category_description
        })
        if res:
            response = {'status':True, 'message':"category added"}
        else:
            response = {'status':False, 'message':"category {} was not added".format(category_name)}
    except Exception as e:
        response = {'status':False, 'message':"service error {}".format(str(e))}
    return Response(json.dumps(response, default=json_util.default), mimetype="application/json")


@app.route("/api/v1/<location_id>/<department_id>/all_categories", methods=['GET'])
def list_categories_of_department(location_id, department_id):
    """
        Get categories of a department
    """
    try:
        category_list= list()
        catg_data = db_handle['categories'].find({'department_id' : ObjectId(department_id)})
        if catg_data.count()>0:
            for catgry in catg_data:
                category_list.append({'_id':catgry.get('_id'), 'category_name':catgry.get('category_name'), 'category_description':catgry.get('category_description')})                
            response = {'status':True, 'data': category_list}
        else:
            response = {'status':False, 'message':"categories were not found for department{}".format(department_id)}
    except Exception as e:
        response = {'status':False, 'message':"service error {}".format(str(e))}
    return Response(json.dumps(response, default=json_util.default), mimetype="application/json")


@app.route("/api/v1/<location_id>/department/<department_id>/category/<category_id>", methods=['GET'])
def get_category_details(location_id,department_id,category_id):
    """
        Get the details of a department
    """
    try:
        catg_details = db_handle['categories'].find_one({ '_id': ObjectId(category_id), 'department_id' : ObjectId(department_id) })
        if catg_details:
            response = {'status':True, 'data': catg_details}
        else:
            response = {'status':False, 'message':"category details not found{}".format(category_id)}
    except Exception as e:
        response = {'status':False, 'message':"service error {}".format(str(e))}
    return Response(json.dumps(response, default=json_util.default), mimetype="application/json")


@app.route("/api/v1/<location_id>/department/<department_id>/category/<category_id>", methods=['PUT'])
def update_category(location_id,department_id,category_id):
    """
        payload : {"category_name": "Bakery Bread", "category_description": "Bread cooked"}
    """
    try:
        json_data = request.get_json(force=True)
        upd_items = dict()
        if json_data.get('category_name'):
            upd_items['category_name'] = json_data.get('category_name')
        if json_data.get('category_description'):
            upd_items['category_description'] = json_data.get('category_description') 
        upd_res = db_handle['categories'].update_one({'_id':ObjectId(category_id),'department_id' : ObjectId(department_id)}, {"$set": upd_items})        
        if upd_res:
            response = {'status':True, 'message': "category udpated"}
        else:
            response = {'status':False, 'message':"category {} was not updated".format(category_id)}
    except Exception as e:
        response = {'status':False, 'message':"service error {}".format(str(e))}
    return Response(json.dumps(response, default=json_util.default), mimetype="application/json")


@app.route("/api/v1/category/<category_id>", methods=['DELETE'])
def delete_category(category_id):
    """
        Deletes the category
    """
    try:
        del_res = db_handle['categories'].delete_one({ '_id':ObjectId(category_id)})
        if del_res.deleted_count == 1:
            response = {'status':True, 'message': "category deleted"}
        else:
            response = {'status':False, 'message':"category {} was not deleted".format(category_id)}
    except Exception as e:
        response = {'status':False, 'message':"service error {}".format(str(e))}
    return Response(json.dumps(response, default=json_util.default), mimetype="application/json")



if __name__ == "main":
    app.run()

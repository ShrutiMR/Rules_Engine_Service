import json
import csv
from flask import Flask, request, jsonify
from Utils import *
from Customer import *


app = Flask(__name__)

class RulesEngine:

    def __init__(self, csv_file_path, utils):
        self.csv_file_path = csv_file_path
        self.utils = utils

    def formatInput(self, input_data):
        format_input = json.loads(input_data)
        customer_info = Customer(format_input['customer']['name'], format_input['customer']['state'])
        print(format_input.keys(), type(format_input.keys()))
        if 'income' in format_input:
            return self.evaluateRule(format_input['name'], format_input['income'], customer_info)
        elif 'age' in format_input:
            return self.evaluateRule(format_input['name'], format_input['age'], customer_info)
        
    def performAction(self, req_action, rule_condition, customer_info):
        req_action_parts = req_action.split()
        req_action_type = req_action_parts[0]

        if req_action_type == 'initial_state':
            new_state = 'accept_state'
            customer_info.set_state(new_state)
            transition_msg = f"State transition: {customer_info.name} -> {new_state}"
            print(f"State transition: {customer_info.name} -> {new_state}")

    def evaluateRule(self, rule_name, rule_condition, customer_info):
        existing_rows = self.utils.getExistingRows(self.csv_file_path)

        req_condition = ''
        req_action = ''
        for row in existing_rows:
            if row[1] == rule_name:
                req_condition = row[2]
                req_action = row[3]
                break
        
        prev_state = customer_info.state
        if self.utils.checkConditions(rule_condition, req_condition):
            self.utils.performAction(req_action, rule_condition, customer_info)
            return 'Rule satisfied', f"State transition of {customer_info.name}: {prev_state} -> {customer_info.state}"
        else:
            new_state = 'reject_state'
            customer_info.set_state(new_state)
            return 'Rule not satisfied', f"State transition of {customer_info.name}: {prev_state} -> {customer_info.state}"


rule_engine = RulesEngine("rules_engine_db/RulesFile.csv", Utils())

@app.route('/rules-engine', methods=['GET'])
def evaluate_rule():
    try:
        input_data = request.get_json()
        res, transition_msg = rule_engine.formatInput(input_data)
        return jsonify({'status': 'ok', 'message': 'Rule engine success!', 'result': res, 'transition': transition_msg}), 200

    except ValueError as ve:
        raise ValueError(str(ve))
        
    except Exception as e:
        raise Exception(str(e))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=9002)
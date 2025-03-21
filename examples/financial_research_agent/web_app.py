from flask import Flask, render_template, request, jsonify
import asyncio
from .manager import FinancialResearchManager
from asgiref.sync import async_to_sync
from agents import trace, custom_span

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    query = request.json.get('query')
    if not query:
        return jsonify({'error': 'No query provided'}), 400
    
    try:
        async def run_analysis():
            mgr = FinancialResearchManager()
            results = []
            agent_details = {}
            
            class ResultCollector:
                def update_item(self, name, message, is_done=False, hide_checkmark=False):
                    results.append({'name': name, 'message': message, 'is_done': is_done})
                    if name not in agent_details:
                        agent_details[name] = {
                            'input': None,
                            'output': None,
                            'status': 'running',
                            'details': []
                        }
                    agent_details[name]['output'] = message
                    if is_done:
                        agent_details[name]['status'] = 'completed'
                
                def mark_item_done(self, name):
                    if name in agent_details:
                        agent_details[name]['status'] = 'completed'
                
                def end(self):
                    pass
            
            mgr.printer = ResultCollector()
            
            # Create a trace for the entire analysis
            with trace("Financial Research Analysis") as current_trace:
                # Capture the input query
                agent_details['input'] = {'query': query}
                
                # Run the analysis
                await mgr.run(query)
                
                # Capture the final outputs from each agent
                for name, details in agent_details.items():
                    if name in ['planner', 'search', 'writer', 'verifier']:
                        with custom_span(f"{name}_output") as span:
                            if hasattr(mgr, f'_{name}_result'):
                                result = getattr(mgr, f'_{name}_result')
                                details['details'].append({
                                    'type': 'output',
                                    'content': str(result)
                                })
            
            return {
                'progress': results,
                'agent_details': agent_details,
                'trace_id': current_trace.trace_id
            }

        result_data = async_to_sync(run_analysis)()
        
        return jsonify({
            'status': 'success',
            'results': result_data['progress'],
            'agent_details': result_data['agent_details'],
            'trace_id': result_data['trace_id']
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True) 
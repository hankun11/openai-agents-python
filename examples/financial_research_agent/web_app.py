from flask import Flask, render_template, request, jsonify
import asyncio
from .manager import FinancialResearchManager
from asgiref.sync import async_to_sync

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
        # Create an async function to run the analysis
        async def run_analysis():
            mgr = FinancialResearchManager()
            results = []
            report_data = {
                'progress': results,
                'report': None,
                'follow_up': None,
                'verification': None
            }
            
            # Override the printer to collect results
            class ResultCollector:
                def update_item(self, name, message, is_done=False, hide_checkmark=False):
                    results.append({'name': name, 'message': message, 'is_done': is_done})
                    if name == "final_report":
                        report_data['report'] = message
                
                def mark_item_done(self, name):
                    pass
                
                def end(self):
                    pass
            
            mgr.printer = ResultCollector()
            await mgr.run(query)
            return report_data

        # Run the async function using async_to_sync
        result_data = async_to_sync(run_analysis)()
        
        return jsonify({
            'status': 'success',
            'results': result_data['progress'],
            'report': result_data['report']
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True) 